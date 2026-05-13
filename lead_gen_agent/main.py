"""
AI Lead Generation Agent — CLI entry point.

Usage:
    python -m lead_gen_agent.main
    python -m lead_gen_agent.main "We sell HR software for startups in India and the US"
    python -m lead_gen_agent.main --input description.txt --output leads.json
"""
from __future__ import annotations
import io
import json
import sys
import warnings
import urllib3
warnings.filterwarnings("ignore", category=urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)
import argparse
from datetime import datetime
from pathlib import Path

# Ensure UTF-8 output on Windows terminals
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
if sys.stderr.encoding and sys.stderr.encoding.lower() != "utf-8":
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.table import Table
from rich import box

from .config import GROQ_API_KEY
from .models import Lead, LeadType
from .pipeline import run_pipeline
from .excel_exporter import export_to_excel

console = Console(highlight=True)

_LEAD_TYPE_STYLE = {
    LeadType.HOT: "[bold red]HOT[/bold red]",
    LeadType.WARM: "[bold yellow]WARM[/bold yellow]",
    LeadType.COLD: "[bold blue]COLD[/bold blue]",
}

_SCORE_COLOR = lambda s: "green" if s >= 70 else "yellow" if s >= 40 else "red"


def _print_icp(icp) -> None:
    lines = [
        f"[bold]Industries:[/bold] {', '.join(icp.target_industries[:4])}{'...' if len(icp.target_industries) > 4 else ''}",
        f"[bold]Company size:[/bold] {icp.company_size}",
        f"[bold]Geographies:[/bold] {', '.join(icp.geographies)}",
        f"[bold]Pain points:[/bold] {'; '.join(icp.pain_points[:3])}",
        f"\n[italic]{icp.description}[/italic]",
    ]
    console.print(Panel("\n".join(lines), title="[bold cyan]Ideal Customer Profile[/bold cyan]", border_style="cyan"))


def _print_leads_table(leads: list[Lead]) -> None:
    table = Table(
        title=f"[bold green]Top Leads ({len(leads)} total)[/bold green]",
        box=box.ROUNDED,
        show_lines=True,
        header_style="bold magenta",
    )
    table.add_column("Rank", style="dim", width=4, justify="right")
    table.add_column("Company", min_width=18)
    table.add_column("Industry", min_width=14)
    table.add_column("Score", width=7, justify="center")
    table.add_column("Fit", width=6, justify="center")
    table.add_column("Type", width=12)
    table.add_column("Email", min_width=20)
    table.add_column("Reason", min_width=30)

    for rank, lead in enumerate(leads, 1):
        score_str = f"[{_SCORE_COLOR(lead.lead_score)}]{lead.lead_score}[/{_SCORE_COLOR(lead.lead_score)}]"
        table.add_row(
            str(rank),
            f"[link={lead.website}]{lead.company_name}[/link]",
            lead.industry or "-",
            score_str,
            lead.fit_percentage,
            _LEAD_TYPE_STYLE.get(lead.lead_type, lead.lead_type),
            lead.contact_email or "-",
            lead.reason[:120] + ("…" if len(lead.reason) > 120 else ""),
        )

    console.print(table)


def _save_output(leads: list[Lead], out_path: Path) -> None:
    data = [lead.model_dump() for lead in leads]
    # Convert enum to string value
    for d in data:
        d["lead_type"] = d["lead_type"].value if hasattr(d["lead_type"], "value") else d["lead_type"]
    out_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    console.print(f"\n[green]✓[/green] Results saved to [bold]{out_path}[/bold]")


def main() -> None:
    parser = argparse.ArgumentParser(description="AI Lead Generation Agent")
    parser.add_argument("description", nargs="?", help="Business description string")
    parser.add_argument("--input", "-i", help="Text file with business description")
    parser.add_argument("--output", "-o", help="Output JSON file path")
    args = parser.parse_args()

    if not GROQ_API_KEY:
        console.print("[bold red]Error:[/bold red] GROQ_API_KEY not set. Add it to .env or environment.")
        sys.exit(1)

    # Get business description
    if args.input:
        description = Path(args.input).read_text(encoding="utf-8").strip()
    elif args.description:
        description = args.description.strip()
    else:
        console.print("[bold cyan]AI Lead Generation Agent[/bold cyan]")
        description = console.input("[bold]Enter your business description:[/bold] ").strip()

    if not description:
        console.print("[red]No business description provided.[/red]")
        sys.exit(1)

    console.print(Panel(description, title="[bold]Business Description[/bold]", border_style="bright_black"))

    # Determine output path
    if args.output:
        out_path = Path(args.output)
    else:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_path = Path(f"leads_{ts}.json")

    icp = None
    leads: list[Lead] = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        TimeElapsedColumn(),
        console=console,
        transient=False,
    ) as progress:
        task = progress.add_task("Starting pipeline...", total=None)

        def on_step(msg: str) -> None:
            progress.update(task, description=msg)

        try:
            icp, leads = run_pipeline(description, on_step=on_step)
        except Exception as exc:
            console.print(f"\n[bold red]Pipeline error:[/bold red] {exc}")
            sys.exit(1)

    console.print()
    if icp:
        _print_icp(icp)

    console.print()
    if leads:
        _print_leads_table(leads)
        _save_output(leads, out_path)

        # Excel export
        excel_path = out_path.with_suffix(".xlsx")
        export_to_excel(leads, icp, description, excel_path)
        console.print(f"[green]✓[/green] Excel saved to  [bold]{excel_path}[/bold]")

        hot = sum(1 for l in leads if l.lead_type == LeadType.HOT)
        warm = sum(1 for l in leads if l.lead_type == LeadType.WARM)
        cold = sum(1 for l in leads if l.lead_type == LeadType.COLD)
        console.print(
            f"\n[bold]Summary:[/bold] "
            f"[red]{hot} Hot[/red]  [yellow]{warm} Warm[/yellow]  [blue]{cold} Cold[/blue]  "
            f"— avg score {sum(l.lead_score for l in leads)//len(leads)}"
        )
    else:
        console.print("[yellow]No leads found.[/yellow]")


if __name__ == "__main__":
    main()

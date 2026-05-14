"""Orchestrates the full lead generation pipeline."""
from __future__ import annotations
from typing import List, Callable, Optional
from .models import ICP, Company, Lead
from .icp_generator import generate_icp
from .searcher import search_companies
from .scraper import scrape_all
from .scorer import score_leads


def run_pipeline(
    business_description: str,
    location_filter: Optional[str] = None,
    on_step: Optional[Callable[[str], None]] = None,
) -> tuple[ICP, List[Lead]]:
    """
    Full pipeline: description → ICP → search → scrape → score → leads.
    `location_filter` biases scoring toward a specific city/country.
    `on_step` is an optional callback for progress reporting.
    Returns (icp, sorted_leads).
    """

    def _step(msg: str) -> None:
        if on_step:
            on_step(msg)

    _step("Generating Ideal Customer Profile...")
    icp: ICP = generate_icp(business_description)

    _step(f"Searching the web with {len(icp.search_queries)} queries...")
    companies: List[Company] = search_companies(icp)
    _step(f"Found {len(companies)} unique companies.")

    _step(f"Scraping {len(companies)} company websites...")
    companies = scrape_all(companies)
    scraped_ok = sum(1 for c in companies if not c.scrape_error)
    _step(f"Scraped {scraped_ok}/{len(companies)} sites successfully.")

    loc_msg = f" (filtering for: {location_filter})" if location_filter else ""
    _step(f"Scoring and ranking leads{loc_msg}...")
    leads: List[Lead] = score_leads(companies, icp, location_filter=location_filter)

    leads.sort(key=lambda l: l.lead_score, reverse=True)
    _step(f"Done. Ranked {len(leads)} leads.")

    return icp, leads

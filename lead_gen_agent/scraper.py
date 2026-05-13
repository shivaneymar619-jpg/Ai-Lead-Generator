"""Scrape company homepage to enrich Company objects."""
from __future__ import annotations
import re
import time
import warnings
from typing import List
import requests
from bs4 import BeautifulSoup
from .models import Company
from .config import SCRAPE_TIMEOUT, SCRAPE_DELAY, RAW_TEXT_LIMIT

warnings.filterwarnings("ignore", message="Unverified HTTPS request")

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

_EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")
_SKIP_EMAIL_TOKENS = {"example", "noreply", "no-reply", "privacy", "legal", "abuse"}


def _extract_email(html: str) -> str:
    emails = _EMAIL_RE.findall(html)
    for e in emails:
        if not any(t in e.lower() for t in _SKIP_EMAIL_TOKENS):
            return e
    return ""


def _visible_text(soup: BeautifulSoup) -> str:
    for tag in soup(["script", "style", "noscript", "nav", "footer", "header", "aside"]):
        tag.decompose()
    return " ".join(soup.get_text(separator=" ").split())


def scrape_company(company: Company) -> Company:
    try:
        resp = requests.get(
            company.website,
            headers=_HEADERS,
            timeout=SCRAPE_TIMEOUT,
            verify=False,
            allow_redirects=True,
        )
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        # Meta description → best short description
        meta = soup.find("meta", attrs={"name": re.compile(r"description", re.I)})
        meta_text = (meta.get("content") or "").strip() if meta else ""

        # OG description fallback
        og = soup.find("meta", property="og:description")
        og_text = (og.get("content") or "").strip() if og else ""

        description = meta_text or og_text or (company.description or "")

        visible = _visible_text(soup)
        email = _extract_email(resp.text)

        company.description = description[:500] if description else None
        company.contact_email = email or None
        company.raw_text = visible[:RAW_TEXT_LIMIT]

    except requests.exceptions.Timeout:
        company.scrape_error = "timeout"
    except requests.exceptions.SSLError:
        company.scrape_error = "ssl_error"
    except Exception as exc:
        company.scrape_error = str(exc)[:80]

    return company


def scrape_all(companies: List[Company]) -> List[Company]:
    enriched = []
    for company in companies:
        enriched.append(scrape_company(company))
        time.sleep(SCRAPE_DELAY)
    return enriched

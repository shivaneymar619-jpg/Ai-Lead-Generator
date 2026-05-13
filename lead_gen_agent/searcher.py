"""Search the web for companies matching ICP search queries."""
from __future__ import annotations
import re
from urllib.parse import urlparse
from typing import List
from ddgs import DDGS
from .models import Company, ICP
from .config import MAX_RESULTS_PER_QUERY, MAX_COMPANIES

# Skip social media, news, directories, government, and list/article sites
_BLOCKLIST = {
    "linkedin.com", "facebook.com", "twitter.com", "x.com",
    "instagram.com", "youtube.com", "wikipedia.org", "reddit.com",
    "glassdoor.com", "indeed.com", "crunchbase.com", "bloomberg.com",
    "forbes.com", "techcrunch.com", "medium.com", "quora.com",
    "amazon.com", "google.com", "bing.com", "yahoo.com",
    # Startup directories and list sites
    "failory.com", "topstartups.io", "growthlist.co", "f6s.com",
    "tracxn.com", "angellist.com", "wellfound.com", "ycombinator.com",
    "startupindia.gov.in", "inc42.com", "yourstory.com", "entrackr.com",
    "business-standard.com", "economictimes.com", "livemint.com",
    "hindustantimes.com", "ndtv.com", "timesofindia.com",
    "techcrunch.com", "venturebeat.com", "wsj.com", "cnbc.com",
    "gov.uk", "gov.in", "usa.gov", "usembassy.gov",
    "britannica.com", "wikiwand.com", "companiesmarketcap.com",
    "nseindia.com", "bseindia.com",
}

# URL path patterns that indicate list/article pages, not company homepages
_PATH_BLOCKLIST = [
    "/blog/", "/news/", "/article/", "/post/", "/stories/",
    "/list-of-", "/top-", "/best-", "/startups-in-",
]


def _root_domain(url: str) -> str:
    host = urlparse(url).netloc.lower()
    return re.sub(r"^www\.", "", host)


def _is_valid(url: str) -> bool:
    domain = _root_domain(url)
    if not domain or any(b in domain for b in _BLOCKLIST):
        return False
    path = urlparse(url).path.lower()
    if any(p in path for p in _PATH_BLOCKLIST):
        return False
    return True


def search_companies(icp: ICP) -> List[Company]:
    """Run each ICP search query through DuckDuckGo and return unique companies."""
    seen_domains: set[str] = set()
    companies: List[Company] = []

    with DDGS() as ddgs:
        for query in icp.search_queries:
            if len(companies) >= MAX_COMPANIES:
                break
            try:
                results = list(ddgs.text(query, max_results=MAX_RESULTS_PER_QUERY))
            except Exception:
                continue

            for r in results:
                url: str = r.get("href", "")
                title: str = r.get("title", "")
                body: str = r.get("body", "")

                if not url or not _is_valid(url):
                    continue

                domain = _root_domain(url)
                if domain in seen_domains:
                    continue

                parsed = urlparse(url)
                homepage = f"{parsed.scheme}://{parsed.netloc}"

                seen_domains.add(domain)
                companies.append(
                    Company(
                        name=title.split("|")[0].split("-")[0].strip() or domain,
                        website=homepage,
                        description=body[:300] if body else None,
                    )
                )

                if len(companies) >= MAX_COMPANIES:
                    break

    return companies

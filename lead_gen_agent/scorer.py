"""Batch-score all companies against the ICP using Groq."""
from __future__ import annotations
import json
from groq import Groq
from typing import List
from .config import GROQ_API_KEY, GROQ_MODEL
from .models import Company, ICP, Lead, LeadType

_SYSTEM = """You are a B2B sales intelligence expert. You receive an Ideal Customer Profile (ICP)
and a list of scraped company summaries. You score each company as a potential sales lead.

Scoring rubric (0-100):
  90-100  Perfect ICP match - industry, size, geography, pain points all align
  70-89   Strong match - most ICP criteria met
  50-69   Partial match - some criteria met, worth nurturing
  30-49   Weak match - limited alignment
  0-29    Poor fit

lead_type mapping:
  Hot   -> score 70-100
  Warm  -> score 40-69
  Cold  -> score 0-39

Return a JSON array only - no prose, no markdown fences."""

_COMPANY_TEMPLATE = """Company #{i}
Name: {name}
Website: {website}
Description: {description}
Page excerpt: {raw_text}
---"""

_LEAD_SCHEMA = """{
  "company_name": "...",
  "website": "...",
  "industry": "...",
  "description": "one sentence about the company",
  "contact_email": "...",
  "lead_score": 0-100,
  "fit_percentage": "0-100%",
  "reason": "2-3 sentences explaining the score",
  "lead_type": "Hot | Warm | Cold"
}"""


def score_leads(companies: List[Company], icp: ICP) -> List[Lead]:
    if not companies:
        return []

    client = Groq(api_key=GROQ_API_KEY)

    icp_block = (
        f"Target Industries: {', '.join(icp.target_industries)}\n"
        f"Company Size: {icp.company_size}\n"
        f"Geographies: {', '.join(icp.geographies)}\n"
        f"Pain Points: {'; '.join(icp.pain_points)}\n"
        f"Keywords: {', '.join(icp.keywords)}\n"
        f"ICP Summary: {icp.description}"
    )

    companies_block = "\n".join(
        _COMPANY_TEMPLATE.format(
            i=i + 1,
            name=c.name,
            website=c.website,
            description=c.description or "N/A",
            raw_text=(c.raw_text or "")[:600],
        )
        for i, c in enumerate(companies)
    )

    prompt = (
        f"## ICP\n{icp_block}\n\n"
        f"## Companies to score\n{companies_block}\n\n"
        f"Return a JSON array with one object per company using this schema:\n{_LEAD_SCHEMA}\n\n"
        f"Preserve the original contact_email from company data where available. "
        f"Array must have exactly {len(companies)} items in the same order."
    )

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        temperature=0.2,
        messages=[
            {"role": "system", "content": _SYSTEM},
            {"role": "user", "content": prompt},
        ],
    )

    raw = response.choices[0].message.content.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.rsplit("```", 1)[0].strip()

    data: list = json.loads(raw)

    leads: List[Lead] = []
    for item, company in zip(data, companies):
        if not item.get("contact_email") and company.contact_email:
            item["contact_email"] = company.contact_email
        if not item.get("contact_email"):
            item["contact_email"] = ""

        item["lead_score"] = max(0, min(100, int(item.get("lead_score", 0))))
        score = item["lead_score"]
        item["lead_type"] = (
            LeadType.HOT if score >= 70
            else LeadType.WARM if score >= 40
            else LeadType.COLD
        ).value

        fp = str(item.get("fit_percentage", score))
        item["fit_percentage"] = fp if "%" in fp else f"{fp}%"

        leads.append(Lead(**item))

    return leads

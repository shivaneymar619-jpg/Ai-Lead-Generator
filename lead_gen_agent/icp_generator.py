"""Generate Ideal Customer Profile from a business description using Groq."""
from __future__ import annotations
import json
from groq import Groq
from .config import GROQ_API_KEY, GROQ_MODEL
from .models import ICP

_SYSTEM = """You are a B2B sales strategist and ICP (Ideal Customer Profile) expert.
Given a business description you produce precise ICPs and targeted lead-search queries.
Always respond with valid JSON only - no markdown fences, no commentary."""

_SCHEMA = """{
  "target_industries": ["5-8 specific verticals this business should target"],
  "company_size":      "employee or revenue range, e.g. '20-500 employees'",
  "geographies":       ["target countries or regions"],
  "pain_points":       ["5-7 pain points the business solves for customers"],
  "keywords":          ["12-15 keywords that describe ideal customers"],
  "search_queries":    ["8-10 web-search queries to discover matching companies"],
  "description":       "2-3 sentence ICP summary"
}"""


def generate_icp(business_description: str) -> ICP:
    client = Groq(api_key=GROQ_API_KEY)

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        temperature=0.3,
        messages=[
            {"role": "system", "content": _SYSTEM},
            {
                "role": "user",
                "content": (
                    f"Business description:\n{business_description}\n\n"
                    f"Return JSON matching exactly this schema:\n{_SCHEMA}"
                ),
            },
        ],
    )

    raw = response.choices[0].message.content.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.rsplit("```", 1)[0].strip()

    data = json.loads(raw)
    return ICP(**{k: v for k, v in data.items() if k in ICP.model_fields})

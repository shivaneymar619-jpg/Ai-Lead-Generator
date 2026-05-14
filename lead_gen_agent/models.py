from __future__ import annotations
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class LeadType(str, Enum):
    HOT = "Hot"
    WARM = "Warm"
    COLD = "Cold"


class ICP(BaseModel):
    target_industries: List[str]
    company_size: str
    geographies: List[str]
    pain_points: List[str]
    keywords: List[str]
    search_queries: List[str]
    description: str


class Company(BaseModel):
    name: str
    website: str
    industry: Optional[str] = None
    description: Optional[str] = None
    contact_email: Optional[str] = None
    raw_text: Optional[str] = None
    scrape_error: Optional[str] = None


class Lead(BaseModel):
    company_name: str
    website: str
    industry: str = ""
    location: str = ""          # city, country or region
    description: str = ""
    contact_email: str = ""
    lead_score: int = Field(ge=0, le=100)
    fit_percentage: str
    reason: str
    lead_type: LeadType

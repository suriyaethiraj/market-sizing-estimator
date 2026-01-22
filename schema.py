from __future__ import annotations
from typing import List, Optional, Dict
from pydantic import BaseModel, Field


class MarketInput(BaseModel):
    product_description: str
    industry_vertical: str
    geographies: List[str]
    company_stage: str        # Startup / SMB / Enterprise
    target_persona: str
    pricing_model: str        # SaaS / Transactional / Marketplace / Hardware / Freemium
    avg_price: float          # ACV or price per unit
    price_unit: str           # per user/month, per transaction, per seat/year, etc.
    custom_research: Optional[str] = None


class ScenarioValue(BaseModel):
    low: float
    mid: float
    high: float
    unit: str = "USD"


class Assumption(BaseModel):
    label: str
    value: str
    source: str
    confidence: str  # High / Medium / Low


class MethodologyResult(BaseModel):
    methodology: str          # Top-Down / Bottom-Up / Value-Theory
    tam: ScenarioValue
    sam: ScenarioValue
    som: ScenarioValue
    key_assumptions: List[Assumption]
    narrative: str


class YearProjection(BaseModel):
    year: int
    tam: float
    sam: float
    som: float
    cagr_applied: float


class SensitivityAxis(BaseModel):
    variable: str
    values: List[str]
    som_impacts: List[float]   # SOM mid for each value


class MarketSizingReport(BaseModel):
    title: str
    product_description: str
    industry: str
    geographies: List[str]
    methodology_results: List[MethodologyResult]
    reconciled_tam: ScenarioValue
    reconciled_sam: ScenarioValue
    reconciled_som: ScenarioValue
    five_year_projection: List[YearProjection]
    sensitivity_axes: List[SensitivityAxis]
    world_bank_data_used: List[str]
    executive_summary: str
    investor_narrative: str    # 3-sentence pitch-ready framing
    confidence_rating: str     # High / Medium / Low — overall
    key_risks: List[str]
    generated_at: str

"""Pydantic schemas for Dashboard and Analytics (DASH-001, DASH-002, DASH-003)."""
from pydantic import BaseModel, ConfigDict
from typing import Optional
from app.schemas.scan import ScanSummaryResponse


class ComplianceBreakdown(BaseModel):
    compliant: int = 0
    non_compliant: int = 0
    partial: int = 0
    manual_review_required: int = 0


class NutritionBreakdown(BaseModel):
    excellent: int = 0
    good: int = 0
    moderate: int = 0
    high_risk: int = 0
    insufficient_data: int = 0


class DashboardStats(BaseModel):
    total_scans: int = 0
    average_compliance_score: Optional[float] = None
    average_nutrition_score: Optional[float] = None
    compliance_breakdown: ComplianceBreakdown
    nutrition_breakdown: NutritionBreakdown
    recent_scans: list[ScanSummaryResponse] = []

    model_config = ConfigDict(from_attributes=True)

"""Pydantic schemas for Scan, ScanField, and Finding endpoints."""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Any
from datetime import datetime
from app.models.scan import ScanStatus, ComplianceStatus, NutritionStatus
from app.models.finding import FindingType, FindingSeverity
from app.schemas.rules import RuleResponse


class ScanFieldResponse(BaseModel):
    id: str
    field_name: str
    field_category: str
    raw_value: Optional[str] = None
    normalized_value: Optional[str] = None
    unit: Optional[str] = None
    confidence_score: Optional[float] = None
    is_present: bool
    is_readable: bool
    extraction_method: str
    metadata_payload: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(from_attributes=True)


class FindingResponse(BaseModel):
    id: str
    rule_id: Optional[str] = None
    field_name: str
    module: str
    finding_type: FindingType
    severity: FindingSeverity
    title: str
    message: str
    observed_value: Optional[str] = None
    expected_condition: Optional[str] = None
    is_font_size_flag: bool
    requires_manual_review: bool
    rule: Optional[RuleResponse] = None

    model_config = ConfigDict(from_attributes=True)


class ScanSummaryResponse(BaseModel):
    id: str
    user_id: str
    rule_version_id: str
    product_name: Optional[str] = None
    brand_name: Optional[str] = None
    category: str
    overall_status: ScanStatus
    compliance_status: ComplianceStatus
    nutrition_status: NutritionStatus
    compliance_score: Optional[float] = None
    nutrition_score: Optional[float] = None
    has_font_size_flags: bool
    is_data_insufficient: bool
    ocr_confidence_avg: Optional[float] = None
    scan_duration_ms: Optional[int] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class ScanDetailResponse(ScanSummaryResponse):
    original_image_url: str
    processed_image_url: Optional[str] = None
    pdf_report_url: Optional[str] = None
    ocr_raw_text: Optional[str] = None
    uncertainty_flags: list[Any] = []
    barcode: Optional[str] = None
    barcode_format: Optional[str] = None
    barcode_country: Optional[str] = None
    qr_code: Optional[str] = None
    barcode_metadata: Optional[dict[str, Any]] = None
    fields: list[ScanFieldResponse] = []
    findings: list[FindingResponse] = []
    rule_version_tag: Optional[str] = None
    evidence_images: list[str] = []

    model_config = ConfigDict(from_attributes=True)


class BatchScanResponse(BaseModel):
    total_uploaded: int
    successful_scans: list[ScanDetailResponse]
    failed_uploads: list[dict[str, str]] = []


class PaginatedScanHistoryResponse(BaseModel):
    items: list[ScanSummaryResponse]
    total: int
    page: int
    per_page: int
    total_pages: int

"""Scan record model with independent compliance and nutritional scoring (SCORE-001, SCORE-002)."""
import uuid
import enum
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Text, Float, Integer, ForeignKey, JSON, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class ScanStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ComplianceStatus(str, enum.Enum):
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIAL = "partial"
    MANUAL_REVIEW_REQUIRED = "manual_review_required"
    PENDING = "pending"


class NutritionStatus(str, enum.Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    MODERATE = "moderate"
    HIGH_RISK = "high_risk"
    INSUFFICIENT_DATA = "insufficient_data"
    PENDING = "pending"


class Scan(Base):
    __tablename__ = "scans"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    rule_version_id: Mapped[str] = mapped_column(String(36), ForeignKey("rule_versions.id"), nullable=False, index=True)

    # Product Metadata
    product_name: Mapped[str] = mapped_column(String(255), nullable=True)
    brand_name: Mapped[str] = mapped_column(String(255), nullable=True)
    category: Mapped[str] = mapped_column(String(100), default="packaged_food", nullable=False)

    # Evidence Storage (SCAN-003, SEC-006)
    original_image_path: Mapped[str] = mapped_column(String(500), nullable=False)
    processed_image_path: Mapped[str] = mapped_column(String(500), nullable=True)
    pdf_report_path: Mapped[str] = mapped_column(String(500), nullable=True)

    # OCR Output & Metadata
    ocr_raw_text: Mapped[str] = mapped_column(Text, nullable=True)
    ocr_confidence_avg: Mapped[float] = mapped_column(Float, nullable=True)

    # Independent Scores (SCORE-001, SCORE-002: Completely separated)
    compliance_score: Mapped[float] = mapped_column(Float, nullable=True)  # 0.0 - 100.0
    nutrition_score: Mapped[float] = mapped_column(Float, nullable=True)   # 0.0 - 100.0

    # Categorical Statuses
    overall_status: Mapped[ScanStatus] = mapped_column(SAEnum(ScanStatus, name="scan_statuses"), default=ScanStatus.PENDING, nullable=False)
    compliance_status: Mapped[ComplianceStatus] = mapped_column(SAEnum(ComplianceStatus, name="compliance_statuses"), default=ComplianceStatus.PENDING, nullable=False)
    nutrition_status: Mapped[NutritionStatus] = mapped_column(SAEnum(NutritionStatus, name="nutrition_statuses"), default=NutritionStatus.PENDING, nullable=False)

    # Guardrail Indicators (LM-005, SCORE-004)
    has_font_size_flags: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_data_insufficient: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    uncertainty_flags: Mapped[list] = mapped_column(JSON, default=list, nullable=False)

    # Performance / Timing
    scan_duration_ms: Mapped[int] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    completed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="scans")
    rule_version: Mapped["RuleVersion"] = relationship("RuleVersion", back_populates="scans")
    fields: Mapped[list["ScanField"]] = relationship("ScanField", back_populates="scan", cascade="all, delete-orphan", lazy="select")
    findings: Mapped[list["Finding"]] = relationship("Finding", back_populates="scan", cascade="all, delete-orphan", lazy="select")

    def __repr__(self) -> str:
        return f"<Scan {self.id} compliance={self.compliance_score} nutrition={self.nutrition_score}>"

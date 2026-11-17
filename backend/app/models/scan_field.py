"""ScanField model representing extracted label declarations and nutrients."""
import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Text, Float, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class ScanField(Base):
    __tablename__ = "scan_fields"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    scan_id: Mapped[str] = mapped_column(String(36), ForeignKey("scans.id", ondelete="CASCADE"), nullable=False, index=True)

    field_name: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g., net_quantity, mrp, energy_kcal
    field_category: Mapped[str] = mapped_column(String(50), default="declaration", nullable=False)  # declaration, nutrition, ingredient

    # Raw OCR evidence vs Normalized Value (OCR-007: Zero fabrication)
    raw_value: Mapped[str] = mapped_column(Text, nullable=True)
    normalized_value: Mapped[str] = mapped_column(Text, nullable=True)
    unit: Mapped[str] = mapped_column(String(50), nullable=True)

    # Reliability & Confidence
    confidence_score: Mapped[float] = mapped_column(Float, nullable=True)  # 0.0 - 100.0 from Tesseract
    is_present: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_readable: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    extraction_method: Mapped[str] = mapped_column(String(50), default="regex", nullable=False)

    metadata_payload: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    scan: Mapped["Scan"] = relationship("Scan", back_populates="fields")

    def __repr__(self) -> str:
        return f"<ScanField {self.field_name}={self.normalized_value} present={self.is_present}>"

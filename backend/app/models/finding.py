"""Finding model for granular compliance and nutrition check results (LM-003, LM-004, NUT-006)."""
import uuid
import enum
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Text, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class FindingType(str, enum.Enum):
    PASS = "pass"
    FAIL = "fail"
    NOT_FOUND = "not_found"
    UNCERTAIN = "uncertain"
    MANUAL_REVIEW = "manual_review"
    INFO = "info"


class FindingSeverity(str, enum.Enum):
    CRITICAL = "critical"
    MAJOR = "major"
    MINOR = "minor"
    INFO = "info"


class Finding(Base):
    __tablename__ = "findings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    scan_id: Mapped[str] = mapped_column(String(36), ForeignKey("scans.id", ondelete="CASCADE"), nullable=False, index=True)
    rule_id: Mapped[str] = mapped_column(String(36), ForeignKey("rules.id", ondelete="SET NULL"), nullable=True, index=True)

    field_name: Mapped[str] = mapped_column(String(100), nullable=False)
    module: Mapped[str] = mapped_column(String(50), default="legal_metrology", nullable=False)  # legal_metrology, nutrition, allergen

    finding_type: Mapped[FindingType] = mapped_column(SAEnum(FindingType, name="finding_types"), nullable=False)
    severity: Mapped[FindingSeverity] = mapped_column(SAEnum(FindingSeverity, name="finding_severities"), default=FindingSeverity.INFO, nullable=False)

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    observed_value: Mapped[str] = mapped_column(Text, nullable=True)
    expected_condition: Mapped[str] = mapped_column(Text, nullable=True)

    # Physical attribute / scale disclaimer flag (LM-005)
    is_font_size_flag: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    requires_manual_review: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    scan: Mapped["Scan"] = relationship("Scan", back_populates="findings")
    rule: Mapped["Rule"] = relationship("Rule", back_populates="findings")

    def __repr__(self) -> str:
        return f"<Finding {self.finding_type} for {self.field_name}: {self.title}>"

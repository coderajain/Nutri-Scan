"""Versioned Legal Metrology Rules Models (LM-001, LM-006, HIS-003)."""
import uuid
import enum
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Text, ForeignKey, JSON, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base


class RuleSeverity(str, enum.Enum):
    CRITICAL = "critical"
    MAJOR = "major"
    MINOR = "minor"
    RECOMMENDED = "recommended"


class RuleVersion(Base):
    __tablename__ = "rule_versions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    version_tag: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    created_by_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    rules: Mapped[list["Rule"]] = relationship("Rule", back_populates="rule_version", cascade="all, delete-orphan", lazy="select")
    scans: Mapped[list["Scan"]] = relationship("Scan", back_populates="rule_version", lazy="select")

    def __repr__(self) -> str:
        return f"<RuleVersion {self.version_tag} active={self.is_active}>"


class Rule(Base):
    __tablename__ = "rules"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    rule_version_id: Mapped[str] = mapped_column(String(36), ForeignKey("rule_versions.id", ondelete="CASCADE"), nullable=False, index=True)
    rule_code: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    field_name: Mapped[str] = mapped_column(String(100), nullable=False)
    category: Mapped[str] = mapped_column(String(100), default="legal_metrology", nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    legal_reference: Mapped[str] = mapped_column(String(255), nullable=True)  # e.g., Rule 6(1)(a) of LM-PC-2011
    severity: Mapped[RuleSeverity] = mapped_column(SAEnum(RuleSeverity, name="rule_severities"), default=RuleSeverity.CRITICAL, nullable=False)
    is_mandatory: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    validation_type: Mapped[str] = mapped_column(String(50), nullable=False)  # presence, regex, format, font_size, allergen
    validation_params: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    rule_version: Mapped["RuleVersion"] = relationship("RuleVersion", back_populates="rules")
    findings: Mapped[list["Finding"]] = relationship("Finding", back_populates="rule", lazy="select")

    def __repr__(self) -> str:
        return f"<Rule {self.rule_code}: {self.title}>"

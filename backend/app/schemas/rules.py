"""Pydantic schemas for versioned compliance rules (LM-001, LM-006)."""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Any
from datetime import datetime
from app.models.rule_version import RuleSeverity


class RuleBase(BaseModel):
    rule_code: str = Field(..., pattern=r"^[A-Z0-9\-]+$", description="Code such as LM-R-001")
    title: str = Field(..., min_length=3, max_length=255)
    field_name: str = Field(..., min_length=2, max_length=100)
    category: str = "legal_metrology"
    description: str
    legal_reference: Optional[str] = None
    severity: RuleSeverity = RuleSeverity.CRITICAL
    is_mandatory: bool = True
    validation_type: str = "presence"
    validation_params: dict[str, Any] = Field(default_factory=dict)
    is_active: bool = True


class RuleCreate(RuleBase):
    pass


class RuleResponse(RuleBase):
    id: str
    rule_version_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RuleVersionBase(BaseModel):
    version_tag: str = Field(..., pattern=r"^[A-Za-z0-9\.\-_]+$", description="e.g. LM-PC-2011-v1.0")
    title: str = Field(..., min_length=3, max_length=255)
    description: Optional[str] = None


class RuleVersionCreate(RuleVersionBase):
    is_active: bool = True


class RuleVersionResponse(RuleVersionBase):
    id: str
    is_active: bool
    created_at: datetime
    created_by_id: Optional[str] = None
    rules: list[RuleResponse] = []

    model_config = ConfigDict(from_attributes=True)

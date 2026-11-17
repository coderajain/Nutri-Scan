"""Rules management endpoints with versioning traceability (LM-001, LM-006, HIS-003)."""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from app.models.rule_version import RuleVersion, Rule
from app.schemas.rules import (
    RuleVersionResponse, RuleVersionCreate, RuleResponse, RuleCreate
)
from app.api.deps import get_current_user, require_admin, log_audit_event
import logging

logger = logging.getLogger("nutriscan.api.rules")
router = APIRouter(prefix="/rules", tags=["Regulatory Rules"])


@router.get("/versions", response_model=list[RuleVersionResponse])
def list_rule_versions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lists all configured Legal Metrology and FSSAI rule versions."""
    return db.query(RuleVersion).order_by(RuleVersion.created_at.desc()).all()


@router.get("/versions/active", response_model=RuleVersionResponse)
def get_active_rule_version(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieves the default active statutory rule version."""
    rule_version = db.query(RuleVersion).filter(RuleVersion.is_active == True).first()
    if not rule_version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active rule version found",
        )
    return rule_version


@router.get("/versions/{version_id}", response_model=RuleVersionResponse)
def get_rule_version(
    version_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieves a specific rule version with its associated rules (LM-001, HIS-003)."""
    rule_version = db.query(RuleVersion).filter(RuleVersion.id == version_id).first()
    if not rule_version:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rule version not found")
    return rule_version


@router.post("/versions", response_model=RuleVersionResponse, status_code=status.HTTP_201_CREATED)
def create_rule_version(
    version_in: RuleVersionCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin),
):
    """
    Creates a new rule version (Admin only) (LM-006, SEC-009).
    Existing scans remain permanently linked to their original version.
    """
    existing = db.query(RuleVersion).filter(RuleVersion.version_tag == version_in.version_tag).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Rule version with tag '{version_in.version_tag}' already exists.",
        )

    # If new version is set active, deactivate other versions
    if version_in.is_active:
        db.query(RuleVersion).update({RuleVersion.is_active: False})

    new_version = RuleVersion(
        version_tag=version_in.version_tag,
        title=version_in.title,
        description=version_in.description,
        is_active=version_in.is_active,
        created_by_id=current_admin.id,
    )
    db.add(new_version)
    db.commit()
    db.refresh(new_version)

    log_audit_event(
        db=db,
        user=current_admin,
        action="RULE_VERSION_CREATE",
        resource_type="rule_version",
        resource_id=new_version.id,
        details={"version_tag": new_version.version_tag},
        request=request,
    )
    return new_version


@router.post("/versions/{version_id}/rules", response_model=RuleResponse, status_code=status.HTTP_201_CREATED)
def add_rule_to_version(
    version_id: str,
    rule_in: RuleCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin),
):
    """Adds a statutory rule to a rule version (Admin only)."""
    version = db.query(RuleVersion).filter(RuleVersion.id == version_id).first()
    if not version:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rule version not found")

    new_rule = Rule(
        rule_version_id=version.id,
        rule_code=rule_in.rule_code,
        title=rule_in.title,
        field_name=rule_in.field_name,
        category=rule_in.category,
        description=rule_in.description,
        legal_reference=rule_in.legal_reference,
        severity=rule_in.severity,
        is_mandatory=rule_in.is_mandatory,
        validation_type=rule_in.validation_type,
        validation_params=rule_in.validation_params,
        is_active=rule_in.is_active,
    )
    db.add(new_rule)
    db.commit()
    db.refresh(new_rule)

    log_audit_event(
        db=db,
        user=current_admin,
        action="RULE_ADD",
        resource_type="rule",
        resource_id=new_rule.id,
        details={"rule_code": new_rule.rule_code, "version_id": version.id},
        request=request,
    )
    return new_rule

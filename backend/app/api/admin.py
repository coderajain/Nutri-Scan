"""Administrator management endpoints (AUTH-004, AUTH-006, SEC-003, SEC-009)."""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User, UserRole
from app.models.audit_log import AuditLog
from app.schemas.auth import UserResponse
from app.api.deps import require_admin, log_audit_event
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/admin", tags=["Administrator Operations"])


class RoleUpdateRequest(BaseModel):
    role: UserRole


class AuditLogResponse(BaseModel):
    id: str
    user_id: str | None
    action: str
    resource_type: str
    resource_id: str | None
    ip_address: str | None
    details: dict
    created_at: datetime

    class Config:
        from_attributes = True


@router.get("/users", response_model=list[UserResponse])
def list_system_users(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Lists all registered users and their assigned roles (Admin only)."""
    return db.query(User).order_by(User.created_at.desc()).all()


@router.patch("/users/{user_id}/role", response_model=UserResponse)
def update_user_role(
    user_id: str,
    payload: RoleUpdateRequest,
    request: Request,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Changes a user's role (Admin only) (SEC-009)."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    old_role = user.role
    user.role = payload.role
    db.commit()
    db.refresh(user)

    log_audit_event(
        db=db,
        user=admin,
        action="USER_ROLE_CHANGE",
        resource_type="user",
        resource_id=user.id,
        details={"old_role": old_role.value, "new_role": user.role.value},
        request=request,
    )
    return user


@router.get("/audit-logs", response_model=list[AuditLogResponse])
def get_audit_trail(
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Retrieves system security and administrative audit trail (AUTH-006, SEC-009)."""
    return db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit).all()

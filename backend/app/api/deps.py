"""API dependencies for authentication, role authorization, and auditing (AUTH-003, SEC-003, SEC-009)."""
from typing import Generator, Optional
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.security import decode_access_token
from app.models.user import User, UserRole
from app.models.audit_log import AuditLog
from app.core.exceptions import InsufficientPermissionsException

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> User:
    """Validates JWT bearer token and retrieves authenticated User model."""
    payload = decode_access_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token payload missing subject identifier",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or account is deactivated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def require_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """Enforces administrator role check (AUTH-003, SEC-003)."""
    if current_user.role != UserRole.ADMINISTRATOR:
        raise InsufficientPermissionsException("This operation requires Administrator privileges.")
    return current_user


def log_audit_event(
    db: Session,
    user: Optional[User],
    action: str,
    resource_type: str,
    resource_id: Optional[str] = None,
    details: Optional[dict] = None,
    request: Optional[Request] = None,
) -> AuditLog:
    """Persists a tamper-evident administrative or security audit log entry (AUTH-006, SEC-009)."""
    ip_addr = None
    uagent = None
    if request:
        ip_addr = request.client.host if request.client else None
        uagent = request.headers.get("user-agent")

    log_entry = AuditLog(
        user_id=user.id if user else None,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        ip_address=ip_addr,
        user_agent=uagent,
        details=details or {},
    )
    db.add(log_entry)
    db.commit()
    return log_entry

"""Authentication and registration endpoints (AUTH-001, AUTH-002, AUTH-005)."""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User, UserRole
from app.schemas.auth import UserCreate, UserLogin, UserResponse, Token
from app.core.security import hash_password, verify_password, create_access_token
from app.api.deps import get_current_user, log_audit_event
import logging

logger = logging.getLogger("nutriscan.api.auth")
router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, request: Request, db: Session = Depends(get_db)):
    """Registers a new standard user account."""
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address is already registered.",
        )

    user = User(
        email=user_in.email,
        hashed_password=hash_password(user_in.password),
        full_name=user_in.full_name,
        role=UserRole.STANDARD,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    log_audit_event(
        db=db,
        user=user,
        action="USER_REGISTER",
        resource_type="user",
        resource_id=user.id,
        details={"email": user.email},
        request=request,
    )
    return user


@router.post("/login", response_model=Token)
def login(request: Request, db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    """Authenticates credentials and returns a JWT access token (AUTH-001, AUTH-002)."""
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        # Generic error message to prevent account enumeration (AUTH-002)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account has been deactivated",
        )

    access_token = create_access_token(subject=user.id, role=user.role.value)

    log_audit_event(
        db=db,
        user=user,
        action="USER_LOGIN",
        resource_type="auth",
        resource_id=user.id,
        request=request,
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user,
    }


@router.post("/login-json", response_model=Token)
def login_json(credentials: UserLogin, request: Request, db: Session = Depends(get_db)):
    """JSON-body alternative for frontend client login."""
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account has been deactivated",
        )

    access_token = create_access_token(subject=user.id, role=user.role.value)

    log_audit_event(
        db=db,
        user=user,
        action="USER_LOGIN",
        resource_type="auth",
        resource_id=user.id,
        request=request,
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user,
    }


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Returns the authenticated user profile."""
    return current_user

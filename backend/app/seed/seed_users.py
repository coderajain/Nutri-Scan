"""Seed default Administrator and Standard Demo users (AUTH-001, AUTH-004)."""
from sqlalchemy.orm import Session
from app.models.user import User, UserRole
from app.core.security import hash_password
from app.core.config import settings
import logging

logger = logging.getLogger("nutriscan.seed.users")


def seed_users(db: Session) -> dict[str, User]:
    """Ensures default admin and demo user accounts exist."""
    users_created = {}

    # 1. Admin user
    admin_user = db.query(User).filter(User.email == settings.ADMIN_EMAIL).first()
    if not admin_user:
        admin_user = User(
            email=settings.ADMIN_EMAIL,
            hashed_password=hash_password(settings.ADMIN_PASSWORD),
            full_name="Aashay Jain (Project Lead / Admin)",
            role=UserRole.ADMINISTRATOR,
            is_active=True,
        )
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        logger.info(f"Seeded default administrator: {settings.ADMIN_EMAIL}")
    users_created["admin"] = admin_user

    # 2. Standard demo user
    demo_user = db.query(User).filter(User.email == settings.DEMO_EMAIL).first()
    if not demo_user:
        demo_user = User(
            email=settings.DEMO_EMAIL,
            hashed_password=hash_password(settings.DEMO_PASSWORD),
            full_name="Medi-Caps Evaluator (Demo User)",
            role=UserRole.STANDARD,
            is_active=True,
        )
        db.add(demo_user)
        db.commit()
        db.refresh(demo_user)
        logger.info(f"Seeded default demo user: {settings.DEMO_EMAIL}")
    users_created["demo"] = demo_user

    return users_created

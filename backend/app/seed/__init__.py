"""Seed runner module to initialize users and default rule versions."""
from sqlalchemy.orm import Session
from app.seed.seed_users import seed_users
from app.seed.seed_rules import seed_lm_rules
import logging

logger = logging.getLogger("nutriscan.seed")


def run_all_seeds(db: Session) -> dict:
    """Runs all initial seeds in order."""
    logger.info("Starting database seeding...")
    users = seed_users(db)
    admin_user = users.get("admin")
    rule_version = seed_lm_rules(db, admin_user=admin_user)
    logger.info("Database seeding completed successfully.")
    return {
        "users": users,
        "rule_version": rule_version,
    }

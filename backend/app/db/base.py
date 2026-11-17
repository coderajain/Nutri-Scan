"""Base model class and declarative metadata registry."""
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


# Import all models here so that Alembic and Base.metadata recognize them
from app.models.user import User  # noqa: F401, E402
from app.models.rule_version import RuleVersion, Rule  # noqa: F401, E402
from app.models.scan import Scan  # noqa: F401, E402
from app.models.scan_field import ScanField  # noqa: F401, E402
from app.models.finding import Finding  # noqa: F401, E402
from app.models.audit_log import AuditLog  # noqa: F401, E402

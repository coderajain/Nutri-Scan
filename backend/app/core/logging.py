"""Structured logging configuration for NutriScan."""
import logging
import sys
import re
from app.core.config import settings

# Sensitive tokens/passwords filter to prevent logging in plaintext (SEC-002)
SENSITIVE_PATTERNS = [
    re.compile(r'(password[\'\"]?\s*[:=]\s*[\'\"]?)([^\'\"]+)([\'\"]?)', re.IGNORECASE),
    re.compile(r'(token[\'\"]?\s*[:=]\s*[\'\"]?)([^\'\"]+)([\'\"]?)', re.IGNORECASE),
    re.compile(r'(Bearer\s+)([A-Za-z0-9\-_\.]+)', re.IGNORECASE),
]


class SanitizingFormatter(logging.Formatter):
    """Custom formatter that redacts passwords and bearer tokens."""
    def format(self, record: logging.LogRecord) -> str:
        original = super().format(record)
        for pattern in SENSITIVE_PATTERNS:
            original = pattern.sub(r'\1[REDACTED]\3', original)
        return original


def setup_logging():
    """Initializes root and application loggers."""
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    
    handler = logging.StreamHandler(sys.stdout)
    formatter = SanitizingFormatter(
        fmt="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    # Clear existing handlers to avoid duplicates
    root_logger.handlers = [handler]

    # Set external libraries to warning to keep logs clean
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    
    app_logger = logging.getLogger("nutriscan")
    app_logger.setLevel(log_level)
    return app_logger


logger = setup_logging()

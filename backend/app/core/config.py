"""Application configuration loaded from environment variables."""
import os
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    # Application Info
    APP_NAME: str = "NutriScan"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    DEBUG: bool = False

    # Database Settings
    POSTGRES_HOST: str = "db"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "nutriscan"
    POSTGRES_USER: str = "nutriscan_user"
    POSTGRES_PASSWORD: str = "nutriscan_secure_pass_2026"
    DATABASE_URL_OVERRIDE: Optional[str] = None
    DATABASE_URL_CONFIG: Optional[str] = os.getenv("DATABASE_URL")

    @property
    def DATABASE_URL(self) -> str:
        if self.DATABASE_URL_OVERRIDE:
            return self.DATABASE_URL_OVERRIDE
        env_url = os.getenv("DATABASE_URL") or self.DATABASE_URL_CONFIG
        if env_url:
            return env_url
        
        # Check if psycopg2 is installed; if not, use SQLite fallback for local testing
        try:
            import psycopg2  # noqa: F401
            return (
                f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
                f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            )
        except ImportError:
            db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "nutriscan.db")
            return f"sqlite:///{db_path}"

    # JWT Security Settings
    SECRET_KEY: str = "94a5e3f48a12e84d72bc9166f283d5a49c0683058b8f2d57929a531bcf91c01e"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120

    # Evidence & Report Storage
    EVIDENCE_DIR: str = os.getenv("EVIDENCE_DIR", os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "evidence"))
    MAX_UPLOAD_SIZE_MB: int = 15
    ALLOWED_IMAGE_TYPES: list[str] = ["image/jpeg", "image/png", "image/jpg", "image/webp"]

    # Initial Users Seed
    ADMIN_EMAIL: str = "admin@nutriscan.local"
    ADMIN_PASSWORD: str = "AdminPassword@2026!"
    DEMO_EMAIL: str = "demo@nutriscan.local"
    DEMO_PASSWORD: str = "DemoPassword@2026!"

    # CORS
    CORS_ORIGINS: list[str] = ["*"]

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

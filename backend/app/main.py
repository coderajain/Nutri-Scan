"""NutriScan v1.0 FastAPI Main Application Entrypoint."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging import logger
from app.core.exceptions import register_exception_handlers
from app.db.base import Base
from app.db.session import engine, SessionLocal
from app.seed import run_all_seeds

# Import API Routers
from app.api.auth import router as auth_router
from app.api.scans import router as scans_router
from app.api.rules import router as rules_router
from app.api.history import router as history_router
from app.api.dashboard import router as dashboard_router
from app.api.admin import router as admin_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: database initialization and statutory seed execution."""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION} [{settings.ENVIRONMENT}]")
    
    # 1. Ensure tables exist in database
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database schema verified / created successfully.")
    except Exception as exc:
        logger.error(f"Error ensuring database tables: {exc}")

    # 2. Run initial seeds (default admin, demo user, LM-PC-2011 v1.0 ruleset)
    try:
        db = SessionLocal()
        run_all_seeds(db)
        db.close()
    except Exception as exc:
        logger.error(f"Seeding error during startup: {exc}")

    yield

    logger.info(f"Shutting down {settings.APP_NAME}")


app = FastAPI(
    title="NutriScan API",
    description=(
        "AI-assisted packaged food label analysis, nutritional assessment, "
        "and Legal Metrology (Packaged Commodities) Rules, 2011 compliance screening."
    ),
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Safe Exception Handling (SEC-011)
register_exception_handlers(app)


# System Health Check Endpoint
@app.get("/api/v1/health", tags=["Health"])
@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint for Docker container status monitoring."""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
    }


# Register Versioned API Routers
API_V1_PREFIX = "/api/v1"
app.include_router(auth_router, prefix=API_V1_PREFIX)
app.include_router(scans_router, prefix=API_V1_PREFIX)
app.include_router(rules_router, prefix=API_V1_PREFIX)
app.include_router(history_router, prefix=API_V1_PREFIX)
app.include_router(dashboard_router, prefix=API_V1_PREFIX)
app.include_router(admin_router, prefix=API_V1_PREFIX)

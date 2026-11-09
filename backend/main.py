"""
CrowdWisdom AI Studio — FastAPI Application Entry Point
"""
import sys
import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

# Initialize framework paths for official Hermes and OpenMontage
backend_dir = Path(__file__).parent.resolve()
hermes_path = backend_dir / "vendor" / "hermes_agent"
om_path = backend_dir / "video_engine" / "openmontage"

if hermes_path.exists() and str(hermes_path) not in sys.path:
    sys.path.insert(0, str(hermes_path))
if om_path.exists() and str(om_path) not in sys.path:
    sys.path.append(str(om_path))

try:
    import tools
    om_tools = str((om_path / "tools").resolve())
    if hasattr(tools, "__path__") and om_tools not in tools.__path__:
        tools.__path__.append(om_tools)
except Exception:
    pass

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles

from config import settings, mask_connection_url
from database.connection import connect_to_mongo, close_mongo_connection
from services.integration_service import initialize_default_integrations
from workers.job_manager import job_manager

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle."""
    logger.info("Starting CrowdWisdom AI Studio backend...")

    # 0. Validate Environment Configuration
    env_status = settings.validate_environment()
    if not env_status["valid"]:
        for issue in env_status["issues"]:
            logger.error(f"[SECURITY_CONFIG_ERROR] {issue}")
        if settings.is_production:
            raise RuntimeError(f"Startup aborted due to critical security issues: {env_status['issues']}")
    for warning in env_status.get("warnings", []):
        logger.warning(f"[CONFIG_WARNING] {warning}")

    logger.info(f"Loaded configuration for environment '{settings.APP_ENV}'")

    # 1. Connect to MongoDB
    await connect_to_mongo()

    # 2. Recover any interrupted jobs from previous server crash
    await job_manager.recover_orphaned_jobs_on_boot()

    # 3. Initialize default integration records
    await initialize_default_integrations()

    # 4. Ensure media directories exist
    media_dir = Path(settings.MEDIA_DIR)
    for subdir in ["videos", "thumbnails", "assets"]:
        (media_dir / subdir).mkdir(parents=True, exist_ok=True)

    logger.info("CrowdWisdom AI Studio backend ready.")
    yield

    # Shutdown
    await close_mongo_connection()
    logger.info("CrowdWisdom AI Studio backend stopped.")


app = FastAPI(
    title="CrowdWisdom AI Studio API",
    description="Autonomous AI Marketing Agent & Cinematic Video Advertising Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# --- Root & Documentation Compatibility Redirects ---
@app.get("/", include_in_schema=False)
async def root():
    """Root platform discovery endpoint."""
    return {
        "service": "CrowdWisdom AI Studio API",
        "status": "online",
        "version": "1.0.0",
        "docs": "/docs",
        "openapi": "/openapi.json",
        "health": "/health",
    }


@app.get("/api/docs", include_in_schema=False)
async def redirect_api_docs():
    """Redirect /api/docs to /docs for seamless developer navigation."""
    return RedirectResponse(url="/docs")


@app.get("/api/redoc", include_in_schema=False)
async def redirect_api_redoc():
    """Redirect /api/redoc to /redoc."""
    return RedirectResponse(url="/redoc")


@app.get("/api/openapi.json", include_in_schema=False)
async def redirect_api_openapi():
    """Redirect /api/openapi.json to /openapi.json."""
    return RedirectResponse(url="/openapi.json")

# --- Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Range", "Accept-Ranges", "Content-Length", "Content-Type"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# --- Import and register routers ---
from api.auth import router as auth_router
from api.campaigns import router as campaigns_router
from api.agents import router as agents_router
from api.scripts import router as scripts_router
from api.videos import router as videos_router
from api.research import router as research_router
from api.integrations import router as integrations_router
from api.creative_briefs import router as creative_briefs_router
from api.websocket import router as ws_router
from api.dashboard import dashboard_router, assets_router, media_router, workflow_router

API_PREFIX = "/api"

app.include_router(auth_router, prefix=API_PREFIX)
app.include_router(campaigns_router, prefix=API_PREFIX)
app.include_router(agents_router, prefix=API_PREFIX)
app.include_router(scripts_router, prefix=API_PREFIX)
app.include_router(videos_router, prefix=API_PREFIX)
app.include_router(research_router, prefix=API_PREFIX)
app.include_router(creative_briefs_router, prefix=API_PREFIX)
app.include_router(integrations_router, prefix=API_PREFIX)
app.include_router(dashboard_router, prefix=API_PREFIX)
app.include_router(assets_router, prefix=API_PREFIX)
app.include_router(media_router, prefix=API_PREFIX, include_in_schema=False)
app.include_router(media_router)  # Also serve at /media/videos/... and /media/thumbnails/...
app.include_router(workflow_router, prefix=API_PREFIX)
app.include_router(ws_router)  # WebSocket endpoint /ws/{client_id}


# Direct asset fallback routes
@app.get("/assets/{filepath:path}")
async def serve_direct_asset_route(filepath: str):
    from api.dashboard import serve_asset
    return await serve_asset(filepath)


def _sanitize_error_message(exc: Exception) -> str:
    """Scrub potential credentials and sensitive database URIs from exception messages."""
    import re
    msg = mask_connection_url(str(exc))
    msg = re.sub(r"(AIzaSy[A-Za-z0-9_-]{8,})", r"AIzaSy****[REDACTED]", msg)
    msg = re.sub(r"(sk-[A-Za-z0-9_-]{8,})", r"sk-****[REDACTED]", msg)
    msg = re.sub(r"(nvapi-[A-Za-z0-9_-]{8,})", r"nvapi-****[REDACTED]", msg)
    msg = re.sub(r"(tvly-[A-Za-z0-9_-]{8,})", r"tvly-****[REDACTED]", msg)
    msg = re.sub(r"(apify_api_[A-Za-z0-9_-]{8,})", r"apify_api_****[REDACTED]", msg)
    return msg


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global catch-all exception handler to log tracebacks and prevent secret leakage."""
    sanitized_msg = _sanitize_error_message(exc)
    logger.error(f"[UnhandledException] {request.method} {request.url.path}: {sanitized_msg}", exc_info=True)

    if settings.is_production:
        client_detail = "Internal server error. Incident logged."
    else:
        client_detail = f"Internal server error: {sanitized_msg}"

    return JSONResponse(
        status_code=500,
        content={"detail": client_detail}
    )


@app.get("/health", tags=["Health"])
@app.get("/api/health", tags=["Health"])
async def health_check():
    """Health check endpoint for Render service probes and uptime monitors."""
    from database.connection import get_database
    from services.memory_monitor import get_process_memory_mb
    from workers.job_manager import job_manager
    try:
        db = get_database()
        await db.command("ping")
        db_status = "connected"
    except Exception:
        db_status = "disconnected"

    mem = get_process_memory_mb()
    metrics = job_manager.get_metrics()

    return {
        "status": "ok",
        "service": "CrowdWisdom AI Studio",
        "version": "1.0.0",
        "database": db_status,
        "environment": settings.APP_ENV,
        "memory": {
            "rss_mb": mem["rss_mb"],
            "active_renders": metrics["active_renders"],
            "queued_renders": metrics["queued_renders"],
            "limit_mb": float(getattr(settings, "VIDEO_RENDER_MEMORY_LIMIT_MB", 450.0)),
        }
    }


@app.get("/api/system/memory", tags=["Health"])
async def system_memory_diagnostics():
    """Detailed memory and concurrency telemetry for infrastructure monitoring."""
    from workers.job_manager import job_manager
    return job_manager.get_metrics()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.APP_ENV == "development",
        log_level="info",
    )

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
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles

from config import settings
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
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# --- Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
app.include_router(media_router, prefix=API_PREFIX)
app.include_router(media_router)  # Also serve at /media/videos/... and /media/thumbnails/...
app.include_router(workflow_router, prefix=API_PREFIX)
app.include_router(ws_router)  # WebSocket endpoint /ws/{client_id}


# Direct asset fallback routes
@app.get("/assets/{filename}")
async def serve_direct_asset_route(filename: str):
    from api.dashboard import serve_asset
    return await serve_asset(filename)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global catch-all exception handler to log tracebacks and prevent silent 500s."""
    logger.error(f"[UnhandledException] {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"}
    )


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    from database.connection import get_database
    try:
        db = get_database()
        await db.command("ping")
        db_status = "connected"
    except Exception:
        db_status = "disconnected"

    return {
        "status": "ok",
        "service": "CrowdWisdom AI Studio",
        "version": "1.0.0",
        "database": db_status,
        "environment": settings.APP_ENV,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.APP_ENV == "development",
        log_level="info",
    )

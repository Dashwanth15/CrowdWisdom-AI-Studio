"""
CrowdWisdom AI Studio — Dashboard, Assets & Workflow API Routes
"""
import os
from typing import Annotated, List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import FileResponse, StreamingResponse, Response
from bson import ObjectId

from database.connection import get_database
from models.schemas import DashboardStats, MediaAssetOut, WorkflowTaskOut
from api.auth import get_current_user
from config import settings

# --- Dashboard Router ---
dashboard_router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@dashboard_router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    current_user: Annotated[dict, Depends(get_current_user)],
):
    """Get real dashboard metrics from MongoDB reflecting system ground truth."""
    db = get_database()
    owner_id = str(current_user["_id"])
    user_role = current_user.get("role", "viewer")
    is_privileged = user_role in ("admin", "marketing_manager", "creative_editor")

    # Campaign metrics: count all accessible campaigns
    camp_query = {} if is_privileged else {"$or": [{"owner_id": owner_id}, {"owner_id": None}]}
    total_campaigns = await db.campaigns.count_documents(camp_query)
    active_campaigns = await db.campaigns.count_documents({**camp_query, "status": "active"})

    # Global Ad Intelligence metrics (matches Ads Research page ground truth)
    ads_researched = await db.advertisements.count_documents({})
    insights_generated = await db.marketing_insights.count_documents({})

    # Creative & Production Pipeline metrics
    scripts_generated = await db.scripts.count_documents({})
    scripts_pending = await db.scripts.count_documents({"status": "pending_approval"})
    videos_generated = await db.video_jobs.count_documents({"status": "completed"})
    videos_in_progress = await db.video_jobs.count_documents(
        {"status": {"$in": ["queued", "processing", "composing", "rendering"]}}
    )

    # Agent success rate across all executions
    total_executions = await db.agent_executions.count_documents(
        {"status": {"$in": ["completed", "failed"]}}
    )
    successful = await db.agent_executions.count_documents(
        {"status": "completed"}
    )
    success_rate = (successful / total_executions * 100) if total_executions > 0 else 100.0

    # Recent activity (last 10 executions)
    recent_logs = await db.agent_executions.find({}).sort("created_at", -1).limit(10).to_list(10)

    recent_activity = [
        {
            "id": str(log["_id"]),
            "agent_type": log.get("agent_type"),
            "task_name": log.get("task_name"),
            "status": log.get("status"),
            "campaign_id": log.get("campaign_id"),
            "created_at": log["created_at"].isoformat() if isinstance(log.get("created_at"), datetime) else datetime.now(timezone.utc).isoformat(),
        }
        for log in recent_logs
    ]

    return DashboardStats(
        total_campaigns=total_campaigns,
        active_campaigns=active_campaigns,
        ads_researched=ads_researched,
        insights_generated=insights_generated,
        scripts_generated=scripts_generated,
        scripts_pending_approval=scripts_pending,
        videos_generated=videos_generated,
        videos_in_progress=videos_in_progress,
        agent_success_rate=round(success_rate, 1),
        recent_activity=recent_activity,
    )


# --- Assets Router ---
assets_router = APIRouter(prefix="/assets", tags=["Assets"])


@assets_router.get("", response_model=List[MediaAssetOut])
async def list_assets(
    current_user: Annotated[dict, Depends(get_current_user)],
    campaign_id: Optional[str] = None,
    asset_type: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    db = get_database()
    query = {}
    if campaign_id:
        query["campaign_id"] = campaign_id
    if asset_type:
        query["asset_type"] = asset_type

    cursor = db.media_assets.find(query).sort("created_at", -1).skip(skip).limit(limit)
    docs = await cursor.to_list(limit)
    return [_serialize_asset(d) for d in docs]


@assets_router.delete("/{asset_id}", status_code=204)
async def delete_asset(
    asset_id: str,
    current_user: Annotated[dict, Depends(get_current_user)],
):
    db = get_database()
    if not ObjectId.is_valid(asset_id):
        raise HTTPException(status_code=400, detail="Invalid asset ID.")

    asset = await db.media_assets.find_one({"_id": ObjectId(asset_id)})
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found.")

    # Delete physical file
    if asset.get("file_path") and os.path.exists(asset["file_path"]):
        os.remove(asset["file_path"])

    await db.media_assets.delete_one({"_id": ObjectId(asset_id)})


# --- Media serving router ---
media_router = APIRouter(prefix="/media", tags=["Media"])


@media_router.api_route("/videos/{filename}", methods=["GET", "HEAD"])
async def serve_video(filename: str, request: Request):
    """Serve generated video files with robust location resolution, HEAD support, and HTTP 206 Partial Content streaming."""
    import pathlib
    clean_filename = pathlib.Path(filename).name
    backend_root = pathlib.Path(__file__).resolve().parent.parent
    project_root = backend_root.parent
    candidates = [
        project_root / "media" / "videos" / clean_filename,
        pathlib.Path(settings.MEDIA_DIR) / "videos" / clean_filename,
        pathlib.Path(settings.MEDIA_DIR).resolve() / "videos" / clean_filename,
        backend_root / "media" / "videos" / clean_filename,
        project_root / "media" / "assets" / "stock_footage" / clean_filename,
        pathlib.Path(settings.MEDIA_DIR) / "assets" / "stock_footage" / clean_filename,
        backend_root / "media" / "assets" / "stock_footage" / clean_filename,
        project_root / "media" / "assets" / clean_filename,
        pathlib.Path(settings.MEDIA_DIR) / "assets" / clean_filename,
        backend_root / "media" / "assets" / clean_filename,
        pathlib.Path.cwd() / "media" / "videos" / clean_filename,
        pathlib.Path.cwd() / "backend" / "media" / "videos" / clean_filename,
    ]
    video_path = next((p for p in candidates if p.exists() and p.is_file()), None)
    if not video_path:
        raise HTTPException(status_code=404, detail="Video file not found.")

    file_size = os.path.getsize(video_path)
    if file_size == 0:
        raise HTTPException(status_code=404, detail="Video file is empty.")

    range_header = request.headers.get("range")

    if range_header:
        byte_range = range_header.replace("bytes=", "").split("-")
        start = int(byte_range[0]) if byte_range[0] else 0
        end = int(byte_range[1]) if len(byte_range) > 1 and byte_range[1] else file_size - 1
        end = min(end, file_size - 1)
        content_length = (end - start) + 1

        headers = {
            "Content-Range": f"bytes {start}-{end}/{file_size}",
            "Accept-Ranges": "bytes",
            "Content-Length": str(content_length),
            "Content-Type": "video/mp4",
            "Content-Encoding": "identity",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Expose-Headers": "Content-Range, Accept-Ranges, Content-Length, Content-Type",
        }

        if request.method == "HEAD":
            return Response(status_code=206, headers=headers)

        def iter_file():
            with open(video_path, "rb") as f:
                f.seek(start)
                remaining = content_length
                chunk_size = 1024 * 512
                while remaining > 0:
                    read_bytes = min(remaining, chunk_size)
                    data = f.read(read_bytes)
                    if not data:
                        break
                    remaining -= len(data)
                    yield data

        return StreamingResponse(iter_file(), status_code=206, headers=headers)

    headers = {
        "Accept-Ranges": "bytes",
        "Content-Length": str(file_size),
        "Content-Type": "video/mp4",
        "Content-Encoding": "identity",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Expose-Headers": "Content-Range, Accept-Ranges, Content-Length, Content-Type",
    }

    if request.method == "HEAD":
        return Response(status_code=200, headers=headers)

    return FileResponse(
        str(video_path),
        media_type="video/mp4",
        filename=clean_filename,
        headers=headers,
    )


@media_router.get("/thumbnails/{filename}")
async def serve_thumbnail(filename: str):
    """Serve video thumbnail files with robust path resolution."""
    import pathlib
    clean_filename = pathlib.Path(filename).name
    backend_root = pathlib.Path(__file__).resolve().parent.parent
    project_root = backend_root.parent
    candidates = [
        project_root / "media" / "thumbnails" / clean_filename,
        pathlib.Path(settings.MEDIA_DIR) / "thumbnails" / clean_filename,
        backend_root / "media" / "thumbnails" / clean_filename,
        pathlib.Path.cwd() / "media" / "thumbnails" / clean_filename,
        pathlib.Path.cwd() / "backend" / "media" / "thumbnails" / clean_filename,
    ]
    thumb_path = next((p for p in candidates if p.exists() and p.is_file()), None)
    if not thumb_path:
        raise HTTPException(status_code=404, detail="Thumbnail not found.")
    return FileResponse(str(thumb_path), media_type="image/jpeg")


@media_router.get("/assets/{filepath:path}")
async def serve_asset(filepath: str):
    """Serve storyboard scene visual asset files with robust path resolution across project, backend, stock footage, and fallback dirs."""
    import pathlib
    clean_filepath = filepath.replace("\\", "/").lstrip("/")
    clean_filename = pathlib.Path(clean_filepath).name
    backend_root = pathlib.Path(__file__).resolve().parent.parent
    project_root = backend_root.parent

    media_dir = pathlib.Path(settings.MEDIA_DIR)
    candidates = [
        project_root / "media" / "assets" / clean_filepath,
        media_dir / "assets" / clean_filepath,
        backend_root / "media" / "assets" / clean_filepath,
        project_root / "media" / "assets" / clean_filename,
        media_dir / "assets" / clean_filename,
        backend_root / "media" / "assets" / clean_filename,
        project_root / "media" / "assets" / "stock_footage" / clean_filename,
        media_dir / "assets" / "stock_footage" / clean_filename,
        backend_root / "media" / "assets" / "stock_footage" / clean_filename,
        project_root / "media" / "assets" / "fallback_library" / clean_filename,
        media_dir / "assets" / "fallback_library" / clean_filename,
        backend_root / "media" / "assets" / "fallback_library" / clean_filename,
        pathlib.Path.cwd() / "media" / "assets" / clean_filepath,
        pathlib.Path.cwd() / "backend" / "media" / "assets" / clean_filepath,
    ]
    asset_path = next((p for p in candidates if p.exists() and p.is_file()), None)
    if not asset_path:
        # Check if any asset in candidate directories starts with the same script/hash suffix
        for search_dir in [project_root / "media" / "assets", media_dir / "assets"]:
            if search_dir.exists():
                matched = list(search_dir.glob(f"*{clean_filename.split('_')[-1]}*"))
                if matched:
                    asset_path = matched[0]
                    break

    if not asset_path:
        # Graceful fallback: return any existing asset rather than breaking the UI with 404
        for search_dir in [project_root / "media" / "assets", media_dir / "assets"]:
            if search_dir.exists():
                any_assets = list(search_dir.glob("*.jpg")) or list(search_dir.glob("*.png"))
                if any_assets:
                    asset_path = any_assets[0]
                    logger.info(f"Visual asset {filepath} not found, served graceful fallback {asset_path.name}")
                    break

    if not asset_path:
        raise HTTPException(status_code=404, detail=f"Visual asset {filepath} not found.")

    suffix = str(asset_path).lower()
    if suffix.endswith(".png"):
        media_type = "image/png"
    elif suffix.endswith((".mp4", ".mov", ".webm")):
        media_type = "video/mp4"
    else:
        media_type = "image/jpeg"

    headers = {
        "Accept-Ranges": "bytes",
        "Content-Length": str(os.path.getsize(asset_path)),
        "Access-Control-Allow-Origin": "*",
    }
    return FileResponse(str(asset_path), media_type=media_type, headers=headers)


# --- Workflow Router ---
workflow_router = APIRouter(prefix="/workflows", tags=["Workflows"])


@workflow_router.get("/tasks", response_model=List[WorkflowTaskOut])
async def list_workflow_tasks(
    current_user: Annotated[dict, Depends(get_current_user)],
    campaign_id: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    db = get_database()
    query = {}
    if campaign_id:
        query["campaign_id"] = campaign_id
    if status:
        query["status"] = status

    cursor = db.workflow_tasks.find(query).sort("created_at", -1).skip(skip).limit(limit)
    docs = await cursor.to_list(limit)
    return [_serialize_task(d) for d in docs]


def _serialize_asset(doc: dict) -> MediaAssetOut:
    return MediaAssetOut(
        id=str(doc["_id"]),
        campaign_id=doc.get("campaign_id"),
        asset_type=doc.get("asset_type", "image"),
        filename=doc.get("filename", ""),
        file_path=doc.get("file_path", ""),
        url=doc.get("url"),
        file_size_bytes=doc.get("file_size_bytes"),
        duration_seconds=doc.get("duration_seconds"),
        width=doc.get("width"),
        height=doc.get("height"),
        mime_type=doc.get("mime_type"),
        tags=doc.get("tags", []),
        created_at=doc["created_at"],
    )


def _serialize_task(doc: dict) -> WorkflowTaskOut:
    return WorkflowTaskOut(
        id=str(doc["_id"]),
        campaign_id=doc.get("campaign_id", ""),
        task_name=doc.get("task_name", ""),
        description=doc.get("description"),
        agent_type=doc.get("agent_type"),
        status=doc.get("status", "pending"),
        priority=doc.get("priority", 0),
        depends_on=doc.get("depends_on", []),
        execution_id=doc.get("execution_id"),
        started_at=doc.get("started_at"),
        completed_at=doc.get("completed_at"),
        created_at=doc["created_at"],
    )


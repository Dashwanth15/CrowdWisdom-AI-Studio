"""
CrowdWisdom AI Studio — Videos API Routes
Video job management, production launch, and media serving.
"""
import os
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import Annotated, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from bson import ObjectId

from database.connection import get_database
from models.schemas import VideoJobCreate, VideoJobOut
from api.auth import get_current_user
from orchestrator.hermes_orchestrator import orchestrator
from config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/videos", tags=["Videos"])


def _serialize_job(doc: dict) -> VideoJobOut:
    now = datetime.now(timezone.utc)
    return VideoJobOut(
        id=str(doc["_id"]),
        campaign_id=doc.get("campaign_id", ""),
        script_id=doc.get("script_id", ""),
        status=doc.get("status", "queued"),
        aspect_ratio=doc.get("aspect_ratio", "9:16"),
        duration_seconds=doc.get("duration_seconds", doc.get("duration_requested", 45)),
        quality=doc.get("quality", "high"),
        progress_percent=doc.get("progress_percent", 0),
        current_stage=doc.get("current_stage"),
        video_path=doc.get("video_path"),
        thumbnail_path=doc.get("thumbnail_path"),
        video_url=doc.get("video_url"),
        duration_actual=doc.get("duration_actual"),
        file_size_mb=doc.get("file_size_mb"),
        error_message=doc.get("error_message"),
        production_log=doc.get("production_log", []),
        started_at=doc.get("started_at"),
        completed_at=doc.get("completed_at"),
        created_at=doc.get("created_at") or doc.get("started_at") or now,
    )


@router.post("/generate", status_code=202)
async def generate_video(
    data: VideoJobCreate,
    current_user: Annotated[dict, Depends(get_current_user)],
):
    """Launch the Video Production Agent for an approved script."""
    db = get_database()

    # 1. Fallback: Auto-resolve campaign_id from script if missing or invalid
    if not data.campaign_id or not ObjectId.is_valid(data.campaign_id):
        if data.script_id and ObjectId.is_valid(data.script_id):
            script_doc = await db.scripts.find_one({"_id": ObjectId(data.script_id)})
            if script_doc and script_doc.get("campaign_id") and ObjectId.is_valid(script_doc["campaign_id"]):
                data.campaign_id = script_doc["campaign_id"]

    # 2. Verify campaign access
    if not data.campaign_id or not ObjectId.is_valid(data.campaign_id):
        raise HTTPException(
            status_code=400,
            detail="Valid campaign ID is required. Please ensure the storyboard is linked to an active campaign."
        )

    user_role = current_user.get("role", "viewer")
    user_id = str(current_user["_id"])
    query: dict = {"_id": ObjectId(data.campaign_id)}
    if user_role not in ("admin", "marketing_manager", "creative_editor"):
        query["owner_id"] = user_id

    campaign = await db.campaigns.find_one(query)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found.")

    try:
        result = await orchestrator.launch_video_production(
            campaign_id=data.campaign_id,
            video_input={
                "script_id": data.script_id,
                "aspect_ratio": data.aspect_ratio.value,
                "duration_seconds": data.duration_seconds,
                "quality": data.quality,
            },
        )
        return {"message": "Video production launched", **result}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))


async def _reconcile_video_job(doc: dict, db) -> dict:
    """Self-heals orphaned or stalled video jobs when fetched by API."""
    if not doc:
        return doc
    status = doc.get("status")
    if status in ("queued", "processing", "composing", "rendering"):
        now = datetime.now(timezone.utc)
        created_at = doc.get("created_at")
        started_at = doc.get("started_at")
        anchor_time = started_at or created_at
        if anchor_time:
            if anchor_time.tzinfo is None:
                anchor_time = anchor_time.replace(tzinfo=timezone.utc)
            # If job has been in intermediate state for > 5 minutes
            if (now - anchor_time).total_seconds() > 300:
                v_id = str(doc["_id"])
                from pathlib import Path
                mp4_candidates = [
                    Path("backend/media/videos") / f"video_{v_id}.mp4",
                    Path("media/videos") / f"video_{v_id}.mp4",
                ]
                thumb_candidates = [
                    Path("backend/media/thumbnails") / f"thumb_{v_id}.jpg",
                    Path("media/thumbnails") / f"thumb_{v_id}.jpg",
                ]
                found_mp4 = next((p for p in mp4_candidates if p.exists() and p.stat().st_size > 100_000), None)
                found_thumb = next((p for p in thumb_candidates if p.exists() and p.stat().st_size > 1_000), None)

                if found_mp4:
                    file_size_mb = round(found_mp4.stat().st_size / (1024 * 1024), 2)
                    updates = {
                        "status": "completed",
                        "progress_percent": 100,
                        "video_url": f"/media/videos/{found_mp4.name}",
                        "video_path": str(found_mp4.resolve()),
                        "thumbnail_path": str(found_thumb.resolve()) if found_thumb else None,
                        "duration_actual": doc.get("duration_seconds", 60),
                        "file_size_mb": file_size_mb,
                        "error_message": None,
                        "completed_at": now,
                    }
                    await db.video_jobs.update_one({"_id": doc["_id"]}, {"$set": updates})
                    doc.update(updates)
                else:
                    updates = {
                        "status": "failed",
                        "error_message": "Video rendering was interrupted. Click Retry to re-render.",
                        "completed_at": now,
                    }
                    await db.video_jobs.update_one({"_id": doc["_id"]}, {"$set": updates})
                    doc.update(updates)
    elif status == "completed":
        v_id = str(doc["_id"])
        from pathlib import Path
        clean_name = f"video_{v_id}.mp4"
        raw_url = doc.get("video_url") or ""
        if raw_url:
            clean_name = Path(raw_url).name
        
        candidates = [
            Path(settings.MEDIA_DIR) / "videos" / clean_name,
            Path("backend/media/videos") / clean_name,
            Path("media/videos") / clean_name,
            Path(doc.get("video_path") or ""),
        ]
        file_exists = any(c.exists() and c.is_file() and c.stat().st_size > 100_000 for c in candidates if str(c))
        if not file_exists:
            # Physical file missing from container filesystem (e.g. after deployment or ephemeral restart)
            now = datetime.now(timezone.utc)
            updates = {
                "status": "failed",
                "error_message": "Rendered video file is unavailable on this server instance. Click Re-render to regenerate.",
                "progress_percent": 0,
                "video_url": None,
                "completed_at": now,
            }
            await db.video_jobs.update_one({"_id": doc["_id"]}, {"$set": updates})
            doc.update(updates)
    return doc


@router.get("", response_model=List[VideoJobOut])
async def list_video_jobs(
    current_user: Annotated[dict, Depends(get_current_user)],
    campaign_id: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    db = get_database()
    query: dict = {}
    if campaign_id:
        query["campaign_id"] = campaign_id
    if status:
        query["status"] = status

    cursor = db.video_jobs.find(query).sort("created_at", -1).skip(skip).limit(limit)
    docs = await cursor.to_list(limit)
    reconciled = [await _reconcile_video_job(d, db) for d in docs]
    return [_serialize_job(d) for d in reconciled]


@router.get("/{job_id}", response_model=VideoJobOut)
async def get_video_job(
    job_id: str,
    current_user: Annotated[dict, Depends(get_current_user)],
):
    db = get_database()
    if not ObjectId.is_valid(job_id):
        raise HTTPException(status_code=400, detail="Invalid job ID.")
    doc = await db.video_jobs.find_one({"_id": ObjectId(job_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Video job not found.")
    doc = await _reconcile_video_job(doc, db)
    return _serialize_job(doc)


@router.post("/{job_id}/retry", status_code=202)
async def retry_video_job(
    job_id: str,
    current_user: Annotated[dict, Depends(get_current_user)],
):
    """Retry a failed video generation job."""
    db = get_database()
    if not ObjectId.is_valid(job_id):
        raise HTTPException(status_code=400, detail="Invalid job ID.")

    job = await db.video_jobs.find_one({"_id": ObjectId(job_id)})
    if not job:
        raise HTTPException(status_code=404, detail="Video job not found.")
    if job["status"] not in ("failed", "cancelled"):
        # Allow retry if stalled in composing/processing for > 5 minutes
        started = job.get("started_at") or job.get("created_at")
        is_stale = False
        if started:
            if started.tzinfo is None:
                started = started.replace(tzinfo=timezone.utc)
            if (datetime.now(timezone.utc) - started).total_seconds() > 300:
                is_stale = True
        if not is_stale:
            raise HTTPException(status_code=400, detail="Can only retry failed or stalled jobs.")

    result = await orchestrator.launch_video_production(
        campaign_id=job["campaign_id"],
        video_input={
            "script_id": job["script_id"],
            "aspect_ratio": job.get("aspect_ratio", "9:16"),
            "duration_seconds": job.get("duration_seconds", 45),
            "quality": job.get("quality", "high"),
        },
    )
    return {"message": "Video job retried", **result}


@router.delete("/clear-failed")
async def clear_failed_videos(
    current_user: Annotated[dict, Depends(get_current_user)],
):
    """Delete all failed video jobs and purge any temporary artifacts."""
    db = get_database()
    cursor = db.video_jobs.find({"status": "failed"})
    failed_jobs = await cursor.to_list(500)

    deleted_count = 0
    for job in failed_jobs:
        for field in ("video_path", "thumbnail_path"):
            path_str = job.get(field)
            if path_str:
                p = Path(path_str)
                if p.exists() and p.is_file():
                    try:
                        p.unlink()
                    except Exception as e:
                        logger.warning(f"Failed to delete {p}: {e}")
        await db.video_jobs.delete_one({"_id": job["_id"]})
        deleted_count += 1

    return {"message": f"Successfully cleared {deleted_count} failed video jobs.", "deleted_count": deleted_count}


@router.delete("/{job_id}")
async def delete_video_job(
    job_id: str,
    current_user: Annotated[dict, Depends(get_current_user)],
):
    """Delete a video job and remove its rendered MP4 and thumbnail from disk."""
    db = get_database()
    if not ObjectId.is_valid(job_id):
        raise HTTPException(status_code=400, detail="Invalid job ID.")

    job = await db.video_jobs.find_one({"_id": ObjectId(job_id)})
    if not job:
        raise HTTPException(status_code=404, detail="Video job not found.")

    for field in ("video_path", "thumbnail_path"):
        path_str = job.get(field)
        if path_str:
            p = Path(path_str)
            if p.exists() and p.is_file():
                try:
                    p.unlink()
                except Exception as e:
                    logger.warning(f"Failed to remove file {p}: {e}")

    await db.video_jobs.delete_one({"_id": ObjectId(job_id)})
    await db.agent_executions.delete_many({"input_data.video_job_id": job_id})

    return {"message": "Video job and media files deleted successfully.", "job_id": job_id}


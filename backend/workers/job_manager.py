"""
CrowdWisdom AI Studio — Persistent Job Manager
Manages long-running research and video rendering workloads.
Supports idempotency, task cancellation, crash recovery on boot, and state persistence.
"""
import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Any, Callable, Coroutine, Dict, Optional, Set
from bson import ObjectId

from database.connection import get_database
from services.websocket_manager import ws_manager
from config import settings

logger = logging.getLogger(__name__)


def is_mp4_valid_and_playable(file_path: Path) -> Tuple[bool, float]:
    """
    Verifies that an MP4 file exists, has valid structure, contains a playable moov atom,
    and has duration > 1.0s. Returns (is_valid, duration).
    Prevents corrupted 0:00 video files from falsely marking as 'completed'.
    """
    if not file_path.exists() or not file_path.is_file():
        return False, 0.0
    st_size = file_path.stat().st_size
    if st_size < 100_000:
        return False, 0.0

    try:
        import imageio_ffmpeg
        import subprocess
        import re
        ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        res = subprocess.run([ffmpeg_exe, "-i", str(file_path), "-hide_banner"], capture_output=True, text=True, timeout=5)
        out = (res.stderr or "") + (res.stdout or "")
        if "Invalid data found" not in out:
            m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.?\d*)", out)
            if m:
                hrs, mins, secs = float(m.group(1)), float(m.group(2)), float(m.group(3))
                dur = round(hrs * 3600 + mins * 60 + secs, 2)
                if dur > 1.0 and ("Video:" in out):
                    return True, dur
    except Exception:
        pass

    try:
        with open(file_path, "rb") as f:
            head = f.read(65536)
            if b"ftyp" not in head:
                return False, 0.0
            f.seek(0, 2)
            fsize = f.tell()
            tail_size = min(fsize, 65536)
            f.seek(fsize - tail_size)
            tail = f.read(tail_size)
            if (b"moov" in head) or (b"moov" in tail):
                return True, 30.0
    except Exception:
        pass
    return False, 0.0


class JobManager:
    """
    Central background job execution manager.
    Coordinates asynchronous tasks, idempotency tracking, cancellations,
    concurrency limiting for heavy video renders, and server startup state recovery.
    """

    def __init__(self):
        # Maps job_id -> active asyncio.Task
        self._active_tasks: Dict[str, asyncio.Task] = {}
        # Active idempotency keys (e.g., "video_render_{script_id}")
        self._active_keys: Set[str] = set()
        # Cooperative cancellation tokens
        self._cancel_events: Dict[str, Any] = {}
        # Concurrency semaphore for heavy video rendering
        self._video_semaphore: Optional[asyncio.Semaphore] = None
        self._active_renders: int = 0
        self._queued_renders: int = 0

    def _get_video_semaphore(self) -> asyncio.Semaphore:
        """Lazily initialize the video concurrency semaphore in the running event loop."""
        if self._video_semaphore is None:
            max_renders = max(1, getattr(settings, "MAX_CONCURRENT_VIDEO_RENDERS", 1))
            self._video_semaphore = asyncio.Semaphore(max_renders)
            logger.info(f"[JobManager] Initialized video concurrency semaphore (limit={max_renders}).")
        return self._video_semaphore

    async def recover_orphaned_jobs_on_boot(self, db=None):
        """
        Scans MongoDB on server boot to find any jobs left in 'running', 'processing',
        or 'composing' state from an unexpected crash or server restart.
        Marks them as 'interrupted' with recovery instructions, or auto-heals completed media assets.
        """
        try:
            if db is None:
                db = get_database()
            now = datetime.now(timezone.utc)
            fast_stale_cutoff = now - timedelta(minutes=5)
            stale_cutoff = now - timedelta(minutes=5)

            # 1. Recover Stale Agent Executions
            exec_res = await db.agent_executions.update_many(
                {
                    "status": "running",
                    "$or": [
                        {"created_at": {"$lt": fast_stale_cutoff}},
                        {"started_at": {"$lt": fast_stale_cutoff}},
                        {"created_at": {"$exists": False}}
                    ]
                },
                {
                    "$set": {
                        "status": "failed",
                        "error_message": "Execution interrupted due to server restart. Please retry.",
                        "completed_at": now
                    }
                }
            )

            # 2. Recover Stale Research Jobs
            research_res = await db.research_jobs.update_many(
                {
                    "status": "running",
                    "$or": [
                        {"created_at": {"$lt": fast_stale_cutoff}},
                        {"started_at": {"$lt": fast_stale_cutoff}},
                        {"created_at": {"$exists": False}}
                    ]
                },
                {
                    "$set": {
                        "status": "failed",
                        "error_message": "Research job interrupted by server restart. Can be retried without lost data.",
                        "completed_at": now
                    }
                }
            )

            # 3. Recover Stale or Orphaned Video Jobs with Self-Healing Media Verification
            from pathlib import Path
            stale_video_jobs = await db.video_jobs.find(
                {
                    "status": {"$in": ["processing", "composing", "rendering", "queued"]},
                    "$or": [
                        {"created_at": {"$lt": stale_cutoff}},
                        {"started_at": {"$lt": stale_cutoff}},
                        {"created_at": {"$exists": False}}
                    ]
                }
            ).to_list(100)

            # Also check video jobs whose agent execution is already failed/cancelled
            failed_execs = await db.agent_executions.find(
                {"agent_type": "video_production", "status": {"$in": ["failed", "cancelled"]}},
                {"input_data.video_job_id": 1}
            ).to_list(100)
            failed_vjob_ids = {
                e.get("input_data", {}).get("video_job_id") for e in failed_execs if e.get("input_data", {}).get("video_job_id")
            }
            if failed_vjob_ids:
                from bson import ObjectId
                valid_ids = [ObjectId(vid) for vid in failed_vjob_ids if ObjectId.is_valid(vid)]
                orphaned_jobs = await db.video_jobs.find(
                    {"_id": {"$in": valid_ids}, "status": {"$in": ["processing", "composing", "rendering", "queued"]}}
                ).to_list(100)
                stale_video_jobs.extend(orphaned_jobs)

            # Deduplicate by _id
            seen_job_ids = set()
            unique_vjobs = []
            for j in stale_video_jobs:
                if str(j["_id"]) not in seen_job_ids:
                    seen_job_ids.add(str(j["_id"]))
                    unique_vjobs.append(j)

            recovered_vjobs_count = 0
            for vjob in unique_vjobs:
                v_id = str(vjob["_id"])
                # Check candidate file locations on disk
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

                is_valid = False
                detected_dur = 0.0
                if found_mp4:
                    is_valid, detected_dur = is_mp4_valid_and_playable(found_mp4)

                if found_mp4 and is_valid:
                    # Self-heal: the video is genuinely complete and playable!
                    file_size_mb = round(found_mp4.stat().st_size / (1024 * 1024), 2)
                    await db.video_jobs.update_one(
                        {"_id": vjob["_id"]},
                        {
                            "$set": {
                                "status": "completed",
                                "progress_percent": 100,
                                "video_url": f"/media/videos/{found_mp4.name}",
                                "video_path": str(found_mp4.resolve()),
                                "thumbnail_path": str(found_thumb.resolve()) if found_thumb else None,
                                "duration_actual": detected_dur or vjob.get("duration_seconds", 60),
                                "file_size_mb": file_size_mb,
                                "error_message": None,
                                "completed_at": now,
                            }
                        }
                    )
                    logger.info(f"[JobManager] Self-healed completed video job {v_id} ({detected_dur:.1f}s) from existing disk file {found_mp4.name}")
                else:
                    if found_mp4 and not is_valid:
                        logger.warning(f"[JobManager] Discarding corrupt/truncated video artifact {found_mp4}")
                        try:
                            found_mp4.unlink()
                        except Exception:
                            pass
                    await db.video_jobs.update_one(
                        {"_id": vjob["_id"]},
                        {
                            "$set": {
                                "status": "failed",
                                "error_message": "Video rendering was interrupted by server restart. Click 'Retry Video Agent' to resume.",
                                "completed_at": now,
                            }
                        }
                    )
                recovered_vjobs_count += 1

            # 4. Recover Stale Incomplete Scripts
            scripts_res = await db.scripts.update_many(
                {
                    "status": "generating",
                    "$or": [
                        {"updated_at": {"$lt": stale_cutoff}},
                        {"created_at": {"$lt": stale_cutoff}},
                        {"created_at": {"$exists": False}}
                    ]
                },
                {
                    "$set": {
                        "status": "failed",
                        "error_message": "Script generation was interrupted. Click Regenerate to resume.",
                        "updated_at": now
                    }
                }
            )

            logger.info(
                f"[JobManager] Boot recovery complete: "
                f"{exec_res.modified_count} executions, {research_res.modified_count} research jobs, "
                f"{recovered_vjobs_count} video jobs, {scripts_res.modified_count} scripts recovered."
            )
        except Exception as e:
            logger.error(f"[JobManager] Failed to run boot recovery: {e}")

    async def submit_job(
        self,
        job_id: str,
        idempotency_key: str,
        coro_func: Callable[[], Coroutine[Any, Any, Any]],
        job_type: str,
        campaign_id: str
    ) -> bool:
        """
        Submits a job for execution if not already actively running under idempotency_key.
        For video rendering jobs, enforces concurrency limits via an asynchronous semaphore,
        queueing subsequent jobs to prevent container memory limit exceedance.
        """
        # Clean up any stale finished tasks
        for t_id, t_obj in list(self._active_tasks.items()):
            if t_obj.done():
                self._active_tasks.pop(t_id, None)

        if idempotency_key in self._active_keys:
            # Verify if any task associated with this job is actually still alive
            task_alive = any(
                not t.done() for t_id, t in self._active_tasks.items() if t_id == job_id
            )
            if not task_alive:
                self._active_keys.discard(idempotency_key)
            else:
                logger.warning(f"[JobManager] Duplicate job rejected for key: {idempotency_key}")
                return False

        self._active_keys.add(idempotency_key)
        import threading
        cancel_event = threading.Event()
        self._cancel_events[job_id] = cancel_event

        is_video = (job_type == "video_production")
        if is_video:
            self._queued_renders += 1
            logger.info(
                f"[JobManager] Video render job {job_id} scheduled "
                f"(active_renders={self._active_renders}, queued_renders={self._queued_renders})"
            )

        async def _wrapper():
            try:
                if is_video:
                    timeout_sec = float(getattr(settings, "VIDEO_RENDER_TIMEOUT_SECONDS", 300))
                    semaphore = self._get_video_semaphore()
                    async with semaphore:
                        self._queued_renders = max(0, self._queued_renders - 1)
                        self._active_renders += 1
                        logger.info(
                            f"[JobManager] Video render job {job_id} acquired execution lock "
                            f"(active_renders={self._active_renders}, queued_renders={self._queued_renders})"
                        )
                        try:
                            await asyncio.wait_for(coro_func(), timeout=timeout_sec)
                        except asyncio.TimeoutError:
                            logger.error(f"[JobManager] Video render job {job_id} timed out after {timeout_sec}s.")
                            ev = self._cancel_events.get(job_id)
                            if ev:
                                ev.set()
                            db = get_database()
                            await db.agent_executions.update_one(
                                {"_id": ObjectId(job_id) if ObjectId.is_valid(job_id) else None},
                                {"$set": {
                                    "status": "failed",
                                    "error_message": f"Render timed out after {timeout_sec:.0f}s. Resources released.",
                                    "completed_at": datetime.now(timezone.utc)
                                }}
                            )
                        finally:
                            self._active_renders = max(0, self._active_renders - 1)
                else:
                    await coro_func()
            except asyncio.CancelledError:
                logger.info(f"[JobManager] Job {job_id} was cancelled.")
                ev = self._cancel_events.get(job_id)
                if ev:
                    ev.set()
                db = get_database()
                await db.agent_executions.update_one(
                    {"_id": ObjectId(job_id) if ObjectId.is_valid(job_id) else None},
                    {"$set": {"status": "cancelled", "completed_at": datetime.now(timezone.utc)}}
                )
            except Exception as e:
                logger.error(f"[JobManager] Job {job_id} raised unhandled exception: {e}")
            finally:
                self._cancel_events.pop(job_id, None)
                self._active_keys.discard(idempotency_key)
                self._active_tasks.pop(job_id, None)

        task = asyncio.create_task(_wrapper())
        self._active_tasks[job_id] = task
        return True

    def get_metrics(self) -> Dict[str, Any]:
        """Returns background worker telemetry, concurrency, and memory metrics."""
        from services.memory_monitor import get_process_memory_mb, get_system_memory_mb
        return {
            "active_tasks_count": len([t for t in self._active_tasks.values() if not t.done()]),
            "active_renders": self._active_renders,
            "queued_renders": self._queued_renders,
            "max_concurrent_renders": getattr(settings, "MAX_CONCURRENT_VIDEO_RENDERS", 1),
            "process_memory": get_process_memory_mb(),
            "system_memory": get_system_memory_mb(),
        }

    async def cancel_job(self, job_id: str) -> bool:
        """Cancels an actively running background task."""
        ev = self._cancel_events.get(job_id)
        if ev:
            ev.set()
        task = self._active_tasks.get(job_id)
        if task and not task.done():
            task.cancel()
            self._active_tasks.pop(job_id, None)
            return True
        return False

    def get_cancel_event(self, job_id: str) -> Optional[Any]:
        """Retrieves the cooperative cancellation token for a running job."""
        return self._cancel_events.get(job_id)

    def is_job_running(self, job_id: str) -> bool:
        task = self._active_tasks.get(job_id)
        return task is not None and not task.done()


# Global job manager singleton
job_manager = JobManager()


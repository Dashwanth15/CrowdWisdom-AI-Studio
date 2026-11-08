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

logger = logging.getLogger(__name__)


class JobManager:
    """
    Central background job execution manager.
    Coordinates asynchronous tasks, idempotency tracking, cancellations,
    and server startup state recovery.
    """

    def __init__(self):
        # Maps job_id -> active asyncio.Task
        self._active_tasks: Dict[str, asyncio.Task] = {}
        # Active idempotency keys (e.g., "video_render_{script_id}")
        self._active_keys: Set[str] = set()

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

                if found_mp4:
                    # Self-heal: the video was successfully rendered to disk!
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
                                "duration_actual": vjob.get("duration_seconds", 60),
                                "file_size_mb": file_size_mb,
                                "error_message": None,
                                "completed_at": now,
                            }
                        }
                    )
                    logger.info(f"[JobManager] Self-healed completed video job {v_id} from existing disk file {found_mp4.name}")
                else:
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

        async def _wrapper():
            try:
                await coro_func()
            except asyncio.CancelledError:
                logger.info(f"[JobManager] Job {job_id} was cancelled.")
                db = get_database()
                await db.agent_executions.update_one(
                    {"_id": ObjectId(job_id) if ObjectId.is_valid(job_id) else None},
                    {"$set": {"status": "cancelled", "completed_at": datetime.now(timezone.utc)}}
                )
            except Exception as e:
                logger.error(f"[JobManager] Job {job_id} raised unhandled exception: {e}")
            finally:
                self._active_keys.discard(idempotency_key)
                self._active_tasks.pop(job_id, None)

        task = asyncio.create_task(_wrapper())
        self._active_tasks[job_id] = task
        return True

    async def cancel_job(self, job_id: str) -> bool:
        """Cancels an actively running background task."""
        task = self._active_tasks.get(job_id)
        if task and not task.done():
            task.cancel()
            self._active_tasks.pop(job_id, None)
            return True
        return False

    def is_job_running(self, job_id: str) -> bool:
        task = self._active_tasks.get(job_id)
        return task is not None and not task.done()


# Global job manager singleton
job_manager = JobManager()


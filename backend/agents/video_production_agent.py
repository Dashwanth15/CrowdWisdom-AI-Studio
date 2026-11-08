"""
CrowdWisdom AI Studio — Video Production Agent
Transforms approved storyboards into actual MP4 video advertisements.
Integrates with OpenMontage for programmatic video composition.
"""
import json
import os
import logging
import asyncio
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from bson import ObjectId

from agents.base_agent import BaseHermesAgent
from services.integration_service import get_decrypted_api_key
from database.connection import get_database
from video_engine.openmontage_adapter import openmontage_adapter
from config import settings

logger = logging.getLogger(__name__)


class VideoProductionAgent(BaseHermesAgent):
    agent_type = "video_production"
    agent_name = "Video Production Agent"
    agent_description = "Transforms approved storyboards into cinematic MP4 video advertisements using OpenMontage."

    async def _run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        campaign_id = input_data["campaign_id"]
        video_job_id = input_data["video_job_id"]
        script_id = input_data["script_id"]
        aspect_ratio = input_data.get("aspect_ratio", "9:16")
        quality = input_data.get("quality", "high")

        db = get_database()
        campaign = await db.campaigns.find_one({"_id": ObjectId(campaign_id)}) if ObjectId.is_valid(campaign_id) else None
        campaign_duration = campaign.get("video_duration_seconds", 60) if campaign else 60
        duration = int(input_data.get("duration_seconds") or campaign_duration)

        # Update video job status
        await db.video_jobs.update_one(
            {"_id": ObjectId(video_job_id)},
            {"$set": {"status": "processing", "started_at": datetime.now(timezone.utc)}}
        )

        # --- Step 1: Load approved script ---
        await self._log_progress("loading_script", "Loading approved script...", 5)

        script_doc = await db.scripts.find_one({"_id": ObjectId(script_id)})
        if not script_doc:
            raise ValueError(f"Script {script_id} not found.")
        if script_doc.get("status") != "approved":
            raise ValueError("Script must be approved before video production.")

        scenes = script_doc.get("scenes", [])
        if not scenes:
            raise ValueError("Script has no scenes defined.")

        for sc in scenes:
            sc["script_id"] = str(script_doc.get("_id", ""))

        # --- Step 1.B: Strict Pre-Flight Visual Asset Validation Gate ---
        await self._log_progress("validating_assets", "Performing pre-flight visual asset validation...", 8)
        from PIL import Image
        from services.visual_asset_service import visual_asset_service

        def is_scene_asset_valid(scene_dict: dict) -> bool:
            m_type = scene_dict.get("media_type")
            # animated_chart generates its own frames dynamically via procedural canvas
            if m_type == "animated_chart":
                return True

            p = scene_dict.get("visual_asset_path")
            if not p:
                return m_type == "product_demo"

            candidates = [
                Path(p),
                Path(settings.MEDIA_DIR) / "assets" / Path(p).name,
                Path(settings.MEDIA_DIR) / "assets" / "stock_footage" / Path(p).name,
                Path("media") / "assets" / Path(p).name,
                Path("media") / "assets" / "stock_footage" / Path(p).name,
                Path("backend") / "media" / "assets" / Path(p).name,
                Path("backend") / "media" / "assets" / "stock_footage" / Path(p).name,
                Path.cwd() / p,
                Path.cwd() / "backend" / p,
            ]
            valid_cand = None
            for c in candidates:
                if c.exists() and c.is_file() and c.stat().st_size > 1000:
                    valid_cand = c
                    break

            if not valid_cand:
                return False

            # Verify readability
            if not str(valid_cand).lower().endswith((".mp4", ".mov", ".webm")):
                try:
                    with Image.open(valid_cand) as img:
                        img.verify()
                except Exception:
                    return False
            return True

        invalid_indices = [i + 1 for i, sc in enumerate(scenes) if not is_scene_asset_valid(sc)]
        if invalid_indices:
            logger.warning(
                f"[VideoProductionAgent] Pre-flight validation found missing/corrupt assets for Scene(s) {invalid_indices} "
                f"in script {script_id}. Initiating auto-recovery..."
            )
            await self._log_progress("recovering_assets", f"Auto-recovering visual assets for scene(s) {invalid_indices}...", 9)
            updated_scenes = await visual_asset_service.ensure_script_visual_assets(
                script_doc=script_doc,
                aspect_ratio=aspect_ratio,
                db=db,
                force_refresh=True,
            )
            scenes = updated_scenes
            for sc in scenes:
                sc["script_id"] = str(script_doc.get("_id", ""))

            # Re-verify post recovery
            still_invalid = [i + 1 for i, sc in enumerate(scenes) if not is_scene_asset_valid(sc)]
            if still_invalid:
                err_msg = f"Pre-flight visual validation failed: Scene(s) {still_invalid} missing valid visual assets. Rendering halted."
                logger.error(f"[VideoProductionAgent] {err_msg}")
                await db.video_jobs.update_one(
                    {"_id": ObjectId(video_job_id)},
                    {"$set": {"status": "failed", "error_message": err_msg}}
                )
                raise ValueError(err_msg)

            logger.info(f"[VideoProductionAgent] Pre-flight auto-recovery successfully verified all {len(scenes)} scene assets.")

        # --- Step 2: Check video engine ---
        await self._log_progress("initializing_engine", "Initializing video engine...", 10)

        engine_result = await self._initialize_openmontage()

        # --- Step 3: Prepare output directory ---
        media_dir = Path(settings.MEDIA_DIR)
        videos_dir = media_dir / "videos"
        thumbnails_dir = media_dir / "thumbnails"
        videos_dir.mkdir(parents=True, exist_ok=True)
        thumbnails_dir.mkdir(parents=True, exist_ok=True)

        output_filename = f"video_{video_job_id}.mp4"
        output_path = videos_dir / output_filename
        thumbnail_filename = f"thumb_{video_job_id}.jpg"
        thumbnail_path = thumbnails_dir / thumbnail_filename

        # --- Step 4: Compose video via OpenMontage Engine ---
        await self._log_progress("composing", "Composing video scenes via OpenMontage engine...", 20)

        try:
            render_meta = await self._compose_video(
                scenes=scenes,
                script_doc=script_doc,
                output_path=str(output_path),
                thumbnail_path=str(thumbnail_path),
                aspect_ratio=aspect_ratio,
                duration=duration,
                quality=quality,
                video_job_id=video_job_id,
                db=db,
            )
        except Exception as e:
            logger.error(f"Video composition failed: {e}")
            await db.video_jobs.update_one(
                {"_id": ObjectId(video_job_id)},
                {"$set": {"status": "failed", "error_message": str(e)}}
            )
            raise

        # --- Step 5: Save asset record ---
        await self._log_progress("saving", "Saving video asset...", 95)

        file_size_mb = render_meta.get("file_size_mb")
        actual_duration = render_meta.get("duration")

        asset_doc = {
            "campaign_id": campaign_id,
            "asset_type": "video",
            "filename": output_filename,
            "file_path": str(output_path),
            "url": f"/media/videos/{output_filename}",
            "file_size_bytes": int(file_size_mb * 1024 * 1024) if file_size_mb else None,
            "duration_seconds": actual_duration,
            "mime_type": "video/mp4",
            "tags": ["generated", "advertisement", aspect_ratio],
            "created_at": datetime.now(timezone.utc),
        }
        asset_result = await db.media_assets.insert_one(asset_doc)

        # Update video job
        await db.video_jobs.update_one(
            {"_id": ObjectId(video_job_id)},
            {
                "$set": {
                    "status": "completed",
                    "video_path": str(output_path),
                    "thumbnail_path": str(thumbnail_path) if os.path.exists(str(thumbnail_path)) else None,
                    "video_url": f"/media/videos/{output_filename}",
                    "duration_actual": actual_duration,
                    "file_size_mb": file_size_mb,
                    "progress_percent": 100,
                    "completed_at": datetime.now(timezone.utc),
                    "error_message": None,
                }
            },
        )

        # Mark campaign as completed
        if ObjectId.is_valid(campaign_id):
            await db.campaigns.update_one(
                {"_id": ObjectId(campaign_id)},
                {"$set": {"status": "completed", "updated_at": datetime.now(timezone.utc)}}
            )

        from services.websocket_manager import ws_manager
        # Explicit completed status broadcast for both job_id keys (video_job_id and execution_id)
        await ws_manager.send_job_progress(
            job_id=video_job_id,
            job_type="video_production",
            campaign_id=campaign_id,
            status="completed",
            progress_percent=100,
            current_stage="done",
            data={
                "video_job_id": video_job_id,
                "video_url": f"/media/videos/{output_filename}",
                "script_id": script_id,
                "message": "Video production complete!",
            },
        )
        if self._execution_id:
            await ws_manager.send_job_progress(
                job_id=self._execution_id,
                job_type="video_production",
                campaign_id=campaign_id,
                status="completed",
                progress_percent=100,
                current_stage="done",
                data={
                    "video_job_id": video_job_id,
                    "video_url": f"/media/videos/{output_filename}",
                    "script_id": script_id,
                    "message": "Video production complete!",
                },
            )

        await self._log_progress("done", "Video production complete!", 100)

        return {
            "video_job_id": video_job_id,
            "video_url": f"/media/videos/{output_filename}",
            "file_size_mb": file_size_mb,
            "duration_seconds": actual_duration,
            "asset_id": str(asset_result.inserted_id),
        }

    async def _initialize_openmontage(self) -> Dict[str, Any]:
        """Initialize OpenMontage tool registry if available."""
        if openmontage_adapter.is_openmontage_available:
            return {"engine": "openmontage", "available": True}

        openmontage_path = Path(settings.MEDIA_DIR).parent / "video_engine" / "openmontage"
        registry_file = openmontage_path / "tools" / "tool_registry.py"
        if openmontage_path.exists() and registry_file.exists():
            try:
                import importlib.util
                spec = importlib.util.spec_from_file_location("openmontage_tool_registry", str(registry_file))
                if spec and spec.loader:
                    tool_mod = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(tool_mod)
                    registry = getattr(tool_mod, "registry", None)
                    if registry and hasattr(registry, "discover"):
                        registry.discover()
                        envelope = getattr(registry, "support_envelope", lambda: {})()
                        logger.info(f"OpenMontage initialized: {envelope}")
                        return {"engine": "openmontage", "envelope": envelope, "available": True}
            except Exception as e:
                logger.warning(f"OpenMontage initialization failed: {e}. Using MoviePy fallback.")

        return {"engine": "openmontage_moviepy_composite", "available": True}

    async def _compose_video(
        self,
        scenes: List[Dict],
        script_doc: Dict,
        output_path: str,
        thumbnail_path: str,
        aspect_ratio: str,
        duration: int,
        quality: str,
        video_job_id: str,
        db,
    ) -> Dict[str, Any]:
        """
        Compose the video using the unified OpenMontage adapter.
        Emits progress updates to DB and WebSocket, and renders high-fidelity MP4.
        """
        await db.video_jobs.update_one(
            {"_id": ObjectId(video_job_id)},
            {"$set": {"status": "composing", "progress_percent": 25, "current_stage": "composing_scenes"}}
        )

        async def _progress(pct: int, msg: str):
            await db.video_jobs.update_one(
                {"_id": ObjectId(video_job_id)},
                {"$set": {"progress_percent": pct, "current_stage": msg}}
            )
            await self._log_progress("rendering", msg, pct)
            try:
                from services.websocket_manager import ws_manager
                await ws_manager.send_job_progress(
                    job_id=video_job_id,
                    job_type="video_production",
                    campaign_id=self._campaign_id or str(script_doc.get("campaign_id", "")),
                    status="rendering" if pct < 100 else "completed",
                    progress_percent=pct,
                    current_stage=msg,
                    data={
                        "video_job_id": video_job_id,
                        "script_id": str(script_doc.get("_id", "")),
                    },
                )
            except Exception:
                pass

        render_res = await openmontage_adapter.render_video(
            scenes=scenes,
            output_file_path=output_path,
            thumbnail_file_path=thumbnail_path,
            aspect_ratio=aspect_ratio,
            target_duration=duration,
            quality=quality,
            progress_callback=_progress
        )
        return render_res


video_production_agent = VideoProductionAgent()


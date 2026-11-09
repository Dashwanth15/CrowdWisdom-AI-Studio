"""
CrowdWisdom AI Studio — Hermes Orchestrator
Central workflow engine coordinating the specialized AI agents:
1. AdsManagerAgent → Discovers and evaluates ad campaigns
2. CreativeIntelligenceEngine → Synthesizes research into creative briefs (Checkpoint 1)
3. ScriptAgent → Generates cinematic storyboards (Checkpoint 2: Human Approval)
4. VideoProductionAgent → Produces MP4 video advertisements (Checkpoint 3: Review)
"""
import asyncio
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from bson import ObjectId

from database.connection import get_database
from services.websocket_manager import ws_manager
from workers.job_manager import job_manager
from services.creative_intelligence_engine import creative_intelligence_engine

logger = logging.getLogger(__name__)


class HermesOrchestrator:
    """
    Orchestrates the complete autonomous AI marketing workflow with persistent state,
    human approval gates, and resilient job execution.
    """

    async def create_execution(
        self,
        campaign_id: str,
        agent_type: str,
        task_name: str,
        input_data: Dict[str, Any],
    ) -> str:
        """Create a new agent execution record in MongoDB."""
        db = get_database()
        doc = {
            "campaign_id": campaign_id,
            "agent_type": agent_type,
            "task_name": task_name,
            "status": "pending",
            "input_data": input_data,
            "output_data": None,
            "error_message": None,
            "duration_seconds": None,
            "tool_calls": [],
            "current_stage": None,
            "progress_percent": 0,
            "started_at": None,
            "completed_at": None,
            "created_at": datetime.now(timezone.utc),
        }
        result = await db.agent_executions.insert_one(doc)
        return str(result.inserted_id)

    async def create_workflow_task(
        self,
        campaign_id: str,
        task_name: str,
        description: str,
        agent_type: Optional[str] = None,
        execution_id: Optional[str] = None,
        depends_on: Optional[List[str]] = None,
        priority: int = 0,
    ) -> str:
        """Create a persistent workflow task card for the Kanban board."""
        db = get_database()
        doc = {
            "campaign_id": campaign_id,
            "task_name": task_name,
            "description": description,
            "agent_type": agent_type,
            "status": "pending",
            "priority": priority,
            "depends_on": depends_on or [],
            "execution_id": execution_id,
            "started_at": None,
            "completed_at": None,
            "created_at": datetime.now(timezone.utc),
        }
        result = await db.workflow_tasks.insert_one(doc)
        return str(result.inserted_id)

    async def launch_research(
        self, campaign_id: str, research_input: Dict[str, Any]
    ) -> Dict[str, str]:
        """
        Launch the Ads Manager Agent for advertisement research.
        Enforces idempotency: only one active research job per campaign at a time.
        """
        db = get_database()
        idempotency_key = f"research_{campaign_id}"

        # Retrieve campaign target country
        campaign_doc = await db.campaigns.find_one({"_id": ObjectId(campaign_id)})
        target_country = (
            research_input.get("target_country")
            or (campaign_doc.get("target_country") if campaign_doc else None)
            or (campaign_doc.get("audience", {}).get("target_country") if campaign_doc else None)
            or "IN"
        )
        if target_country == "BOTH":
            target_country = "IN"

        # 1. Create persistent research job record
        research_job_doc = {
            "campaign_id": campaign_id,
            "target_country": target_country,
            "status": "pending",
            "keywords": research_input.get("keywords", []),
            "competitor_names": research_input.get("competitor_names", []),
            "date_range_days": research_input.get("date_range_days", 30),
            "ads_found": 0,
            "ads_evaluated": 0,
            "insights_extracted": 0,
            "error_message": None,
            "started_at": None,
            "completed_at": None,
            "created_at": datetime.now(timezone.utc),
        }
        research_result = await db.research_jobs.insert_one(research_job_doc)
        research_job_id = str(research_result.inserted_id)

        # 2. Create execution record
        full_input = {**research_input, "campaign_id": campaign_id, "research_job_id": research_job_id, "target_country": target_country}
        execution_id = await self.create_execution(
            campaign_id=campaign_id,
            agent_type="ads_manager",
            task_name="Advertisement Research & Analysis",
            input_data=full_input,
        )

        # 3. Create Kanban task
        await self.create_workflow_task(
            campaign_id=campaign_id,
            task_name="Advertisement Research",
            description=f"Meta Ads research on keywords: {research_input.get('keywords', [])}",
            agent_type="ads_manager",
            execution_id=execution_id,
            priority=10,
        )

        # 4. Submit to persistent Job Manager
        async def _run():
            await self._run_agent_task("ads_manager", campaign_id, execution_id, full_input)
            # Automatic synthesis by Creative Intelligence Engine
            try:
                logger.info(f"[Orchestrator] Invoking Creative Intelligence Engine for campaign {campaign_id}")
                await creative_intelligence_engine.generate_creative_brief(
                    campaign_id=campaign_id,
                    research_job_id=research_job_id
                )
            except Exception as cie_err:
                logger.warning(f"[Orchestrator] Auto CIE brief generation notice: {cie_err}")

        submitted = await job_manager.submit_job(
            job_id=execution_id,
            idempotency_key=idempotency_key,
            coro_func=_run,
            job_type="ads_manager",
            campaign_id=campaign_id
        )

        if not submitted:
            await db.research_jobs.update_one(
                {"_id": ObjectId(research_job_id)},
                {"$set": {"status": "failed", "error_message": "A research job is already actively running for this campaign."}}
            )
            raise ValueError("A research job is already running for this campaign.")

        return {"execution_id": execution_id, "research_job_id": research_job_id}

    async def launch_script_generation(
        self, campaign_id: str, script_input: Dict[str, Any]
    ) -> Dict[str, str]:
        """
        Launch the Script Agent to generate an advertising storyboard.
        """
        db = get_database()

        approach = script_input.get("approach", "pain_point")
        approach_label = approach.replace("_", " ").title()

        # Retrieve campaign target country
        campaign_doc = await db.campaigns.find_one({"_id": ObjectId(campaign_id)})
        target_country = (
            script_input.get("target_country")
            or (campaign_doc.get("target_country") if campaign_doc else None)
            or (campaign_doc.get("audience", {}).get("target_country") if campaign_doc else None)
            or "IN"
        )
        if target_country == "BOTH":
            target_country = "IN"

        # Clean up any prior unapproved/stale scripts for the same campaign & approach
        # This prevents duplicate pending approval cards from piling up
        await db.scripts.delete_many({
            "campaign_id": campaign_id,
            "approach": approach,
            "status": {"$in": ["generating", "pending_approval", "failed", "draft"]}
        })

        # Create persistent script record with explicit generating state
        script_doc = {
            "campaign_id": campaign_id,
            "target_country": target_country,
            "approach": approach,
            "status": "generating",
            "version": 1,
            "campaign_title": f"Generating {approach_label} Concept...",
            "target_audience": None,
            "pain_point": None,
            "marketing_angle": None,
            "core_message": "AI Script Agent is actively synthesizing research, hook variations, and scene-by-scene storyboard...",
            "unique_selling_proposition": None,
            "emotional_direction": None,
            "visual_hook": None,
            "full_script": None,
            "scenes": [],
            "voiceover_full": None,
            "on_screen_texts": [],
            "music_direction": None,
            "sound_effects": [],
            "call_to_action": None,
            "estimated_duration_seconds": None,
            "research_references": [],
            "supporting_evidence": [],
            "approved_by": None,
            "approved_at": None,
            "rejection_reason": None,
            "error_message": None,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
        script_result = await db.scripts.insert_one(script_doc)
        script_id = str(script_result.inserted_id)

        # Increment campaign script counter
        await db.campaigns.update_one(
            {"_id": ObjectId(campaign_id)},
            {"$inc": {"scripts_generated": 1}}
        )

        full_input = {**script_input, "campaign_id": campaign_id, "script_id": script_id, "target_country": target_country}
        execution_id = await self.create_execution(
            campaign_id=campaign_id,
            agent_type="script",
            task_name="Cinematic Script & Storyboard Creation",
            input_data=full_input,
        )

        await self.create_workflow_task(
            campaign_id=campaign_id,
            task_name="Script & Storyboard Generation",
            description=f"Generate {script_input.get('approach', 'pain_point')} storyboard concept",
            agent_type="script",
            execution_id=execution_id,
            priority=8,
        )

        idempotency_key = f"script_{script_id}"
        await job_manager.submit_job(
            job_id=execution_id,
            idempotency_key=idempotency_key,
            coro_func=lambda: self._run_agent_task("script", campaign_id, execution_id, full_input),
            job_type="script",
            campaign_id=campaign_id
        )

        return {"execution_id": execution_id, "script_id": script_id}

    async def launch_video_production(
        self, campaign_id: str, video_input: Dict[str, Any]
    ) -> Dict[str, str]:
        """
        Launch the Video Production Agent to render video.
        STRICT CHECKPOINT 2: Script must have status == 'approved'.
        """
        db = get_database()
        script_id = video_input.get("script_id")
        if not script_id or not ObjectId.is_valid(script_id):
            raise ValueError("Valid script_id is required for video production.")

        # Verify script is approved
        script_doc = await db.scripts.find_one({"_id": ObjectId(script_id)})
        if not script_doc:
            raise ValueError(f"Script {script_id} not found.")

        if script_doc.get("status") != "approved":
            raise ValueError(
                f"Checkpoint Error: Script must be approved by marketing manager before video production. Current status: '{script_doc.get('status')}'"
            )

        # Pre-flight asset verification: Auto-heal any missing scene visual assets before queueing
        scenes = script_doc.get("scenes", [])
        if any(not sc.get("visual_asset_path") or sc.get("visual_asset_status") == "failed" for sc in scenes):
            from services.visual_asset_service import visual_asset_service
            logger.info(f"[Orchestrator] Storyboard {script_id} contains unpopulated scene assets. Initiating auto-recovery...")
            updated_scenes = await visual_asset_service.ensure_script_visual_assets(
                script_doc=script_doc,
                aspect_ratio=video_input.get("aspect_ratio", "9:16"),
                db=db,
                force_refresh=True
            )
            script_doc["scenes"] = updated_scenes

        # Enforce idempotency on video rendering for this script
        idempotency_key = f"video_render_{script_id}"

        # Resolve target duration from campaign configuration
        campaign = await db.campaigns.find_one({"_id": ObjectId(campaign_id)})
        campaign_duration = campaign.get("video_duration_seconds", 60) if campaign else 60
        target_duration = int(video_input.get("duration_seconds") or campaign_duration)

        # Create persistent video job record
        video_job_doc = {
            "campaign_id": campaign_id,
            "script_id": script_id,
            "status": "queued",
            "aspect_ratio": video_input.get("aspect_ratio", "9:16"),
            "duration_seconds": target_duration,
            "quality": video_input.get("quality", "high"),
            "progress_percent": 0,
            "current_stage": "queued",
            "video_path": None,
            "thumbnail_path": None,
            "video_url": None,
            "duration_actual": None,
            "file_size_mb": None,
            "error_message": None,
            "production_log": [],
            "started_at": None,
            "completed_at": None,
            "created_at": datetime.now(timezone.utc),
        }
        job_result = await db.video_jobs.insert_one(video_job_doc)
        video_job_id = str(job_result.inserted_id)

        full_input = {
            **video_input,
            "duration_seconds": target_duration,
            "campaign_id": campaign_id,
            "video_job_id": video_job_id,
        }
        execution_id = await self.create_execution(
            campaign_id=campaign_id,
            agent_type="video_production",
            task_name="Cinematic Video Rendering",
            input_data=full_input,
        )

        await self.create_workflow_task(
            campaign_id=campaign_id,
            task_name="Video Production & Rendering",
            description=f"Produce {video_input.get('aspect_ratio', '9:16')} commercial MP4",
            agent_type="video_production",
            execution_id=execution_id,
            priority=5,
        )

        # Store execution_id on the video_job document for dual-key tracking
        await db.video_jobs.update_one(
            {"_id": ObjectId(video_job_id)},
            {"$set": {"execution_id": execution_id}}
        )

        submitted = await job_manager.submit_job(
            job_id=execution_id,
            idempotency_key=idempotency_key,
            coro_func=lambda: self._run_agent_task("video_production", campaign_id, execution_id, full_input),
            job_type="video_production",
            campaign_id=campaign_id,
            related_id=video_job_id,
        )

        if not submitted:
            await db.video_jobs.update_one(
                {"_id": ObjectId(video_job_id)},
                {"$set": {"status": "failed", "error_message": "A rendering job is already actively processing for this script."}}
            )
            raise ValueError("A rendering job is already processing for this script.")

        # Update campaign video counter
        await db.campaigns.update_one(
            {"_id": ObjectId(campaign_id)},
            {"$inc": {"videos_generated": 1}}
        )

        return {"execution_id": execution_id, "video_job_id": video_job_id}

    async def _run_agent_task(
        self, agent_type: str, campaign_id: str, execution_id: str, input_data: Dict
    ) -> None:
        """Background agent runner updating persistent state prior to broadcasting."""
        db = get_database()
        try:
            if agent_type == "ads_manager":
                from agents.ads_manager_agent import AdsManagerAgent
                agent = AdsManagerAgent()
            elif agent_type == "script":
                from agents.script_agent import ScriptAgent
                agent = ScriptAgent()
            elif agent_type == "video_production":
                from agents.video_production_agent import VideoProductionAgent
                agent = VideoProductionAgent()
            else:
                raise ValueError(f"Unknown agent type: {agent_type}")

            await agent.execute(campaign_id, execution_id, input_data)

            # Update Kanban task to completed or awaiting_approval
            new_task_status = "completed" if agent_type != "script" else "awaiting_approval"
            await db.workflow_tasks.update_one(
                {"execution_id": execution_id},
                {
                    "$set": {
                        "status": new_task_status,
                        "completed_at": datetime.now(timezone.utc),
                    }
                },
            )

            # Broadcast persisted state
            await ws_manager.send_notification(
                title=f"{agent_type.replace('_', ' ').title()} Finished",
                message_text=f"Agent workflow step completed successfully for campaign {campaign_id}.",
                category="agent",
                action_url=f"/campaigns/{campaign_id}",
            )

        except Exception as e:
            logger.error(f"[Orchestrator] Execution {execution_id} ({agent_type}) failed: {e}")
            await db.workflow_tasks.update_one(
                {"execution_id": execution_id},
                {"$set": {"status": "failed", "completed_at": datetime.now(timezone.utc)}},
            )
            # Reconcile associated video job if this was a video production execution
            if agent_type == "video_production" and input_data.get("video_job_id"):
                v_id = input_data["video_job_id"]
                if ObjectId.is_valid(v_id):
                    await db.video_jobs.update_one(
                        {"_id": ObjectId(v_id), "status": {"$in": ["queued", "processing", "composing", "rendering"]}},
                        {
                            "$set": {
                                "status": "failed",
                                "error_message": f"Rendering failed: {str(e)[:200]}",
                                "completed_at": datetime.now(timezone.utc),
                            }
                        }
                    )
            await ws_manager.send_notification(
                title=f"{agent_type.replace('_', ' ').title()} Error",
                message_text=f"Execution error: {str(e)[:180]}",
                category="error",
            )

    async def cancel_execution(self, execution_id: str) -> bool:
        """Cancels an active execution via JobManager and updates MongoDB."""
        db = get_database()
        # Cancel background task
        await job_manager.cancel_job(execution_id)

        result = await db.agent_executions.update_one(
            {"_id": ObjectId(execution_id), "status": {"$in": ["pending", "running"]}},
            {"$set": {"status": "cancelled", "completed_at": datetime.now(timezone.utc)}}
        )
        if result.modified_count:
            await db.workflow_tasks.update_one(
                {"execution_id": execution_id},
                {"$set": {"status": "failed"}},
            )
            # Also cancel related video job if this was a video production execution
            exec_doc = await db.agent_executions.find_one({"_id": ObjectId(execution_id)})
            if exec_doc and exec_doc.get("agent_type") == "video_production":
                v_id = exec_doc.get("input_data", {}).get("video_job_id")
                if v_id and ObjectId.is_valid(v_id):
                    await db.video_jobs.update_one(
                        {"_id": ObjectId(v_id), "status": {"$in": ["queued", "processing", "composing", "rendering"]}},
                        {
                            "$set": {
                                "status": "failed",
                                "error_message": "Rendering was cancelled by user.",
                                "completed_at": datetime.now(timezone.utc),
                            }
                        }
                    )
        return result.modified_count > 0

    async def retry_execution(self, execution_id: str) -> Optional[str]:
        """Retries a failed execution cleanly."""
        db = get_database()
        original = await db.agent_executions.find_one({"_id": ObjectId(execution_id)})
        if not original:
            return None
        if original["status"] not in ("failed", "cancelled"):
            raise ValueError("Only failed or cancelled executions can be retried.")

        new_execution_id = await self.create_execution(
            campaign_id=original["campaign_id"],
            agent_type=original["agent_type"],
            task_name=f"{original['task_name']} (Retry)",
            input_data=original["input_data"],
        )

        related_id = None
        if original.get("agent_type") == "video_production":
            related_id = original.get("input_data", {}).get("video_job_id")
            if related_id and ObjectId.is_valid(related_id):
                await db.video_jobs.update_one(
                    {"_id": ObjectId(related_id)},
                    {"$set": {
                        "status": "queued",
                        "progress_percent": 0,
                        "error_message": None,
                        "execution_id": new_execution_id,
                        "started_at": datetime.now(timezone.utc),
                    }}
                )

        idempotency_key = f"retry_{original['agent_type']}_{new_execution_id}"
        await job_manager.submit_job(
            job_id=new_execution_id,
            idempotency_key=idempotency_key,
            coro_func=lambda: self._run_agent_task(
                original["agent_type"],
                original["campaign_id"],
                new_execution_id,
                original["input_data"],
            ),
            job_type=original["agent_type"],
            campaign_id=original["campaign_id"],
            related_id=related_id,
        )
        return new_execution_id


# Global orchestrator singleton
orchestrator = HermesOrchestrator()

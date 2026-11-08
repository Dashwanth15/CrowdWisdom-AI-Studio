"""
CrowdWisdom AI Studio — Base Hermes Agent Wrapper
Bridges the Hermes AIAgent sync interface to FastAPI async context.
"""
import asyncio
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from bson import ObjectId

logger = logging.getLogger(__name__)


class BaseHermesAgent(ABC):
    """
    Abstract base class for all CrowdWisdom AI Studio agents.
    Wraps Hermes AIAgent with async support, execution tracking,
    WebSocket progress broadcasting, and MongoDB logging.
    """

    agent_type: str = "base"
    agent_name: str = "Base Agent"
    agent_description: str = "Base agent"

    def __init__(self):
        self._hermes_agent = None
        self._execution_id: Optional[str] = None
        self._campaign_id: Optional[str] = None
        self._execution_mode: str = "native_hermes"
        self._db = None
        self._ws_manager = None

    async def _initialize_hermes(self, model: str, api_key: str, provider_base_url: Optional[str] = None, enabled_toolsets: Optional[List[str]] = None) -> bool:
        """Initialize the official NousResearch Hermes AIAgent in a thread to avoid blocking the event loop."""
        try:
            import os
            import sys
            from pathlib import Path

            hermes_dir = Path(__file__).resolve().parent.parent / "vendor" / "hermes_agent"
            if hermes_dir.exists() and str(hermes_dir) not in sys.path:
                sys.path.insert(0, str(hermes_dir))

            # Set provider env vars for Hermes
            base_url = provider_base_url or "https://openrouter.ai/api/v1"
            os.environ["OPENAI_BASE_URL"] = base_url
            os.environ["OPENROUTER_API_KEY"] = api_key
            os.environ["OPENAI_API_KEY"] = api_key

            def _init():
                try:
                    import importlib
                    run_agent_mod = importlib.import_module("".join(["run_", "agent"]))
                    AIAgent = getattr(run_agent_mod, "AIAgent")
                    return AIAgent(
                        base_url=base_url,
                        api_key=api_key,
                        model=model or "meta-llama/llama-3.3-70b-instruct",
                        quiet_mode=True,
                        skip_memory=True,
                        save_trajectories=False,
                        enabled_toolsets=enabled_toolsets or ["crowdwisdom"],
                    )
                except Exception as e:
                    logger.warning(f"Official Hermes AIAgent initialization notice: {e}. Falling back to direct LLM.")
                    return None

            self._hermes_agent = await asyncio.to_thread(_init)
            return self._hermes_agent is not None
        except Exception as e:
            logger.error(f"Failed to initialize Hermes agent: {e}")
            return False

    async def _chat(self, prompt: str) -> str:
        """Send a message to the Hermes agent and get a response."""
        if self._hermes_agent is None:
            raise RuntimeError("Hermes agent not initialized.")

        def _run():
            return self._hermes_agent.chat(prompt)

        return await asyncio.to_thread(_run)

    async def _log_progress(self, stage: str, message: str, progress_percent: int) -> None:
        """Log progress to MongoDB execution log and broadcast via WebSocket."""
        from database.connection import get_database
        from services.websocket_manager import ws_manager

        db = get_database()
        log_entry = {
            "execution_id": self._execution_id,
            "campaign_id": self._campaign_id,
            "agent_type": self.agent_type,
            "execution_mode": self._execution_mode,
            "stage": stage,
            "message": message,
            "progress_percent": progress_percent,
            "created_at": datetime.now(timezone.utc),
        }
        await db.execution_logs.insert_one(log_entry)

        # Update execution record
        if self._execution_id and ObjectId.is_valid(self._execution_id):
            await db.agent_executions.update_one(
                {"_id": ObjectId(self._execution_id)},
                {"$set": {"current_stage": stage, "progress_percent": progress_percent}},
            )

        # Broadcast via WebSocket
        if self._campaign_id:
            await ws_manager.send_job_progress(
                job_id=self._execution_id or "unknown",
                job_type=self.agent_type,
                campaign_id=self._campaign_id,
                status="running",
                progress_percent=progress_percent,
                current_stage=stage,
                data={"message": message},
            )

    async def execute(
        self,
        campaign_id: str,
        execution_id: str,
        input_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Main execution entry point.
        Records execution state, runs the agent, and updates MongoDB.
        """
        from database.connection import get_database
        from services.websocket_manager import ws_manager

        self._campaign_id = campaign_id
        self._execution_id = execution_id
        db = get_database()

        # Mark execution as running
        if ObjectId.is_valid(execution_id):
            await db.agent_executions.update_one(
                {"_id": ObjectId(execution_id)},
                {
                    "$set": {
                        "status": "running",
                        "execution_mode": self._execution_mode,
                        "started_at": datetime.now(timezone.utc),
                        "agent_type": self.agent_type,
                    }
                },
            )

        await ws_manager.send_agent_status(
            agent_type=self.agent_type,
            campaign_id=campaign_id,
            status="running",
            execution_id=execution_id,
        )

        start_time = datetime.now(timezone.utc)
        try:
            result = await self._run(input_data)

            # Detect mode from result if provided
            if isinstance(result, dict) and "execution_mode" in result:
                self._execution_mode = result["execution_mode"]

            duration = (datetime.now(timezone.utc) - start_time).total_seconds()
            if ObjectId.is_valid(execution_id):
                await db.agent_executions.update_one(
                    {"_id": ObjectId(execution_id)},
                    {
                        "$set": {
                            "status": "completed",
                            "execution_mode": self._execution_mode,
                            "output_data": result,
                            "error_message": None,
                            "completed_at": datetime.now(timezone.utc),
                            "duration_seconds": duration,
                        }
                    },
                )

            await ws_manager.send_agent_status(
                agent_type=self.agent_type,
                campaign_id=campaign_id,
                status="completed",
                execution_id=execution_id,
            )
            return result

        except Exception as e:
            duration = (datetime.now(timezone.utc) - start_time).total_seconds()
            error_msg = str(e)
            logger.error(f"Agent {self.agent_type} execution {execution_id} failed: {error_msg}")

            if ObjectId.is_valid(execution_id):
                await db.agent_executions.update_one(
                    {"_id": ObjectId(execution_id)},
                    {
                        "$set": {
                            "status": "failed",
                            "execution_mode": "failed",
                            "error_message": error_msg,
                            "completed_at": datetime.now(timezone.utc),
                            "duration_seconds": duration,
                        }
                    },
                )

            await ws_manager.send_agent_status(
                agent_type=self.agent_type,
                campaign_id=campaign_id,
                status="failed",
                execution_id=execution_id,
            )
            raise

    @abstractmethod
    async def _run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Implement the agent's core logic here."""
        pass


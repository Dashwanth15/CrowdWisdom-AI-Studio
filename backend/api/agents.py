"""
CrowdWisdom AI Studio — Agents API Routes
Agent control, execution management, and status monitoring.
"""
from datetime import datetime, timezone
from typing import Annotated, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from bson import ObjectId

from database.connection import get_database
from models.schemas import AgentExecutionOut, ResearchJobCreate, ResearchJobOut, ScriptCreate
from api.auth import get_current_user
from orchestrator.hermes_orchestrator import orchestrator

router = APIRouter(prefix="/agents", tags=["Agents"])


def _serialize_execution(doc: dict) -> AgentExecutionOut:
    return AgentExecutionOut(
        id=str(doc["_id"]),
        campaign_id=doc.get("campaign_id", ""),
        agent_type=doc.get("agent_type", ""),
        task_name=doc.get("task_name", ""),
        status=doc.get("status", "pending"),
        execution_mode=doc.get("execution_mode", "native_hermes"),
        framework_version=doc.get("framework_version", "NousResearch/hermes-agent@c55af2c9"),
        input_data=doc.get("input_data"),
        output_data=doc.get("output_data"),
        error_message=doc.get("error_message"),
        duration_seconds=doc.get("duration_seconds"),
        tool_calls=doc.get("tool_calls", []),
        started_at=doc.get("started_at"),
        completed_at=doc.get("completed_at"),
        created_at=doc.get("created_at") or datetime.now(timezone.utc),
    )


@router.post("/research/launch", status_code=202)
async def launch_research(
    data: ResearchJobCreate,
    current_user: Annotated[dict, Depends(get_current_user)],
):
    """Launch the Ads Manager Agent for advertisement research."""
    db = get_database()

    # Verify campaign access
    if not ObjectId.is_valid(data.campaign_id):
        raise HTTPException(status_code=400, detail="Invalid campaign ID.")
    user_role = current_user.get("role", "viewer")
    user_id = str(current_user["_id"])
    query: dict = {"_id": ObjectId(data.campaign_id)}
    if user_role not in ("admin", "marketing_manager", "creative_editor"):
        query["owner_id"] = user_id

    campaign = await db.campaigns.find_one(query)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found.")

    result = await orchestrator.launch_research(
        campaign_id=data.campaign_id,
        research_input={
            "keywords": data.keywords,
            "competitor_names": data.competitor_names or [],
            "date_range_days": data.date_range_days,
        },
    )
    return {"message": "Research launched", **result}


@router.post("/scripts/generate", status_code=202)
async def generate_script(
    data: ScriptCreate,
    current_user: Annotated[dict, Depends(get_current_user)],
):
    """Launch the Script Agent to generate an advertising concept."""
    db = get_database()

    if not ObjectId.is_valid(data.campaign_id):
        raise HTTPException(status_code=400, detail="Invalid campaign ID.")
    user_role = current_user.get("role", "viewer")
    user_id = str(current_user["_id"])
    query: dict = {"_id": ObjectId(data.campaign_id)}
    if user_role not in ("admin", "marketing_manager", "creative_editor"):
        query["owner_id"] = user_id

    campaign = await db.campaigns.find_one(query)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found.")

    result = await orchestrator.launch_script_generation(
        campaign_id=data.campaign_id,
        script_input={
            "approach": data.approach.value,
            "campaign_config": {
                "audience": campaign.get("audience", {}),
                "video_duration_seconds": campaign.get("video_duration_seconds", 45),
                "creative_direction": campaign.get("creative_direction"),
            },
            "custom_prompt": data.custom_prompt,
        },
    )
    return {"message": "Script generation launched", **result}


@router.post("/{execution_id}/cancel", status_code=200)
async def cancel_execution(
    execution_id: str,
    current_user: Annotated[dict, Depends(get_current_user)],
):
    """Cancel a running agent execution."""
    cancelled = await orchestrator.cancel_execution(execution_id)
    if not cancelled:
        raise HTTPException(status_code=400, detail="Cannot cancel: execution not found or not running.")
    return {"message": "Execution cancelled.", "execution_id": execution_id}


@router.post("/{execution_id}/retry", status_code=202)
async def retry_execution(
    execution_id: str,
    current_user: Annotated[dict, Depends(get_current_user)],
):
    """Retry a failed agent execution."""
    new_id = await orchestrator.retry_execution(execution_id)
    if not new_id:
        raise HTTPException(status_code=404, detail="Execution not found.")
    return {"message": "Execution retried.", "new_execution_id": new_id}


@router.get("/executions", response_model=List[AgentExecutionOut])
async def list_executions(
    current_user: Annotated[dict, Depends(get_current_user)],
    campaign_id: Optional[str] = None,
    agent_type: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    """List agent executions."""
    db = get_database()
    query: dict = {}
    if campaign_id:
        query["campaign_id"] = campaign_id
    if agent_type:
        query["agent_type"] = agent_type
    if status:
        query["status"] = status

    cursor = db.agent_executions.find(query).sort("created_at", -1).skip(skip).limit(limit)
    docs = await cursor.to_list(limit)
    return [_serialize_execution(d) for d in docs]


@router.get("/executions/{execution_id}", response_model=AgentExecutionOut)
async def get_execution(
    execution_id: str,
    current_user: Annotated[dict, Depends(get_current_user)],
):
    db = get_database()
    if not ObjectId.is_valid(execution_id):
        raise HTTPException(status_code=400, detail="Invalid execution ID.")
    doc = await db.agent_executions.find_one({"_id": ObjectId(execution_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Execution not found.")
    return _serialize_execution(doc)


@router.get("/executions/{execution_id}/logs")
async def get_execution_logs(
    execution_id: str,
    current_user: Annotated[dict, Depends(get_current_user)],
    limit: int = Query(100, ge=1, le=500),
):
    """Get execution logs for a specific agent run."""
    db = get_database()
    cursor = db.execution_logs.find(
        {"execution_id": execution_id}
    ).sort("created_at", 1).limit(limit)
    logs = await cursor.to_list(limit)
    return [
        {
            "id": str(log["_id"]),
            "stage": log.get("stage"),
            "message": log.get("message"),
            "execution_mode": log.get("execution_mode", "native_hermes"),
            "progress_percent": log.get("progress_percent", 0),
            "created_at": log["created_at"].isoformat(),
        }
        for log in logs
    ]


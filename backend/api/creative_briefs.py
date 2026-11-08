"""
CrowdWisdom AI Studio — Creative Briefs API Routes
Human Approval Checkpoint 1: Review and sign off on Creative Intelligence Briefs before script writing.
"""
from datetime import datetime, timezone
from typing import Annotated, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from bson import ObjectId

from database.connection import get_database
from api.auth import get_current_user
from services.creative_intelligence_engine import creative_intelligence_engine

router = APIRouter(prefix="/creative-briefs", tags=["Creative Briefs"])


@router.post("/generate", status_code=201)
async def generate_creative_brief(
    campaign_id: str = Body(..., embed=True),
    custom_instructions: Optional[str] = Body(None, embed=True),
    current_user: Annotated[dict, Depends(get_current_user)] = None,
):
    """Generates a creative brief using the Creative Intelligence Engine."""
    try:
        brief = await creative_intelligence_engine.generate_creative_brief(
            campaign_id=campaign_id,
            custom_instructions=custom_instructions
        )
        return brief
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=List[dict])
async def list_creative_briefs(
    current_user: Annotated[dict, Depends(get_current_user)],
    campaign_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = Query(20, ge=1, le=100),
):
    db = get_database()
    query = {}
    if campaign_id:
        query["campaign_id"] = campaign_id
    if status:
        query["status"] = status

    docs = await db.creative_briefs.find(query).sort("created_at", -1).limit(limit).to_list(limit)
    for d in docs:
        d["id"] = str(d["_id"])
        del d["_id"]
    return docs


@router.get("/campaign/{campaign_id}")
async def get_brief_by_campaign(
    campaign_id: str,
    current_user: Annotated[dict, Depends(get_current_user)],
):
    db = get_database()
    doc = await db.creative_briefs.find_one({"campaign_id": campaign_id})
    if not doc:
        return None
    doc["id"] = str(doc["_id"])
    del doc["_id"]
    return doc


@router.get("/{brief_id}")
async def get_creative_brief(
    brief_id: str,
    current_user: Annotated[dict, Depends(get_current_user)],
):
    db = get_database()
    if not ObjectId.is_valid(brief_id):
        raise HTTPException(status_code=400, detail="Invalid brief ID.")

    doc = await db.creative_briefs.find_one({"_id": ObjectId(brief_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Creative brief not found.")
    doc["id"] = str(doc["_id"])
    del doc["_id"]
    return doc


@router.post("/{brief_id}/approve")
async def approve_creative_brief(
    brief_id: str,
    current_user: Annotated[dict, Depends(get_current_user)],
):
    """Checkpoint 1: Human Approval for Creative Strategic Brief."""
    db = get_database()
    if not ObjectId.is_valid(brief_id):
        raise HTTPException(status_code=400, detail="Invalid brief ID.")

    updated = await creative_intelligence_engine.approve_brief(
        brief_id=brief_id,
        user_id=str(current_user["_id"])
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Creative brief not found.")

    updated["id"] = str(updated["_id"])
    del updated["_id"]
    return {"message": "Creative Brief approved successfully. Ready for Script Agent.", "brief": updated}


@router.post("/{brief_id}/reject")
async def reject_creative_brief(
    brief_id: str,
    reason: str = Body(..., embed=True),
    current_user: Annotated[dict, Depends(get_current_user)] = None,
):
    db = get_database()
    if not ObjectId.is_valid(brief_id):
        raise HTTPException(status_code=400, detail="Invalid brief ID.")

    now = datetime.now(timezone.utc)
    updated = await db.creative_briefs.find_one_and_update(
        {"_id": ObjectId(brief_id)},
        {"$set": {"status": "rejected", "rejection_reason": reason, "updated_at": now}},
        return_document=True
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Creative brief not found.")
    updated["id"] = str(updated["_id"])
    del updated["_id"]
    return {"message": "Creative Brief rejected.", "brief": updated}


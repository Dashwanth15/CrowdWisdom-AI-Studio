"""
CrowdWisdom AI Studio — Campaigns API Routes
"""
import asyncio
from datetime import datetime, timezone
from typing import Annotated, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from bson import ObjectId

from database.connection import get_database
from models.schemas import CampaignCreate, CampaignOut, CampaignUpdate, CampaignStatus
from api.auth import get_current_user
from services.market_intelligence import market_intelligence_engine

router = APIRouter(prefix="/campaigns", tags=["Campaigns"])


async def _enrich_campaign(db, doc: dict) -> CampaignOut:
    now = datetime.now(timezone.utc)
    cid = str(doc.get("_id", ""))

    # Dynamically compute actual related resource counts from database collections
    ads_count = await db.advertisements.count_documents({
        "$or": [{"campaign_id": cid}, {"associated_campaign_ids": cid}]
    })
    scripts_count = await db.scripts.count_documents({"campaign_id": cid})
    videos_count = await db.video_jobs.count_documents({"campaign_id": cid, "status": "completed"})

    # Compute genuine lifecycle status
    raw_status = doc.get("status", "draft")
    if raw_status in ("paused", "archived"):
        effective_status = raw_status
    elif videos_count > 0:
        effective_status = "completed"
    elif scripts_count > 0 or ads_count > 0:
        effective_status = "active"
    else:
        effective_status = "draft"

    # Persist updated status & counts to MongoDB if different
    if raw_status != effective_status and ObjectId.is_valid(cid):
        await db.campaigns.update_one(
            {"_id": ObjectId(cid)},
            {"$set": {
                "status": effective_status,
                "ads_researched": ads_count,
                "scripts_generated": scripts_count,
                "videos_generated": videos_count,
                "updated_at": now,
            }}
        )

    return CampaignOut(
        id=cid,
        name=doc.get("name") or "Untitled Campaign",
        description=doc.get("description"),
        target_country=doc.get("target_country") or doc.get("audience", {}).get("target_country") or "IN",
        objective=doc.get("objective", "brand_awareness"),
        status=effective_status,
        audience=doc.get("audience") or {},
        research_approaches=doc.get("research_approaches") or ["pain_point"],
        video_duration_seconds=doc.get("video_duration_seconds", 45),
        video_aspect_ratio=doc.get("video_aspect_ratio", "9:16"),
        creative_direction=doc.get("creative_direction"),
        additional_instructions=doc.get("additional_instructions"),
        owner_id=doc.get("owner_id", ""),
        created_at=doc.get("created_at") or now,
        updated_at=doc.get("updated_at") or now,
        ads_researched=ads_count,
        scripts_generated=scripts_count,
        videos_generated=videos_count,
    )


def _serialize_campaign(doc: dict) -> CampaignOut:
    now = datetime.now(timezone.utc)
    return CampaignOut(
        id=str(doc.get("_id", "")),
        name=doc.get("name") or "Untitled Campaign",
        description=doc.get("description"),
        target_country=doc.get("target_country") or doc.get("audience", {}).get("target_country") or "IN",
        objective=doc.get("objective", "brand_awareness"),
        status=doc.get("status", "draft"),
        audience=doc.get("audience") or {},
        research_approaches=doc.get("research_approaches") or ["pain_point"],
        video_duration_seconds=doc.get("video_duration_seconds", 45),
        video_aspect_ratio=doc.get("video_aspect_ratio", "9:16"),
        creative_direction=doc.get("creative_direction"),
        additional_instructions=doc.get("additional_instructions"),
        owner_id=doc.get("owner_id", ""),
        created_at=doc.get("created_at") or now,
        updated_at=doc.get("updated_at") or now,
        ads_researched=doc.get("ads_researched", 0),
        scripts_generated=doc.get("scripts_generated", 0),
        videos_generated=doc.get("videos_generated", 0),
    )


@router.post("", response_model=CampaignOut, status_code=201)
async def create_campaign(
    data: CampaignCreate,
    current_user: Annotated[dict, Depends(get_current_user)],
):
    db = get_database()
    now = datetime.now(timezone.utc)
    user_id = str(current_user["_id"])

    # If 'BOTH' markets requested, generate coordinated country-specific campaign variants
    if data.target_country == "BOTH":
        variants = await market_intelligence_engine.create_dual_market_campaign_variants(
            base_campaign_data=data.model_dump(),
            owner_id=user_id,
        )
        # Return the primary created variant (India)
        first_doc = variants[0]
        first_doc["_id"] = first_doc.get("id")
        return _serialize_campaign(first_doc)

    doc = {
        **data.model_dump(),
        "target_country": data.target_country or "IN",
        "owner_id": user_id,
        "status": "draft",
        "ads_researched": 0,
        "scripts_generated": 0,
        "videos_generated": 0,
        "created_at": now,
        "updated_at": now,
    }
    result = await db.campaigns.insert_one(doc)
    doc["_id"] = result.inserted_id
    return _serialize_campaign(doc)


@router.get("", response_model=List[CampaignOut])
async def list_campaigns(
    current_user: Annotated[dict, Depends(get_current_user)],
    status: Optional[CampaignStatus] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    db = get_database()
    query: dict = {}
    user_role = current_user.get("role", "viewer")
    user_id = str(current_user["_id"])
    if user_role not in ("admin", "marketing_manager", "creative_editor"):
        query["owner_id"] = user_id
    cursor = db.campaigns.find(query).sort("created_at", -1).skip(skip).limit(limit)
    campaigns = await cursor.to_list(limit)

    # Concurrently enrich campaigns with live counts & dynamic lifecycle status
    enriched = await asyncio.gather(*[_enrich_campaign(db, c) for c in campaigns])
    if status:
        return [c for c in enriched if c.status == status.value]
    return list(enriched)


@router.get("/{campaign_id}", response_model=CampaignOut)
async def get_campaign(
    campaign_id: str,
    current_user: Annotated[dict, Depends(get_current_user)],
):
    db = get_database()
    if not ObjectId.is_valid(campaign_id):
        raise HTTPException(status_code=400, detail="Invalid campaign ID.")
    
    user_role = current_user.get("role", "viewer")
    user_id = str(current_user["_id"])
    query: dict = {"_id": ObjectId(campaign_id)}
    if user_role not in ("admin", "marketing_manager", "creative_editor"):
        query["owner_id"] = user_id

    doc = await db.campaigns.find_one(query)
    if not doc:
        raise HTTPException(status_code=404, detail="Campaign not found.")
    return await _enrich_campaign(db, doc)


@router.patch("/{campaign_id}", response_model=CampaignOut)
async def update_campaign(
    campaign_id: str,
    data: CampaignUpdate,
    current_user: Annotated[dict, Depends(get_current_user)],
):
    db = get_database()
    if not ObjectId.is_valid(campaign_id):
        raise HTTPException(status_code=400, detail="Invalid campaign ID.")

    update_data = {k: v for k, v in data.model_dump(exclude_none=True).items()}
    if not update_data:
        raise HTTPException(status_code=400, detail="No update data provided.")

    update_data["updated_at"] = datetime.now(timezone.utc)
    user_role = current_user.get("role", "viewer")
    user_id = str(current_user["_id"])
    query: dict = {"_id": ObjectId(campaign_id)}
    if user_role not in ("admin", "marketing_manager", "creative_editor"):
        query["owner_id"] = user_id

    result = await db.campaigns.update_one(query, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Campaign not found.")

    doc = await db.campaigns.find_one({"_id": ObjectId(campaign_id)})
    return await _enrich_campaign(db, doc)


@router.delete("/{campaign_id}", status_code=204)
async def delete_campaign(
    campaign_id: str,
    current_user: Annotated[dict, Depends(get_current_user)],
):
    db = get_database()
    if not ObjectId.is_valid(campaign_id):
        raise HTTPException(status_code=400, detail="Invalid campaign ID.")

    result = await db.campaigns.delete_one(
        {"_id": ObjectId(campaign_id), "owner_id": str(current_user["_id"])}
    )
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Campaign not found.")


@router.post("/{campaign_id}/duplicate", response_model=CampaignOut, status_code=201)
async def duplicate_campaign(
    campaign_id: str,
    current_user: Annotated[dict, Depends(get_current_user)],
):
    db = get_database()
    if not ObjectId.is_valid(campaign_id):
        raise HTTPException(status_code=400, detail="Invalid campaign ID.")

    original = await db.campaigns.find_one(
        {"_id": ObjectId(campaign_id), "owner_id": str(current_user["_id"])}
    )
    if not original:
        raise HTTPException(status_code=404, detail="Campaign not found.")

    now = datetime.now(timezone.utc)
    new_doc = {k: v for k, v in original.items() if k != "_id"}
    new_doc["name"] = f"{original['name']} (Copy)"
    new_doc["status"] = "draft"
    new_doc["ads_researched"] = 0
    new_doc["scripts_generated"] = 0
    new_doc["videos_generated"] = 0
    new_doc["created_at"] = now
    new_doc["updated_at"] = now

    result = await db.campaigns.insert_one(new_doc)
    new_doc["_id"] = result.inserted_id
    return _serialize_campaign(new_doc)


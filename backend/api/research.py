"""
CrowdWisdom AI Studio — Research & Insights API Routes
"""
from datetime import datetime, timezone, timedelta
from typing import Annotated, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from pydantic import BaseModel
from bson import ObjectId

from database.connection import get_database
from services.date_normalization import extract_and_normalize_publication_date
from models.schemas import (
    AdvertisementOut,
    AdEvaluationScore,
    ResearchJobOut,
    MarketingInsightOut,
)
from api.auth import get_current_user

router = APIRouter(prefix="/research", tags=["Research & Insights"])


class AssociateAdsRequest(BaseModel):
    campaign_id: str
    ad_ids: List[str]


@router.post("/associate-campaign")
async def associate_ads_to_campaign(
    payload: AssociateAdsRequest,
    current_user: Annotated[dict, Depends(get_current_user)],
):
    """
    Associate selected advertisements (and their derived marketing insights)
    with a specific campaign.
    """
    db = get_database()
    campaign_id = payload.campaign_id
    if not ObjectId.is_valid(campaign_id):
        raise HTTPException(status_code=400, detail="Invalid campaign ID.")

    camp = await db.campaigns.find_one({"_id": ObjectId(campaign_id)})
    if not camp:
        raise HTTPException(status_code=404, detail="Campaign not found.")

    matched_ads = []
    for aid in payload.ad_ids:
        q = {"$or": [{"ad_id": aid}]}
        if ObjectId.is_valid(aid):
            q["$or"].append({"_id": ObjectId(aid)})
        ad = await db.advertisements.find_one(q)
        if ad:
            matched_ads.append(ad)

    if not matched_ads:
        raise HTTPException(status_code=404, detail="No matching advertisements found.")

    ad_db_ids = [a["_id"] for a in matched_ads]
    ad_str_ids = [str(a.get("ad_id") or a["_id"]) for a in matched_ads]

    # 1. Associate ads with this campaign
    await db.advertisements.update_many(
        {"_id": {"$in": ad_db_ids}},
        {"$addToSet": {"associated_campaign_ids": campaign_id}}
    )
    # Also populate primary campaign_id if unset
    await db.advertisements.update_many(
        {"_id": {"$in": ad_db_ids}, "campaign_id": {"$in": [None, "", "null"]}},
        {"$set": {"campaign_id": campaign_id}}
    )

    # 2. Also associate marketing insights that cite these ads
    await db.marketing_insights.update_many(
        {"source_ad_ids": {"$in": ad_str_ids}},
        {"$addToSet": {"associated_campaign_ids": campaign_id}}
    )

    # 3. Recalculate campaign's associated ads count and update campaign state
    total_associated_ads = await db.advertisements.count_documents({
        "$or": [{"campaign_id": campaign_id}, {"associated_campaign_ids": campaign_id}]
    })

    new_status = camp.get("status")
    if new_status == "draft":
        new_status = "active"

    await db.campaigns.update_one(
        {"_id": ObjectId(campaign_id)},
        {"$set": {
            "ads_researched": total_associated_ads,
            "status": new_status,
            "updated_at": datetime.now(timezone.utc),
        }}
    )

    return {
        "success": True,
        "campaign_id": campaign_id,
        "associated_count": len(matched_ads),
        "total_campaign_ads": total_associated_ads,
    }


@router.get("/jobs", response_model=List[ResearchJobOut])
async def list_research_jobs(
    current_user: Annotated[dict, Depends(get_current_user)],
    campaign_id: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    db = get_database()
    query = {}
    if campaign_id:
        query["$or"] = [
            {"campaign_id": campaign_id},
            {"associated_campaign_ids": campaign_id}
        ]

    cursor = db.research_jobs.find(query).sort("created_at", -1).skip(skip).limit(limit)
    docs = await cursor.to_list(limit)
    return [_serialize_research_job(d) for d in docs]


@router.get("/jobs/{job_id}", response_model=ResearchJobOut)
async def get_research_job(
    job_id: str,
    current_user: Annotated[dict, Depends(get_current_user)],
):
    db = get_database()
    if not ObjectId.is_valid(job_id):
        raise HTTPException(status_code=400, detail="Invalid job ID.")
    doc = await db.research_jobs.find_one({"_id": ObjectId(job_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Research job not found.")
    return _serialize_research_job(doc)


@router.get("/advertisements", response_model=List[AdvertisementOut])
async def list_advertisements(
    current_user: Annotated[dict, Depends(get_current_user)],
    campaign_id: Optional[str] = None,
    advertiser: Optional[str] = None,
    min_score: Optional[float] = None,
    verification_status: Optional[str] = Query(None, description="Filter by date_verification_status ('verified' or 'unverified')"),
    date_range_days: Optional[int] = Query(None, description="Filter published within last N days"),
    sort_by: Optional[str] = Query("newest", description="Sorting option: 'newest', 'oldest', 'score'"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    db = get_database()
    query = {}
    if campaign_id:
        query["$or"] = [
            {"campaign_id": campaign_id},
            {"associated_campaign_ids": campaign_id}
        ]
    if advertiser:
        query["advertiser"] = {"$regex": advertiser, "$options": "i"}
    if min_score is not None:
        query["evaluation_score.overall"] = {"$gte": min_score}
    if verification_status:
        query["date_verification_status"] = verification_status
    if date_range_days:
        cutoff = datetime.now(timezone.utc) - timedelta(days=date_range_days)
        query["published_at"] = {"$gte": cutoff}

    # Dynamic sorting
    sort_spec = [("created_at", -1)]
    if sort_by == "newest":
        sort_spec = [("published_at", -1), ("created_at", -1)]
    elif sort_by == "oldest":
        sort_spec = [("published_at", 1), ("created_at", 1)]
    elif sort_by == "score":
        sort_spec = [("evaluation_score.overall", -1), ("created_at", -1)]

    cursor = db.advertisements.find(query).sort(sort_spec).skip(skip).limit(limit)
    docs = await cursor.to_list(limit)
    return [_serialize_ad(d) for d in docs]


@router.get("/advertisements/export")
async def export_advertisements_json(
    current_user: Annotated[dict, Depends(get_current_user)],
    campaign_id: Optional[str] = None,
):
    """Export collected Meta advertisements as human-readable formatted JSON."""
    import json
    db = get_database()
    query = {}
    if campaign_id:
        query["$or"] = [
            {"campaign_id": campaign_id},
            {"associated_campaign_ids": campaign_id}
        ]

    cursor = db.advertisements.find(query).sort("created_at", -1)
    docs = await cursor.to_list(500)
    serialized = [_serialize_ad(d).model_dump(mode="json") for d in docs]

    verified_count = sum(1 for a in serialized if a.get("date_verification_status") == "verified")
    export_payload = {
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "total_advertisements": len(serialized),
        "verified_publication_dates_count": verified_count,
        "unverified_publication_dates_count": len(serialized) - verified_count,
        "campaign_id": campaign_id,
        "advertisements": serialized,
    }
    json_bytes = json.dumps(export_payload, indent=2).encode("utf-8")
    return Response(
        content=json_bytes,
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=meta_ads_research.json"}
    )


@router.get("/advertisements/{ad_id}")
async def get_advertisement(
    ad_id: str,
    current_user: Annotated[dict, Depends(get_current_user)],
):
    db = get_database()
    if not ObjectId.is_valid(ad_id):
        raise HTTPException(status_code=400, detail="Invalid ad ID.")
    doc = await db.advertisements.find_one({"_id": ObjectId(ad_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Advertisement not found.")
    return _serialize_ad(doc)


@router.get("/insights", response_model=List[MarketingInsightOut])
async def list_insights(
    current_user: Annotated[dict, Depends(get_current_user)],
    campaign_id: Optional[str] = None,
    category: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    db = get_database()
    query = {}
    if campaign_id:
        query["$or"] = [
            {"campaign_id": campaign_id},
            {"associated_campaign_ids": campaign_id}
        ]
    if category:
        query["category"] = category

    cursor = db.marketing_insights.find(query).sort("confidence", -1).skip(skip).limit(limit)
    docs = await cursor.to_list(limit)
    return [_serialize_insight(d) for d in docs]


def _serialize_research_job(doc: dict) -> ResearchJobOut:
    return ResearchJobOut(
        id=str(doc["_id"]),
        campaign_id=doc.get("campaign_id", ""),
        status=doc.get("status", "pending"),
        keywords=doc.get("keywords", []),
        competitor_names=doc.get("competitor_names"),
        date_range_days=doc.get("date_range_days", 30),
        ads_found=doc.get("ads_found", 0),
        ads_evaluated=doc.get("ads_evaluated", 0),
        insights_extracted=doc.get("insights_extracted", 0),
        error_message=doc.get("error_message"),
        started_at=doc.get("started_at"),
        completed_at=doc.get("completed_at"),
        created_at=doc["created_at"],
    )


def _serialize_ad(doc: dict) -> AdvertisementOut:
    raw_score = doc.get("evaluation_score")
    score = None
    if isinstance(raw_score, dict):
        score = AdEvaluationScore(
            overall=float(raw_score.get("overall", 8.0)),
            hook_strength=float(raw_score.get("hook_strength", 8.0)),
            emotional_appeal=float(raw_score.get("emotional_appeal", 7.5)),
            clarity=float(raw_score.get("clarity", 8.0)),
            cta_effectiveness=float(raw_score.get("cta_effectiveness", 7.5)),
            compliance_score=float(raw_score.get("compliance_score", 9.0)),
            emotional_resonance=float(raw_score.get("emotional_resonance", 8.0)),
            offer_clarity=float(raw_score.get("offer_clarity", 8.0)),
            evidence_basis=raw_score.get("evidence_basis") or "ai_assessment",
            rationale=raw_score.get("rationale") or "Evaluated by AI advertising analyst."
        )

    created_at = doc.get("created_at") or datetime.now(timezone.utc)

    # Date normalization & verification resolution
    published_at = doc.get("published_at")
    published_at_raw = doc.get("published_at_raw")
    published_date_source = doc.get("published_date_source")
    scraped_at = doc.get("scraped_at")
    date_verification_status = doc.get("date_verification_status")
    meta_ads_url = doc.get("meta_ads_url")
    age_days = doc.get("age_days")

    if date_verification_status is None:
        # Fallback to normalize on the fly for legacy documents
        norm = extract_and_normalize_publication_date(doc, scraped_at=created_at)
        published_at = norm["published_at"]
        published_at_raw = norm["published_at_raw"]
        published_date_source = norm["published_date_source"]
        scraped_at = norm["scraped_at"]
        date_verification_status = norm["date_verification_status"]
        age_days = norm["age_days"]
        meta_ads_url = norm["meta_ads_url"]

    if published_at and age_days is None and isinstance(published_at, datetime):
        age_days = max(0, (datetime.now(timezone.utc) - published_at).days)

    ad_id = str(doc.get("ad_id") or doc.get("id") or "")
    if not meta_ads_url and ad_id and not ad_id.startswith("ad_meta_benchmark"):
        meta_ads_url = f"https://www.facebook.com/ads/library/?id={ad_id}"

    return AdvertisementOut(
        id=str(doc["_id"]),
        campaign_id=doc.get("campaign_id", ""),
        research_job_id=doc.get("research_job_id", ""),
        ad_id=doc.get("ad_id", ""),
        source=doc.get("source", "meta_ads_library"),
        advertiser=doc.get("advertiser", "Unknown"),
        ad_text=doc.get("ad_text"),
        creative_reference=doc.get("creative_reference"),
        first_seen=str(doc.get("first_seen")) if doc.get("first_seen") else None,
        last_seen=str(doc.get("last_seen")) if doc.get("last_seen") else None,
        published_at=published_at,
        published_at_raw=published_at_raw,
        published_date_source=published_date_source,
        scraped_at=scraped_at,
        date_verification_status=date_verification_status or "unverified",
        age_days=age_days,
        meta_ads_url=meta_ads_url,
        landing_page=doc.get("landing_page"),
        target_audience_hypothesis=doc.get("target_audience_hypothesis"),
        marketing_angle=doc.get("marketing_angle"),
        pain_point=doc.get("pain_point"),
        hook=doc.get("hook"),
        evaluation_score=score,
        raw_data=None,  # Never return full raw data to frontend
        created_at=created_at,
    )


def _serialize_insight(doc: dict) -> MarketingInsightOut:
    created_at = doc.get("created_at") or datetime.now(timezone.utc)
    return MarketingInsightOut(
        id=str(doc["_id"]),
        campaign_id=doc.get("campaign_id", ""),
        research_job_id=doc.get("research_job_id", ""),
        category=doc.get("category", "pattern"),
        title=doc.get("title", "Untitled"),
        description=doc.get("description", ""),
        evidence=doc.get("evidence", []),
        source_ad_ids=doc.get("source_ad_ids", []),
        confidence=float(doc.get("confidence", 0.5)),
        created_at=created_at,
    )


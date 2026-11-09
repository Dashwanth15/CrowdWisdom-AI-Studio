"""
CrowdWisdom AI Studio — Market Intelligence API Routes
Provides endpoints for country profiles, audience segmentation, real-time research,
creative recommendations, and regulatory compliance validation for India and the Philippines.
"""
import logging
from typing import Annotated, Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from bson import ObjectId

from database.connection import get_database
from api.auth import get_current_user
from services.market_intelligence import (
    market_intelligence_engine,
    compliance_validator,
)
from services.market_intelligence.provider_health_service import provider_health_service
from services.market_intelligence.market_research_service import market_research_service
from models.schemas import (
    CountryOverviewOut,
    AudienceSegmentOut,
    MarketResearchRequest,
    ComplianceValidationRequest,
    ComplianceValidationOut,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/market-intelligence", tags=["Market Intelligence"])


@router.get("/provider-health")
async def get_provider_health(
    current_user: Annotated[dict, Depends(get_current_user)],
) -> Dict[str, Any]:
    """Diagnoses and returns real-time operational status, latency, and capabilities across research providers."""
    return await provider_health_service.check_all_providers()


@router.get("/comparison")
async def get_dual_market_comparison(
    current_user: Annotated[dict, Depends(get_current_user)],
) -> Dict[str, Any]:
    """Returns structured 8-category comparative marketing intelligence between India and the Philippines."""
    import os
    import json
    comp_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "scripts", "market_comparison_output.json")
    if os.path.exists(comp_file):
        try:
            with open(comp_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Error reading market_comparison_output.json: {e}")
    # Fallback to dual market generator
    return await market_intelligence_engine.create_dual_market_campaign_variants("Retail Trading Clarity", "IN")


@router.get("/competitor-ads")
async def list_competitor_ads(
    current_user: Annotated[dict, Depends(get_current_user)],
    country: Optional[str] = Query(None, description="Target country code: 'IN' or 'PH'"),
    ad_classification: Optional[str] = Query(None, description="LIVE_META_AD | HISTORICAL_META_AD | VERIFIED_DOMAIN_BENCHMARK"),
    advertiser: Optional[str] = Query(None, description="Filter by advertiser name"),
    limit: int = Query(20, ge=1, le=100),
) -> List[Dict[str, Any]]:
    """Returns stored competitor advertising intelligence filtered by country, classification, and advertiser."""
    db = get_database()
    query: Dict[str, Any] = {}
    if country:
        query["country"] = country.upper().strip()
    if ad_classification:
        query["ad_classification"] = ad_classification
    if advertiser:
        query["advertiser"] = {"$regex": advertiser, "$options": "i"}

    ads = await db.advertisements.find(query).sort([("created_at", -1)]).limit(limit).to_list(limit)
    result = []
    for ad in ads:
        item = dict(ad)
        if "_id" in item:
            item["id"] = str(item["_id"])
            del item["_id"]
        result.append(item)
    return result


@router.get("/countries")
async def list_supported_countries(
    current_user: Annotated[dict, Depends(get_current_user)],
) -> List[Dict[str, Any]]:
    """Lists all supported target countries with regulatory and market metadata."""
    return market_intelligence_engine.get_supported_countries()


@router.get("/{country}/overview", response_model=CountryOverviewOut)
async def get_country_overview(
    country: str,
    current_user: Annotated[dict, Depends(get_current_user)],
):
    """Retrieves high-level market profile, ecosystem, and research freshness for a country."""
    norm_country = country.upper().strip()
    if norm_country not in ("IN", "PH"):
        raise HTTPException(status_code=400, detail=f"Unsupported country code '{country}'. Supported: 'IN', 'PH'.")
    return market_intelligence_engine.get_country_overview(norm_country)


@router.get("/{country}/audiences", response_model=List[AudienceSegmentOut])
async def get_audience_segments(
    country: str,
    current_user: Annotated[dict, Depends(get_current_user)],
    experience_level: Optional[str] = Query(None, description="Filter by experience: beginner, intermediate, advanced, all"),
    interest: Optional[str] = Query(None, description="Filter by trading or investment focus"),
    channel: Optional[str] = Query(None, description="Filter by preferred marketing channel"),
):
    """Retrieves country-specific audience personas with tailored pain points and preferences."""
    norm_country = country.upper().strip()
    if norm_country not in ("IN", "PH"):
        raise HTTPException(status_code=400, detail=f"Unsupported country code '{country}'. Supported: 'IN', 'PH'.")
    return market_intelligence_engine.get_audience_segments(
        country_code=norm_country,
        experience_level=experience_level,
        interest=interest,
        channel=channel,
    )


@router.get("/{country}/trends")
async def get_market_trends(
    country: str,
    current_user: Annotated[dict, Depends(get_current_user)],
    topic: str = Query("retail trading sentiment", description="Market research topic"),
    force_refresh: bool = Query(False, description="Force live API refresh from Tavily/Exa"),
):
    """Retrieves real-time research evidence, verified facts, and publisher attribution."""
    norm_country = country.upper().strip()
    if norm_country not in ("IN", "PH"):
        raise HTTPException(status_code=400, detail=f"Unsupported country code '{country}'. Supported: 'IN', 'PH'.")
    return await market_intelligence_engine.get_market_trends_and_evidence(
        country_code=norm_country,
        topic=topic,
        force_refresh=force_refresh,
    )


@router.post("/research")
async def execute_market_research(
    body: MarketResearchRequest,
    current_user: Annotated[dict, Depends(get_current_user)],
):
    """Triggers live research across Tavily, Exa, and domain sources for country-specific intelligence."""
    norm_country = body.country_code.upper().strip()
    if norm_country not in ("IN", "PH"):
        raise HTTPException(status_code=400, detail=f"Unsupported country code '{body.country_code}'. Supported: 'IN', 'PH'.")
    return await market_intelligence_engine.get_market_trends_and_evidence(
        country_code=norm_country,
        topic=body.topic,
        force_refresh=body.force_refresh,
    )


@router.get("/{country}/recommendations")
async def get_campaign_recommendations(
    country: str,
    current_user: Annotated[dict, Depends(get_current_user)],
):
    """Returns creative narrative angles, local terminology, platform strategies, and disclaimers."""
    norm_country = country.upper().strip()
    if norm_country not in ("IN", "PH"):
        raise HTTPException(status_code=400, detail=f"Unsupported country code '{country}'. Supported: 'IN', 'PH'.")
    return market_intelligence_engine.get_campaign_recommendations(norm_country)


@router.get("/campaign/{campaign_id}")
async def get_campaign_market_context(
    campaign_id: str,
    current_user: Annotated[dict, Depends(get_current_user)],
    country_override: Optional[str] = Query(None, description="Optional override country: 'IN' or 'PH'"),
):
    """Builds and returns the comprehensive MarketContext for a specific campaign."""
    db = get_database()
    if not ObjectId.is_valid(campaign_id):
        raise HTTPException(status_code=400, detail="Invalid campaign ID format.")

    camp = await db.campaigns.find_one({"_id": ObjectId(campaign_id)})
    if not camp:
        raise HTTPException(status_code=404, detail="Campaign not found.")

    try:
        return await market_intelligence_engine.build_campaign_market_context(
            campaign_id=campaign_id,
            country_override=country_override,
        )
    except Exception as e:
        logger.error(f"[MarketIntelligenceAPI] Error building context for campaign {campaign_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to build market context: {str(e)}")


@router.post("/validate-compliance", response_model=ComplianceValidationOut)
async def validate_content_compliance(
    body: ComplianceValidationRequest,
    current_user: Annotated[dict, Depends(get_current_user)],
):
    """
    Validates marketing copy, scripts, and creative briefs against SEBI (India)
    or SEC Philippines financial advertising regulations.
    """
    norm_country = body.country_code.upper().strip()
    if norm_country not in ("IN", "PH"):
        norm_country = "IN"

    return compliance_validator.validate_content(
        country_code=norm_country,
        text_content=body.text_content,
        content_type=body.content_type,
    )


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
from models.schemas import (
    CountryOverviewOut,
    AudienceSegmentOut,
    MarketResearchRequest,
    ComplianceValidationRequest,
    ComplianceValidationOut,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/market-intelligence", tags=["Market Intelligence"])


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


"""
CrowdWisdom AI Studio — Market Intelligence Engine
Master service coordinating evidence-based market profiles, real-time research,
country-aware audience segmentation, and compliance validation for India and the Philippines.
"""
import copy
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from bson import ObjectId

from database.connection import get_database
from services.market_intelligence.india_market_profile import INDIA_MARKET_PROFILE, get_india_market_profile
from services.market_intelligence.philippines_market_profile import PHILIPPINES_MARKET_PROFILE, get_philippines_market_profile
from services.market_intelligence.audience_segmentation import audience_segmentation_engine
from services.market_intelligence.market_research_service import market_research_service
from services.market_intelligence.market_validation import compliance_validator
from services.market_intelligence.market_context_builder import market_context_builder

logger = logging.getLogger(__name__)


class MarketIntelligenceEngine:
    """
    Unified entry point for country-specific market intelligence operations.
    Seamlessly integrates with Campaign Management, Orchestrator, and AI Agents.
    """

    def __init__(self):
        self._profiles = {
            "IN": INDIA_MARKET_PROFILE,
            "PH": PHILIPPINES_MARKET_PROFILE,
        }

    def get_supported_countries(self) -> List[Dict[str, Any]]:
        """Returns metadata for all supported target countries."""
        return [
            {
                "country_code": "IN",
                "country_name": "India",
                "flag_emoji": "🇮🇳",
                "currency": "INR (₹)",
                "primary_exchange": "National Stock Exchange (NSE) / BSE",
                "benchmark_index": "Nifty 50 & Bank Nifty",
                "regulator": "Securities and Exchange Board of India (SEBI)",
                "dominant_trading": "Index Options (F&O) & Equities",
            },
            {
                "country_code": "PH",
                "country_name": "Philippines",
                "flag_emoji": "🇵🇭",
                "currency": "PHP (₱)",
                "primary_exchange": "Philippine Stock Exchange (PSE)",
                "benchmark_index": "PSEi (Composite Index)",
                "regulator": "Securities and Exchange Commission (SEC Philippines)",
                "dominant_trading": "Equities, REITs, Mobile Wallet Investing & OFW Allocations",
            },
            {
                "country_code": "BOTH",
                "country_name": "Both Markets (India & Philippines)",
                "flag_emoji": "🌐",
                "description": "Generates coordinated, country-specific campaign variants for both India and the Philippines.",
            }
        ]

    def get_country_overview(self, country_code: str) -> Dict[str, Any]:
        """Returns high-level market profile, ecosystem, and research freshness."""
        code = country_code.upper().strip() if country_code else "IN"
        profile = self._profiles.get(code, INDIA_MARKET_PROFILE)

        return {
            "country_code": profile["country_code"],
            "country_name": profile["country_name"],
            "currency": profile["currency"],
            "timezone": profile["timezone"],
            "market_hours": profile["market_hours"],
            "market_ecosystem": profile["market_ecosystem"],
            "regulator": profile["regulatory_safeguards"]["regulator"],
            "key_segments_count": len(profile.get("audience_segments", [])),
            "dominant_languages": profile.get("regional_intelligence", {}).get("language_dynamics", {}),
            "research_freshness": "Current (Real-time live feeds & regulatory benchmarks)",
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

    def get_audience_segments(
        self,
        country_code: str,
        experience_level: Optional[str] = None,
        interest: Optional[str] = None,
        channel: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Retrieves and filters audience segments for a given country."""
        return audience_segmentation_engine.get_segments_for_country(
            country_code=country_code,
            experience_level=experience_level,
            interest=interest,
            channel=channel,
        )

    async def get_market_trends_and_evidence(
        self,
        country_code: str,
        topic: str = "retail trading sentiment",
        force_refresh: bool = False,
    ) -> Dict[str, Any]:
        """Returns verified empirical research evidence and current market trends."""
        code = country_code.upper().strip() if country_code else "IN"
        evidence = await market_research_service.get_market_research_evidence(
            country_code=code,
            topic=topic,
            force_refresh=force_refresh,
            limit=15
        )

        profile = self._profiles.get(code, INDIA_MARKET_PROFILE)

        return {
            "country_code": code,
            "country_name": profile["country_name"],
            "topic": topic,
            "evidence_count": len(evidence),
            "evidence_items": evidence,
            "ecosystem_summary": profile["market_ecosystem"]["market_structure"],
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
        }

    def get_campaign_recommendations(self, country_code: str) -> Dict[str, Any]:
        """Returns creative hooks, narrative angles, and recommended channel strategies."""
        code = country_code.upper().strip() if country_code else "IN"
        profile = self._profiles.get(code, INDIA_MARKET_PROFILE)
        mkt = profile.get("marketing_intelligence", {})

        return {
            "country_code": code,
            "country_name": profile["country_name"],
            "recommended_angles": mkt.get("creative_angles", []),
            "local_terminology": mkt.get("local_terminology", []),
            "platform_strategy": mkt.get("platforms", {}),
            "voiceover_recommendation": mkt.get("voiceover_specifications", {}),
            "mandatory_disclaimers": profile.get("regulatory_safeguards", {}).get("mandatory_disclaimers", []),
        }

    async def build_campaign_market_context(
        self,
        campaign_id: str,
        country_override: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Builds a comprehensive MarketContext for a specific campaign by loading
        its audience settings from MongoDB and executing contextual synthesis.
        """
        db = get_database()
        campaign = await db.campaigns.find_one({"_id": ObjectId(campaign_id)})
        if not campaign:
            raise ValueError(f"Campaign {campaign_id} not found.")

        # Determine target country
        country = country_override or campaign.get("target_country") or campaign.get("audience", {}).get("target_country") or "IN"
        if country == "BOTH":
            country = "IN"  # Fallback to India for single context render

        audience_cfg = campaign.get("audience", {})
        context = await market_context_builder.build_context(
            country_code=country,
            audience_config=audience_cfg,
            include_live_research=True,
            research_limit=6
        )

        # Cache or persist to campaign_market_context collection for auditability
        context_doc = {
            "campaign_id": campaign_id,
            "country_code": country,
            "context": context,
            "built_at": datetime.now(timezone.utc),
        }
        await db.campaign_market_context.update_one(
            {"campaign_id": campaign_id},
            {"$set": context_doc},
            upsert=True
        )

        return context

    def validate_content_compliance(
        self,
        country_code: str,
        text_content: str,
        content_type: str = "script"
    ) -> Dict[str, Any]:
        """Validates copy or script against country-specific regulatory safeguards."""
        return compliance_validator.validate_content(
            country_code=country_code,
            text_content=text_content,
            content_type=content_type
        )

    def generate_dual_market_variant_dicts(
        self,
        base_campaign_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Pure data transformation helper: generates localized dictionary specs
        for both India and the Philippines variants.
        """
        base_name = base_campaign_data.get("name", "CrowdWisdom Alpha Launch")
        variants_config = [
            {
                "country": "IN",
                "name_suffix": "— India 🇮🇳",
                "default_segment": "in_options_derivative_trader",
                "creative_hook": "Nifty and Bank Nifty pre-market consensus",
            },
            {
                "country": "PH",
                "name_suffix": "— Philippines 🇵🇭",
                "default_segment": "ph_active_equity_trader",
                "creative_hook": "PSEi and global US equity crowd conviction",
            },
        ]
        specs = []
        for variant in variants_config:
            camp_copy = copy.deepcopy(base_campaign_data)
            camp_copy["name"] = f"{base_name} {variant['name_suffix']}"
            camp_copy["target_country"] = variant["country"]
            if "audience" not in camp_copy or not isinstance(camp_copy["audience"], dict):
                camp_copy["audience"] = {}
            camp_copy["audience"]["target_country"] = variant["country"]
            camp_copy["audience"]["segments"] = [variant["default_segment"]]
            existing_cd = camp_copy.get("creative_direction") or ""
            camp_copy["creative_direction"] = f"{existing_cd} [Target Market: {variant['country']} - {variant['creative_hook']}]".strip()
            specs.append(camp_copy)
        return specs

    async def create_dual_market_campaign_variants(
        self,
        base_campaign_data: Dict[str, Any],
        owner_id: str
    ) -> List[Dict[str, Any]]:
        """
        When 'BOTH' is selected, creates two coordinated, country-specific campaign variants
        instead of a diluted generic campaign:
        1. [Campaign Name] — India 🇮🇳
        2. [Campaign Name] — Philippines 🇵🇭
        """
        db = get_database()
        specs = self.generate_dual_market_variant_dicts(base_campaign_data)
        created_campaigns = []
        now = datetime.now(timezone.utc)

        for camp_copy in specs:
            camp_copy["owner_id"] = owner_id
            camp_copy["status"] = "draft"
            camp_copy["created_at"] = now
            camp_copy["updated_at"] = now
            camp_copy["ads_researched"] = 0
            camp_copy["scripts_generated"] = 0
            camp_copy["videos_generated"] = 0

            result = await db.campaigns.insert_one(camp_copy)
            camp_copy["id"] = str(result.inserted_id)
            if "_id" in camp_copy:
                del camp_copy["_id"]
            created_campaigns.append(camp_copy)

        return created_campaigns


market_intelligence_engine = MarketIntelligenceEngine()

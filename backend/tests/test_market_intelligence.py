"""
CrowdWisdom AI Studio — Market Intelligence Automated Test Suite
Verifies India and Philippines market profiles, audience segmentation,
real-time research caching, compliance validation, and dual-market campaign creation.
"""
import pytest
import asyncio
import os
import sys

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from services.market_intelligence.india_market_profile import (
    INDIA_MARKET_PROFILE,
    get_india_market_profile,
)
from services.market_intelligence.philippines_market_profile import (
    PHILIPPINES_MARKET_PROFILE,
    get_philippines_market_profile,
)
from services.market_intelligence.audience_segmentation import (
    AudienceSegmentationEngine,
    audience_segmentation_engine,
)
from services.market_intelligence.market_validation import (
    MarketComplianceValidator,
    compliance_validator,
)
from services.market_intelligence.market_research_service import (
    MarketResearchService,
    market_research_service,
)
from services.market_intelligence.market_context_builder import (
    MarketContextBuilder,
    market_context_builder,
)
from services.market_intelligence.market_intelligence_engine import (
    MarketIntelligenceEngine,
    market_intelligence_engine,
)


class TestMarketProfiles:
    """Verifies empirical integrity of India and Philippines market profiles."""

    def test_india_market_profile_structure(self):
        profile = get_india_market_profile()
        assert profile["country_code"] == "IN"
        assert profile["country_name"] == "India"
        assert profile["currency"]["code"] == "INR"
        assert profile["currency"]["symbol"] == "₹"
        assert any("NSE" in ex for ex in profile["market_ecosystem"]["primary_exchanges"])
        assert any("BSE" in ex for ex in profile["market_ecosystem"]["primary_exchanges"])
        assert "Nifty 50" in profile["market_ecosystem"]["benchmark_indices"]
        assert "SEBI" in profile["regulatory_safeguards"]["regulator"]
        assert len(profile["audience_segments"]) >= 5
        assert len(profile["regulatory_safeguards"]["mandatory_disclaimers"]) >= 1

    def test_philippines_market_profile_structure(self):
        profile = get_philippines_market_profile()
        assert profile["country_code"] == "PH"
        assert profile["country_name"] == "Philippines"
        assert profile["currency"]["code"] == "PHP"
        assert profile["currency"]["symbol"] == "₱"
        assert any("PSE" in ex for ex in profile["market_ecosystem"]["primary_exchanges"])
        assert any("PSEi" in idx for idx in profile["market_ecosystem"]["benchmark_indices"])
        assert "SEC Philippines" in profile["regulatory_safeguards"]["regulator"]
        assert len(profile["audience_segments"]) >= 5
        assert len(profile["regulatory_safeguards"]["mandatory_disclaimers"]) >= 1


class TestAudienceSegmentation:
    """Tests country-aware audience segmentation and filtering."""

    def test_get_india_segments(self):
        segments = audience_segmentation_engine.get_segments_for_country("IN")
        assert len(segments) >= 5
        segment_ids = [s["segment_id"] for s in segments]
        assert "in_options_derivative_trader" in segment_ids
        assert "in_beginner_retail_investor" in segment_ids
        assert "in_disciplined_swing_trader" in segment_ids

    def test_get_philippines_segments(self):
        segments = audience_segmentation_engine.get_segments_for_country("PH")
        assert len(segments) >= 5
        segment_ids = [s["segment_id"] for s in segments]
        assert "ph_active_equity_trader" in segment_ids
        assert "ph_young_fintech_professional" in segment_ids
        assert "ph_ofw_wealth_builder" in segment_ids

    def test_segment_filtering_by_experience(self):
        advanced_in = audience_segmentation_engine.get_segments_for_country("IN", experience_level="advanced")
        assert all("advanced" in s["experience_level"].lower() for s in advanced_in)

        beginner_ph = audience_segmentation_engine.get_segments_for_country("PH", experience_level="beginner")
        assert all("beginner" in s["experience_level"].lower() for s in beginner_ph)


class TestComplianceValidator:
    """Verifies SEBI and SEC Philippines compliance rules and predatory claim detection."""

    def test_flags_predatory_claims_universally(self):
        predatory_text = "Join now for 100% guaranteed profit and double your money with zero risk!"
        res_in = compliance_validator.validate_content("IN", predatory_text)
        assert res_in["is_compliant"] is False
        assert len(res_in["violations"]) >= 1

        res_ph = compliance_validator.validate_content("PH", predatory_text)
        assert res_ph["is_compliant"] is False
        assert len(res_ph["violations"]) >= 1

    def test_validates_clean_script_with_disclaimer_india(self):
        clean_text = (
            "Over 80% of retail options traders lose money in pre-market volatility. "
            "CrowdWisdom's sentiment engine aggregates market conviction in sixty seconds. "
            "Investment in securities market are subject to market risks. "
            "CrowdWisdom is an analytical educational platform, not a SEBI-registered advisor."
        )
        res = compliance_validator.validate_content("IN", clean_text)
        assert res["compliance_score"] >= 9.0
        assert len(res["violations"]) == 0

    def test_validates_clean_script_philippines(self):
        clean_text = (
            "Most PSE traders struggle with inconsistent stock tips across social groups. "
            "CrowdPulse provides objective sentiment clarity for PSEi and REITs. "
            "CrowdWisdom is an educational and analytical research tool, not an SEC-registered investment adviser."
        )
        res = compliance_validator.validate_content("PH", clean_text)
        assert res["compliance_score"] >= 9.0
        assert len(res["violations"]) == 0


class TestMarketResearchService:
    """Verifies empirical research caching and ground-truth evidence retrieval."""

    @pytest.mark.asyncio
    async def test_get_india_research_evidence(self):
        evidence = await market_research_service.get_market_research_evidence("IN", "retail trading sentiment")
        assert len(evidence) > 0
        first = evidence[0]
        assert first["country"] == "IN"
        assert first["confidence_score"] > 0.8
        assert "source_url" in first
        assert "publisher" in first

    @pytest.mark.asyncio
    async def test_get_philippines_research_evidence(self):
        evidence = await market_research_service.get_market_research_evidence("PH", "retail equities behavior")
        assert len(evidence) > 0
        first = evidence[0]
        assert first["country"] == "PH"
        assert first["confidence_score"] > 0.8
        assert "source_url" in first
        assert "publisher" in first

    @pytest.mark.asyncio
    async def test_research_cache_hit(self):
        # First call populates cache
        ev1 = await market_research_service.get_market_research_evidence("IN", "cache_test_topic")
        # Second call should return cached result instantly
        ev2 = await market_research_service.get_market_research_evidence("IN", "cache_test_topic")
        assert len(ev1) == len(ev2)

    def test_calculate_source_quality_tier1_regulator(self):
        res = market_research_service.calculate_source_quality(
            url="https://www.sebi.gov.in/reports-and-statistics/research/study.html",
            raw_publication_date="2026-01-15",
            is_benchmark=True,
        )
        assert res["tier"] == 1
        assert res["tier_name"] == "Official Regulators & Central Exchanges"
        assert res["final_score"] >= 9.5
        assert res["date_verification_status"] == "verified"

    def test_calculate_source_quality_tier2_financial_press(self):
        res = market_research_service.calculate_source_quality(
            url="https://www.livemint.com/market/retail-investor-sentiment",
            raw_publication_date="2026-10-01",
        )
        assert res["tier"] == 2
        assert res["confidence_level"] == "high"
        assert res["final_score"] >= 8.5

    def test_calculate_source_quality_staleness_penalty(self):
        fresh = market_research_service.calculate_source_quality(
            url="https://www.livemint.com/news",
            raw_publication_date="2026-11-01",
        )
        aged = market_research_service.calculate_source_quality(
            url="https://www.livemint.com/news",
            raw_publication_date="2024-01-01",
        )
        assert aged["final_score"] < fresh["final_score"]
        assert aged["staleness_factor"] == "aged_over_1_year"

    def test_calculate_source_quality_unverified_date(self):
        res = market_research_service.calculate_source_quality(
            url="https://hawky.ai/ad-gallery/angel-one",
            raw_publication_date=None,
        )
        assert res["tier"] == 3
        assert res["publication_date"] is None
        assert res["date_verification_status"] == "unverified"
        assert res["staleness_factor"] == "undated"


class TestMarketContextBuilder:
    """Verifies contextual synthesis and prompt directive generation."""

    def test_build_india_prompt_directive(self):
        directive = market_context_builder.get_agent_prompt_directive("IN", "script")
        assert "India (IN)" in directive
        assert "SEBI" in directive
        assert "MANDATORY REGULATORY COMPLIANCE" in directive

    def test_build_philippines_prompt_directive(self):
        directive = market_context_builder.get_agent_prompt_directive("PH", "script")
        assert "Philippines (PH)" in directive
        assert "SEC Philippines" in directive
        assert "PSE" in directive
        assert "MANDATORY REGULATORY COMPLIANCE" in directive


class TestMarketIntelligenceEngine:
    """Verifies unified engine capabilities and dual-market variant generation."""

    def test_supported_countries(self):
        countries = market_intelligence_engine.get_supported_countries()
        codes = [c["country_code"] for c in countries]
        assert "IN" in codes
        assert "PH" in codes
        assert "BOTH" in codes

    def test_country_overview_in(self):
        overview = market_intelligence_engine.get_country_overview("IN")
        assert overview["country_code"] == "IN"
        assert overview["country_name"] == "India"
        assert "INR" in str(overview["currency"])

    def test_country_overview_ph(self):
        overview = market_intelligence_engine.get_country_overview("PH")
        assert overview["country_code"] == "PH"
        assert overview["country_name"] == "Philippines"
        assert "PHP" in str(overview["currency"])

    def test_campaign_recommendations(self):
        recs_in = market_intelligence_engine.get_campaign_recommendations("IN")
        assert len(recs_in["recommended_angles"]) > 0
        assert len(recs_in["local_terminology"]) > 0

        recs_ph = market_intelligence_engine.get_campaign_recommendations("PH")
        assert len(recs_ph["recommended_angles"]) > 0
        assert len(recs_ph["local_terminology"]) > 0

    def test_create_dual_market_campaign_variants(self):
        base_data = {
            "name": "Q4 Volatility Protocol",
            "description": "Autonomous multi-market campaign",
            "objective": "brand_awareness",
            "video_duration_seconds": 45,
            "video_aspect_ratio": "9:16",
            "creative_direction": "Cinematic visual sentiment clarity",
            "audience": {
                "segments": ["active_traders"],
                "interests": ["sentiment"],
            },
        }

        variants = market_intelligence_engine.generate_dual_market_variant_dicts(base_data)
        assert len(variants) == 2
        var_in, var_ph = variants[0], variants[1]

        # India Variant
        assert var_in["target_country"] == "IN"
        assert "India" in var_in["name"]
        assert var_in["audience"]["target_country"] == "IN"
        assert "in_options_derivative_trader" in var_in["audience"]["segments"]

        # Philippines Variant
        assert var_ph["target_country"] == "PH"
        assert "Philippines" in var_ph["name"]
        assert var_ph["audience"]["target_country"] == "PH"
        assert "ph_active_equity_trader" in var_ph["audience"]["segments"]

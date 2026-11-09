"""
CrowdWisdom AI Studio — Research Intelligence 2.0 Test Suite
Covers:
1. Provider Health Service diagnostics & latency tracking
2. Claim-level evidence verification & 5-tier source scoring
3. Apify ad normalization & classification (LIVE_META_AD vs HISTORICAL_META_AD vs BENCHMARK)
4. Date normalization with Apify actor fields
5. Compliance validator rejecting predatory/absolute claims
6. Market Context Builder positioning & regulatory disclaimers
"""
import pytest
import asyncio
import os
import sys
from datetime import datetime, timezone
from unittest.mock import patch, AsyncMock

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from services.market_intelligence.provider_health_service import (
    ProviderHealthService,
    provider_health_service,
)
from services.market_intelligence.market_research_service import (
    MarketResearchService,
    market_research_service,
)
from services.market_intelligence.market_context_builder import (
    MarketContextBuilder,
    market_context_builder,
)
from services.date_normalization import extract_and_normalize_publication_date
from agents.ads_manager_agent import AdsManagerAgent


class TestProviderHealthService:
    """Tests provider health checks and status reporting."""

    @pytest.mark.asyncio
    async def test_check_all_providers_returns_all_expected_keys(self):
        service = ProviderHealthService()
        with patch("services.market_intelligence.provider_health_service.get_decrypted_api_key", new=AsyncMock(return_value=None)):
            result = await service.check_all_providers()
            assert "timestamp" in result
            assert "providers" in result
            providers = result["providers"]
            for expected in ["exa", "apify", "nvidia_nim", "tavily", "gemini"]:
                assert expected in providers
                p_data = providers[expected]
                assert "category" in p_data
                assert "status" in p_data
                assert "latency_ms" in p_data or "error" in p_data

    @pytest.mark.asyncio
    async def test_ping_provider_gemini_fails_gracefully(self):
        service = ProviderHealthService()
        with patch("services.market_intelligence.provider_health_service.get_decrypted_api_key", new=AsyncMock(return_value="dummy_expired_token")):
            status = await service.ping_provider("gemini")
            assert status["status"] in ["AUTH_FAILED", "UNAUTHENTICATED", "ERROR"]
            assert status["provider"] == "Gemini"

    @pytest.mark.asyncio
    async def test_ping_provider_tavily_reports_quota_or_status(self):
        service = ProviderHealthService()
        with patch("services.market_intelligence.provider_health_service.get_decrypted_api_key", new=AsyncMock(return_value="tvly-mock-key")):
            status = await service.ping_provider("tavily")
            assert status["status"] in ["QUOTA_EXCEEDED", "LIVE_AND_VERIFIED", "ERROR"]
            assert status["provider"] == "Tavily"


class TestClaimLevelEvidenceVerification:
    """Tests claim verification and 5-tier scoring."""

    def test_claim_structure_contains_all_12_required_fields(self):
        service = MarketResearchService()
        evidence_in = service._get_verified_ground_truth_benchmarks("IN", "retail trading")
        assert len(evidence_in) > 0
        required_fields = [
            "claim_text",
            "source_url",
            "publisher",
            "article_title",
            "publication_date",
            "retrieval_timestamp",
            "target_country",
            "source_tier",
            "supporting_excerpt",
            "evidence_classification",
            "confidence_score",
            "verification_status",
        ]
        for claim in evidence_in:
            for field in required_fields:
                assert field in claim, f"Missing field {field} in claim: {claim.get('claim_text')}"
            assert claim["evidence_classification"] in [
                "DIRECTLY_SUPPORTED",
                "PARTIALLY_SUPPORTED",
                "CONTRADICTED",
                "AI_INTERPRETATION",
                "UNVERIFIED",
            ]
            assert 1 <= claim["source_tier"] <= 5
            assert 0.0 <= claim["confidence_score"] <= 10.0

    def test_staleness_penalty_calculation(self):
        service = MarketResearchService()
        # In late 2026, 2026-10-01 is fresh (<180 days)
        q_fresh = service.calculate_source_quality(
            url="https://www.sebi.gov.in/reports/study.html",
            raw_publication_date="2026-10-01",
            is_benchmark=False
        )
        # 2022-01-01 is aged over 1 year
        q_stale = service.calculate_source_quality(
            url="https://www.sebi.gov.in/reports/study.html",
            raw_publication_date="2022-01-01",
            is_benchmark=False
        )
        assert q_fresh["staleness_penalty"] == 1.0
        assert q_stale["staleness_penalty"] == 0.85
        assert q_stale["final_score"] < q_fresh["final_score"]

    def test_undated_penalty_calculation(self):
        service = MarketResearchService()
        q_dated = service.calculate_source_quality(
            url="https://www.nseindia.com/market-data",
            raw_publication_date="2026-10-01",
            is_benchmark=False
        )
        q_undated = service.calculate_source_quality(
            url="https://www.nseindia.com/market-data",
            raw_publication_date="",
            is_benchmark=False
        )
        assert q_undated["staleness_penalty"] == 0.90
        assert q_undated["final_score"] < q_dated["final_score"]


class TestCompetitorAdNormalization:
    """Tests normalization of Meta Ads and classification."""

    def test_apify_date_normalization_start_date_formatted(self):
        raw_ad = {
            "adArchiveId": "1067875839006071",
            "startDateFormatted": "2026-08-06T07:00:00.000Z",
            "publisherPlatform": ["facebook", "instagram"]
        }
        res = extract_and_normalize_publication_date(raw_ad)
        assert res["published_at"] is not None
        assert res["date_verification_status"] == "verified"
        assert res["published_date_source"] == "startDateFormatted"
        assert res["published_at_raw"] == "2026-08-06T07:00:00.000Z"
        assert "1067875839006071" in res["meta_ads_url"]

    def test_ad_classification_distinguishes_live_vs_benchmark(self):
        agent = AdsManagerAgent()
        
        # Test real Apify record structure
        apify_item = {
            "adArchiveId": "831263616157275",
            "pageName": "Trade-Investing Now",
            "isActive": True,
            "snapshot": {
                "body": {"text": "Start Trading From ₱180. Bonus Up To $200"},
                "title": "Trade-Investing Now",
                "ctaText": "Install now",
                "linkUrl": "https://example.com"
            },
            "startDateFormatted": "2025-11-09T08:00:00.000Z",
            "publisherPlatform": ["facebook"]
        }
        normalized = agent.normalize_ad(apify_item, "PH")
        assert normalized["ad_classification"] == "LIVE_META_AD"
        assert normalized["competitor_name"] == "Trade-Investing Now"
        assert normalized["cta"] == "Install now"
        assert normalized["meta_ad_archive_id"] == "831263616157275"
        assert normalized["target_country"] == "PH"

        # Test benchmark record structure
        benchmark_item = {
            "competitor_name": "Zerodha Coin",
            "ad_copy": "Invest in direct mutual funds with zero brokerage",
            "target_country": "IN",
            "is_benchmark": True
        }
        normalized_bm = agent.normalize_ad(benchmark_item, "IN")
        assert normalized_bm["ad_classification"] == "VERIFIED_DOMAIN_BENCHMARK"


class TestComplianceAndContextBuilder:
    """Tests strict compliance against absolute/unsubstantiated claims."""

    def test_market_context_builder_forbids_absolute_claims(self):
        directive_in = market_context_builder.get_agent_prompt_directive("IN", "script")
        assert "NEVER promise guaranteed returns" in directive_in
        assert "scam-proof" in directive_in.lower()
        assert "Research-Backed Clarity for More Informed Investing" in directive_in

        directive_ph = market_context_builder.get_agent_prompt_directive("PH", "script")
        assert "NEVER promise guaranteed returns" in directive_ph
        assert "Research-Backed Clarity for More Informed Investing" in directive_ph

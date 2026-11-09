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


class TestCompetitorRelevanceClassification:
    """Tests 7-category competitor relevance classification and unrelated ad filtering."""

    def test_shopee_classified_as_unrelated(self):
        res = AdsManagerAgent.classify_advertiser_relevance(
            advertiser="Shopee",
            text="Big Sale 11.11! Free shipping on millions of items.",
            headline="Shop Now",
            landing_page="https://shopee.com",
            cta="Install now"
        )
        assert res["relevance_category"] == "UNRELATED_ADVERTISER"
        assert res["is_competitor"] is False
        assert "Shopee is a general consumer e-commerce marketplace" in res["relevance_explanation"]

    def test_direct_competitor_classification(self):
        res = AdsManagerAgent.classify_advertiser_relevance(
            advertiser="Hawky",
            text="Real-time market sentiment and options flow tracker.",
            headline="Market Sentiment Radar",
            landing_page="https://hawky.ai",
            cta="Learn more"
        )
        assert res["relevance_category"] == "DIRECT_COMPETITOR"
        assert res["is_competitor"] is True

    def test_indirect_competitor_classification(self):
        res = AdsManagerAgent.classify_advertiser_relevance(
            advertiser="TradingView",
            text="Advanced technical analysis charts and stock screener.",
            headline="Track All Markets",
            landing_page="https://tradingview.com",
            cta="Sign up"
        )
        assert res["relevance_category"] == "INDIRECT_COMPETITOR"
        assert res["is_competitor"] is True

    def test_broker_platform_classification(self):
        res = AdsManagerAgent.classify_advertiser_relevance(
            advertiser="Zerodha",
            text="Invest in direct mutual funds and trade equities with zero brokerage.",
            headline="Open a Demat Account",
            landing_page="https://zerodha.com",
            cta="Open Account"
        )
        assert res["relevance_category"] == "BROKER_OR_TRADING_PLATFORM"
        assert res["is_competitor"] is False

    def test_financial_platform_classification(self):
        res = AdsManagerAgent.classify_advertiser_relevance(
            advertiser="GCash",
            text="Send money, pay bills, and buy stocks directly in the GCash app.",
            headline="GStocks PH",
            landing_page="https://gcash.com/services/gstocks-ph",
            cta="Learn more"
        )
        assert res["relevance_category"] == "FINANCIAL_PLATFORM"
        assert res["is_competitor"] is False

    def test_financial_education_classification(self):
        res = AdsManagerAgent.classify_advertiser_relevance(
            advertiser="Pro Trader Academy",
            text="Join our weekend masterclass course on price action trading.",
            headline="Learn to Trade",
            landing_page="https://example.com/course",
            cta="Sign up"
        )
        assert res["relevance_category"] == "FINANCIAL_EDUCATION"
        assert res["is_competitor"] is False

    def test_historical_ad_active_status_enforced(self):
        agent = AdsManagerAgent()
        raw_ad = {
            "adArchiveId": "999999999",
            "pageName": "Old Campaign",
            "isActive": False,
            "endDateFormatted": "2026-01-01T00:00:00.000Z",
            "snapshot": {"body": {"text": "Old ad copy"}, "title": "Old ad"}
        }
        normalized = agent.normalize_ad(raw_ad, "IN")
        assert normalized["active_status"] == "inactive"
        assert normalized["ad_classification"] == "HISTORICAL_META_AD"

    def test_country_targeting_evidence_distinction(self):
        agent = AdsManagerAgent()
        explicit_ad = {
            "adArchiveId": "111",
            "pageName": "Targeted Brand",
            "targetedOrReachedCountries": ["IN", "AE"],
            "snapshot": {"body": {"text": "Trading app"}}
        }
        norm_exp = agent.normalize_ad(explicit_ad, "IN")
        assert norm_exp["country_evidence_type"] == "explicit_meta_targeting"
        assert "IN, AE" in norm_exp["country_evidence_details"]

        inferred_ad = {
            "adArchiveId": "222",
            "pageName": "Global Brand",
            "snapshot": {"body": {"text": "Trading app"}}
        }
        norm_inf = agent.normalize_ad(inferred_ad, "PH")
        assert norm_inf["country_evidence_type"] == "query_country_filter"


class TestEvidenceIntegrity:
    """Tests audit evidence integrity, separating empirical statistics from AI hypotheses."""

    def test_ofw_remittance_macro_statistic_is_verified_fact(self):
        service = MarketResearchService()
        benchmarks = service._get_verified_ground_truth_benchmarks("PH", "remittances")
        bsp_claim = next(b for b in benchmarks if "BSP" in b.get("publisher", ""))
        assert bsp_claim["is_verified_fact"] is True
        assert bsp_claim["evidence_classification"] == "DIRECTLY_SUPPORTED"
        assert "$37.2 billion" in bsp_claim["finding"]
        assert "equities" not in bsp_claim["finding"]
        assert "REITs" not in bsp_claim["finding"]

    def test_ofw_reit_allocation_is_classified_as_ai_interpretation(self):
        service = MarketResearchService()
        benchmarks = service._get_verified_ground_truth_benchmarks("PH", "reits")
        hyp_claim = next(b for b in benchmarks if "market hypothesis" in b.get("topic", ""))
        assert hyp_claim["is_verified_fact"] is False
        assert hyp_claim["evidence_classification"] == "AI_INTERPRETATION"
        assert hyp_claim["confidence_score"] < 8.0

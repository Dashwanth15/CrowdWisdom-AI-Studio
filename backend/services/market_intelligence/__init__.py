"""
CrowdWisdom AI Studio — Market Intelligence Services Package
"""
from services.market_intelligence.india_market_profile import INDIA_MARKET_PROFILE, get_india_market_profile
from services.market_intelligence.philippines_market_profile import PHILIPPINES_MARKET_PROFILE, get_philippines_market_profile
from services.market_intelligence.audience_segmentation import audience_segmentation_engine, AudienceSegmentationEngine
from services.market_intelligence.market_research_service import market_research_service, MarketResearchService
from services.market_intelligence.market_validation import compliance_validator, MarketComplianceValidator
from services.market_intelligence.market_context_builder import market_context_builder, MarketContextBuilder
from services.market_intelligence.market_intelligence_engine import market_intelligence_engine, MarketIntelligenceEngine

__all__ = [
    "INDIA_MARKET_PROFILE",
    "PHILIPPINES_MARKET_PROFILE",
    "get_india_market_profile",
    "get_philippines_market_profile",
    "audience_segmentation_engine",
    "AudienceSegmentationEngine",
    "market_research_service",
    "MarketResearchService",
    "compliance_validator",
    "MarketComplianceValidator",
    "market_context_builder",
    "MarketContextBuilder",
    "market_intelligence_engine",
    "MarketIntelligenceEngine",
]

"""
CrowdWisdom AI Studio — Market Context Builder
Synthesizes country profiles, audience segmentation, real-time research evidence,
and regulatory requirements into rich, structured contexts for AI agents.
"""
import json
import logging
from typing import Any, Dict, List, Optional
from services.market_intelligence.india_market_profile import INDIA_MARKET_PROFILE
from services.market_intelligence.philippines_market_profile import PHILIPPINES_MARKET_PROFILE
from services.market_intelligence.audience_segmentation import audience_segmentation_engine
from services.market_intelligence.market_research_service import market_research_service
from services.market_intelligence.market_validation import compliance_validator

logger = logging.getLogger(__name__)


class MarketContextBuilder:
    """
    Builds country-specific market context objects tailored for consumption
    by the Ads Manager Agent, Creative Intelligence Engine, Script Agent, and Video Agent.
    """

    async def build_context(
        self,
        country_code: str,
        audience_config: Optional[Dict[str, Any]] = None,
        include_live_research: bool = True,
        research_limit: int = 5,
    ) -> Dict[str, Any]:
        """
        Builds a complete, multi-layered market context for a campaign.
        """
        country = country_code.upper().strip() if country_code else "IN"
        if country not in ("IN", "PH"):
            country = "IN"

        profile = INDIA_MARKET_PROFILE if country == "IN" else PHILIPPINES_MARKET_PROFILE
        audience_cfg = audience_config or {}

        # 1. Match Audience Segment
        seg_match = audience_segmentation_engine.match_campaign_audience(country, audience_cfg)
        primary_segment = seg_match.get("matched_segment", {})

        # 2. Retrieve Evidence-Backed Research
        evidence = []
        if include_live_research:
            try:
                evidence = await market_research_service.get_market_research_evidence(
                    country_code=country,
                    topic="retail trader sentiment",
                    limit=research_limit
                )
            except Exception as e:
                logger.warning(f"[MarketContextBuilder] Research fetch notice: {e}")

        # 3. Format Local Terminology and Creative Hooks
        mkt_info = profile.get("marketing_intelligence", {})
        creative_angles = mkt_info.get("creative_angles", [])
        local_terms = mkt_info.get("local_terminology", [])
        voice_spec = mkt_info.get("voiceover_specifications", {})
        reg_safeguards = profile.get("regulatory_safeguards", {})

        # 4. Synthesize Prompt Directives for LLMs
        agent_directives = self._build_agent_prompt_directives(
            country=country,
            profile=profile,
            segment=primary_segment,
            evidence=evidence,
            creative_angles=creative_angles,
            local_terms=local_terms,
            reg_safeguards=reg_safeguards
        )

        return {
            "country_code": country,
            "country_name": profile.get("country_name"),
            "currency": profile.get("currency"),
            "timezone": profile.get("timezone"),
            "market_hours": profile.get("market_hours"),
            "market_ecosystem": profile.get("market_ecosystem"),
            "audience": {
                "matched_segment": primary_segment,
                "preferred_languages": primary_segment.get("preferred_languages", []),
                "dominant_channels": primary_segment.get("dominant_channels", []),
                "pain_points": primary_segment.get("pain_points", []),
                "regional_intelligence": profile.get("regional_intelligence"),
            },
            "creative": {
                "recommended_angles": creative_angles,
                "local_terminology": local_terms,
                "voiceover_spec": voice_spec,
            },
            "research_evidence": evidence,
            "regulatory_safeguards": reg_safeguards,
            "agent_directives": agent_directives,
        }

    def get_agent_prompt_directive(self, country_code: str, agent_type: str = "script") -> str:
        """Helper to get prompt directive for a specific country and agent."""
        country = country_code.upper().strip() if country_code else "IN"
        profile = INDIA_MARKET_PROFILE if country == "IN" else PHILIPPINES_MARKET_PROFILE
        segments = profile.get("audience_segments", [])
        segment = segments[0] if segments else {}
        mkt = profile.get("marketing_intelligence", {})
        directives = self._build_agent_prompt_directives(
            country=country,
            profile=profile,
            segment=segment,
            evidence=[],
            creative_angles=mkt.get("creative_angles", []),
            local_terms=mkt.get("local_terminology", []),
            reg_safeguards=profile.get("regulatory_safeguards", {})
        )
        return directives.get(agent_type, directives.get("script", ""))

    def _build_agent_prompt_directives(
        self,
        country: str,
        profile: Dict[str, Any],
        segment: Dict[str, Any],
        evidence: List[Dict[str, Any]],
        creative_angles: List[Dict[str, Any]],
        local_terms: List[str],
        reg_safeguards: Dict[str, Any]
    ) -> Dict[str, str]:
        """
        Creates prompt injection strings customized for each agent.
        """
        c_name = profile.get("country_name", "India")
        seg_name = segment.get("name", "Retail Trader")
        pain_points_str = "\n".join(f"- {p}" for p in segment.get("pain_points", []))
        terms_str = ", ".join(local_terms[:8])
        disclaimers_str = " | ".join(reg_safeguards.get("mandatory_disclaimers", []))

        evidence_str = "\n".join(
            f"- [{e.get('publisher')}]: \"{e.get('finding')[:180]}...\" (Source: {e.get('source_url')})"
            for e in evidence[:3]
        ) if evidence else "Evidence: Official regulatory market statistics."

        # Prompt for Script Agent
        script_prompt_directive = f"""
======================================================================
TARGET COUNTRY: {c_name} ({country})
TARGET AUDIENCE: {seg_name} ({segment.get('experience_level', 'All')})
LOCAL LANGUAGE NUANCE: {', '.join(segment.get('preferred_languages', ['English']))}
LOCAL FINANCIAL TERMINOLOGY TO NATURALLY INTEGRATE: {terms_str}

CORE AUDIENCE PAIN POINTS IN {c_name.upper()}:
{pain_points_str}

GROUND-TRUTH MARKET RESEARCH EVIDENCE (Cite or ground in script):
{evidence_str}

MANDATORY REGULATORY COMPLIANCE ({reg_safeguards.get('regulator')}):
1. NEVER promise guaranteed returns, win rates, or risk-free profits.
2. NEVER use absolute terms like 'scam-proof', 'foolproof', or claim to eliminate investment risk. Position platform as 'Research-Backed Clarity for More Informed Investing'.
3. Emphasize that CrowdWisdom provides objective market sentiment and consensus tools for research.
4. Users execute trades on their own brokerages.
5. Mandatory disclaimer to include: "{disclaimers_str}"
======================================================================
"""

        # Prompt for Ads Manager Agent
        ads_prompt_directive = f"""
Country Focus: {c_name} ({country}). Focus competitor discovery and analysis on financial advertising active in {c_name}.
Search for verified advertising themes addressing local trader pain points: {segment.get('pain_points', ['conflicting signals'])[0]}.
"""

        # Prompt for Video Agent
        video_prompt_directive = f"""
Target Country: {c_name}
Voiceover Locale: {profile.get('marketing_intelligence', {}).get('voiceover_specifications', {}).get('locale', 'en-US')}
Recommended Narrator: {profile.get('marketing_intelligence', {}).get('voiceover_specifications', {}).get('recommended_voices', [{}])[0].get('voice_id', 'en-US-ChristopherNeural')}
Visual Context: Subtle cinematic elements reflecting {c_name}'s modern trading environment without heavy stereotypes.
On-Screen Mandatory Disclaimer: "{reg_safeguards.get('mandatory_disclaimers', ['Educational and sentiment research only.'])[0]}"
"""

        return {
            "script": script_prompt_directive.strip(),
            "script_agent": script_prompt_directive.strip(),
            "ads": ads_prompt_directive.strip(),
            "ads_manager_agent": ads_prompt_directive.strip(),
            "video": video_prompt_directive.strip(),
            "video_agent": video_prompt_directive.strip(),
            "video_production_agent": video_prompt_directive.strip(),
        }


market_context_builder = MarketContextBuilder()

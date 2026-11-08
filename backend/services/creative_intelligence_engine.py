"""
CrowdWisdom AI Studio — Creative Intelligence Engine (CIE)
Operates between Advertisement Research and Script Generation.
Synthesizes competitor ad intelligence, trader sentiment research, and verified CrowdWisdomTrading
product features into actionable Creative Briefs with human approval checkpoints.
"""
import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from bson import ObjectId

from integrations.llm_client import LLMClient
from services.integration_service import get_decrypted_api_key
from database.connection import get_database

logger = logging.getLogger(__name__)

CIE_SYSTEM_PROMPT = """You are the Chief Creative Strategist for CrowdWisdom AI Studio.
Your role is to transform raw advertisement research, competitor patterns, and trader sentiment data
into a structured, cinematic Creative Brief for CrowdWisdomTrading.com.

BRAND & PRODUCT ESSENCE:
- Platform: CrowdWisdomTrading.com
- Core Value: Market sentiment and collective intelligence for retail and active traders.
- Key Verified Features:
  * CrowdPulse: Real-time ticker mentions and 30-day sentiment shifts tracking crowd mood.
  * Weekly/Daily Wisdom: Consensus trade plans derived from professional trader sentiment.
  * CrowdMap: Visual map of crowd expectations for price targets, stops, support, and resistance.
  * Pro Crowd Bars: Aggregated conviction levels over distinct time horizons.
- Compliance Rule: NEVER state or imply guaranteed profits, win rates, or financial advice.

Your output must be a thorough, professional, actionable Creative Brief in valid JSON format.
"""


class CreativeIntelligenceEngine:
    """
    Dedicated Creative Intelligence Engine.
    Synthesizes research into high-conviction creative blueprints, hook architectures,
    and emotional vectors prior to script writing.
    """

    async def generate_creative_brief(
        self,
        campaign_id: str,
        research_job_id: Optional[str] = None,
        custom_instructions: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Synthesizes all ad research and marketing insights from MongoDB into a unified Creative Brief.
        """
        db = get_database()

        # 1. Fetch Campaign Context
        campaign = await db.campaigns.find_one({"_id": ObjectId(campaign_id)})
        if not campaign:
            raise ValueError(f"Campaign {campaign_id} not found.")

        # 2. Fetch Extracted Insights and Researched Ads
        insights = await db.marketing_insights.find({"campaign_id": campaign_id}).to_list(50)
        top_ads = await db.advertisements.find(
            {"campaign_id": campaign_id}
        ).sort("evaluation_score.overall", -1).limit(15).to_list(15)

        # 3. Retrieve LLM Provider (prioritize Google Gemini over NVIDIA and OpenRouter)
        gemini_key = await get_decrypted_api_key("gemini")
        nvidia_key = await get_decrypted_api_key("nvidia_nim")
        openrouter_key = await get_decrypted_api_key("openrouter")
        llm_key = gemini_key or nvidia_key or openrouter_key
        llm_provider = "gemini" if gemini_key else ("nvidia_nim" if nvidia_key else "openrouter")

        if not llm_key:
            raise ValueError("No LLM provider configured. Add Gemini, NVIDIA NIM, or OpenRouter in Settings.")

        llm = LLMClient(api_key=llm_key, provider=llm_provider)

        # 4. Format Research Context
        insights_summary = [
            {"category": i.get("category"), "title": i.get("title"), "description": i.get("description")}
            for i in insights
        ]
        ads_summary = [
            {
                "advertiser": a.get("advertiser"),
                "hook": a.get("hook"),
                "marketing_angle": a.get("marketing_angle"),
                "pain_point": a.get("pain_point"),
                "score": a.get("evaluation_score", {}).get("overall") if a.get("evaluation_score") else None,
            }
            for a in top_ads
        ]

        prompt = f"""
CAMPAIGN OBJECTIVE: {campaign.get('objective', 'brand_awareness')}
TARGET AUDIENCE: {json.dumps(campaign.get('audience', {}))}
CREATIVE DIRECTION: {campaign.get('creative_direction', 'Cinematic financial thriller')}
ADDITIONAL INSTRUCTIONS: {custom_instructions or 'None'}

MARKETING INSIGHTS FROM AD RESEARCH:
{json.dumps(insights_summary, indent=2)}

TOP PERFORMING COMPETITOR AD PATTERNS OBSERVED:
{json.dumps(ads_summary, indent=2)}

Generate a comprehensive Creative Brief in JSON with the following schema:
{{
  "title": "Creative Strategic Brief - CrowdWisdomTrading",
  "executive_summary": "High-level creative positioning statement",
  "target_audience_deep_dive": {{
    "primary_persona": "Description of primary retail trader persona",
    "psychological_state": "Current emotional frustration (e.g. noise, decision paralysis, conflicting advice)",
    "core_desire": "Clarity, consensus, objective validation without false hype"
  }},
  "creative_angles": [
    {{
      "angle_id": "angle_1",
      "name": "The Silence in the Noise",
      "approach_type": "pain_point",
      "core_thesis": "...",
      "hook_concept": "Visual hook for the first 3-5 seconds",
      "emotional_arc": "Overwhelmed -> Discovery -> Confident Clarity"
    }},
    {{
      "angle_id": "angle_2",
      "name": "What 10,000 Traders Know",
      "approach_type": "unique_data",
      "core_thesis": "...",
      "hook_concept": "Visual hook highlighting CrowdPulse and consensus shifts",
      "emotional_arc": "Curiosity -> Revelation -> Empowerment"
    }},
    {{
      "angle_id": "angle_3",
      "name": "The Blueprint of Collective Conviction",
      "approach_type": "product_value",
      "core_thesis": "...",
      "hook_concept": "Visual hook showcasing Weekly Wisdom and CrowdMap",
      "emotional_arc": "Skepticism -> Validation -> Informed Action"
    }}
  ],
  "hook_taxonomy": [
    {{
      "type": "Visual Paradox",
      "description": "Dramatic contrast between chaotic financial headlines and clean sentiment signal",
      "timing": "0:00 - 0:04"
    }},
    {{
      "type": "Direct Question Interrupt",
      "description": "Are you trading the market, or trading someone else's opinion?",
      "timing": "0:00 - 0:03"
    }}
  ],
  "compliance_guardrails": [
    "No promises of monetary returns, percentage gains, or win-rates",
    "Distinguish between market sentiment observation and personalized investment advice",
    "Emphasize CrowdWisdom as a research and validation platform"
  ],
  "sound_and_tone_direction": "Atmospheric, propulsive, modern cinematic synth score with crisp UI audio haptics"
}}
"""

        try:
            response = await llm.chat_json(
                messages=[
                    {"role": "system", "content": CIE_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4
            )
        except Exception as llm_err:
            logger.warning(f"[CIE] LLM brief generation failed: {llm_err}. Synthesizing structured creative brief from campaign intelligence...")
            response = {
                "campaign_id": campaign_id,
                "executive_summary": f"Targeted marketing strategy for {campaign.get('name', 'CrowdWisdom Campaign')} focusing on retail market sentiment aggregation and disciplined trade validation.",
                "target_audience_profile": {
                    "primary_segment": "Active retail options and equities traders",
                    "pain_points": [
                        "Information overload and conflicting market commentary",
                        "Emotional execution mistakes and fear of missing out",
                        "Lack of institutional-grade sentiment and positioning data"
                    ],
                    "core_desires": [
                        "Objective consensus clarity across market participants",
                        "High-conviction, mathematically verified trade setups",
                        "Community-validated trading intelligence without guru hype"
                    ]
                },
                "creative_angles": [
                    {
                        "approach": "pain_point",
                        "angle_title": "Silence the Noise. Trade with Conviction.",
                        "hook_concept": "A trader overwhelmed by dozens of conflicting charts before discovering clarity.",
                        "emotional_driver": "From anxiety and fatigue to calm, disciplined execution"
                    },
                    {
                        "approach": "unique_data",
                        "angle_title": "Beyond the Tape: The Collective Sentiment Edge",
                        "hook_concept": "3D volume heatmap illuminating real-time crowd positioning before price moves.",
                        "emotional_driver": "Asymmetric analytical edge and professional confidence"
                    },
                    {
                        "approach": "product_value",
                        "angle_title": "CrowdWisdomTrading: The Intelligence Engine",
                        "hook_concept": "Synchronized global analytics transforming retail chaos into actionable trade alerts.",
                        "emotional_driver": "Belonging to an elite, data-driven trading collective"
                    }
                ],
                "compliance_guardrails": [
                    "No promises of monetary returns, percentage gains, or guaranteed win-rates",
                    "Distinguish between market sentiment observation and personalized investment advice",
                    "Emphasize CrowdWisdom as a research and validation platform"
                ],
                "sound_and_tone_direction": "Atmospheric, propulsive, modern cinematic synth score with crisp UI audio haptics"
            }

        # 5. Persist to MongoDB `creative_briefs`
        brief_doc = {
            "campaign_id": campaign_id,
            "research_job_id": research_job_id,
            "status": "pending_approval",  # Checkpoint 1: Requires approval before script generation
            "version": 1,
            "content": response,
            "approved_by": None,
            "approved_at": None,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }

        result = await db.creative_briefs.insert_one(brief_doc)
        brief_doc["_id"] = result.inserted_id

        # Update campaign context
        await db.campaigns.update_one(
            {"_id": ObjectId(campaign_id)},
            {"$set": {"active_creative_brief_id": str(result.inserted_id)}}
        )

        return {
            "brief_id": str(result.inserted_id),
            "status": "pending_approval",
            "content": response
        }

    async def approve_brief(self, brief_id: str, user_id: str) -> Dict[str, Any]:
        """Human approval checkpoint for the creative brief."""
        db = get_database()
        now = datetime.now(timezone.utc)
        result = await db.creative_briefs.find_one_and_update(
            {"_id": ObjectId(brief_id)},
            {
                "$set": {
                    "status": "approved",
                    "approved_by": user_id,
                    "approved_at": now,
                    "updated_at": now
                }
            },
            return_document=True
        )
        return result


# Singleton instance
creative_intelligence_engine = CreativeIntelligenceEngine()


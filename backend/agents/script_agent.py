"""
CrowdWisdom AI Studio — Script Agent
Converts research and product knowledge into cinematic advertising scripts.
Supports three approaches: Pain-Point, Unique-Data, and Product-Value.
"""
import copy
import json
import logging
import hashlib
import random
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from bson import ObjectId

from agents.base_agent import BaseHermesAgent
from integrations.tavily_client import TavilyClient
from integrations.exa_client import ExaClient
from integrations.llm_client import LLMClient
from services.integration_service import get_decrypted_api_key
from database.connection import get_database
from services.market_intelligence import market_context_builder, compliance_validator

logger = logging.getLogger(__name__)

CROWDWISDOM_PRODUCT_CONTEXT = """
CrowdWisdomTrading.com is a market sentiment and collective intelligence platform for retail traders and investors.

VERIFIED PLATFORM FEATURES:
- CrowdPulse: Tracks daily ticker mentions and monitors 30-day sentiment shifts and "whiplash" in market attention
- Weekly/Daily Wisdom: Consensus trade plans from professional trader sentiment (directional bias, entries, stop-losses, profit targets)
- CrowdMap: Visual representation of where the crowd places expectations for price targets, stops, support, resistance
- Pro Crowd Bars: Displays collective trader conviction levels over a given period
- Aggregates and filters public commentary from professional traders and market experts
- Designed as a research and validation tool — users execute trades on their own brokerages

TARGET AUDIENCES:
- Retail traders overwhelmed by conflicting information
- Options traders seeking market consensus
- Active stock/ETF investors using sentiment as a research signal
- Financial research enthusiasts tracking crowd behavior

COMPLIANCE REQUIREMENTS — NEVER INCLUDE IN SCRIPTS:
- Guaranteed profits or returns
- Specific win rates or performance claims without verified source
- Fabricated testimonials or success stories
- Misleading urgency or fear tactics
- Investment advice claims
"""

SCRIPT_SYSTEM_PROMPT = f"""You are an award-winning creative director, commercial filmmaker, and financial screenwriter specializing in high-production cinematic fintech advertisements.

{CROWDWISDOM_PRODUCT_CONTEXT}

COMMERCIAL PRODUCTION DIRECTIVES:
1. Cinematic film aesthetic: Write each scene like a prestige commercial (Apple, Stripe, Bloomberg, Robinhood).
2. Distinctive opening hook: Grab attention in the first 3 seconds with a visceral, original visual.
3. Authentic trader voiceover: Natural, confident human speech. Zero corporate buzzwords or generic hype.
4. Strict anti-cliché rule: DO NOT default to a tired trader staring at red screens with multiple monitors.
5. Concrete visual directions: Detail lighting (moody, golden hour, neon dusk), lens choices (macro 35mm, anamorphic), and concrete actions.

NARRATIVE ARCHETYPES TO ADAPT:
- The Confession: A real trader admitting a costly mistake from following social media hype, finding math/consensus.
- The 60-Second Routine: Minimalist dawn coffee routine showing how CrowdPulse filters hours of noise in 60 seconds.
- The Microstructure Whistleblower: Showing how market makers exploit fragmented retail noise, and how CrowdMap levels the playing field.
- The Macro Catalyst: A high-stakes Fed rate decision or volatility spike where CrowdWisdom conviction bars stay calm and clear.
- The 1978 Trap: Contrasting archaic 50-year-old lagging indicators (RSI/MACD) with modern real-time crowd velocity.
- The Contrarian Trap: Detecting extreme euphoria before a market top via sentiment divergence.
- The Collective Edge: A solitary trader tapping into a synchronized global network of disciplined minds.

Always respond with valid JSON only."""


def _tokenize(text: str) -> set:
    stop_words = {
        "the", "a", "an", "and", "or", "to", "in", "of", "with", "for", "on", "at",
        "is", "it", "this", "that", "crowdwisdom", "crowdwisdomtrading", "trading",
        "trader", "traders", "market", "markets", "com", "you", "your", "are", "be"
    }
    words = re.findall(r'[a-zA-Z]{3,}', text.lower())
    return {w for w in words if w not in stop_words}


def _jaccard(s1: set, s2: set) -> float:
    if not s1 or not s2:
        return 0.0
    return len(s1.intersection(s2)) / len(s1.union(s2))


def _bigrams(text: str) -> set:
    words = [w for w in re.findall(r'[a-zA-Z]{3,}', text.lower())]
    if len(words) < 2:
        return set()
    return {f"{words[i]}_{words[i+1]}" for i in range(len(words)-1)}


def _ngram_similarity(text1: str, text2: str) -> float:
    b1 = _bigrams(text1)
    b2 = _bigrams(text2)
    return _jaccard(b1, b2)


def calculate_script_similarity(
    candidate: Dict[str, Any],
    existing_scripts: List[Dict[str, Any]]
) -> Tuple[float, str, Dict[str, float]]:
    """
    Computes multi-dimensional similarity between a candidate script and existing campaign scripts:
    1. Semantic Similarity (50%): High penalty on identical or near-identical titles + core message & visual hook overlap.
    2. Structural & Narrative Similarity (30%): Overlap in emotional arc, marketing angle, and pain point strategy.
    3. Visual Composition Similarity (20%): Overlap in physical scene settings, camera direction, and lighting aesthetics.

    Returns: (max_composite_similarity, most_similar_script_title, similarity_breakdown)
    """
    max_sim = 0.0
    most_similar_title = "None"
    breakdown = {"title": 0.0, "semantic": 0.0, "structural": 0.0, "visual": 0.0}

    cand_title = candidate.get("campaign_title") or candidate.get("title") or ""
    cand_core = candidate.get("core_message", "")
    cand_hook = candidate.get("visual_hook", "")
    cand_struct = f"{candidate.get('emotional_direction', '')} {candidate.get('marketing_angle', '')} {candidate.get('pain_point', '')}"
    cand_vis = " ".join([s.get("visual_description", "") for s in candidate.get("scenes", [])])

    cand_title_tok = _tokenize(cand_title)
    cand_core_tok = _tokenize(cand_core)
    cand_hook_tok = _tokenize(cand_hook)
    cand_struct_tok = _tokenize(cand_struct)
    cand_vis_tok = _tokenize(cand_vis)

    for ex in existing_scripts:
        ex_title = ex.get("campaign_title") or ex.get("title") or ""
        ex_core = ex.get("core_message", "")
        ex_hook = ex.get("visual_hook", "")
        ex_struct = f"{ex.get('emotional_direction', '')} {ex.get('marketing_angle', '')} {ex.get('pain_point', '')}"
        ex_vis = " ".join([s.get("visual_description", "") for s in ex.get("scenes", [])])

        sim_title = _jaccard(cand_title_tok, _tokenize(ex_title))
        if _ngram_similarity(cand_title, ex_title) > 0.6:
            sim_title = max(sim_title, 0.9)

        sim_core = 0.6 * _jaccard(cand_core_tok, _tokenize(ex_core)) + 0.4 * _ngram_similarity(cand_core, ex_core)
        sim_hook = 0.6 * _jaccard(cand_hook_tok, _tokenize(ex_hook)) + 0.4 * _ngram_similarity(cand_hook, ex_hook)

        sim_sem = 0.50 * sim_title + 0.30 * sim_core + 0.20 * sim_hook
        sim_struct = _jaccard(cand_struct_tok, _tokenize(ex_struct))
        sim_vis = _jaccard(cand_vis_tok, _tokenize(ex_vis))

        # Direct title collisions trigger high baseline similarity
        if sim_title >= 0.7:
            composite = max(0.65, 0.50 * sim_sem + 0.30 * sim_struct + 0.20 * sim_vis)
        else:
            composite = 0.45 * sim_sem + 0.35 * sim_struct + 0.20 * sim_vis

        if composite > max_sim:
            max_sim = composite
            most_similar_title = ex_title
            breakdown = {"title": sim_title, "semantic": sim_sem, "structural": sim_struct, "visual": sim_vis}

    return max_sim, most_similar_title, breakdown


def _clean_on_screen_text(text: str, scene_num: int = 1) -> str:
    """
    Enforces strict typography and tone for on-screen text overlays:
    - Replaces shouting meme slogans ('BUY NOW! DUMP IT! FED HAWKISH? TO THE MOON!') with institutional clarity.
    - Limits word length to 4-6 concise words.
    - Formats into clean Title Case headlines.
    """
    if not text:
        return f"Scene {scene_num:02d} • Market Conviction"

    meme_patterns = [
        r'\bBUY\s+NOW!?\b',
        r'\bDUMP\s+IT!?\b',
        r'\bFED\s+HAWKISH\??\b',
        r'\bTO\s+THE\s+MOON!?\b',
        r'\bHODL\b',
        r'\bLFG\b',
        r'\b100X\b',
    ]
    cleaned = text
    for pat in meme_patterns:
        cleaned = re.sub(pat, '', cleaned, flags=re.IGNORECASE)

    cleaned = re.sub(r'[\s!?;:,]{2,}', ' ', cleaned).strip()
    cleaned = cleaned.strip(' !?;:,-')

    words = cleaned.split()
    if len(words) > 6:
        cleaned = " ".join(words[:6])

    if len(words) >= 3 and cleaned.isupper():
        cleaned = cleaned.title()

    if not cleaned or len(cleaned.strip()) < 3:
        fallbacks = {
            1: "Market Overwhelm • The Hidden Trap",
            2: "Order Book Skew • Institutional Footprint",
            3: "CrowdMap™ • Verified Consensus Levels",
            4: "Trade With Clarity • CrowdWisdomTrading"
        }
        cleaned = fallbacks.get(scene_num, "CrowdWisdomTrading.com")

    return cleaned


class ScriptAgent(BaseHermesAgent):
    agent_type = "script"
    agent_name = "Script Agent"
    agent_description = "Converts research and product knowledge into cinematic advertising scripts using three creative approaches."

    async def _run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        campaign_id = input_data["campaign_id"]
        script_id = input_data["script_id"]
        approach = input_data.get("approach", "pain_point")
        campaign_config = input_data.get("campaign_config", {})
        custom_prompt = input_data.get("custom_prompt")

        db = get_database()

        # Retrieve campaign context and target country
        campaign_doc = await db.campaigns.find_one({"_id": ObjectId(campaign_id)})
        campaign_name = campaign_doc.get("name", "Options Volatility Master") if campaign_doc else "CrowdWisdom Trading"
        target_country = (
            input_data.get("target_country")
            or (campaign_doc.get("target_country") if campaign_doc else None)
            or (campaign_doc.get("audience", {}).get("target_country") if campaign_doc else None)
            or "IN"
        )
        if target_country == "BOTH":
            target_country = "IN"

        # Build dynamic market intelligence context
        market_ctx = {}
        market_prompt_directive = ""
        try:
            market_ctx = await market_context_builder.build_context(
                country_code=target_country,
                audience_config=campaign_config.get("audience", {}) or (campaign_doc.get("audience", {}) if campaign_doc else {}),
                include_live_research=True,
                research_limit=4
            )
            market_prompt_directive = market_ctx.get("agent_directives", {}).get("script_agent", "")
        except Exception as mc_err:
            logger.warning(f"[ScriptAgent] Market context notice: {mc_err}")

        # Update script status
        await db.scripts.update_one(
            {"_id": ObjectId(script_id)},
            {"$set": {"status": "generating", "target_country": target_country, "updated_at": datetime.now(timezone.utc)}}
        )

        # --- Load credentials ---
        await self._log_progress("initializing", "Loading API credentials...", 5)

        gemini_key = await get_decrypted_api_key("gemini")
        nvidia_key = await get_decrypted_api_key("nvidia_nim")
        openrouter_key = await get_decrypted_api_key("openrouter")

        if gemini_key:
            llm_key = gemini_key
            llm_provider = "gemini"
            llm_model = "gemini-2.5-flash"
        elif nvidia_key:
            llm_key = nvidia_key
            llm_provider = "nvidia_nim"
            llm_model = "nvidia/nemotron-3.5-bolt-e4b"
        else:
            llm_key = openrouter_key
            llm_provider = "openrouter"
            llm_model = "meta-llama/llama-3.3-70b-instruct"

        tavily_key = await get_decrypted_api_key("tavily")
        exa_key = await get_decrypted_api_key("exa")

        if not llm_key:
            msg = "No LLM provider configured. Please add Gemini, NVIDIA NIM, or OpenRouter credentials in Settings."
            await db.scripts.update_one(
                {"_id": ObjectId(script_id)},
                {"$set": {"status": "failed", "error_message": msg}}
            )
            raise ValueError(msg)

        llm = LLMClient(api_key=llm_key, provider=llm_provider, model=llm_model)

        # Initialize official Hermes AIAgent if OpenRouter is available
        hermes_initialized = False
        if llm_provider == "openrouter":
            hermes_initialized = await self._initialize_hermes(
                model="meta-llama/llama-3.3-70b-instruct",
                api_key=llm_key,
                enabled_toolsets=["crowdwisdom_script", "crowdwisdom"]
            )
            if hermes_initialized:
                self._execution_mode = "native_hermes"
                try:
                    import importlib
                    tools_reg_mod = importlib.import_module("tools.registry")
                    registry = getattr(tools_reg_mod, "registry")
                    def _platform_features_tool(args, **kw):
                        return "CrowdWisdom Verified Features: CrowdPulse, Weekly/Daily Wisdom, CrowdMap, Pro Crowd Bars."
                    registry.register(
                        name="get_crowdwisdom_verified_features",
                        toolset="crowdwisdom_script",
                        schema={
                            "name": "get_crowdwisdom_verified_features",
                            "description": "Retrieves verified CrowdWisdomTrading platform feature definitions",
                            "parameters": {"type": "object", "properties": {}}
                        },
                        handler=_platform_features_tool,
                        override=True
                    )
                except Exception as reg_err:
                    logger.debug(f"Hermes script tool registration notice: {reg_err}")
            else:
                self._execution_mode = "llm_fallback"
        else:
            self._execution_mode = "llm_fallback"

        # --- Gather research context based on approach ---
        research_context = ""
        research_references = []

        if approach == "pain_point":
            research_context, research_references = await self._research_pain_points(
                tavily_key, exa_key, country=target_country
            )
        elif approach == "unique_data":
            research_context = await self._gather_product_data(db, campaign_id)
        elif approach == "product_value":
            research_context = await self._research_product_value(exa_key)

        # Inject country market profile and regulatory directives
        if market_prompt_directive:
            research_context = f"{market_prompt_directive}\n\n{research_context}"

        # Ingest ground-truth market research evidence into references
        for ev in market_ctx.get("research_evidence", []):
            if ev.get("source_url") and ev.get("source_url") not in research_references:
                research_references.append(f"[{ev.get('publisher')}]: {ev.get('finding')[:120]}... ({ev.get('source_url')})")

        # --- Fetch existing ad research for context ---
        await self._log_progress("loading_research", "Loading ad research intelligence...", 25)
        
        # 1. Fetch campaign-specific ads & insights
        campaign_ads = await db.advertisements.find({
            "$or": [{"campaign_id": campaign_id}, {"associated_campaign_ids": campaign_id}]
        }).sort([("evaluation_score.overall", -1), ("published_at", -1)]).to_list(10)

        insights = await db.marketing_insights.find({
            "$or": [{"campaign_id": campaign_id}, {"associated_campaign_ids": campaign_id}]
        }).sort("confidence", -1).to_list(10)

        # 2. Resilient research inheritance: If no campaign-specific ads exist yet, pull top verified ads & insights
        # from platform research repository so scripts are ALWAYS backed by real Meta Ads research
        if not campaign_ads:
            logger.info(f"[ScriptAgent] No direct ads associated with campaign {campaign_id}. Inheriting top verified ads from Meta Ads repository.")
            campaign_ads = await db.advertisements.find({
                "date_verification_status": "verified"
            }).sort([("evaluation_score.overall", -1), ("published_at", -1)]).to_list(6)
            if not campaign_ads:
                campaign_ads = await db.advertisements.find({}).sort("evaluation_score.overall", -1).to_list(6)

        if not insights:
            logger.info(f"[ScriptAgent] Inheriting global verified marketing insights for campaign {campaign_id}.")
            insights = await db.marketing_insights.find({}).sort("confidence", -1).to_list(10)

        # 3. Format competitor ads & insights into human-readable research intelligence for the LLM
        competitor_ads_context = []
        ad_references = []
        for ad in campaign_ads:
            advertiser = ad.get("advertiser", "Unknown Competitor")
            hook = ad.get("hook") or "N/A"
            angle = ad.get("marketing_angle") or "N/A"
            pain = ad.get("pain_point") or "N/A"
            score = ad.get("evaluation_score", {}).get("overall", 8.0) if isinstance(ad.get("evaluation_score"), dict) else 8.0
            meta_url = ad.get("meta_ads_url") or f"https://www.facebook.com/ads/library/?id={ad.get('ad_id', '')}"

            competitor_ads_context.append({
                "advertiser": advertiser,
                "hook": hook,
                "marketing_angle": angle,
                "pain_point": pain,
                "overall_score": score,
                "source_url": meta_url
            })
            ad_references.append(f"Meta Ad [{advertiser}]: \"{hook}\" — {meta_url}")

        insights_text = json.dumps(
            [{"category": i["category"], "title": i["title"], "description": i["description"]}
             for i in insights],
            indent=2
        ) if insights else "No prior insights available."

        ads_text = json.dumps(competitor_ads_context, indent=2) if competitor_ads_context else "No competitor ads available."

        # Merge references
        research_references = list(dict.fromkeys(research_references + ad_references))

        # --- Stage 1 & 2: Two-Stage Creative Pipeline with Similarity Validation ---
        await self._log_progress("generating", f"Synthesizing dynamic {approach} creative concept...", 40)

        audience = campaign_config.get("audience", {})
        audience_desc = ", ".join(audience.get("segments", ["retail traders"]))
        duration = campaign_config.get("video_duration_seconds", 45)

        # Retrieve existing campaign scripts to enforce negative constraints and similarity bounds
        existing_scripts = await db.scripts.find({"campaign_id": campaign_id}).to_list(30)
        logger.info(f"[ScriptAgent] Found {len(existing_scripts)} existing scripts for campaign {campaign_id}")

        script_data = None
        rejected_concepts = []
        max_similarity_threshold = 0.45

        try:
            for attempt in range(1, 4):
                try:
                    await self._log_progress("ideating", f"Ideating distinct concept (attempt {attempt}/3)...", 40 + attempt * 7)
                    # Stage 1: Creative Concept Ideation
                    concept = await self._generate_creative_concept(
                        llm=llm,
                        campaign_name=campaign_name,
                        approach=approach,
                        target_audience=audience_desc,
                        duration=duration,
                        research_context=research_context,
                        ads_text=ads_text,
                        insights_text=insights_text,
                        custom_prompt=custom_prompt,
                        existing_scripts=existing_scripts,
                        rejected_concepts=rejected_concepts,
                    )

                    if not concept or not isinstance(concept, dict) or not concept.get("concept_title"):
                        logger.warning(f"[ScriptAgent] Stage 1 returned incomplete concept on attempt {attempt}")
                        continue

                    await self._log_progress("screenwriting", f"Drafting screenplay for '{concept.get('concept_title')}'...", 60)
                    # Stage 2: Screenplay Generation from Concept
                    raw_script = await self._generate_screenplay_from_concept(
                        llm=llm,
                        concept=concept,
                        approach=approach,
                        duration=duration,
                        campaign_config=campaign_config,
                    )

                    # Validate and normalize screenplay
                    is_valid, normalized_script, val_errors = self._validate_and_normalize_script(
                        raw_script, approach, duration, campaign_config
                    )

                    if not is_valid and (not normalized_script.get("scenes") or len(normalized_script["scenes"]) < 3):
                        logger.warning(f"Screenplay validation failed on attempt {attempt}: {val_errors}")
                        continue

                    # Calculate multi-dimensional similarity against existing scripts
                    sim_score, sim_title, breakdown = calculate_script_similarity(normalized_script, existing_scripts)
                    logger.info(
                        f"[ScriptAgent] Attempt {attempt} Candidate '{normalized_script.get('campaign_title')}' "
                        f"similarity: {sim_score:.1%} against '{sim_title}' (Breakdown: {breakdown})"
                    )

                    if sim_score > max_similarity_threshold:
                        logger.warning(
                            f"[ScriptAgent] Candidate script '{normalized_script.get('campaign_title')}' rejected "
                            f"due to {sim_score:.1%} similarity with existing '{sim_title}'. Retrying with negative constraint..."
                        )
                        rejected_concepts.append(concept)
                        continue

                    # Candidate accepted!
                    logger.info(f"[ScriptAgent] Candidate script '{normalized_script.get('campaign_title')}' approved with {sim_score:.1%} similarity.")
                    script_data = normalized_script
                    break

                except Exception as attempt_err:
                    logger.warning(f"[ScriptAgent] Generation attempt {attempt} error: {attempt_err}")

            # If LLM failed or all attempts rejected, fallback to deterministic domain synthesizer
            if not script_data or not isinstance(script_data, dict):
                logger.info(f"[ScriptAgent] Synthesizing script narrative via CrowdWisdom Domain Intelligence Synthesizer for {target_country}...")
                script_data = self._generate_fallback_script(
                    approach=approach,
                    duration=duration,
                    campaign_config=campaign_config,
                    campaign_id=str(campaign_id),
                    campaign_name=campaign_name,
                    existing_scripts=existing_scripts,
                    target_country=target_country,
                )
                _, script_data, _ = self._validate_and_normalize_script(
                    script_data, approach, duration, campaign_config
                )

        except Exception as e:
            logger.error(f"Script generation failed: {e}")
            await db.scripts.update_one(
                {"_id": ObjectId(script_id)},
                {"$set": {"status": "failed", "error_message": str(e)}}
            )
            raise

        # --- Pre-generate scene visual assets ---
        await self._log_progress("generating_visuals", "Generating scene-specific visual assets...", 80)
        from services.visual_asset_service import visual_asset_service
        aspect_ratio = campaign_config.get("video_aspect_ratio", "9:16")
        enhanced_scenes = await visual_asset_service.ensure_script_visual_assets(
            script_doc={
                "_id": script_id,
                "campaign_id": str(campaign_id),
                "scenes": script_data["scenes"],
                "campaign_title": script_data["campaign_title"],
                "approach": approach,
                "target_country": target_country,
            },
            aspect_ratio=aspect_ratio,
        )
        for sc in enhanced_scenes:
            sc["target_country"] = target_country
        script_data["scenes"] = enhanced_scenes

        # --- Validate compliance against regulatory standards (SEBI / SEC Philippines) ---
        full_script_text = f"{script_data.get('campaign_title', '')} {script_data.get('core_message', '')} {script_data.get('voiceover_full', '')}"
        compliance_report = compliance_validator.validate_content(
            country_code=target_country,
            text_content=full_script_text,
            content_type="script"
        )
        logger.info(f"[ScriptAgent] Script compliance score for {target_country}: {compliance_report['compliance_score']}/10.0 (Compliant: {compliance_report['is_compliant']})")

        # --- Save validated script to MongoDB ---
        await self._log_progress("saving", "Saving verified script storyboard to database...", 90)

        update_data = {
            "campaign_title": script_data["campaign_title"],
            "title": script_data["campaign_title"],
            "target_country": target_country,
            "compliance_report": compliance_report,
            "target_audience": script_data["target_audience"],
            "pain_point": script_data["pain_point"],
            "marketing_angle": script_data["marketing_angle"],
            "core_message": script_data["core_message"],
            "unique_selling_proposition": script_data["unique_selling_proposition"],
            "emotional_direction": script_data["emotional_direction"],
            "visual_hook": script_data["visual_hook"],
            "full_script": script_data["full_script"],
            "scenes": script_data["scenes"],
            "voiceover_full": script_data["voiceover_full"],
            "on_screen_texts": script_data["on_screen_texts"],
            "music_direction": script_data["music_direction"],
            "sound_effects": script_data["sound_effects"],
            "call_to_action": script_data["call_to_action"],
            "estimated_duration_seconds": script_data["estimated_duration_seconds"],
            "research_references": research_references,
            "supporting_evidence": script_data["supporting_evidence"],
            "status": "pending_approval",  # Checkpoint 2: Ready for human review
            "version": 1,
            "updated_at": datetime.now(timezone.utc),
        }

        await db.scripts.update_one(
            {"_id": ObjectId(script_id)},
            {"$set": update_data}
        )

        await self._log_progress("done", "Script generated and awaiting approval.", 100)

        return {
            "script_id": script_id,
            "campaign_title": script_data["campaign_title"],
            "approach": approach,
            "scenes_count": len(script_data["scenes"]),
            "status": "pending_approval",
            "execution_mode": self._execution_mode,
        }

    async def _generate_creative_concept(
        self,
        llm: LLMClient,
        campaign_name: str,
        approach: str,
        target_audience: str,
        duration: int,
        research_context: str,
        ads_text: str,
        insights_text: str,
        custom_prompt: Optional[str],
        existing_scripts: List[Dict[str, Any]],
        rejected_concepts: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Stage 1: Dynamic Creative Concept Ideator.
        Generates an original advertising premise, sensory hook, and narrative angle.
        Enforces negative constraints against existing campaign scripts to guarantee genuine diversity.
        """
        existing_titles = [
            s.get("campaign_title") or s.get("title") for s in existing_scripts
            if (s.get("campaign_title") or s.get("title"))
        ]
        existing_hooks = [
            s.get("visual_hook") for s in existing_scripts
            if s.get("visual_hook")
        ]

        forbidden_titles_str = "\n".join([f"- {t}" for t in existing_titles[:8]]) if existing_titles else "None yet."
        forbidden_hooks_str = "\n".join([f"- {h}" for h in existing_hooks[:5]]) if existing_hooks else "None yet."

        rejected_str = ""
        if rejected_concepts:
            rejected_str = "\nPREVIOUSLY REJECTED CONCEPTS (DO NOT REPEAT):\n" + "\n".join([
                f"- Rejected Title: {rc.get('concept_title', '')} (Thesis: {rc.get('creative_thesis', '')})"
                for rc in rejected_concepts
            ])

        approach_archetype_rules = {
            "pain_point": (
                "Focus on visceral trader friction and emotional exhaustion: "
                "costly mistakes from following viral social media influencers, "
                "the anxiety of 6:30 AM pre-market analysis paralysis, "
                "getting trapped as exit liquidity, or second-guessing high-stakes trades."
            ),
            "unique_data": (
                "Focus on structural market asymmetry and proprietary intelligence: "
                "CrowdMap resting liquidity zones, 30-day sentiment shifts, "
                "sentiment divergence before major reversals, or contrasting obsolete "
                "1978 lagging indicators (RSI/MACD) with real-time crowd velocity."
            ),
            "product_value": (
                "Focus on institutional execution clarity and actionable workflows: "
                "Daily and Weekly Wisdom consensus trade plans with verified entry and stop levels, "
                "Pro Crowd Bars conviction metrics, and streamlined confident execution without second-guessing."
            )
        }

        concept_prompt = f"""You are the Executive Creative Director for CrowdWisdomTrading.
Generate a NEW, ORIGINAL, and HIGH-CONVICTION commercial concept for an institutional-grade fintech advertisement.

CAMPAIGN: {campaign_name}
APPROACH: {approach.upper()}
AUDIENCE: {target_audience}
DURATION: {duration} seconds

APPROACH CREATIVE DIRECTIVE:
{approach_archetype_rules.get(approach, "High-conviction fintech commercial")}

RESEARCH INTELLIGENCE CONTEXT:
{research_context[:800]}

MARKETING INSIGHTS:
{insights_text[:600]}

{f'SPECIAL USER INSTRUCTIONS: {custom_prompt}' if custom_prompt else ''}

STRICT NEGATIVE CONSTRAINTS (DO NOT REPEAT ANY OF THESE):
1. FORBIDDEN TITLES (Already used in this campaign):
{forbidden_titles_str}
Do NOT use titles containing "The Signal in the Noise", "Signal in the Noise", "Finding Your Signal", or close variations.

2. FORBIDDEN VISUAL HOOKS (Already used in this campaign):
{forbidden_hooks_str}
Do NOT use chrome spheres, floating metallic balls, or generic swirling digital data storms.

3. FORBIDDEN OVERUSED SLOGANS:
- "Stop drowning in a sea of conflicting information"
- "Noise vs Signal" / "Signal in the noise"
- "BUY NOW! DUMP IT! FED HAWKISH? TO THE MOON!"

{rejected_str}

Produce a completely original creative concept in valid JSON:
{{
  "concept_title": "Distinct, provocative commercial title (max 6 words)",
  "creative_thesis": "Counter-intuitive advertising premise in 1 sentence",
  "narrative_angle": "The storytelling mechanism (e.g. Confession, Morning Routine, Microstructure, Contrarian, Volatility)",
  "sensory_hook": "Specific, visceral 3-second opening cinematic visual and sound design",
  "emotional_arc": "Progression from initial tension/doubt to disciplined clarity",
  "visual_composition_style": "Specific lighting, physical environment (e.g. dawn apartment, modern terrace, trading floor), and camera lenses",
  "pain_point": "The authentic trading problem addressed",
  "core_message": "Clear, memorable core message for retail traders",
  "call_to_action": "High-conviction call to action"
}}"""

        messages = [
            {"role": "system", "content": SCRIPT_SYSTEM_PROMPT},
            {"role": "user", "content": concept_prompt}
        ]
        return await llm.chat_json(messages=messages, temperature=0.75)

    async def _generate_screenplay_from_concept(
        self,
        llm: LLMClient,
        concept: Dict[str, Any],
        approach: str,
        duration: int,
        campaign_config: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Stage 2: Cinematic Screenplay Generator.
        Converts the dynamic creative concept specification into a 4-scene cinematic screenplay.
        Enforces explicit scene_visual_type and strict typographic rules on on_screen_text.
        """
        per_scene = max(4, duration // 4)

        screenplay_prompt = f"""You are an award-winning commercial director and screenwriter.
Transform the following approved Creative Concept into a full 4-scene cinematic advertisement screenplay.

APPROVED CREATIVE CONCEPT:
- Title: {concept.get('concept_title', 'Market Clarity')}
- Thesis: {concept.get('creative_thesis', '')}
- Narrative Angle: {concept.get('narrative_angle', '')}
- Opening Hook: {concept.get('sensory_hook', '')}
- Emotional Arc: {concept.get('emotional_arc', '')}
- Visual Style: {concept.get('visual_composition_style', '')}
- Core Message: {concept.get('core_message', '')}
- Call to Action: {concept.get('call_to_action', 'CrowdWisdomTrading.com')}

TARGET DURATION: {duration} seconds (approximately 4 scenes, {per_scene}s each)

CRITICAL PRODUCTION RULES:
1. DIVERSE & BALANCED SCENE VISUAL TYPES:
   To create a compelling, dynamic commercial (not a repetitive slideshow), you MUST vary "scene_visual_type" across scenes:
   - "human_cinematography": Genuine real-world humans in professional environments (trader at workstation, dawn skyline, hands typing on mechanical keyboard, high-rise office). Recommended for Scene 1 (Hook) and/or Scene 4 (Resolution).
   - "product_demo": Sleek user interface demonstrations of CrowdWisdom features (CrowdPulse™ Radar, Pro Crowd Bars, real-time accumulation telemetry, tablet or full-screen UI). REQUIRED for Scene 3 (Discovery/Solution).
   - "animated_chart": Dynamic candlestick charts, volume order-flow skew, sentiment divergence curves, or market volatility metrics. Ideal for Scene 2 (Market Conflict/Chaos).
   DO NOT make all scenes the same type! A great commercial transitions seamlessly between human tension, market data, and proprietary product software intelligence.

2. ON-SCREEN TEXT TYPOGRAPHY (STRICT):
   - Maximum 4 to 6 words per scene.
   - Professional institutional headline style (e.g. "Consensus Entries • Verified Stops" or "-$10,450.00 • The Cost of Hype").
   - ABSOLUTELY ZERO shouting meme caps ("BUY NOW! DUMP IT! FED HAWKISH? TO THE MOON!").
   - Do NOT simply repeat the voiceover text verbatim.

3. AUTHENTIC TRADER VOICEOVER:
   - Natural human dialogue/monologue under 25 words per scene. No corporate jargon.

Generate the complete screenplay in valid JSON:
{{
  "campaign_title": "{concept.get('concept_title', 'Market Clarity')}",
  "approach": "{approach}",
  "target_audience": "Active retail traders and investors",
  "pain_point": "{concept.get('pain_point', '')}",
  "marketing_angle": "{concept.get('narrative_angle', '')}",
  "core_message": "{concept.get('core_message', '')}",
  "unique_selling_proposition": "CrowdWisdomTrading verified collective sentiment and consensus",
  "emotional_direction": "{concept.get('emotional_arc', '')}",
  "visual_hook": "{concept.get('sensory_hook', '')}",
  "full_script": "...",
  "scenes": [
    {{
      "scene_number": 1,
      "duration_seconds": {per_scene},
      "scene_visual_type": "human_cinematography",
      "visual_description": "Detailed cinematic lighting, camera lens, human action, setting...",
      "camera_direction": "Slow push-in / tracking shot...",
      "voiceover": "Natural spoken voiceover...",
      "on_screen_text": "Clean 4-6 word headline",
      "audio_direction": "Sound design...",
      "transition": "Smooth cut / cross-dissolve"
    }}
  ],
  "voiceover_full": "...",
  "on_screen_texts": ["..."],
  "music_direction": "Cinematic fintech soundtrack with rhythmic 120 BPM pulse",
  "sound_effects": ["Soft UI click", "Subtle sweep transition"],
  "call_to_action": "{concept.get('call_to_action', 'CrowdWisdomTrading.com')}",
  "estimated_duration_seconds": {duration},
  "supporting_evidence": ["CrowdWisdom collective intelligence platform"]
}}"""

        messages = [
            {"role": "system", "content": SCRIPT_SYSTEM_PROMPT},
            {"role": "user", "content": screenplay_prompt}
        ]
        return await llm.chat_json(messages=messages, temperature=0.6)

    def _validate_and_normalize_script(
        self, script_data: Dict[str, Any], approach: str, duration: int, campaign_config: Dict[str, Any]
    ) -> tuple[bool, Dict[str, Any], List[str]]:
        """
        Validates that generated script meets all production requirements:
        - Mandatory script fields (title, core_message, hook, marketing_angle, call_to_action)
        - Scene-by-scene storyboard (at least 3 scenes)
        - Every scene contains mandatory fields: scene_number, duration, visual_description, camera_direction, voiceover, on_screen_text, audio_direction, transition.
        - Total scene duration is valid and positive.
        """
        errors = []
        if not isinstance(script_data, dict):
            return False, {}, ["LLM output is not a valid JSON object"]

        def _to_clean_str(val, fallback=""):
            if isinstance(val, list):
                return " ".join(str(x) for x in val if x).strip() or fallback
            if val is None:
                return fallback
            return str(val).strip() or fallback

        # 1. Script Title
        title = _to_clean_str(script_data.get("campaign_title") or script_data.get("title"), f"{approach.replace('_', ' ').title()} — The Wisdom of the Crowd")

        # 2. Core Message
        core_message = _to_clean_str(script_data.get("core_message"))
        if not core_message:
            errors.append("Missing core_message")

        # 3. Visual Hook
        visual_hook = _to_clean_str(script_data.get("visual_hook") or script_data.get("hook"), "A chaotic financial ticker flashes red before crystallizing into a calm, pulsing green crowd consensus curve.")

        # 4. Marketing Angle & CTA
        marketing_angle = _to_clean_str(script_data.get("marketing_angle"), f"Transforming retail trading sentiment into actionable market clarity through {approach}.")
        call_to_action = _to_clean_str(script_data.get("call_to_action"), "Join the intelligence revolution today at CrowdWisdomTrading.com.")
        pain_point = _to_clean_str(script_data.get("pain_point"), "Retail traders overwhelmed by conflicting market noise and emotional drawdowns.")
        target_audience = _to_clean_str(script_data.get("target_audience"), "Active retail traders and investors")

        # 5. Scenes Validation & Normalization
        raw_scenes = script_data.get("scenes", [])
        if not isinstance(raw_scenes, list) or len(raw_scenes) < 3:
            errors.append(f"Insufficient storyboard scenes (found {len(raw_scenes) if isinstance(raw_scenes, list) else 0}, minimum 3 required)")

        normalized_scenes = []
        total_dur = 0
        default_dur_per_scene = max(4, duration // max(len(raw_scenes) if isinstance(raw_scenes, list) and len(raw_scenes) > 0 else 4, 1))

        for idx, sc in enumerate(raw_scenes if isinstance(raw_scenes, list) else [], 1):
            if not isinstance(sc, dict):
                continue
            sc_num = sc.get("scene_number", idx)
            raw_dur = sc.get("duration_seconds")
            if raw_dur is not None:
                try:
                    sc_dur = max(3, int(float(str(raw_dur))))
                except (ValueError, TypeError):
                    sc_dur = default_dur_per_scene
            else:
                sc_dur = default_dur_per_scene

            vis_desc = _to_clean_str(sc.get("visual_description"), f"Cinematic financial interface displaying CrowdWisdom market intelligence indicators for scene {idx}.")
            cam_dir = _to_clean_str(sc.get("camera_direction"), "Slow cinematic push-in")
            vo = _to_clean_str(sc.get("voiceover"))
            raw_on_screen = _to_clean_str(sc.get("on_screen_text"))
            on_screen = _clean_on_screen_text(raw_on_screen, sc_num)
            audio_dir = _to_clean_str(sc.get("audio_direction"), "Subtle ambient synthesizer with crisp UI audio haptics")
            transition = _to_clean_str(sc.get("transition"), "Smooth cross-dissolve")

            # Validate and accurately classify scene_visual_type
            vis_type = sc.get("scene_visual_type")
            vis_desc_lower = vis_desc.lower()
            desc_check = (vis_desc + " " + cam_dir + " " + (on_screen or "") + " " + (vo or "")).lower()

            # Pure product interface indicators
            is_dedicated_product_ui = any(k in vis_desc_lower for k in [
                "crowdpulse", "crowdmap", "radar", "radar sweep", "software interface", "platform ui",
                "conviction meter", "pro crowd bar", "accumulation telemetry", "tablet", "ipad", "laptop",
                "hardware_tablet", "hardware_laptop", "fullscreen terminal", "terminal display", "dashboard",
                "sentiment waveform", "consensus curves"
            ])

            # Market data and chart indicators
            is_chart_indicator = any(k in desc_check for k in [
                "candlestick", "candlesticks", "order flow skew", "depth-of-market", "volatility drop",
                "divergence curve", "financial chart", "volume profile", "vix", "rsi", "macd"
            ])

            # Human action indicators for Hook & Resolution scenes
            is_human_scene = any(h in vis_desc_lower for h in [
                "trader", "person", "woman", "man", "hands", "face", "apartment", "rooftop",
                "coffee", "skyline", "office", "street", "terrace", "balcony", "leaning back",
                "looking", "closing", "standing", "boardroom", "walking"
            ])

            if sc_num == 1:
                # Scene 1 is always the cinematic hook: prioritize human cinematography unless purely dedicated UI
                vis_type = "product_demo" if (is_dedicated_product_ui and not is_human_scene) else "human_cinematography"
            elif sc_num == 2:
                # Scene 2 represents the market chaos, divergence, or order flow: dynamic animated chart
                vis_type = "animated_chart"
            elif sc_num == 3:
                # Scene 3 represents the proprietary solution: dynamic CrowdWisdom product demo
                vis_type = "product_demo"
            elif sc_num == 4:
                # Scene 4 represents decisive trader resolution & brand CTA
                vis_type = "human_cinematography"
            else:
                # Supplementary scenes (scene 5+)
                if is_dedicated_product_ui:
                    vis_type = "product_demo"
                elif is_chart_indicator:
                    vis_type = "animated_chart"
                else:
                    vis_type = "human_cinematography"

            if not vo and not on_screen:
                errors.append(f"Scene {idx} missing both voiceover and on-screen text")

            normalized_scenes.append({
                "scene_number": sc_num,
                "duration_seconds": sc_dur,
                "scene_visual_type": vis_type,
                "visual_description": vis_desc,
                "camera_direction": cam_dir,
                "voiceover": vo,
                "on_screen_text": on_screen,
                "audio_direction": audio_dir,
                "transition": transition,
                "asset_references": sc.get("asset_references", [])
            })
            total_dur += sc_dur

        # Enforce narrative & visual diversity across scenes (Prevent multiple scenes being identical product_demo)
        product_demos = [sc for sc in normalized_scenes if sc["scene_visual_type"] == "product_demo"]
        if len(product_demos) > 1:
            # Preserve Scene 3 (or the primary solution discovery scene) as the sole dedicated product demo
            prime_demo_num = 3 if any(sc["scene_number"] == 3 for sc in product_demos) else product_demos[0]["scene_number"]
            for sc in normalized_scenes:
                if sc["scene_visual_type"] == "product_demo" and sc["scene_number"] != prime_demo_num:
                    if sc["scene_number"] in [1, 4]:
                        sc["scene_visual_type"] = "human_cinematography"
                    else:
                        sc["scene_visual_type"] = "animated_chart"

        # Ensure storyboard scene durations strictly align to campaign target duration
        if normalized_scenes and abs(total_dur - duration) > 2:
            scale_factor = duration / max(total_dur, 1)
            new_total = 0
            for sc in normalized_scenes:
                sc["duration_seconds"] = max(3, round(sc["duration_seconds"] * scale_factor))
                new_total += sc["duration_seconds"]
            diff = duration - new_total
            normalized_scenes[-1]["duration_seconds"] = max(3, normalized_scenes[-1]["duration_seconds"] + diff)
            total_dur = duration

        if len(normalized_scenes) < 3:
            errors.append("Storyboard must have at least 3 valid scenes")

        normalized_script = {
            "campaign_title": title,
            "approach": approach,
            "target_audience": target_audience,
            "pain_point": pain_point,
            "marketing_angle": marketing_angle,
            "core_message": core_message or "Trade with clarity and verified crowd intelligence at CrowdWisdomTrading.com.",
            "unique_selling_proposition": _to_clean_str(script_data.get("unique_selling_proposition"), "CrowdWisdomTrading collective sentiment and prediction consensus"),
            "emotional_direction": _to_clean_str(script_data.get("emotional_direction"), "From market noise to calm mathematical clarity"),
            "visual_hook": visual_hook,
            "full_script": _to_clean_str(script_data.get("full_script"), " ".join([s["voiceover"] for s in normalized_scenes if s.get("voiceover")])),
            "scenes": normalized_scenes,
            "voiceover_full": _to_clean_str(script_data.get("voiceover_full"), " ".join([s["voiceover"] for s in normalized_scenes if s.get("voiceover")])),
            "on_screen_texts": script_data.get("on_screen_texts") if isinstance(script_data.get("on_screen_texts"), list) else [s["on_screen_text"] for s in normalized_scenes if s.get("on_screen_text")],
            "music_direction": _to_clean_str(script_data.get("music_direction"), "Modern atmospheric synth score with propulsive percussion"),
            "sound_effects": script_data.get("sound_effects") if isinstance(script_data.get("sound_effects"), list) else ["Soft UI click", "Subtle sweep transition"],
            "call_to_action": call_to_action,
            "estimated_duration_seconds": total_dur or duration,
            "supporting_evidence": script_data.get("supporting_evidence") if isinstance(script_data.get("supporting_evidence"), list) else []
        }

        is_valid = len(errors) == 0
        return is_valid, normalized_script, errors

    async def _research_pain_points(
        self, tavily_key: Optional[str], exa_key: Optional[str], country: str = "IN"
    ) -> tuple[str, List[str]]:
        """Research trading pain points via Tavily/Exa with country-specific queries."""
        norm_country = country.upper().strip() if country else "IN"
        c_label = "India" if norm_country == "IN" else "Philippines"
        await self._log_progress("researching", f"Researching {c_label} trader pain points...", 15)

        results_text = ""
        references = []

        if tavily_key:
            try:
                tavily = TavilyClient(tavily_key)
                if norm_country == "PH":
                    q = "Philippine stock market retail investors trading noise sentiment"
                else:
                    q = "India retail options trading SEBI sentiment noise"
                res = await tavily.search(q, max_results=5, days=30)
                for r in res.get("results", []):
                    results_text += f"\n- {r.get('title', '')}: {r.get('content', '')[:300]}"
                    if r.get("url"):
                        references.append(r["url"])
                logger.info(f"Tavily returned {len(res.get('results', []))} pain point results for {c_label}")
            except Exception as e:
                logger.warning(f"Tavily research failed: {e}")

        if exa_key and not results_text:
            try:
                exa = ExaClient(exa_key)
                topic = f"{c_label} retail trader frustrations challenges market noise"
                results = await exa.find_content_opportunities(topic, days_back=30)
                for r in results[:6]:
                    results_text += f"\n- {r.get('title', '')}: {(r.get('text') or '')[:300]}"
                    if r.get("url"):
                        references.append(r["url"])
            except Exception as e:
                logger.warning(f"Exa research failed: {e}")

        if not results_text:
            results_text = """
Research unavailable (no search provider configured). Using product knowledge context:
- Retail traders face information overload from conflicting analyst opinions
- Difficulty determining genuine market consensus vs. noise
- Decision paralysis from too many trading signals
- Frustration with traditional technical analysis in volatile markets
"""

        return results_text, references[:10]

    async def _gather_product_data(self, db, campaign_id: str) -> str:
        """Gather CrowdWisdomTrading product intelligence from database and known facts."""
        insights = await db.marketing_insights.find({"campaign_id": campaign_id}).to_list(10)
        ads_sample = await db.advertisements.find({"campaign_id": campaign_id}).limit(5).to_list(5)

        context = CROWDWISDOM_PRODUCT_CONTEXT
        if insights:
            context += f"\n\nMARKETING INTELLIGENCE:\n{json.dumps([i['title'] for i in insights], indent=2)}"
        return context

    async def _research_product_value(self, exa_key: Optional[str]) -> str:
        """Research CrowdWisdomTrading's product positioning."""
        context = CROWDWISDOM_PRODUCT_CONTEXT

        if exa_key:
            try:
                exa = ExaClient(exa_key)
                results = await exa.find_content_opportunities(
                    "crowd wisdom trading market sentiment collective intelligence", days_back=90
                )
                for r in results[:5]:
                    context += f"\n- {r.get('title', '')}: {(r.get('text') or '')[:200]}"
            except Exception as e:
                logger.warning(f"Exa product research failed: {e}")

        return context

    def _generate_fallback_script(
        self,
        approach: str,
        duration: int,
        campaign_config: Dict[str, Any],
        campaign_id: str = "",
        campaign_name: str = "",
        existing_scripts: Optional[List[Dict[str, Any]]] = None,
        target_country: str = "IN",
    ) -> Dict[str, Any]:
        """
        Synthesizes a high-fidelity cinematic commercial screenplay selected from a diverse
        library of creative archetypes. Ensures zero repetitive clichés across campaigns.
        Dynamically adapts terminology, currencies, and regulatory disclosures to target country (India vs Philippines).
        """
        per_scene = max(4, duration // 4)
        remainder = duration - (per_scene * 4)

        # Seed selection by campaign and approach to ensure deterministic diversity
        seed_str = f"{campaign_id}_{campaign_name}_{approach}_{duration}"
        seed_int = int(hashlib.md5(seed_str.encode()).hexdigest(), 16)

        # -------------------------------------------------------------
        # ARCHETYPE POOL (7 Distinct Prestige Commercial Screenplays)
        # -------------------------------------------------------------

        # Archetype 1: Confession / Risk ("The $10,000 Mistake")
        archetype_confession = {
            "title": f"The $10,000 Mistake — {campaign_name or 'Alpha Trader'}",
            "core": "Following viral financial influencers cost retail traders millions. CrowdWisdom replaces social media hype with mathematically verified collective conviction.",
            "pain_point": "Trading on unverified social media hype and emotional panic",
            "marketing_angle": "Contrasting influencer exit liquidity with verified crowd conviction",
            "hook": "A dimly lit room illuminated only by an iPad showing an active -$10,450 options loss in flashing red.",
            "scenes": [
                {
                    "scene_number": 1,
                    "duration_seconds": per_scene,
                    "visual_description": "Cinematic close-up of a trader's hands holding an iPad in a dimly lit studio apartment, showing an active -$10,450 drawdown on a volatile earnings trade.",
                    "camera_direction": "Slow push-in racking focus from trembling hands to the red drawdown figures",
                    "voiceover": "I followed the top financial influencer into an earnings play. Ten thousand dollars vanished in four minutes.",
                    "on_screen_text": "-$10,450.00 • The Cost of Trading Social Media Hype",
                    "audio_direction": "Subtle deep bass heartbeat with muted room tone",
                    "transition": "Fast motion blur wipe"
                },
                {
                    "scene_number": 2,
                    "duration_seconds": per_scene,
                    "visual_description": "Kinetic split-screen comparing a frantic influencer hype video with real institutional order book data dumping shares on retail.",
                    "camera_direction": "Dynamic horizontal whip pan across contradictory social media alerts",
                    "voiceover": "They weren't sharing research. They were using retail excitement as exit liquidity for their own positions.",
                    "on_screen_text": "The Brutal Reality: Retail Hype is Exit Liquidity",
                    "audio_direction": "Distorted social media notifications cutting to sharp silence",
                    "transition": "Clean vertical split wipe"
                },
                {
                    "scene_number": 3,
                    "duration_seconds": per_scene,
                    "visual_description": "Clean macro tracking shot of the CrowdWisdom CrowdMap dashboard showing real-time crowd sentiment divergence and verified trader consensus.",
                    "camera_direction": "Gliding camera move across cyan-emerald conviction heatmaps and support lines",
                    "voiceover": "That's when I found CrowdWisdom. Not one person's opinion, but the verified consensus of thousands of disciplined traders.",
                    "on_screen_text": "CrowdMap™: Verified Collective Conviction",
                    "audio_direction": "Crisp harmonic synthesizer chord with clean UI haptic chime",
                    "transition": "Cross-dissolve with light bloom"
                },
                {
                    "scene_number": 4,
                    "duration_seconds": per_scene + remainder,
                    "visual_description": "The trader closing the iPad, leaning back with calm confidence in a bright modern office overlooking the city skyline at dawn.",
                    "camera_direction": "Cinematic pull-back revealing calm clarity and CrowdWisdom beacon",
                    "voiceover": "Stop being someone else's exit liquidity. Trade with verified crowd clarity at CrowdWisdomTrading.com.",
                    "on_screen_text": "CrowdWisdomTrading.com — Trade with Collective Clarity",
                    "audio_direction": "Inspiring synth brass swell into clean branded out-cue",
                    "transition": "Fade to brand card"
                }
            ]
        }

        # Archetype 2: High-Efficiency Workflow ("The 60-Second Morning Protocol")
        archetype_routine = {
            "title": f"The 60-Second Morning Protocol — {campaign_name or 'Market Edge'}",
            "core": "Stop wasting two hours every morning reading 40 contradictory newsletters. CrowdPulse summarizes true market sentiment in 60 seconds.",
            "pain_point": "Information overload and pre-market analysis fatigue",
            "marketing_angle": "High-efficiency pre-market routine with CrowdPulse sentiment intelligence",
            "hook": "Stream of rich dark espresso pouring into a ceramic cup at 6:30 AM next to an ultra-clean trading desk.",
            "scenes": [
                {
                    "scene_number": 1,
                    "duration_seconds": per_scene,
                    "visual_description": "Atmospheric dawn lighting cutting through modern blinds onto a pristine minimalist trading desk with steam rising from a black ceramic coffee mug.",
                    "camera_direction": "Low-angle slider shot revealing a clutter-free desk and single ultra-wide monitor",
                    "voiceover": "Most retail traders burn two hours before market open skimming forty contradictory newsletters. I take sixty seconds.",
                    "on_screen_text": "06:30 AM • The Modern Pre-Market Protocol",
                    "audio_direction": "Gentle acoustic morning ambience with subtle clock tick",
                    "transition": "Smooth directional slide"
                },
                {
                    "scene_number": 2,
                    "duration_seconds": per_scene,
                    "visual_description": "Over-the-shoulder view of the trader opening CrowdWisdom's CrowdPulse radar, tracking thirty-day sentiment shifts and overnight momentum spikes.",
                    "camera_direction": "Smooth tracking shot across glowing volatility indicators and ticker clusters",
                    "voiceover": "CrowdPulse filters hundreds of thousands of market discussions down to two metrics: aggregate conviction and momentum shifts.",
                    "on_screen_text": "CrowdPulse™: 30-Day Sentiment Shifts at a Glance",
                    "audio_direction": "Warm analog synth swell with rhythmic electronic pulse",
                    "transition": "Light bloom cross-fade"
                },
                {
                    "scene_number": 3,
                    "duration_seconds": per_scene,
                    "visual_description": "Close-up of the trader's calm eyes reflecting green conviction bars, identifying an asymmetric risk-reward setup in seconds.",
                    "camera_direction": "Subtle push-in on the monitor showing consensus entry and stop-loss levels",
                    "voiceover": "In one glance, I know where smart capital is positioned, where stops are clustered, and where retail sentiment is diverging.",
                    "on_screen_text": "Consensus Entries • Verified Stop-Loss Levels",
                    "audio_direction": "Resonant synth bass pulse with crisp haptic tone",
                    "transition": "Geometric digital wipe"
                },
                {
                    "scene_number": 4,
                    "duration_seconds": per_scene + remainder,
                    "visual_description": "The trader taking a relaxed sip of coffee and clicking 'Execute' on his brokerage without hesitation or anxiety.",
                    "camera_direction": "Elegant tilt-up to the CrowdWisdom brand beacon and morning sunlight",
                    "voiceover": "Reclaim your mornings. Reclaim your trading edge. Start at CrowdWisdomTrading.com.",
                    "on_screen_text": "CrowdWisdomTrading.com — Institutional Speed for Retail",
                    "audio_direction": "Confident orchestral-synth cadence to clean finish",
                    "transition": "Fade to brand logo"
                }
            ]
        }

        # Archetype 3: Whistleblower / Microstructure ("The Noise Trap")
        archetype_whistleblower = {
            "title": f"The Noise Trap — {campaign_name or 'Institutional Intel'}",
            "core": "Financial media and news channels are built to trigger emotional overtrading. CrowdWisdom cuts through the noise with quantitative crowd metrics.",
            "pain_point": "Sensationalized financial news driving costly emotional overtrading",
            "marketing_angle": "Exposing retail noise traps and replacing them with Pro Crowd conviction",
            "hook": "Close-up macro of an intense trader's hands typing rapidly at a trading workstation amidst flashing sell-off candlestick monitors and conflicting alerts.",
            "scenes": [
                {
                    "scene_number": 1,
                    "duration_seconds": per_scene,
                    "visual_description": "Close-up macro of an intense trader's hands typing rapidly at a trading workstation amidst flashing sell-off candlestick monitors and conflicting financial news alerts.",
                    "camera_direction": "Fast vertigo zoom zooming in while dollying out on chaotic screens",
                    "voiceover": "Market makers love retail chaos. The more conflicting alerts you receive, the more emotional mistakes you make.",
                    "on_screen_text": "Conflicting Newsfeeds = Emotional Drawdowns",
                    "audio_direction": "Tense low-frequency drone with rapid ticker clicks",
                    "transition": "Fast motion blur wipe"
                },
                {
                    "scene_number": 2,
                    "duration_seconds": per_scene,
                    "visual_description": "Professional quantitative analyst in a modern glass office intently studying live multi-monitor order flow skew, depth-of-market histograms, and institutional consensus charts.",
                    "camera_direction": "Cinematic drone glide between towering glass financial skyscrapers at dusk",
                    "voiceover": "Institutional algorithms don't read sensational headlines. They measure aggregate crowd conviction and order flow skew.",
                    "on_screen_text": "Don't Trade the News. Trade Collective Conviction.",
                    "audio_direction": "Crescendo of distorted audio chatter cutting to dead silence",
                    "transition": "Clean vertical split wipe"
                },
                {
                    "scene_number": 3,
                    "duration_seconds": per_scene,
                    "visual_description": "Extreme close-up on modern tablet device on an executive desk displaying the CrowdPulse institutional conviction radar, oscillating sentiment waveforms, and live accumulation telemetry.",
                    "camera_direction": "Smooth linear pan across clean emerald and cyan consensus curves",
                    "voiceover": "CrowdWisdom's Pro Crowd Bars aggregate real trader expectations, revealing true consensus before the market moves.",
                    "on_screen_text": "Pro Crowd Bars: Real-Time Trader Conviction",
                    "audio_direction": "Crisp harmonic synthesizer chord with clean UI haptic chime",
                    "transition": "Cross-dissolve with light bloom"
                },
                {
                    "scene_number": 4,
                    "duration_seconds": per_scene + remainder,
                    "visual_description": "Professional trader standing calmly by a floor-to-ceiling glass window in a modern financial office overlooking the city skyline at dawn, confident and decisive.",
                    "camera_direction": "Wide cinematic pull-back showing complete serenity in the center of the financial capital",
                    "voiceover": "Stop feeding the noise machine. Trade what the data shows at CrowdWisdomTrading.com.",
                    "on_screen_text": "CrowdWisdomTrading.com — Trade What the Data Shows",
                    "audio_direction": "Triumphant musical resolution",
                    "transition": "Fade to brand logo"
                }
            ]
        }

        # Archetype 4: Quantitative Alpha ("The 1978 Indicator Trap")
        archetype_quant = {
            "title": f"The 1978 Indicator Trap — {campaign_name or 'Modern Alpha'}",
            "core": "Traditional technical indicators like RSI and MACD were invented 50 years ago. CrowdWisdom brings real-time crowd sentiment to modern trading.",
            "pain_point": "Lagging technical indicators that fail in modern algorithmic markets",
            "marketing_angle": "Upgrading from 1970s lagging math to real-time collective sentiment",
            "hook": "Vintage 1970s green monochrome CRT computer terminal flickering with primitive RSI charts, dissolving into a modern financial terminal.",
            "scenes": [
                {
                    "scene_number": 1,
                    "duration_seconds": per_scene,
                    "visual_description": "Macro cinematic shot of an ancient 1970s CRT monitor displaying retro green phosphor RSI and MACD formulas, surrounded by vintage computer reels.",
                    "camera_direction": "Slow macro tracking shot across vintage electronics fading into modern dark glass",
                    "voiceover": "RSI was invented in 1978. MACD in 1979. Why are you still trading 2026 markets with fifty-year-old lagging formulas?",
                    "on_screen_text": "RSI (1978) vs. Modern Collective Intelligence",
                    "audio_direction": "Retro CRT phosphor hum fading into deep electronic pulse",
                    "transition": "Geometric digital dissolve"
                },
                {
                    "scene_number": 2,
                    "duration_seconds": per_scene,
                    "visual_description": "Cinematic transition from vintage CRT to a multi-monitor institutional trading desk displaying real-time 3D crowd positioning heatmaps and volume profiles.",
                    "camera_direction": "Dynamic 360-degree orbital rotation around modern multi-screen trading command desk",
                    "voiceover": "Lagging indicators only tell you where price was yesterday. Price velocity is driven by where collective market participants are positioned today.",
                    "on_screen_text": "Price Lag vs. Real-Time Crowd Positioning",
                    "audio_direction": "Crisp electronic whoosh into rhythmic synth arpeggio",
                    "transition": "Smooth directional slide"
                },
                {
                    "scene_number": 3,
                    "duration_seconds": per_scene,
                    "visual_description": "CrowdWisdom's proprietary sentiment velocity curve leading a major stock breakout forty-eight hours before standard moving averages cross.",
                    "camera_direction": "Smooth push-in on the exact inflection point where crowd conviction surges",
                    "voiceover": "CrowdPulse tracks the velocity of crowd sentiment shifts days before traditional moving averages even register the move.",
                    "on_screen_text": "CrowdPulse™: Early Warning Sentiment Velocity",
                    "audio_direction": "Rhythmic arpeggiated synth building forward momentum",
                    "transition": "Light bloom cross-fade"
                },
                {
                    "scene_number": 4,
                    "duration_seconds": per_scene + remainder,
                    "visual_description": "A quantitative trader reviewing multiple asset classes with calm precision on CrowdWisdom's obsidian dashboard.",
                    "camera_direction": "Cinematic medium shot tilting upward to CrowdWisdom institutional badge",
                    "voiceover": "Stop trading the past. Upgrade to real-time collective intelligence at CrowdWisdomTrading.com.",
                    "on_screen_text": "CrowdWisdomTrading.com — Upgrade to Modern Market Alpha",
                    "audio_direction": "Inspiring synth brass swell into clean branded out-cue",
                    "transition": "Smooth fade to black"
                }
            ]
        }

        # Archetype 5: Contrarian Alpha ("The Contrarian Edge")
        archetype_contrarian = {
            "title": f"The Contrarian Edge — {campaign_name or 'Market Sentiment'}",
            "core": "When 95% of social media is euphoric, the market is usually at the top. CrowdWisdom's sentiment divergence flags dangerous tops and bottoms.",
            "pain_point": "Buying at the top due to retail FOMO and extreme social euphoria",
            "marketing_angle": "Spotting exhaustion tops with proprietary sentiment divergence indicators",
            "hook": "Aerial drone shot looking down at thousands of smartphone screens glowing with green buy orders, while a subtle warning oscillator ticks down.",
            "scenes": [
                {
                    "scene_number": 1,
                    "duration_seconds": per_scene,
                    "visual_description": "Overhead cinematic crane shot of a neon-lit city at night, with digital ticker feeds and glowing mobile screens illuminating the streets.",
                    "camera_direction": "High-angle descent into the heart of the city's financial sector",
                    "voiceover": "When ninety-five percent of social media is screaming buy, the smart money is already planning the exit.",
                    "on_screen_text": "The Euphoria Trap • Extreme Retail Sentiment",
                    "audio_direction": "High-pitched digital buzz with distant urban echo",
                    "transition": "Fast motion blur wipe"
                },
                {
                    "scene_number": 2,
                    "duration_seconds": per_scene,
                    "visual_description": "Split-screen visualization showing a stock price making a fresh high while CrowdWisdom's conviction indicator shows retail enthusiasm collapsing.",
                    "camera_direction": "Lateral camera glide comparing price chart to sentiment divergence curve",
                    "voiceover": "CrowdWisdom's sentiment divergence oscillator flags when price pushes higher, but collective trader conviction has secretly evaporated.",
                    "on_screen_text": "Sentiment Divergence: Spot Tops Before They Hit the Tape",
                    "audio_direction": "Deep harmonic bass foundation with glowing warning chime",
                    "transition": "Clean vertical split wipe"
                },
                {
                    "scene_number": 3,
                    "duration_seconds": per_scene,
                    "visual_description": "A disciplined options trader noticing the divergence signal on CrowdWisdom and executing an asymmetric hedge with zero hesitation.",
                    "camera_direction": "Close-up on trader's focused expression and mouse click confirming trade",
                    "voiceover": "Spot market inflection points before they hit the tape. Turn sentiment divergence into your most reliable trading filter.",
                    "on_screen_text": "Asymmetric Risk-Reward • Systematic Sentiment Filter",
                    "audio_direction": "Crisp harmonic synthesizer chord with clean UI haptic chime",
                    "transition": "Cross-dissolve with light bloom"
                },
                {
                    "scene_number": 4,
                    "duration_seconds": per_scene + remainder,
                    "visual_description": "The stock price drops sharply on the chart, but the trader's portfolio rises smoothly thanks to the early warning signal.",
                    "camera_direction": "Cinematic crane shot rising above the workstation to reveal the glowing CrowdWisdom emblem",
                    "voiceover": "See what the market is actually thinking. Experience CrowdWisdomTrading.com today.",
                    "on_screen_text": "CrowdWisdomTrading.com — See What the Market is Thinking",
                    "audio_direction": "Confident orchestral-synth cadence to clean finish",
                    "transition": "Fade to brand logo"
                }
            ]
        }

        # Archetype 6: Collective Intelligence ("The Hive Edge")
        archetype_hive = {
            "title": f"The Collective Edge — {campaign_name or 'Consensus Alpha'}",
            "core": "No single retail trader can out-research Wall Street. But together, thousands of disciplined traders create an unbeatable collective intelligence.",
            "pain_point": "The feeling of isolation and overwhelming disadvantage against institutional funds",
            "marketing_angle": "Uniting disciplined retail traders into a synchronized collective intelligence",
            "hook": "Cinematic montage connecting live trading desks across London, New York, and Tokyo in real time.",
            "scenes": [
                {
                    "scene_number": 1,
                    "duration_seconds": per_scene,
                    "visual_description": "A solitary trader sitting at a multi-screen desk in an evening financial office, contemplating the scale of the global markets.",
                    "camera_direction": "Slow pull-back emphasizing the isolation of individual retail trading",
                    "voiceover": "One trader against the global market is just guessing. But what if thousands of disciplined traders analyzed the market together?",
                    "on_screen_text": "Trading in Isolation vs. Collective Intelligence",
                    "audio_direction": "Subtle electronic pulse with rhythmic data clicks",
                    "transition": "Smooth directional slide"
                },
                {
                    "scene_number": 2,
                    "duration_seconds": per_scene,
                    "visual_description": "Clean split-screen visualization of professional quantitative analysts in modern offices in London, New York, and Singapore verifying market depth.",
                    "camera_direction": "Sweeping cinematic camera move across interconnected financial market data terminals",
                    "voiceover": "CrowdWisdom aggregates verified trade setups, sentiment skews, and consensus price targets from experienced market participants.",
                    "on_screen_text": "Aggregating Thousands of Verified Market Participants",
                    "audio_direction": "Warm analog synth swell with crisp UI clicks",
                    "transition": "Light bloom cross-fade"
                },
                {
                    "scene_number": 3,
                    "duration_seconds": per_scene,
                    "visual_description": "Close-up of the CrowdWisdom Weekly and Daily Wisdom consensus trade plan, detailing verified directional bias, entry points, and profit targets.",
                    "camera_direction": "Smooth tracking shot across consensus price targets and stop-loss levels",
                    "voiceover": "Validate your thesis against collective conviction before risking your capital. See where the crowd actually places expectations.",
                    "on_screen_text": "Daily Wisdom™: Verified Consensus Trade Plans",
                    "audio_direction": "Inspiring synth pulse with crystal-clear audio fidelity",
                    "transition": "Geometric digital dissolve"
                },
                {
                    "scene_number": 4,
                    "duration_seconds": per_scene + remainder,
                    "visual_description": "The trader smiling with calm assurance, reviewing a high-probability trade plan backed by institutional-grade crowd consensus.",
                    "camera_direction": "Cinematic push-in to the CrowdWisdom brand beacon with clean sapphire glow",
                    "voiceover": "Never trade alone again. Unlock the power of collective intelligence at CrowdWisdomTrading.com.",
                    "on_screen_text": "CrowdWisdomTrading.com — Never Trade in Isolation",
                    "audio_direction": "Triumphant musical resolution",
                    "transition": "Fade to brand logo"
                }
            ]
        }

        # Archetype 7: Volatility Master ("Silence in the Storm")
        archetype_volatility = {
            "title": f"Silence in the Storm — {campaign_name or 'Options Mastery'}",
            "core": "Market volatility destroys unprepared accounts. CrowdWisdom gives options traders clear consensus direction when volatility spikes.",
            "pain_point": "Panic and paralysis during unexpected volatility spikes and Fed announcements",
            "marketing_angle": "Navigating options volatility with transparent crowd sentiment skews",
            "hook": "Slow-motion rain sliding down floor-to-ceiling glass windows of a high-rise office as a thunderstorm flashes over the trading capital.",
            "scenes": [
                {
                    "scene_number": 1,
                    "duration_seconds": per_scene,
                    "visual_description": "Dramatic cinematic shot of rain pouring down high-rise windows overlooking a stormy financial district, with thunder illuminating trading screens.",
                    "camera_direction": "Slow cinematic dolly past rain-streaked glass to a calm trader at a dual-monitor setup",
                    "voiceover": "When volatility surges and the market swings wildly, most traders freeze or panic.",
                    "on_screen_text": "Market Volatility Surges • Anxiety Peaks",
                    "audio_direction": "Muffled rain ambience with deep distant thunder roll",
                    "transition": "Fast motion blur wipe"
                },
                {
                    "scene_number": 2,
                    "duration_seconds": per_scene,
                    "visual_description": "Extreme close-up of a spiking VIX volatility index graph flashing violently, transitioning cleanly into CrowdWisdom's calm conviction meters.",
                    "camera_direction": "Fast rack focus from the chaotic index to the steady CrowdWisdom interface",
                    "voiceover": "Options traders don't fear volatility — they master it. CrowdWisdom's consensus indicators show where true support and resistance lie.",
                    "on_screen_text": "Master Volatility with CrowdMap™ Support Levels",
                    "audio_direction": "Tense low-frequency drone with rapid ticker clicks",
                    "transition": "Clean vertical split wipe"
                },
                {
                    "scene_number": 3,
                    "duration_seconds": per_scene,
                    "visual_description": "Interactive demonstration of CrowdWisdom's options sentiment skew, highlighting low-risk, high-probability options setups.",
                    "camera_direction": "Smooth glide along options strike price distributions and consensus targets",
                    "voiceover": "Find clarity in the storm. Identify high-conviction options setups with transparent crowd intelligence.",
                    "on_screen_text": "Transparent Options Sentiment & Strike Skew",
                    "audio_direction": "Crisp harmonic synthesizer chord with clean UI haptic chime",
                    "transition": "Cross-dissolve with light bloom"
                },
                {
                    "scene_number": 4,
                    "duration_seconds": per_scene + remainder,
                    "visual_description": "The clouds outside break as a golden sunrise illuminates the city, reflecting off the trader's monitors and the CrowdWisdom logo.",
                    "camera_direction": "Cinematic crane shot rising toward the sunrise and brand lockup",
                    "voiceover": "Trade volatility with asymmetric confidence. Join CrowdWisdomTrading.com today.",
                    "on_screen_text": "CrowdWisdomTrading.com — Asymmetric Clarity in Every Market",
                    "audio_direction": "Confident orchestral-synth cadence to clean finish",
                    "transition": "Fade to brand logo"
                }
            ]
        }

        # Archetype 8: Unique-Data Microstructure ("The Liquidity Matrix")
        archetype_microstructure = {
            "title": f"The Liquidity Matrix — {campaign_name or 'Order Flow Alpha'}",
            "core": "Most retail traders only see candlestick price charts. CrowdMap reveals the invisible liquidity layers where collective trader expectations lie.",
            "pain_point": "Trading blind without seeing resting market liquidity and crowd clusters",
            "marketing_angle": "Visualizing crowd expectations and liquidity pockets with CrowdMap",
            "hook": "Anamorphic macro lens looking through glass at thousands of floating green and cyan liquidity depth nodes across the market.",
            "scenes": [
                {
                    "scene_number": 1,
                    "duration_seconds": per_scene,
                    "visual_description": "Macro shot through optical glass showing a 3D volumetric depth manifold of floating financial nodes across global exchange feeds.",
                    "camera_direction": "Slow horizontal tracking shot across translucent data layers",
                    "voiceover": "Price is only the surface. What actually moves markets is the hidden weight of collective trader positioning.",
                    "on_screen_text": "Price is the Surface • Liquidity is the Truth",
                    "audio_direction": "Subtle resonant bass pulse with digital shimmer",
                    "transition": "Geometric digital dissolve"
                },
                {
                    "scene_number": 2,
                    "duration_seconds": per_scene,
                    "visual_description": "CrowdMap visual interface displaying sector heatmaps and real-time crowd consensus shifting from neutral to ultra-bullish.",
                    "camera_direction": "Gliding horizontal pan over sector performance tiles",
                    "voiceover": "CrowdWisdom's CrowdMap maps where market participants place expectations for price targets, stops, and major support zones.",
                    "on_screen_text": "CrowdMap™: Visible Stop & Target Clusters",
                    "audio_direction": "Deep harmonic bass foundation with glowing chime",
                    "transition": "Smooth directional slide"
                },
                {
                    "scene_number": 3,
                    "duration_seconds": per_scene,
                    "visual_description": "A close-up of a stock testing a CrowdMap support level and rebounding with precision, validating the crowd's collective level.",
                    "camera_direction": "Zoom in on breakout trigger point and rebound curve",
                    "voiceover": "Spot liquidity clusters before the big move. Trade with institutional-grade structural clarity.",
                    "on_screen_text": "Spot Liquidity Pockets Before the Move",
                    "audio_direction": "Rhythmic arpeggiated synth building forward momentum",
                    "transition": "Light bloom cross-fade"
                },
                {
                    "scene_number": 4,
                    "duration_seconds": per_scene + remainder,
                    "visual_description": "Sleek mobile app interface held by an active options trader reviewing high-conviction trade plans on CrowdWisdomTrading.",
                    "camera_direction": "Cinematic close-up tilting up to professional logo",
                    "voiceover": "Trade the matrix, not the illusion. Access CrowdWisdom's proprietary data at CrowdWisdomTrading.com.",
                    "on_screen_text": "CrowdWisdomTrading.com — Institutional Sentiment for Retail",
                    "audio_direction": "Confident orchestral-synth cadence to clean finish",
                    "transition": "Fade to brand logo"
                }
            ]
        }

        # Archetype 9: Product-Value Playbook ("The Consensus Playbook")
        archetype_playbook = {
            "title": f"The Consensus Playbook — {campaign_name or 'Daily Wisdom'}",
            "core": "No more second-guessing your entries. Daily Wisdom provides community-validated trade plans with directional bias, entries, and stops.",
            "pain_point": "Second-guessing trade setups and lacking objective validation before execution",
            "marketing_angle": "Community-validated trade plans and directional consensus with Daily Wisdom",
            "hook": "A sleek dark leather trading journal opening next to an ultra-modern terminal displaying today's verified trade plans.",
            "scenes": [
                {
                    "scene_number": 1,
                    "duration_seconds": per_scene,
                    "visual_description": "A focused trader sitting at an executive desk at sunrise, reviewing trade setups with a high-end metal fountain pen and notebook.",
                    "camera_direction": "Cinematic low-angle dolly past the open journal to the modern display",
                    "voiceover": "Every morning, active traders face the exact same doubt: Is this breakout real, or am I walking into a bull trap?",
                    "on_screen_text": "The Universal Trader Dilemma: Real Breakout or Bull Trap?",
                    "audio_direction": "Quiet acoustic room tone with deep subtle sub-bass",
                    "transition": "Smooth directional slide"
                },
                {
                    "scene_number": 2,
                    "duration_seconds": per_scene,
                    "visual_description": "The screen highlights CrowdWisdom's Daily Wisdom section, displaying verified trader directional consensus, entry zones, and profit targets.",
                    "camera_direction": "Smooth tracking shot across consensus price targets and stop-loss levels",
                    "voiceover": "Daily Wisdom eliminates the guesswork. We aggregate verified trade plans from disciplined traders into one clear consensus playbook.",
                    "on_screen_text": "Daily Wisdom™: Verified Consensus Trade Plans",
                    "audio_direction": "Warm analog synth swell with crisp UI clicks",
                    "transition": "Light bloom cross-fade"
                },
                {
                    "scene_number": 3,
                    "duration_seconds": per_scene,
                    "visual_description": "Interactive breakdown of Pro Crowd Bars showing 87% collective bullish conviction on the active trade setup.",
                    "camera_direction": "Push-in on the 87% conviction metric and stop-loss level",
                    "voiceover": "Directional bias. Precise entry triggers. Mathematical stop-loss levels. All validated by collective trader conviction.",
                    "on_screen_text": "Directional Bias • Exact Triggers • Collective Conviction",
                    "audio_direction": "Inspiring synth pulse with crystal-clear audio fidelity",
                    "transition": "Geometric digital dissolve"
                },
                {
                    "scene_number": 4,
                    "duration_seconds": per_scene + remainder,
                    "visual_description": "The trader executing the trade with calm confidence, closing the journal as the CrowdWisdom logo glows with sapphire radiance.",
                    "camera_direction": "Cinematic push-in to the CrowdWisdom brand beacon with clean sapphire glow",
                    "voiceover": "Execute your trade plan with verified conviction. Join CrowdWisdomTrading.com today.",
                    "on_screen_text": "CrowdWisdomTrading.com — Execute with Verified Conviction",
                    "audio_direction": "Triumphant musical resolution",
                    "transition": "Fade to brand logo"
                }
            ]
        }

        # Map approaches to 100% mutually exclusive, distinct archetype pools
        if approach == "pain_point":
            candidates = [archetype_confession, archetype_routine, archetype_whistleblower]
        elif approach == "unique_data":
            candidates = [archetype_quant, archetype_contrarian, archetype_microstructure]
        else:
            candidates = [archetype_hive, archetype_volatility, archetype_playbook]

        # Filter out archetypes that already exist in this campaign
        existing_titles = [
            (s.get("campaign_title") or s.get("title") or "").lower()
            for s in (existing_scripts or [])
        ]
        available_candidates = [
            c for c in candidates
            if not any(c["title"].lower() in et or et in c["title"].lower() for et in existing_titles)
        ]
        if not available_candidates:
            available_candidates = candidates

        # Deterministically select archetype from available candidates
        selected = copy.deepcopy(available_candidates[seed_int % len(available_candidates)])

        # Localize screenplay to target country (India vs Philippines)
        norm_country = target_country.upper().strip() if target_country else "IN"
        if norm_country == "PH":
            selected["title"] = selected["title"].replace("$10,000", "₱100,000")
            selected["core"] = selected["core"].replace("retail traders", "Filipino retail investors").replace("Wall Street", "Philippine Stock Exchange")
            for sc in selected["scenes"]:
                sc["voiceover"] = (sc.get("voiceover", "")
                    .replace("$10,000", "₱100,000")
                    .replace("ten thousand dollars", "one hundred thousand pesos")
                    .replace("forty contradictory newsletters", "unverified Facebook stock rumors")
                    .replace("Wall Street", "Philippine Stock Exchange")
                    .replace("New York", "Bonifacio Global City")
                    .replace("London", "Makati CBD")
                    .replace("06:30 AM", "09:15 AM")
                )
                sc["on_screen_text"] = (sc.get("on_screen_text", "")
                    .replace("-$10,450.00", "-₱100,000.00")
                    .replace("06:30 AM", "09:15 AM")
                )
            if not any("SEC" in s.get("on_screen_text", "") for s in selected["scenes"]):
                selected["scenes"][-1]["on_screen_text"] += " • SEC Philippines Compliance"
        elif norm_country == "IN":
            selected["title"] = selected["title"].replace("$10,000", "₹1,00,000")
            selected["core"] = selected["core"].replace("retail traders", "Indian retail traders").replace("Wall Street", "Dalal Street")
            for sc in selected["scenes"]:
                sc["voiceover"] = (sc.get("voiceover", "")
                    .replace("$10,000", "₹1,00,000")
                    .replace("ten thousand dollars", "one lakh rupees")
                    .replace("forty contradictory newsletters", "forty noisy Telegram channels")
                    .replace("Wall Street", "Dalal Street")
                    .replace("New York", "Mumbai")
                    .replace("London", "Bengaluru")
                    .replace("06:30 AM", "09:00 AM")
                )
                sc["on_screen_text"] = (sc.get("on_screen_text", "")
                    .replace("-$10,450.00", "-₹1,00,000.00")
                    .replace("06:30 AM", "09:00 AM")
                )
            if not any("SEBI" in s.get("on_screen_text", "") for s in selected["scenes"]):
                selected["scenes"][-1]["on_screen_text"] += " • SEBI Compliant Research"

        # Adjust scene durations and guarantee scene_visual_type
        scenes = []
        for s in selected["scenes"]:
            s_copy = dict(s)
            s_copy["duration_seconds"] = per_scene if s["scene_number"] < 4 else (per_scene + remainder)
            # Enforce balanced cinematic narrative framework across 4 scenes:
            # Scene 1: Human Tension / Hook
            # Scene 2: Market Chaos / Animated Financial Chart
            # Scene 3: CrowdWisdom Proprietary Software / Product Demo
            # Scene 4: Decisive Resolution / Human Serenity
            s_num = s_copy.get("scene_number", 1)
            if s_num == 1:
                s_copy["scene_visual_type"] = "human_cinematography"
            elif s_num == 2:
                s_copy["scene_visual_type"] = "animated_chart"
            elif s_num == 3:
                s_copy["scene_visual_type"] = "product_demo"
            elif s_num == 4:
                s_copy["scene_visual_type"] = "human_cinematography"
            else:
                desc_check = (s_copy.get("visual_description", "") + " " + s_copy.get("camera_direction", "")).lower()
                if any(k in desc_check for k in ["crowdpulse", "crowdmap", "radar", "conviction meter", "pro crowd", "tablet", "ipad", "laptop", "platform", "dashboard", "software interface", "ui"]):
                    s_copy["scene_visual_type"] = "product_demo"
                elif any(k in desc_check for k in ["candlestick", "chart", "divergence", "order flow", "order book", "skew", "depth-of-market", "volume profile", "vix", "rsi", "macd"]):
                    s_copy["scene_visual_type"] = "animated_chart"
                else:
                    s_copy["scene_visual_type"] = "human_cinematography"
            scenes.append(s_copy)

        raw_target = campaign_config.get("audience", {}).get("segments", ["retail_traders"])
        if isinstance(raw_target, list):
            target_audience_str = ", ".join(str(item) for item in raw_target)
        else:
            target_audience_str = str(raw_target) if raw_target else "Active retail traders and investors"

        return {
            "title": selected["title"],
            "campaign_title": selected["title"],
            "core_message": selected["core"],
            "target_audience": target_audience_str,
            "pain_point": selected["pain_point"],
            "marketing_angle": selected["marketing_angle"],
            "visual_hook": selected["hook"],
            "scenes": scenes,
            "voiceover_full": " ".join(s["voiceover"] for s in scenes),
            "on_screen_texts": [s["on_screen_text"] for s in scenes],
            "call_to_action": scenes[-1]["on_screen_text"],
            "music_direction": "Modern cinematic fintech soundtrack with rhythmic 120 BPM percussive pulse and dynamic sidechain ducking",
            "estimated_duration_seconds": duration,
        }


script_agent = ScriptAgent()


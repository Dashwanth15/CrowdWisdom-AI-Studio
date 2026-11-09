"""
CrowdWisdom AI Studio — Dual-Market Research Intelligence Comparison Runner
Executes real-time research retrieval via Exa, scores evidence quality,
and generates structured 8-category intelligence via NVIDIA NIM
for both India (IN) and the Philippines (PH).
"""
import asyncio
import json
import os
import sys
from datetime import datetime, timezone

backend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend")
sys.path.insert(0, backend_dir)

from config import settings
from integrations.exa_client import ExaClient
from integrations.llm_client import LLMClient
from services.market_intelligence.market_research_service import market_research_service
from services.market_intelligence.india_market_profile import INDIA_MARKET_PROFILE
from services.market_intelligence.philippines_market_profile import PHILIPPINES_MARKET_PROFILE


CATEGORIES = [
    "competitor_positioning",
    "common_marketing_hooks",
    "customer_pain_points",
    "value_propositions",
    "audience_objections",
    "content_strategies",
    "market_opportunities",
    "gaps_in_messaging",
]

ANALYSIS_SYSTEM_PROMPT = """You are a Principal Financial Market Research Specialist and Growth Marketing Strategist for CrowdWisdom (CrowdWisdomTrading.com).
Your mission is to perform an empirical, evidence-grounded marketing intelligence analysis for retail trading in the specified country.

CRITICAL INSTRUCTIONS:
1. You MUST generate findings across all 8 strategic categories:
   - competitor_positioning
   - common_marketing_hooks
   - customer_pain_points
   - value_propositions
   - audience_objections
   - content_strategies
   - market_opportunities
   - gaps_in_messaging
2. STRICT SEPARATION: In each insight, clearly separate:
   - "observed_evidence": List of specific, verifiable empirical facts observed in the research data or market structure (with cited sources/publishers).
   - "ai_interpretation": Your strategic assessment of what this observed evidence means for CrowdWisdom's positioning and ad campaigns.
3. NO HALLUCINATIONS: Do not fabricate statistics, URLs, or dates.
4. Respond ONLY with a valid JSON object matching the requested schema.
"""


async def run_market_comparison():
    print("=" * 70)
    print("CROWDWISDOM AI STUDIO — RESEARCH INTELLIGENCE AUDIT & COMPARISON")
    print("=" * 70)

    # 1. Initialize Clients
    exa = ExaClient(settings.EXA_API_KEY)
    llm = LLMClient(provider="nvidia_nim", api_key=settings.NVIDIA_NIM_API_KEY)

    results = {}

    for country_code, profile, country_name in [
        ("IN", INDIA_MARKET_PROFILE, "India"),
        ("PH", PHILIPPINES_MARKET_PROFILE, "Philippines"),
    ]:
        print(f"\n[+] Executing Empirical Research Pipeline for {country_name} ({country_code})...")

        # Query Exa for live market signals
        query = f"{country_name} retail trading investor sentiment pain points competitor ads"
        exa_raw = await exa.search(query, num_results=5)
        raw_results = exa_raw.get("results", [])

        # Process and score evidence items
        scored_evidence = []
        for r in raw_results:
            url = r.get("url", "")
            if not url:
                continue
            scoring = market_research_service.calculate_source_quality(
                url=url,
                publisher=r.get("author"),
                raw_publication_date=r.get("publishedDate") or r.get("date"),
            )
            item = {
                "title": r.get("title", ""),
                "url": url,
                "text_sample": str(r.get("text", ""))[:300],
                "published_date": scoring["publication_date"],
                "date_verification_status": scoring["date_verification_status"],
                "source_tier": scoring["tier"],
                "source_tier_name": scoring["tier_name"],
                "confidence_score": scoring["final_score"],
                "staleness_factor": scoring["staleness_factor"],
            }
            scored_evidence.append(item)

        print(f"    Retrieved & Scored {len(scored_evidence)} live empirical sources.")
        for idx, ev in enumerate(scored_evidence, 1):
            print(f"    [{idx}] Tier {ev['source_tier']} ({ev['confidence_score']}/10) | {ev['title'][:50]}... | Date: {ev['published_date'] or 'Unverified'}")

        # Inject official benchmarks
        benchmarks = market_research_service._get_verified_ground_truth_benchmarks(country_code, "sentiment")
        print(f"    Injected {len(benchmarks)} official Tier-1 regulatory/exchange benchmarks.")

        # Build prompt for LLM
        prompt = f"""Country: {country_name} ({country_code})
Financial Ecosystem:
- Primary Regulator: {profile['regulatory_safeguards']['regulator']}
- Key Exchanges: {profile['market_ecosystem']['primary_exchanges']}
- Trading Instruments: {profile['market_ecosystem']['dominant_instruments']}
- Domestic Platforms: {profile['market_ecosystem']['key_domestic_platforms']}

Live Empirical Research Evidence:
{json.dumps(scored_evidence, indent=2)}

Official Regulatory Benchmarks:
{json.dumps(benchmarks, indent=2)}

Generate structured marketing intelligence across the 8 categories in JSON:
{{
  "country": "{country_code}",
  "insights": [
    {{
      "category": "competitor_positioning",
      "title": "<title>",
      "observed_evidence": ["<specific fact 1 with citation>", "<specific fact 2>"],
      "ai_interpretation": "<strategic analysis and CrowdWisdom implication>",
      "confidence": 0.95
    }},
    ... for all 8 categories
  ]
}}
"""
        print(f"    Synthesizing 8 strategic categories via NVIDIA NIM...")
        raw_text = await llm.chat(
            messages=[
                {"role": "system", "content": ANALYSIS_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )

        try:
            # Handle potential markdown fence ```json ... ```
            clean_json = raw_text.strip()
            if clean_json.startswith("```json"):
                clean_json = clean_json[7:]
            if clean_json.startswith("```"):
                clean_json = clean_json[3:]
            if clean_json.endswith("```"):
                clean_json = clean_json[:-3]
            parsed = json.loads(clean_json.strip())
        except Exception:
            parsed = {"raw": raw_text}

        results[country_code] = {
            "country_name": country_name,
            "evidence": scored_evidence,
            "benchmarks": benchmarks,
            "analysis": parsed,
        }

    # Save output for audit report
    out_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts", "market_comparison_output.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"\n[✓] Research Comparison Run Complete! Output written to {out_path}")
    return results


if __name__ == "__main__":
    asyncio.run(run_market_comparison())

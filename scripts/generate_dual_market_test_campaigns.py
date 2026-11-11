"""
Phase 8 Execution Script: Real Campaign & Script Generation for India & Philippines.
Uses real market profiles, segmentation, research evidence, and script generation.
"""
import asyncio
import sys
import os
from datetime import datetime, timezone
from bson import ObjectId

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from database.connection import get_database
from services.market_intelligence.country_localization_service import country_localization_service
from services.market_intelligence import market_context_builder
from agents.script_agent import script_agent


async def generate_test_campaigns():
    db = get_database()
    now = datetime.now(timezone.utc)

    # 1. Create India Campaign A
    india_campaign_doc = {
        "name": "Informed Investor Protocol — India 🇮🇳",
        "description": "Help retail investors make more informed decisions using research-backed market intelligence.",
        "target_country": "IN",
        "objective": "brand_awareness",
        "audience": {
            "target_country": "IN",
            "segments": ["retail_traders", "options_traders", "in_options_derivative_trader"],
            "interests": ["Nifty 50", "Bank Nifty", "F&O", "Dalal Street", "options", "trading", "investing"],
        },
        "research_approaches": ["pain_point", "unique_data", "product_value"],
        "video_duration_seconds": 45,
        "video_aspect_ratio": "9:16",
        "creative_direction": "Cinematic financial clarity, disciplined pre-market routine, crisp audio",
        "owner_id": "test_user_admin",
        "status": "active",
        "ads_researched": 0,
        "scripts_generated": 1,
        "videos_generated": 0,
        "created_at": now,
        "updated_at": now,
    }
    in_res = await db.campaigns.insert_one(india_campaign_doc)
    india_campaign_id = str(in_res.inserted_id)
    print(f"Created India Campaign: {india_campaign_id}")

    # 2. Create Philippines Campaign B
    ph_campaign_doc = {
        "name": "Informed Investor Protocol — Philippines 🇵🇭",
        "description": "Help retail investors make more informed decisions using research-backed market intelligence.",
        "target_country": "PH",
        "objective": "brand_awareness",
        "audience": {
            "target_country": "PH",
            "segments": ["pse_equities_trader", "ofw_investor", "young_pro_wealth"],
            "interests": ["PSE", "PSEi", "dividends", "financial freedom", "REITs", "GStocks", "BGC"],
        },
        "research_approaches": ["pain_point", "unique_data", "product_value"],
        "video_duration_seconds": 45,
        "video_aspect_ratio": "9:16",
        "creative_direction": "Modern cinematic Manila tech narrative, BGC sunrise, disciplined wealth protection",
        "owner_id": "test_user_admin",
        "status": "active",
        "ads_researched": 0,
        "scripts_generated": 1,
        "videos_generated": 0,
        "created_at": now,
        "updated_at": now,
    }
    ph_res = await db.campaigns.insert_one(ph_campaign_doc)
    ph_campaign_id = str(ph_res.inserted_id)
    print(f"Created Philippines Campaign: {ph_campaign_id}")

    # 3. Generate Script for India Campaign
    print("\n--- Generating Script for India Campaign ---")
    in_script_doc = {
        "campaign_id": india_campaign_id,
        "target_country": "IN",
        "approach": "pain_point",
        "status": "generating",
        "version": 1,
        "created_at": now,
        "updated_at": now,
    }
    in_s_res = await db.scripts.insert_one(in_script_doc)
    in_script_id = str(in_s_res.inserted_id)

    in_run_result = await script_agent._run({
        "campaign_id": india_campaign_id,
        "script_id": in_script_id,
        "approach": "pain_point",
        "target_country": "IN",
        "campaign_config": india_campaign_doc,
    })
    print(f"India Script Result: {in_run_result}")

    # 4. Generate Script for Philippines Campaign
    print("\n--- Generating Script for Philippines Campaign ---")
    ph_script_doc = {
        "campaign_id": ph_campaign_id,
        "target_country": "PH",
        "approach": "pain_point",
        "status": "generating",
        "version": 1,
        "created_at": now,
        "updated_at": now,
    }
    ph_s_res = await db.scripts.insert_one(ph_script_doc)
    ph_script_id = str(ph_s_res.inserted_id)

    ph_run_result = await script_agent._run({
        "campaign_id": ph_campaign_id,
        "script_id": ph_script_id,
        "approach": "pain_point",
        "target_country": "PH",
        "campaign_config": ph_campaign_doc,
    })
    print(f"Philippines Script Result: {ph_run_result}")

    # 5. Verify India Script from DB
    in_final_script = await db.scripts.find_one({"_id": ObjectId(in_script_id)})
    print("\n================== INDIA SCRIPT RECORD ==================")
    print("ID:", str(in_final_script["_id"]))
    print("Title:", in_final_script.get("title"))
    print("Target Country:", in_final_script.get("target_country"))
    print("Visual Hook:", in_final_script.get("visual_hook"))
    print("Core Message:", in_final_script.get("core_message"))
    print("Consistency Report:", in_final_script.get("consistency_report"))
    for sc in in_final_script.get("scenes", []):
        print(f"  Scene {sc['scene_number']}:")
        print(f"    VO: {sc['voiceover']}")
        print(f"    OST: {sc['on_screen_text']}")
        print(f"    Visual: {sc['visual_description']}")

    # 6. Verify Philippines Script from DB
    ph_final_script = await db.scripts.find_one({"_id": ObjectId(ph_script_id)})
    print("\n================== PHILIPPINES SCRIPT RECORD ==================")
    print("ID:", str(ph_final_script["_id"]))
    print("Title:", ph_final_script.get("title"))
    print("Target Country:", ph_final_script.get("target_country"))
    print("Visual Hook:", ph_final_script.get("visual_hook"))
    print("Core Message:", ph_final_script.get("core_message"))
    print("Consistency Report:", ph_final_script.get("consistency_report"))
    for sc in ph_final_script.get("scenes", []):
        print(f"  Scene {sc['scene_number']}:")
        print(f"    VO: {sc['voiceover']}")
        print(f"    OST: {sc['on_screen_text']}")
        print(f"    Visual: {sc['visual_description']}")


if __name__ == "__main__":
    asyncio.run(generate_test_campaigns())


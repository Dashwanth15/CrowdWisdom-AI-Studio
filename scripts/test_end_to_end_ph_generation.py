import asyncio
import os
import sys
from pathlib import Path
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

load_dotenv(backend_dir / ".env")
uri = os.environ.get("MONGODB_URL")
client = AsyncIOMotorClient(uri)
db = client["crowdwisdom_ai_studio"]

from orchestrator.hermes_orchestrator import orchestrator
from services.market_intelligence.country_localization_service import country_localization_service

async def test_generation():
    print("=== Testing End-to-End Philippines Campaign Script Generation ===")

    # 1. Create a test Philippines Campaign
    camp_doc = {
        "name": "PSE Dividend Alpha & OFW Wealth Growth — Philippines 🇵🇭",
        "description": "Autonomous AI marketing campaign targeting Philippine equities investors and overseas Filipino workers building sustainable long-term portfolios.",
        "target_country": "PH",
        "audience": {
            "target_country": "PH",
            "segments": ["pse_equities_trader", "ofw_investor"],
            "pain_points": ["Social media tipster hype causing drawdowns in volatile mid-caps"],
            "currency": "PHP",
            "currency_symbol": "₱"
        },
        "status": "active",
        "scripts_generated": 0,
        "commercials_created": 0,
        "video_aspect_ratio": "9:16",
        "video_duration_seconds": 45,
    }
    res = await db.campaigns.insert_one(camp_doc)
    camp_id = str(res.inserted_id)
    print(f"Created test campaign with ID: {camp_id}")

    # 2. Launch script generation via orchestrator
    print("Launching script generation via orchestrator...")
    launch_res = await orchestrator.launch_script_generation(
        campaign_id=camp_id,
        script_input={
            "approach": "pain_point",
            "target_country": "PH",
            "campaign_config": {
                "name": camp_doc["name"],
                "target_country": "PH",
                "video_aspect_ratio": "9:16",
                "video_duration_seconds": 45,
            }
        }
    )
    script_id = launch_res["script_id"]
    execution_id = launch_res["execution_id"]
    print(f"Launched! Script ID: {script_id}, Execution ID: {execution_id}")

    # 3. Wait for execution to complete (poll for up to 90 seconds)
    print("Waiting for script generation to complete...")
    for i in range(45):
        await asyncio.sleep(2)
        s_doc = await db.scripts.find_one({"_id": ObjectId(script_id)})
        status = s_doc.get("status") if s_doc else "unknown"
        if status in ("pending_approval", "failed", "completed"):
            print(f"Script reached terminal state: {status}")
            break
        if i % 5 == 0:
            print(f"  [{i*2}s] Still generating (status: {status})...")

    final_script = await db.scripts.find_one({"_id": ObjectId(script_id)})
    assert final_script is not None, "Script not found in DB!"

    print("\n--- Final Script Inspection ---")
    title = final_script.get("title") or final_script.get("campaign_title")
    print("Title:", title)
    print("Target Country:", final_script.get("target_country"))
    print("Status:", final_script.get("status"))
    print("Core Message:", final_script.get("core_message"))
    scenes = final_script.get("scenes", [])
    print(f"Scenes count: {len(scenes)}")
    for sc in scenes:
        print(f"\nScene {sc.get('scene_number')} ({sc.get('duration_seconds')}s):")
        print(f"  Visual: {sc.get('visual_description')[:90]}...")
        print(f"  VO: {sc.get('voiceover')[:90]}...")
        print(f"  OST: {sc.get('on_screen_text')}")
        print(f"  Asset URL: {sc.get('visual_asset_url')}")

    consistency = final_script.get("consistency_report") or {}
    print("\n--- Consistency Report ---")
    print("Is Consistent:", consistency.get("is_consistent"))
    print("Inconsistencies Count:", consistency.get("inconsistencies_count"))
    print("Inconsistencies:", consistency.get("inconsistencies"))
    print("Detected Currencies:", consistency.get("detected_currencies"))

    # Assertions
    assert final_script.get("target_country") == "PH", f"Expected PH, got {final_script.get('target_country')}"
    assert "NSE" not in title, f"NSE found in title: {title}"
    assert "BSE" not in title, f"BSE found in title: {title}"
    assert len(scenes) >= 3, f"Expected at least 3 scenes, got {len(scenes)}"
    last_ost = scenes[-1].get("on_screen_text", "")
    assert "SEBI" not in last_ost, f"SEBI found in final OST: {last_ost}"
    assert consistency.get("is_consistent") is True, f"Inconsistencies detected: {consistency}"
    assert final_script.get("status") == "pending_approval", f"Expected pending_approval (Checkpoint 2), got {final_script.get('status')}"

    print("\n>>> ALL SYSTEM CHECKS PASSED: 100% genuine Philippines context, 0 Indian leaks, active Checkpoint 2. <<<")

if __name__ == "__main__":
    asyncio.run(test_generation())

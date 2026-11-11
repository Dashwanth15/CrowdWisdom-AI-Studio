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

from services.market_intelligence.country_localization_service import country_localization_service
from services.visual_asset_service import visual_asset_service

async def repair_script():
    script_id = "6af4151714e1e47fbd321144"
    doc = await db.scripts.find_one({"_id": ObjectId(script_id)})
    if not doc:
        print(f"Script {script_id} not found!")
        return

    print("Found script:", doc.get("title"))

    # Update Title
    fixed_title = "The Noise Trap — PSE Blue Chip & Dividend Alpha — Philippines 🇵🇭"
    fixed_core = "Unverified social media tips and market rumors trigger emotional overtrading on the Philippine Stock Exchange. CrowdWisdom cuts through the noise with verified crowd conviction metrics."
    fixed_pain = "Trading on unverified social media stock tips and emotional volatility in the PSE"
    fixed_angle = "Replacing speculative group chat rumors with mathematically verified PSE crowd consensus"

    scenes = doc.get("scenes", [])
    if len(scenes) >= 4:
        # Scene 1: Macro hands typing
        scenes[0]["visual_description"] = "Close-up macro of an intense trader's hands typing rapidly on a mechanical keyboard at a trading workstation amidst flashing sell-off candlestick monitors and conflicting alert feeds, shallow depth of field, no visible faces."
        scenes[0]["voiceover"] = "In Philippine equities, unverified social media tips and emotional panic drive retail drawdowns. The more conflicting alerts you chase, the faster capital evaporates."
        scenes[0]["on_screen_text"] = "Social Media Rumors vs. PSE Market Reality"

        # Scene 2: Institutional Order Flow
        scenes[1]["visual_description"] = "Professional quantitative analyst in a modern glass office intently studying live multi-monitor order flow skew, depth-of-market histograms, and institutional consensus charts."
        scenes[1]["voiceover"] = "Institutional capital in Manila doesn't trade on unverified chat tips. Real market edge comes from tracking disciplined volume flows and verified collective conviction."
        scenes[1]["on_screen_text"] = "Don't Trade Rumors. Trade Collective Conviction."

        # Scene 3: Pro Crowd Bars
        scenes[2]["visual_description"] = "Extreme close-up on modern tablet device on an executive desk displaying the CrowdPulse institutional conviction radar, oscillating sentiment waveforms, and live accumulation telemetry."
        scenes[2]["voiceover"] = "CrowdWisdom's Pro Crowd Bars aggregate real trader expectations across Philippine blue chips, revealing true consensus before the market moves."
        scenes[2]["on_screen_text"] = "Pro Crowd Bars: Real-Time PSE Market Conviction"

        # Scene 4: Floor-to-ceiling glass window & SEC Disclaimer
        scenes[3]["visual_description"] = "Professional trader standing calmly by a floor-to-ceiling glass window in a modern Makati financial office overlooking the city skyline at dawn, confident and decisive."
        scenes[3]["voiceover"] = "Stop feeding the noise machine. Trade what verified data shows at CrowdWisdomTrading.com."
        scenes[3]["on_screen_text"] = "CrowdWisdomTrading.com — For Educational & Market Sentiment Research Only (SEC Philippines Disclosures Apply)"

    # Regenerate Scene 1 visual asset with our new macro generator
    print("Regenerating Scene 1 visual asset...")
    s1_asset = await visual_asset_service.generate_scene_visual(
        scene=scenes[0],
        script_id=script_id,
        aspect_ratio="9:16",
        campaign_title=fixed_title,
        approach=doc.get("approach", "pain_point"),
        force_refresh=True,
        campaign_id=str(doc.get("campaign_id")),
        target_country="PH",
    )
    scenes[0]["visual_asset_path"] = s1_asset["visual_asset_path"]
    scenes[0]["visual_asset_url"] = s1_asset["visual_asset_url"]
    scenes[0]["visual_asset_status"] = s1_asset.get("visual_asset_status", "completed")
    scenes[0]["visual_asset_provider"] = s1_asset.get("visual_asset_provider", "pollinations_flux")
    print(f"Scene 1 new asset: {scenes[0]['visual_asset_url']}")

    # Validate consistency
    test_dict = {
        "title": fixed_title,
        "campaign_title": fixed_title,
        "core_message": fixed_core,
        "pain_point": fixed_pain,
        "marketing_angle": fixed_angle,
        "scenes": scenes,
        "target_country": "PH",
    }
    consistency = country_localization_service.validate_script_country_consistency(test_dict, "PH")
    print("Consistency check result:", consistency)

    # Save to MongoDB
    await db.scripts.update_one(
        {"_id": ObjectId(script_id)},
        {
            "$set": {
                "title": fixed_title,
                "campaign_title": fixed_title,
                "core_message": fixed_core,
                "pain_point": fixed_pain,
                "marketing_angle": fixed_angle,
                "scenes": scenes,
                "target_country": "PH",
                "voiceover_full": " ".join(s.get("voiceover", "") for s in scenes),
                "on_screen_texts": [s.get("on_screen_text", "") for s in scenes],
                "consistency_report": consistency,
                "status": "pending_approval",  # Keep Checkpoint 2 active!
            }
        }
    )
    print("Successfully repaired script in MongoDB!")

if __name__ == "__main__":
    asyncio.run(repair_script())

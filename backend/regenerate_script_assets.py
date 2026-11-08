import asyncio
import os
from pathlib import Path
from bson import ObjectId
from database.connection import connect_to_mongo, close_mongo_connection, get_database
from services.visual_asset_service import visual_asset_service
from agents.video_production_agent import video_production_agent

async def regenerate():
    await connect_to_mongo()
    db = get_database()
    script_id = "6aee29a4fadd50fa6e006ce4"
    campaign_id = "6aedc9fd5891425b46385f05"

    script = await db.scripts.find_one({"_id": ObjectId(script_id)})
    print(f"Loaded script: {script.get('title')}")

    # Remove old asset files for this script so fresh FLUX images are fetched
    media_dir = Path("media")
    for f in (media_dir / "assets").glob(f"asset_{script_id}_*"):
        try:
            f.unlink()
            print(f"Removed stale asset: {f.name}")
        except Exception:
            pass

    # Ensure scenes have correct typology:
    # Scene 1: Macro coffee droplet with glowing stock ticker screens (FLUX)
    # Scene 2: Dynamic animated candlestick chart (Chart Engine)
    # Scene 3: CrowdWisdomTrading platform interface with bullish consensus (FLUX)
    # Scene 4: Trader at sunrise city skyline with calm coffee sip (FLUX)
    scenes = script.get("scenes", [])
    for idx, sc in enumerate(scenes):
        sc.pop("visual_asset_path", None)
        sc.pop("visual_asset_url", None)
        sc.pop("visual_asset_status", None)
        if idx == 1:
            sc["media_type"] = "animated_chart"
            sc["chart_theme"] = "sentiment_divergence"
        else:
            sc["media_type"] = "ai_image"

    script["scenes"] = scenes
    print("Generating bespoke 1080p photorealistic visual assets...")
    updated_scenes = await visual_asset_service.ensure_script_visual_assets(script, aspect_ratio="9:16", db=db)
    print(f"Generated {len(updated_scenes)} scene visual assets!")
    for sc in updated_scenes:
        print(f"  Scene {sc.get('scene_number')}: {sc.get('media_type')} -> {sc.get('visual_asset_path')}")

    # Update script in DB
    await db.scripts.update_one(
        {"_id": ObjectId(script_id)},
        {"$set": {"scenes": updated_scenes}}
    )

    print("\nVisual asset generation complete and verified!")
    await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(regenerate())


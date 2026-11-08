import shutil
import asyncio
from pathlib import Path
from bson import ObjectId
from database.connection import connect_to_mongo, close_mongo_connection, get_database

async def update_script():
    await connect_to_mongo()
    db = get_database()
    script_id = "6aee29a4fadd50fa6e006ce4"

    assets_dir = Path("media/assets")
    assets_dir.mkdir(parents=True, exist_ok=True)

    # 1. Copy curated pristine assets to target paths
    s1_dest = assets_dir / f"asset_{script_id}_1_a8e7ed222c.jpg"
    s3_dest = assets_dir / f"asset_{script_id}_3_5349fae01c.jpg"
    s4_dest = assets_dir / f"asset_{script_id}_4_098097500d.jpg"

    shutil.copy("test_refined_scene_1.jpg", s1_dest)
    shutil.copy("media/assets/asset_scene3_new.jpg", s3_dest)
    shutil.copy("media/assets/asset_scene4_new.jpg", s4_dest)
    print("Copied pristine visual assets to media/assets/")

    script = await db.scripts.find_one({"_id": ObjectId(script_id)})
    scenes = script.get("scenes", [])

    # Scene 1: Dark espresso / financial desk (FLUX AI)
    scenes[0]["media_type"] = "ai_image"
    scenes[0]["visual_asset_path"] = str(s1_dest)
    scenes[0]["visual_asset_url"] = f"/media/assets/{s1_dest.name}"
    scenes[0]["visual_asset_status"] = "completed"
    scenes[0]["camera_motion"] = "slow_zoom_in"

    # Scene 2: Dynamic animated candlestick chart
    scenes[1]["media_type"] = "animated_chart"
    scenes[1]["chart_theme"] = "sentiment_divergence"
    scenes[1]["visual_asset_path"] = str(assets_dir / f"asset_{script_id}_2_7a572846f1.jpg")
    scenes[1]["visual_asset_url"] = f"/media/assets/asset_{script_id}_2_7a572846f1.jpg"
    scenes[1]["visual_asset_status"] = "completed"
    scenes[1]["camera_motion"] = "pan_right"

    # Scene 3: Institutional trading workstation (FLUX AI)
    scenes[2]["media_type"] = "ai_image"
    scenes[2]["visual_asset_path"] = str(s3_dest)
    scenes[2]["visual_asset_url"] = f"/media/assets/{s3_dest.name}"
    scenes[2]["visual_asset_status"] = "completed"
    scenes[2]["camera_motion"] = "slow_zoom_in"

    # Scene 4: Confident trader at sunrise city skyline (FLUX AI)
    scenes[3]["media_type"] = "ai_image"
    scenes[3]["visual_asset_path"] = str(s4_dest)
    scenes[3]["visual_asset_url"] = f"/media/assets/{s4_dest.name}"
    scenes[3]["visual_asset_status"] = "completed"
    scenes[3]["camera_motion"] = "pan_right"

    await db.scripts.update_one(
        {"_id": ObjectId(script_id)},
        {"$set": {"scenes": scenes}}
    )
    print("Script document updated in MongoDB with pristine 1080p visual assets!")
    await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(update_script())


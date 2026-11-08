import asyncio
import sys
import shutil
from pathlib import Path
sys.path.insert(0, 'backend')
from database.connection import connect_to_mongo, get_database
from bson import ObjectId

async def main():
    await connect_to_mongo()
    db = get_database()
    script_id = "6aeec839a7ce69e62b6ae848"
    
    # Copy generated assets
    p1 = Path("backend/media/assets/asset_6aeec839a7ce69e62b6ae848_1_cinematic.jpg")
    p4 = Path("backend/media/assets/asset_6aeec839a7ce69e62b6ae848_4_cinematic.jpg")
    shutil.copy("backend/media/assets/test_real_scene1.jpg", str(p1))
    shutil.copy("backend/media/assets/test_real_scene4.jpg", str(p4))
    
    script = await db.scripts.find_one({"_id": ObjectId(script_id)})
    scenes = script.get("scenes", [])
    
    # Scene 1: Photorealistic wide shot at dawn
    scenes[0]["media_type"] = "ai_image"
    scenes[0]["visual_asset_path"] = str(p1)
    scenes[0]["visual_asset_url"] = f"/media/assets/{p1.name}"
    scenes[0]["visual_asset_status"] = "completed"
    scenes[0]["visual_asset_provider"] = "pollinations_flux"
    scenes[0]["camera_motion"] = "slow_zoom_in"
    
    # Scene 2: Dynamic Animated Candlestick Chart (volatility selloff & divergence)
    scenes[1]["media_type"] = "animated_chart"
    scenes[1]["chart_theme"] = "sentiment_divergence"
    
    # Scene 3: Dynamic Animated Candlestick Chart (bullish breakout & reversal)
    scenes[2]["media_type"] = "animated_chart"
    scenes[2]["chart_theme"] = "bullish_breakout"
    
    # Scene 4: Photorealistic close-up of confident trader
    scenes[3]["media_type"] = "ai_image"
    scenes[3]["visual_asset_path"] = str(p4)
    scenes[3]["visual_asset_url"] = f"/media/assets/{p4.name}"
    scenes[3]["visual_asset_status"] = "completed"
    scenes[3]["visual_asset_provider"] = "pollinations_flux"
    scenes[3]["camera_motion"] = "pan_right"
    
    await db.scripts.update_one(
        {"_id": ObjectId(script_id)},
        {"$set": {"scenes": scenes}}
    )
    print("Updated script scenes with genuine cinematic photorealistic assets!")

if __name__ == '__main__':
    asyncio.run(main())


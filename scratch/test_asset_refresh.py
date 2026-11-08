import asyncio
import sys
import os
from bson import ObjectId
sys.path.insert(0, r"backend")
from config import settings
from motor.motor_asyncio import AsyncIOMotorClient
from services.visual_asset_service import VisualAssetService

async def main():
    service = VisualAssetService()
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DB_NAME]
    
    script_id = "6aef5207bfb43a08259f1ed6"
    script = await db.scripts.find_one({"_id": ObjectId(script_id)})
    if not script:
        print("Script not found!")
        return

    print(f"Refreshing visual assets for Script {script_id}: '{script.get('title')}'")
    scenes = script.get("scenes", [])
    updated_scenes = []

    for sc in scenes:
        snum = sc.get("scene_number")
        print(f"\nProcessing Scene {snum}: {sc.get('visual_description')[:60]}...")
        result = await service.generate_scene_visual(
            scene=sc,
            script_id=script_id,
            aspect_ratio="9:16",
            campaign_title=script.get("title", "CrowdWisdom"),
            approach=script.get("approach", "pain_point"),
            force_refresh=True,
            campaign_id=str(script.get("campaign_id"))
        )
        print(f"  -> Generated: media_type='{result.get('media_type')}', provider='{result.get('visual_asset_provider')}', path='{result.get('visual_asset_path')}'")
        
        # Merge results into scene
        sc.update(result)
        updated_scenes.append(sc)

    # Save to MongoDB
    await db.scripts.update_one(
        {"_id": ObjectId(script_id)},
        {"$set": {"scenes": updated_scenes}}
    )
    print("\nUpdated script saved to MongoDB successfully!")

if __name__ == "__main__":
    asyncio.run(main())


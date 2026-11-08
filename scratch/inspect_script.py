import asyncio
import sys
import json
from bson import ObjectId
sys.path.insert(0, r"backend")
from config import settings
from motor.motor_asyncio import AsyncIOMotorClient

async def main():
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DB_NAME]
    script = await db.scripts.find_one({"_id": ObjectId("6aef5207bfb43a08259f1ed6")})
    if not script:
        print("Script not found!")
        return
    
    print("Script Title:", script.get("title"))
    print("Campaign ID:", script.get("campaign_id"))
    print("Approach:", script.get("approach"))
    print("Status:", script.get("status"))
    print("\nScenes count:", len(script.get("scenes", [])))
    for sc in script.get("scenes", []):
        print(f"\n--- Scene {sc.get('scene_number')} ---")
        print("visual_type:", sc.get("scene_visual_type") or sc.get("visual_type"))
        print("media_type:", sc.get("media_type"))
        print("visual_description:", sc.get("visual_description"))
        print("voiceover:", sc.get("voiceover"))
        print("visual_asset_path:", sc.get("visual_asset_path"))
        print("visual_asset_provider:", sc.get("visual_asset_provider"))
        print("transition:", sc.get("transition"))

if __name__ == "__main__":
    asyncio.run(main())


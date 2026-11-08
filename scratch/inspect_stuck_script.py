import asyncio
import sys
from bson import ObjectId

backend_dir = r"c:\Users\dashw\OneDrive\Desktop\my projects\CrowdWisdom AI Studio\backend"
sys.path.insert(0, backend_dir)

from config import settings
from motor.motor_asyncio import AsyncIOMotorClient

async def main():
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DB_NAME]
    
    script = await db.scripts.find_one({"_id": ObjectId("6aef692d547c27366bbc5f21")})
    scenes = script.get("scenes", [])
    print("Total scenes:", len(scenes))
    for sc in scenes:
        print(f"\n--- Scene {sc.get('scene_number')} ---")
        print("duration_seconds:", sc.get("duration_seconds"))
        print("visual_type:", sc.get("scene_visual_type") or sc.get("visual_type"))
        print("media_type:", sc.get("media_type"))
        print("visual_asset_path:", sc.get("visual_asset_path"))
        print("visual_description:", sc.get("visual_description"))
        print("voiceover:", sc.get("voiceover"))
        print("transition:", sc.get("transition"))

if __name__ == "__main__":
    asyncio.run(main())


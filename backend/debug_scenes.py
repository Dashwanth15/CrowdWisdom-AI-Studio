import asyncio
import sys
sys.path.insert(0, 'backend')
from database.connection import connect_to_mongo, get_database
from bson import ObjectId
from video_engine.openmontage_adapter import openmontage_adapter
import os

async def test():
    await connect_to_mongo()
    db = get_database()
    script = await db.scripts.find_one({"_id": ObjectId("6aeec839a7ce69e62b6ae848")})
    scenes = script.get("scenes", [])
    for idx, sc in enumerate(scenes):
        asset_path = sc.get("visual_asset_path")
        media_type = sc.get("media_type")
        print(f"Scene {idx+1}: media_type={media_type}, asset_path={asset_path}")
        print(f"  exists on disk: {os.path.exists(asset_path) if asset_path else False}")
        if asset_path:
            from PIL import Image
            try:
                im = Image.open(asset_path)
                print(f"  Image opened successfully: {im.size}, mode={im.mode}")
            except Exception as e:
                print(f"  FAILED to open image: {e}")

if __name__ == '__main__':
    asyncio.run(test())


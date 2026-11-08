import asyncio
import sys
import os
from bson import ObjectId
from pathlib import Path

sys.path.insert(0, r"backend")
from config import settings
from motor.motor_asyncio import AsyncIOMotorClient

async def main():
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DB_NAME]
    
    script = await db.scripts.find_one({"_id": ObjectId("6aef5207bfb43a08259f1ed6")})
    scenes = script.get("scenes", [])
    print(f"Inspecting voiceover assets for {len(scenes)} scenes:")
    for sc in scenes:
        snum = sc.get("scene_number")
        vo_path = sc.get("voiceover_audio_path")
        print(f"Scene {snum}: vo_path='{vo_path}' | exists={os.path.exists(vo_path) if vo_path else False}")
        if vo_path and not os.path.exists(vo_path):
            cand = Path("media/audio") / Path(vo_path).name
            print(f"  Cand media/audio exists: {cand.exists()}")

if __name__ == "__main__":
    asyncio.run(main())


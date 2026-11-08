import asyncio
import sys
import os
import time
from bson import ObjectId
from pathlib import Path

backend_dir = r"c:\Users\dashw\OneDrive\Desktop\my projects\CrowdWisdom AI Studio\backend"
sys.path.insert(0, backend_dir)

from config import settings
from motor.motor_asyncio import AsyncIOMotorClient
from video_engine.openmontage_adapter import openmontage_adapter

async def reproduce():
    print("=" * 60)
    print("REPRODUCING RENDER FOR SCRIPT 6aef692d547c27366bbc5f21")
    print("=" * 60)

    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DB_NAME]
    
    script_id = "6aef692d547c27366bbc5f21"
    script = await db.scripts.find_one({"_id": ObjectId(script_id)})
    if not script:
        print("Script not found!")
        return

    scenes = script.get("scenes", [])
    print(f"Loaded {len(scenes)} scenes.")
    for sc in scenes:
        print(f"Scene {sc.get('scene_number')}: {sc.get('media_type')} | {sc.get('visual_asset_path')}")

    out_file = "scratch/reproduce_test.mp4"
    thumb_file = "scratch/reproduce_test.jpg"

    def progress(pct, msg):
        print(f"[{time.strftime('%H:%M:%S')}] ({pct}%) {msg}")

    try:
        res = await openmontage_adapter.render_video(
            scenes=scenes,
            output_file_path=out_file,
            thumbnail_file_path=thumb_file,
            aspect_ratio="9:16",
            target_duration=60,
            quality="high",
            progress_callback=progress
        )
        print("SUCCESS! Result:", res)
    except Exception as e:
        import traceback
        print("\n" + "!" * 60)
        print("RENDER CRASHED WITH ERROR:")
        print("!" * 60)
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(reproduce())


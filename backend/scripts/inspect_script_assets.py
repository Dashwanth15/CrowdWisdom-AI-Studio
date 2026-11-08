import asyncio
import sys
from pathlib import Path
from bson import ObjectId

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from database.connection import connect_to_mongo, get_database

async def main():
    await connect_to_mongo()
    db = get_database()
    script = await db.scripts.find_one({"_id": ObjectId("6aee29a4fadd50fa6e006ce4")})
    scenes = script.get("scenes", [])
    for idx, s in enumerate(scenes):
        print(f"Scene {idx+1}:")
        print(f"  dur: {s.get('duration_seconds')}")
        print(f"  desc: {s.get('visual_description')}")
        print(f"  vo: {s.get('voiceover')}")
        print(f"  visual_asset_path: {s.get('visual_asset_path')}")
        print(f"  media_type: {s.get('media_type')}")
        print(f"  provider: {s.get('visual_asset_provider')}")

if __name__ == "__main__":
    asyncio.run(main())


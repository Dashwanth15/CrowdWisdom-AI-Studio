import asyncio
import sys
sys.path.insert(0, 'backend')
from database.connection import connect_to_mongo, get_database
from bson import ObjectId

async def main():
    await connect_to_mongo()
    db = get_database()
    script = await db.scripts.find_one({"_id": ObjectId("6aeec839a7ce69e62b6ae848")})
    for i, sc in enumerate(script.get("scenes", [])):
        print(f"Scene {i+1}:")
        print("  media_type:", sc.get("media_type"))
        print("  visual_asset_path:", sc.get("visual_asset_path"))
        print("  chart_theme:", sc.get("chart_theme"))
        print("  description:", sc.get("description")[:60] if sc.get("description") else None)

if __name__ == '__main__':
    asyncio.run(main())


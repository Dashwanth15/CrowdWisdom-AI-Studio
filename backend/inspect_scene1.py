import asyncio
import sys
sys.path.insert(0, 'backend')
from database.connection import connect_to_mongo, get_database
from bson import ObjectId
import json

async def main():
    await connect_to_mongo()
    db = get_database()
    script = await db.scripts.find_one({"_id": ObjectId("6aeec839a7ce69e62b6ae848")})
    scenes = script.get("scenes", [])
    if scenes:
        print("Keys in Scene 1:", list(scenes[0].keys()))
        for k, v in scenes[0].items():
            print(f"  {k}: {v}")

if __name__ == '__main__':
    asyncio.run(main())


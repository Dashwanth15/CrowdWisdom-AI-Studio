import asyncio
import sys
sys.path.insert(0, 'backend')
from database.connection import connect_to_mongo, get_database
from bson import ObjectId

async def main():
    await connect_to_mongo()
    db = get_database()
    script = await db.scripts.find_one({"_id": ObjectId("6aeec839a7ce69e62b6ae848")})
    scenes = script.get("scenes", [])
    if len(scenes) >= 4:
        print("Scene 4 visual_description:", scenes[3].get("visual_description"))

if __name__ == '__main__':
    asyncio.run(main())


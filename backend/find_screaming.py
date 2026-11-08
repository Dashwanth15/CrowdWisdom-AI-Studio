import asyncio
import sys
sys.path.insert(0, 'backend')
from database.connection import connect_to_mongo, get_database

async def main():
    await connect_to_mongo()
    db = get_database()
    scripts = await db.scripts.find({"scenes.voiceover": {"$regex": "screaming", "$options": "i"}}).to_list(10)
    for s in scripts:
        print(f"Script {s.get('_id')}: {s.get('title')}")
        for i, sc in enumerate(s.get("scenes", [])):
            print(f"  Scene {i+1} VO: {sc.get('voiceover')}")

if __name__ == '__main__':
    asyncio.run(main())


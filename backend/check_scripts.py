import asyncio
import sys
sys.path.insert(0, 'backend')
from database.connection import connect_to_mongo, get_database

async def main():
    await connect_to_mongo()
    db = get_database()
    scripts = await db.scripts.find({"core_message": {"$regex": "overwhelming", "$options": "i"}}).to_list(10)
    for s in scripts:
        print(f"ID: {s.get('_id')} | Title: {s.get('title')} | Campaign: {s.get('campaign_id')} | Status: {s.get('status')}")

if __name__ == '__main__':
    asyncio.run(main())

import asyncio
import pprint
from bson import ObjectId
from database.connection import connect_to_mongo, close_mongo_connection, get_database

async def check():
    await connect_to_mongo()
    db = get_database()
    cid = '6aedab3a1d4c801f02794eb7'
    camp = await db.campaigns.find_one({'_id': ObjectId(cid)})
    print('Campaign keys and full doc:')
    pprint.pprint(camp)
    
    # Check all scripts and print their campaign_id and title
    print("\nAll scripts in db:")
    async for s in db.scripts.find():
        print(f"ID: {s.get('_id')} | Title: {s.get('title')} | Campaign: {s.get('campaign_id')}")

    await close_mongo_connection()

if __name__ == '__main__':
    asyncio.run(check())


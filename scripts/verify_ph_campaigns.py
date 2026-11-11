import asyncio
import os
import sys

backend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend")
sys.path.insert(0, backend_dir)

from database.connection import connect_to_mongo, close_mongo_connection, get_database

async def verify():
    await connect_to_mongo()
    db = get_database()
    camps = await db.campaigns.find({"target_country": "PH"}).to_list(100)
    print(f"Total Philippines campaigns: {len(camps)}")
    for c in camps:
        cid = str(c["_id"])
        c_ads = await db.advertisements.count_documents({"$or": [{"campaign_id": cid}, {"associated_campaign_ids": cid}]})
        c_scripts = await db.scripts.count_documents({"campaign_id": cid})
        name = c.get("name")
        status = c.get("status")
        print(f"  - [{cid}] {name} | Research Ads: {c_ads} | Scripts: {c_scripts} | Status: {status}")
    await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(verify())


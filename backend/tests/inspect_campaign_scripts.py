import asyncio
import sys
import os

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, backend_dir)

from database.connection import get_database, connect_to_mongo
from bson import ObjectId

async def main():
    await connect_to_mongo()
    db = get_database()
    cid = "6aedc9fd5891425b46385f05"
    camp = await db.campaigns.find_one({"_id": ObjectId(cid)})
    print("Campaign name:", camp.get("name") if camp else "Not found")

    scripts = await db.scripts.find({"campaign_id": cid}).to_list(100)
    print(f"\nTotal scripts with campaign_id == '{cid}': {len(scripts)}")
    for s in scripts:
        print(f"  ID: {s['_id']} | approach: {s.get('approach')} | status: {s.get('status')} | title: {s.get('title') or s.get('campaign_title')}")

    # Check all scripts in DB
    all_scripts = await db.scripts.find({}).to_list(200)
    print(f"\nTotal scripts in DB: {len(all_scripts)}")
    cid_types = {}
    for s in all_scripts:
        c_id = str(s.get("campaign_id"))
        cid_types[c_id] = cid_types.get(c_id, 0) + 1
    print("Scripts by campaign_id:")
    for c_id, count in cid_types.items():
        print(f"  {c_id}: {count}")

if __name__ == "__main__":
    asyncio.run(main())

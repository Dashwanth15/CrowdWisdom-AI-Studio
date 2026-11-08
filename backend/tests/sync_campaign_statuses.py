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
    camps = await db.campaigns.find({}).to_list(100)
    print(f"Total campaigns found: {len(camps)}")
    
    counts = {"draft": 0, "active": 0, "completed": 0, "paused": 0}
    for c in camps:
        cid = str(c["_id"])
        ads = await db.advertisements.count_documents({"$or": [{"campaign_id": cid}, {"associated_campaign_ids": cid}]})
        scripts = await db.scripts.count_documents({"campaign_id": cid})
        videos = await db.video_jobs.count_documents({"campaign_id": cid, "status": "completed"})

        raw = c.get("status", "draft")
        if raw in ("paused", "archived"):
            computed = raw
        elif videos > 0:
            computed = "completed"
        elif scripts > 0 or ads > 0:
            computed = "active"
        else:
            computed = "draft"

        counts[computed] = counts.get(computed, 0) + 1
        await db.campaigns.update_one(
            {"_id": c["_id"]},
            {"$set": {
                "status": computed,
                "ads_researched": ads,
                "scripts_generated": scripts,
                "videos_generated": videos,
            }}
        )
        print(f"  {cid} | {c.get('name', 'Untitled')[:32]:<32} | {raw} -> {computed} (ads:{ads}, scripts:{scripts}, videos:{videos})")

    print("\nStatus distribution after synchronization:")
    for k, v in counts.items():
        print(f"  {k}: {v}")

if __name__ == "__main__":
    asyncio.run(main())


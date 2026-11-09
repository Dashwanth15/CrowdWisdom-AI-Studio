import asyncio
import os
import sys

backend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend")
sys.path.insert(0, backend_dir)

from database.connection import connect_to_mongo, get_database
from bson import ObjectId

async def inspect_campaign():
    await connect_to_mongo()
    db = get_database()
    cid = "6aec1fc21d839818c0dc7d4d"
    
    c = await db.campaigns.find_one({"_id": ObjectId(cid)})
    print("CAMPAIGN:", c)
    
    scripts = await db.scripts.find({"campaign_id": cid}).to_list(10)
    print(f"\nSCRIPTS ({len(scripts)}):")
    for s in scripts:
        print("  Script ID:", s["_id"], "Title:", s.get("title"))
        for sc in s.get("scenes", []):
            print("    Scene:", sc.get("scene_number"), "Visual URL:", sc.get("visual_asset_url"))

    briefs = await db.creative_briefs.find({"campaign_id": cid}).to_list(10)
    print(f"\nCREATIVE BRIEFS ({len(briefs)}):")
    for b in briefs:
        print("  Brief ID:", b["_id"])

    vjobs = await db.video_jobs.find({"campaign_id": cid}).to_list(10)
    print(f"\nVIDEO JOBS ({len(vjobs)}):")
    for v in vjobs:
        print("  Video Job ID:", v["_id"], "Status:", v.get("status"), "Video URL:", v.get("video_url"), "Thumb URL:", v.get("thumbnail_path"))

    assets = await db.assets.find({"campaign_id": cid}).to_list(10)
    print(f"\nASSETS ({len(assets)}):")
    for a in assets:
        print("  Asset:", a)

if __name__ == "__main__":
    asyncio.run(inspect_campaign())


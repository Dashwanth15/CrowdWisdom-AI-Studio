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
    camp = await db.campaigns.find_one({"name": {"$regex": "06102918"}})
    if not camp:
        print("No campaign found matching '06102918'")
        return

    cid = str(camp["_id"])
    print(f"Campaign: {cid} | {camp['name']} | Status: {camp.get('status')}")

    scripts = await db.scripts.find({"campaign_id": cid}).to_list(10)
    print(f"Total scripts: {len(scripts)}")
    for s in scripts:
        print(f"  Script: {s['_id']} | status: {s.get('status')} | title: {s.get('title')}")

    videos = await db.video_jobs.find({"campaign_id": cid}).to_list(10)
    print(f"\nTotal video jobs: {len(videos)}")
    for v in videos:
        print(f"  Video: {v['_id']}")
        print(f"    script_id: {v.get('script_id')}")
        print(f"    status: {v.get('status')}")
        print(f"    progress_percent: {v.get('progress_percent')}")
        print(f"    video_url: {v.get('video_url')}")
        print(f"    file_path: {v.get('file_path')}")
        print(f"    thumbnail_url: {v.get('thumbnail_url')}")
        print(f"    error: {v.get('error_message')}")
        print(f"    created_at: {v.get('created_at')}")

if __name__ == "__main__":
    asyncio.run(main())

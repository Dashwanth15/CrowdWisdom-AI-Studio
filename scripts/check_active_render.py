import asyncio
import os
import sys

backend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend")
sys.path.insert(0, backend_dir)

from database.connection import connect_to_mongo, get_database

async def check_active_render():
    await connect_to_mongo()
    db = get_database()
    active_jobs = await db.video_jobs.find({"status": {"$in": ["processing", "rendering", "composing", "queued"]}}).to_list(10)
    print(f"Active Video Jobs ({len(active_jobs)}):")
    for j in active_jobs:
        print(f"  ID: {j['_id']}")
        print(f"  Campaign ID: {j.get('campaign_id')}")
        print(f"  Script ID: {j.get('script_id')}")
        print(f"  Status: {j.get('status')}")
        print(f"  Progress: {j.get('progress_percent')}%")
        print(f"  Stage: {j.get('current_stage')}")
        print(f"  Started At: {j.get('started_at')}")
        print()

if __name__ == "__main__":
    asyncio.run(check_active_render())


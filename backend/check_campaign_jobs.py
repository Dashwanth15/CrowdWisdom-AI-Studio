import asyncio
import sys
sys.path.insert(0, 'backend')
from database.connection import connect_to_mongo, get_database

async def main():
    await connect_to_mongo()
    db = get_database()
    campaign_id = "6aedc9fd5891425b46385f05"
    jobs = await db.video_jobs.find({"campaign_id": campaign_id}).to_list(100)
    print(f"Total jobs for campaign {campaign_id}: {len(jobs)}")
    for j in jobs:
        print(f"ID: {j.get('_id')} | Script: {j.get('script_id')} | Status: {j.get('status')} | Progress: {j.get('progress_percent')} | Video: {j.get('video_path')}")

    scripts = await db.scripts.find({"campaign_id": campaign_id}).to_list(100)
    print(f"\nTotal scripts for campaign {campaign_id}: {len(scripts)}")
    for s in scripts:
        print(f"ID: {s.get('_id')} | Title: {s.get('title')} | Status: {s.get('status')}")

if __name__ == '__main__':
    asyncio.run(main())

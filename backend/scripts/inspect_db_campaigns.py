import asyncio
import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from database.connection import connect_to_mongo, get_database

async def main():
    await connect_to_mongo()
    db = get_database()
    campaigns = await db.campaigns.find().to_list(10)
    print(f"Total Campaigns: {len(campaigns)}")
    for c in campaigns:
        print(f"Campaign: id={c['_id']} | name={c.get('name')} | status={c.get('status')}")
    
    scripts = await db.scripts.find({"status": "approved"}).to_list(10)
    print(f"\nApproved Scripts: {len(scripts)}")
    for s in scripts:
        print(f"Script: id={s['_id']} | title={s.get('title')} | campaign_id={s.get('campaign_id')} | scenes={len(s.get('scenes', []))}")

    videos = await db.video_jobs.find().to_list(10)
    print(f"\nExisting Video Jobs: {len(videos)}")
    for v in videos:
        print(f"VideoJob: id={v['_id']} | status={v.get('status')} | url={v.get('video_url')}")

if __name__ == "__main__":
    asyncio.run(main())


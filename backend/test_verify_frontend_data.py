import asyncio
import sys
sys.path.insert(0, 'backend')
from database.connection import connect_to_mongo, get_database
from bson import ObjectId

async def main():
    await connect_to_mongo()
    db = get_database()
    c = await db.campaigns.find_one({'_id': ObjectId('6aedc9fd5891425b46385f05')})
    vids = await db.video_jobs.find({'campaign_id': '6aedc9fd5891425b46385f05'}).to_list(10)
    scripts = await db.scripts.find({'campaign_id': '6aedc9fd5891425b46385f05'}).to_list(10)
    print("Campaign status:", c.get("status"), "videos_generated:", c.get("videos_generated"))
    print(f"Scripts count: {len(scripts)}")
    for s in scripts:
        print(f"  Script: {s.get('_id')} | Title: {s.get('title')} | Status: {s.get('status')}")
    print(f"Videos count: {len(vids)}")
    for v in vids:
        print(f"  Video: {v.get('_id')} | Script: {v.get('script_id')} | Status: {v.get('status')} | URL: {v.get('video_url')} | Dur: {v.get('duration_actual')}s")

if __name__ == '__main__':
    asyncio.run(main())


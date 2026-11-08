import asyncio
import sys
from pathlib import Path
from bson import ObjectId

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from database.connection import connect_to_mongo, get_database

async def main():
    await connect_to_mongo()
    db = get_database()
    script = await db.scripts.find_one({"title": "The Signal in the Swarm"})
    print("Script found:", script.get("_id"), "campaign_id:", script.get("campaign_id"))
    
    videos = await db.video_jobs.find({"campaign_id": script.get("campaign_id")}).to_list(10)
    print(f"Videos for this campaign ({len(videos)}):")
    for v in videos:
        print(f"  Video: id={v.get('_id')}, script_id={v.get('script_id')}, status={v.get('status')}, pct={v.get('progress_percent')}, url={v.get('video_url')}")

    all_vids_for_script = await db.video_jobs.find({"script_id": str(script.get("_id"))}).to_list(10)
    print(f"Videos for this script_id ({len(all_vids_for_script)}):")
    for v in all_vids_for_script:
        print(f"  Video: id={v.get('_id')}, script_id={v.get('script_id')}, status={v.get('status')}, pct={v.get('progress_percent')}, url={v.get('video_url')}")

if __name__ == "__main__":
    asyncio.run(main())


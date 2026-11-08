import asyncio
import sys
from bson import ObjectId

backend_dir = r"c:\Users\dashw\OneDrive\Desktop\my projects\CrowdWisdom AI Studio\backend"
sys.path.insert(0, backend_dir)

from config import settings
from motor.motor_asyncio import AsyncIOMotorClient

async def main():
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DB_NAME]
    
    # Search for script with title containing "The 60-Second Morning Protocol"
    script = await db.scripts.find_one({"title": {"$regex": "The 60-Second Morning Protocol"}})
    if script:
        print(f"Found Script: {script['_id']} | Status: {script.get('status')}")
        print(f"Campaign ID: {script.get('campaign_id')}")
        for sc in script.get("scenes", []):
            print(f"  Scene {sc.get('scene_number')}: visual_type={sc.get('scene_visual_type') or sc.get('visual_type')} | media_type={sc.get('media_type')} | path={sc.get('visual_asset_path')}")
            
        # Find video jobs for this script or campaign
        vjobs = await db.video_jobs.find({"$or": [{"script_id": str(script["_id"])}, {"campaign_id": str(script.get("campaign_id"))}]}).sort("_id", -1).to_list(10)
        print(f"\nFound {len(vjobs)} video jobs:")
        for vj in vjobs:
            print(f"  Job {vj['_id']}: status={vj.get('status')} progress={vj.get('progress_percent')}% stage='{vj.get('current_stage')}' error='{vj.get('error_message')}' started={vj.get('started_at')}")
    else:
        print("Script 'The 60-Second Morning Protocol' not found, searching latest scripts...")
        latest = await db.scripts.find().sort("_id", -1).to_list(5)
        for l in latest:
            print(f"  Script {l['_id']}: {l.get('title')}")

if __name__ == "__main__":
    asyncio.run(main())


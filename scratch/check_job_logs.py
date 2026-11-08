import asyncio
import sys
import os
from bson import ObjectId

backend_dir = r"c:\Users\dashw\OneDrive\Desktop\my projects\CrowdWisdom AI Studio\backend"
sys.path.insert(0, backend_dir)

from config import settings
from motor.motor_asyncio import AsyncIOMotorClient

async def main():
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DB_NAME]
    
    job_id = "6aef6957547c27366bbc5f33"
    job = await db.video_jobs.find_one({"_id": ObjectId(job_id)})
    print("Video Job Document:")
    for k, v in job.items():
        print(f"  {k}: {v}")

    # Check execution logs for this job or campaign
    logs = await db.execution_logs.find({"$or": [{"job_id": job_id}, {"campaign_id": job.get("campaign_id")}]}).sort("created_at", -1).to_list(20)
    print(f"\nExecution Logs count: {len(logs)}")
    for l in logs:
        print(f"  [{l.get('created_at')}] [{l.get('stage')}] ({l.get('progress_percent')}%) {l.get('message')}")

    # Check if the partial video file exists on disk
    vid_file = f"media/videos/video_{job_id}.mp4"
    if os.path.exists(vid_file):
        print(f"\nVideo file exists: {vid_file}, size: {os.path.getsize(vid_file)} bytes")
    else:
        print(f"\nVideo file does NOT exist at: {vid_file}")

if __name__ == "__main__":
    asyncio.run(main())


import asyncio
import sys
from pathlib import Path

backend_dir = r"c:\Users\dashw\OneDrive\Desktop\my projects\CrowdWisdom AI Studio\backend"
sys.path.insert(0, backend_dir)

from config import settings
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

async def test():
    client = AsyncIOMotorClient(settings.MONGODB_URL, serverSelectionTimeoutMS=8000)
    try:
        db = client[settings.MONGODB_DB_NAME]
        
        # Check all video jobs for this campaign
        cid = "6aecdf6c76d0a89187b9b7fc"
        jobs = await db.video_jobs.find({"campaign_id": cid}).to_list(10)
        print(f"Total video jobs for campaign {cid}: {len(jobs)}")
        for j in jobs:
            print(f"  ID: {j['_id']} | Status: {j['status']} | Progress: {j.get('progress_percent')}% | URL: {j.get('video_url')}")
    finally:
        client.close()

if __name__ == '__main__':
    asyncio.run(test())


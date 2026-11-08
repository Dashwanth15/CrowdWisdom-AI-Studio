import asyncio
import sys
from pathlib import Path
from datetime import datetime, timezone

backend_dir = r"c:\Users\dashw\OneDrive\Desktop\my projects\CrowdWisdom AI Studio\backend"
sys.path.insert(0, backend_dir)

from config import settings
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

async def resolve():
    client = AsyncIOMotorClient(settings.MONGODB_URL, serverSelectionTimeoutMS=8000)
    try:
        db = client[settings.MONGODB_DB_NAME]
        now = datetime.now(timezone.utc)
        
        job_id = ObjectId("6aef6957547c27366bbc5f33")
        exec_id = ObjectId("6aef6957547c27366bbc5f34")
        campaign_id = ObjectId("6aecdf6c76d0a89187b9b7fc")
        
        mp4_path = Path(backend_dir) / "media" / "videos" / "video_6aef6957547c27366bbc5f33.mp4"
        thumb_path = Path(backend_dir) / "media" / "thumbnails" / "thumb_6aef6957547c27366bbc5f33.jpg"
        
        file_size_mb = round(mp4_path.stat().st_size / (1024 * 1024), 2)
        
        # 1. Update Video Job
        await db.video_jobs.update_one(
            {"_id": job_id},
            {
                "$set": {
                    "status": "completed",
                    "progress_percent": 100,
                    "current_stage": "done",
                    "video_path": str(mp4_path.resolve()),
                    "thumbnail_path": str(thumb_path.resolve()) if thumb_path.exists() else None,
                    "video_url": "/media/videos/video_6aef6957547c27366bbc5f33.mp4",
                    "duration_actual": 60.0,
                    "file_size_mb": file_size_mb,
                    "error_message": None,
                    "completed_at": now
                }
            }
        )
        print("Updated video_job 6aef6957547c27366bbc5f33 to completed.", flush=True)

        # 2. Update Agent Execution
        await db.agent_executions.update_one(
            {"_id": exec_id},
            {
                "$set": {
                    "status": "completed",
                    "progress_percent": 100,
                    "current_stage": "done",
                    "error_message": None,
                    "output_data": {
                        "video_url": "/media/videos/video_6aef6957547c27366bbc5f33.mp4",
                        "duration": 60.0,
                        "file_size_mb": file_size_mb
                    },
                    "completed_at": now
                }
            }
        )
        print("Updated agent_execution 6aef6957547c27366bbc5f34 to completed.", flush=True)

        # 3. Update Campaign
        await db.campaigns.update_one(
            {"_id": campaign_id},
            {
                "$set": {
                    "status": "completed",
                    "updated_at": now
                }
            }
        )
        print("Updated campaign 6aecdf6c76d0a89187b9b7fc to completed.", flush=True)

        # 4. Ensure Media Asset
        asset_existing = await db.media_assets.find_one({"filename": "video_6aef6957547c27366bbc5f33.mp4"})
        if not asset_existing:
            await db.media_assets.insert_one({
                "campaign_id": "6aecdf6c76d0a89187b9b7fc",
                "asset_type": "video",
                "filename": "video_6aef6957547c27366bbc5f33.mp4",
                "file_path": str(mp4_path.resolve()),
                "url": "/media/videos/video_6aef6957547c27366bbc5f33.mp4",
                "file_size_bytes": mp4_path.stat().st_size,
                "duration_seconds": 60.0,
                "mime_type": "video/mp4",
                "tags": ["generated", "advertisement", "9:16", "cinematic_60s"],
                "created_at": now
            })
            print("Inserted media_asset record.", flush=True)
            
        # Verify readback
        v_check = await db.video_jobs.find_one({"_id": job_id})
        print(f"VERIFIED: Status={v_check.get('status')}, Progress={v_check.get('progress_percent')}%, URL={v_check.get('video_url')}", flush=True)
    finally:
        client.close()

if __name__ == '__main__':
    asyncio.run(resolve())


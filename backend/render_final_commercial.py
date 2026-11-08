import asyncio
import time
from datetime import datetime, timezone
from bson import ObjectId
from database.connection import connect_to_mongo, close_mongo_connection, get_database
from agents.video_production_agent import video_production_agent

async def render():
    await connect_to_mongo()
    db = get_database()
    campaign_id = "6aedc9fd5891425b46385f05"
    script_id = "6aeec839a7ce69e62b6ae848"

    # 1. Ensure script is marked approved
    await db.scripts.update_one(
        {"_id": ObjectId(script_id)},
        {"$set": {"status": "approved", "approved_at": datetime.now(timezone.utc)}}
    )
    print(f"Script {script_id} set to 'approved'.")

    # 2. Find or create video job for this script
    job = await db.video_jobs.find_one({"script_id": script_id, "campaign_id": campaign_id}, sort=[("created_at", -1)])
    if not job:
        job_doc = {
            "campaign_id": campaign_id,
            "script_id": script_id,
            "status": "queued",
            "aspect_ratio": "9:16",
            "duration_seconds": 45,
            "quality": "high",
            "progress_percent": 0,
            "created_at": time.time(),
        }
        res = await db.video_jobs.insert_one(job_doc)
        job_id = str(res.inserted_id)
    else:
        job_id = str(job["_id"])

    print(f"Executing video production for Job ID {job_id}...")
    t0 = time.time()
    await video_production_agent.execute(
        campaign_id=campaign_id,
        execution_id="phase2_verification",
        input_data={
            "campaign_id": campaign_id,
            "video_job_id": job_id,
            "script_id": script_id,
            "aspect_ratio": "9:16",
            "duration_seconds": 45,
            "quality": "high",
        }
    )
    dt = time.time() - t0
    print(f"Video production successfully executed in {dt:.1f}s!")

    updated_job = await db.video_jobs.find_one({"_id": ObjectId(job_id)})
    print("Job status:", updated_job.get("status"))
    print("Video URL:", updated_job.get("video_url"))
    print("File size:", updated_job.get("file_size_mb"), "MB")

    await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(render())

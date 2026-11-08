import asyncio
import sys
import os
import time
from pathlib import Path
from bson import ObjectId
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).parent.parent))
from database.connection import connect_to_mongo, close_mongo_connection, get_database
from agents.video_production_agent import VideoProductionAgent

async def run_test_render():
    await connect_to_mongo()
    db = get_database()
    
    campaign_id = "6aedc9fd5891425b46385f05"
    script_id = "6aef2e9591eea0f23a8051eb"
    
    script_doc = await db.scripts.find_one({"_id": ObjectId(script_id)})
    if not script_doc:
        print(f"Error: Script {script_id} not found.")
        return
        
    print(f"Starting controlled test render for: {script_doc.get('title')}")
    print(f"Number of scenes: {len(script_doc.get('scenes', []))}")
    for sc in script_doc.get("scenes", []):
        print(f"  Scene {sc.get('scene_number')}: {sc.get('media_type')} | {sc.get('visual_asset_path')}")

    # Create video job in db
    target_duration = 45
    video_job_doc = {
        "campaign_id": campaign_id,
        "script_id": script_id,
        "status": "processing",
        "aspect_ratio": "9:16",
        "duration_seconds": target_duration,
        "quality": "high",
        "progress_percent": 5,
        "current_stage": "initializing",
        "video_path": None,
        "thumbnail_path": None,
        "video_url": None,
        "duration_actual": None,
        "file_size_mb": None,
        "error_message": None,
        "production_log": [],
        "started_at": datetime.now(timezone.utc),
        "completed_at": None,
        "created_at": datetime.now(timezone.utc),
    }
    job_result = await db.video_jobs.insert_one(video_job_doc)
    video_job_id = str(job_result.inserted_id)
    print(f"Created video_job_id: {video_job_id}")

    # Create execution record in db
    exec_doc = {
        "campaign_id": campaign_id,
        "agent_type": "video_production",
        "task_name": "Cinematic Video Rendering",
        "status": "pending",
        "input_data": {},
        "created_at": datetime.now(timezone.utc)
    }
    exec_result = await db.agent_executions.insert_one(exec_doc)
    execution_id = str(exec_result.inserted_id)
    print(f"Created execution_id: {execution_id}")

    agent = VideoProductionAgent()
    video_input = {
        "script_id": script_id,
        "aspect_ratio": "9:16",
        "duration_seconds": target_duration,
        "quality": "high",
        "campaign_id": campaign_id,
        "video_job_id": video_job_id,
    }

    t0 = time.time()
    try:
        result = await agent.execute(
            campaign_id=campaign_id,
            execution_id=execution_id,
            input_data=video_input
        )
        elapsed = time.time() - t0
        print(f"\nRender completed in {elapsed:.1f}s!")
        print("Result:", result)
        
        # Verify generated job in DB
        updated_job = await db.video_jobs.find_one({"_id": ObjectId(video_job_id)})
        print("Final Job Status:", updated_job.get("status"))
        print("Final Video Path:", updated_job.get("video_path"))
        print("Final Video URL:", updated_job.get("video_url"))
        print(f"File Size: {updated_job.get('file_size_mb')} MB, Duration: {updated_job.get('duration_actual')}s")
        
    except Exception as e:
        print(f"\nRender failed: {e}")
        import traceback
        traceback.print_exc()

    await close_mongo_connection()

if __name__ == '__main__':
    asyncio.run(run_test_render())

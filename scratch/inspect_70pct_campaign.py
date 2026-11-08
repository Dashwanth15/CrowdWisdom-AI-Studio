import asyncio
import sys
from pathlib import Path

backend_dir = r"c:\Users\dashw\OneDrive\Desktop\my projects\CrowdWisdom AI Studio\backend"
sys.path.insert(0, backend_dir)

from config import settings
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

async def inspect():
    client = AsyncIOMotorClient(settings.MONGODB_URL, serverSelectionTimeoutMS=8000)
    try:
        db = client[settings.MONGODB_DB_NAME]
        cid = "6aedabfe3b41067ff03d9850"
        
        print("="*60)
        print(f"INSPECTING CAMPAIGN: {cid}")
        print("="*60)
        camp = await db.campaigns.find_one({"_id": ObjectId(cid)})
        if camp:
            print(f"Campaign: {camp.get('title')} | Status: {camp.get('status')}")
        else:
            print("Campaign not found!")
            
        print("\nSCRIPTS:")
        scripts = await db.scripts.find({"campaign_id": cid}).to_list(10)
        for s in scripts:
            print(f"  Script ID: {s['_id']} | Title: {s.get('title')} | Status: {s.get('status')}")
            for sc in s.get("scenes", []):
                print(f"    Scene {sc.get('scene_number')} ({sc.get('duration_seconds')}s): {sc.get('media_type')} | asset: {sc.get('visual_asset_path')} | status: {sc.get('visual_asset_status')}")

        print("\nVIDEO JOBS:")
        vjobs = await db.video_jobs.find({"campaign_id": cid}).sort("created_at", -1).to_list(10)
        for vj in vjobs:
            print(f"  Job ID: {vj['_id']}")
            for k in ["status", "progress_percent", "current_stage", "error_message", "started_at", "completed_at", "created_at", "video_path", "video_url"]:
                print(f"    {k}: {vj.get(k)}")

        print("\nAGENT EXECUTIONS:")
        execs = await db.agent_executions.find({"campaign_id": cid}).sort("created_at", -1).to_list(10)
        for ex in execs:
            print(f"  Exec ID: {ex['_id']} | Agent: {ex.get('agent_type')} | Status: {ex.get('status')} | Stage: {ex.get('current_stage')} | Pct: {ex.get('progress_percent')}")
            print(f"    Error: {ex.get('error_message')}")
            print(f"    Started: {ex.get('started_at')} | Completed: {ex.get('completed_at')}")

    finally:
        client.close()

if __name__ == '__main__':
    asyncio.run(inspect())


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
    
    exec_doc = await db.agent_executions.find_one({"input_data.video_job_id": "6aef6957547c27366bbc5f33"})
    if exec_doc:
        print("Agent Execution Doc:")
        for k, v in exec_doc.items():
            print(f"  {k}: {v}")
    else:
        print("Agent execution not found by input_data.video_job_id, searching latest...")
        latest = await db.agent_executions.find({"agent_type": "video_production"}).sort("_id", -1).to_list(3)
        for l in latest:
            print(f"  Exec {l['_id']}: status={l.get('status')} stage={l.get('current_stage')} pct={l.get('progress_percent')}%")

if __name__ == "__main__":
    asyncio.run(main())


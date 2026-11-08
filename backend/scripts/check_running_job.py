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
    job = await db.video_jobs.find_one({"_id": ObjectId("6aee329ffadd50fa6e006d2b")})
    if job:
        print(f"Status: {job.get('status')}")
        print(f"Progress: {job.get('progress_percent')}%")
        print(f"Stage: {job.get('current_stage')}")
        print(f"Error: {job.get('error_message')}")
        print(f"Video URL: {job.get('video_url')}")
        print(f"Started: {job.get('started_at')}")
        print(f"Completed: {job.get('completed_at')}")

if __name__ == "__main__":
    asyncio.run(main())


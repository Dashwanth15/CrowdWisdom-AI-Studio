import asyncio
import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from database.connection import connect_to_mongo, get_database

async def main():
    await connect_to_mongo()
    db = get_database()
    jobs = await db.video_jobs.find().sort("created_at", -1).to_list(10)
    for j in jobs:
        print(f"Job {j.get('_id')}: status={j.get('status')}, script_id={j.get('script_id')}, pct={j.get('progress_percent')}, stage={j.get('current_stage')}, error={j.get('error_message')}, created={j.get('created_at')}")

if __name__ == "__main__":
    asyncio.run(main())


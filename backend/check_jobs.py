import asyncio
import sys
sys.path.insert(0, 'backend')
from database.connection import connect_to_mongo, get_database

async def main():
    await connect_to_mongo()
    db = get_database()
    jobs = await db.video_jobs.find().to_list(100)
    for j in jobs:
        print(f"ID: {j.get('_id')} | Status: {j.get('status')} | Dur: {j.get('duration_actual')} | Path: {j.get('video_path')} | Script: {j.get('script_id')}")

if __name__ == '__main__':
    asyncio.run(main())

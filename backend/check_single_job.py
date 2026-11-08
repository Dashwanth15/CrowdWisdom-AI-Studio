import asyncio
import sys
sys.path.insert(0, 'backend')
from database.connection import connect_to_mongo, get_database
from bson import ObjectId

async def main():
    await connect_to_mongo()
    db = get_database()
    j = await db.video_jobs.find_one({'_id': ObjectId('6aeecee204a3362a8a5d4a18')})
    print(f"Status: {j.get('status')} | Progress: {j.get('progress_percent')}% | Stage: {j.get('current_stage')}")

if __name__ == '__main__':
    asyncio.run(main())


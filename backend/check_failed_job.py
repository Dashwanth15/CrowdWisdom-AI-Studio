import asyncio
import sys
sys.path.insert(0, 'backend')
from database.connection import connect_to_mongo, get_database
from bson import ObjectId

async def main():
    await connect_to_mongo()
    db = get_database()
    job = await db.video_jobs.find_one({"_id": ObjectId("6aeec824a7ce69e62b6ae844")})
    print("Job 6aeec824a7ce69e62b6ae844:", job)

if __name__ == '__main__':
    asyncio.run(main())


import asyncio
import sys
sys.path.insert(0, 'backend')
from database.connection import connect_to_mongo, get_database
from api.videos import _serialize_job

async def main():
    await connect_to_mongo()
    db = get_database()
    cursor = db.video_jobs.find({"campaign_id": "6aedc9fd5891425b46385f05"}).sort("created_at", -1)
    docs = await cursor.to_list(10)
    for d in docs:
        s = _serialize_job(d)
        print("OK:", s.id, s.status, s.created_at, s.video_url, s.script_id)

if __name__ == '__main__':
    asyncio.run(main())

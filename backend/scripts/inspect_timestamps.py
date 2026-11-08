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
    job = await db.video_jobs.find_one({"_id": ObjectId("6aee29fefadd50fa6e006cee")})
    print("started_at:", job.get("started_at"))
    print("completed_at:", job.get("completed_at"))
    print("created_at:", job.get("created_at"))
    print("duration_actual:", job.get("duration_actual"))
    print("file_size_mb:", job.get("file_size_mb"))

if __name__ == "__main__":
    asyncio.run(main())


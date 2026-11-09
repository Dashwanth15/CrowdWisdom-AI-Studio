import asyncio
import os
import sys

backend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend")
sys.path.insert(0, backend_dir)

from database.connection import connect_to_mongo, get_database
from bson import ObjectId

async def main():
    await connect_to_mongo()
    db = get_database()
    j = await db.video_jobs.find_one({"_id": ObjectId("6af1c417016939d0a6d7eb90")})
    print("STATUS:        ", j.get("status"))
    print("PROGRESS:      ", j.get("progress_percent"))
    print("VIDEO_URL:     ", j.get("video_url"))
    print("DURATION_ACTUAL:", j.get("duration_actual"))
    print("FILE_SIZE_MB:  ", j.get("file_size_mb"))
    print("ERROR_MESSAGE: ", j.get("error_message"))
    print("COMPLETED_AT:  ", j.get("completed_at"))

if __name__ == "__main__":
    asyncio.run(main())


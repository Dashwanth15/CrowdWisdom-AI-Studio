import asyncio
import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from database.connection import connect_to_mongo, get_database

async def main():
    await connect_to_mongo()
    db = get_database()
    res = await db.video_jobs.update_many({"status": "completed"}, {"$set": {"error_message": None}})
    print(f"Updated completed jobs: {res.modified_count}")

if __name__ == "__main__":
    asyncio.run(main())


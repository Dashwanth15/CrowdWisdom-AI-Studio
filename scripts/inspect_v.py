import asyncio, os, sys, json
backend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend")
sys.path.insert(0, backend_dir)
from database.connection import connect_to_mongo, get_database
from bson import ObjectId

async def main():
    await connect_to_mongo()
    db = get_database()
    v = await db.videos.find_one({"_id": ObjectId("6af167eb009d4af8ba1f9a37")})
    print("VIDEO:", json.dumps(v, default=str, indent=2))
    vj = await db.video_jobs.find_one({"_id": ObjectId("6aeffbb319535e71781335c2")})
    print("VIDEO JOB:", json.dumps(vj, default=str, indent=2))

if __name__ == "__main__":
    asyncio.run(main())

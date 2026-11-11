import asyncio
import os
from pathlib import Path
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / "backend" / ".env")
uri = os.environ.get("MONGODB_URL")
client = AsyncIOMotorClient(uri)
db = client["crowdwisdom_ai_studio"]

async def main():
    for sid in ["6af1676f009d4af8ba1f9a33", "6aeffb4b19535e71781335b0"]:
        s = await db.scripts.find_one({"_id": ObjectId(sid)})
        if s:
            print(f"=== Script {sid} ===")
            print("Title:", s.get("title"))
            scenes = s.get("scenes", [])
            for sc in scenes:
                print("  Scene:", sc.get("scene_number"), "path:", sc.get("visual_asset_path"), "url:", sc.get("visual_asset_url"))

asyncio.run(main())

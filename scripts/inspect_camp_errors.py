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
    camp = await db.campaigns.find_one({"_id": ObjectId("6aec1fc21d839818c0dc7d4d")})
    print("Campaign:", camp.get("name"), camp.get("target_country"), camp.get("status"))
    scripts = await db.scripts.find({"campaign_id": "6aec1fc21d839818c0dc7d4d"}).to_list(10)
    print(f"Scripts count: {len(scripts)}")
    for s in scripts:
        print("Script id:", s.get("_id"), s.get("title") or s.get("campaign_title"), s.get("status"))

asyncio.run(main())

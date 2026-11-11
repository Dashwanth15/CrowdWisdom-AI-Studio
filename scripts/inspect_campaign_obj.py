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
    c = await db.campaigns.find_one({"_id": ObjectId("6af40fdda1c92020dd501115")})
    if c:
        print("Campaign Name:", c.get("name"))
        print("Target Country:", c.get("target_country"))
        print("Target Audience:", c.get("target_audience"))

asyncio.run(main())

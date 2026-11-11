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
    s = await db.scripts.find_one({"_id": ObjectId("6af4151714e1e47fbd321144")})
    if not s:
        print("Script not found by ObjectId, searching by title...")
        s = await db.scripts.find_one({"title": {"$regex": "NSE Blue Chip"}})
    if s:
        print("Script ID:", s.get("_id"))
        print("Campaign ID:", s.get("campaign_id"))
        print("Title:", s.get("title") or s.get("campaign_title"))
        print("Target Country:", s.get("target_country"))
        print("Status:", s.get("status"))
        for sc in s.get("scenes", []):
            print(f"Scene {sc.get('scene_number')}:")
            print("  Vis Desc:", sc.get("visual_description")[:80])
            print("  VO:", sc.get("voiceover")[:80])
            print("  OST:", sc.get("on_screen_text"))
            print("  Asset URL:", sc.get("visual_asset_url"))
            print("  Asset Path:", sc.get("visual_asset_path"))

asyncio.run(main())

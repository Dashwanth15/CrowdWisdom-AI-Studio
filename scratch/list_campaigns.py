import asyncio
import sys
sys.path.insert(0, r"backend")
from config import settings
from motor.motor_asyncio import AsyncIOMotorClient

async def main():
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DB_NAME]
    camps = await db.campaigns.find().to_list(10)
    print("Campaigns count:", len(camps))
    for c in camps:
        print(f"Campaign {c.get('_id')}: title={c.get('title')} product_name={c.get('product_name')}")
    
    scripts = await db.scripts.find().sort("_id", -1).to_list(5)
    print("\nRecent scripts count:", len(scripts))
    for s in scripts:
        print(f"Script {s.get('_id')}: camp={s.get('campaign_id')} (type: {type(s.get('campaign_id'))}) title={s.get('title')}")

if __name__ == "__main__":
    asyncio.run(main())


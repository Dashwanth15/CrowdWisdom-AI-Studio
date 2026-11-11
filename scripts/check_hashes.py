import asyncio
import os
import sys
from pathlib import Path
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / "backend" / ".env")
uri = os.environ.get("MONGODB_URL")
client = AsyncIOMotorClient(uri)
db = client["crowdwisdom_ai_studio"]

async def main():
    print("Connected to Mongo...")
    hashes = ["f009d4", "b19535", "21d839", "6aec1fc"]
    for h in hashes:
        print(f"\n--- Searching for {h} ---")
        for coll_name in ["scripts", "campaigns", "media_assets", "advertisements"]:
            cursor = db[coll_name].find()
            async for doc in cursor:
                doc_str = str(doc)
                if h in doc_str:
                    print(f"Found {h} in {coll_name} id={doc.get('_id')}")
                    # let's find matching fields
                    for k, v in doc.items():
                        if h in str(v):
                            print(f"  Field {k}: {str(v)[:150]}")

asyncio.run(main())

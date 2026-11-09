import asyncio
import os
import sys

backend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend")
sys.path.insert(0, backend_dir)

from database.connection import connect_to_mongo, get_database
from bson import ObjectId

async def check():
    await connect_to_mongo()
    db = get_database()

    print("--- Campaigns ---")
    campaigns = await db.campaigns.find().to_list(100)
    for c in campaigns:
        cid = str(c["_id"])
        print(f"Campaign: {cid} | Name: {c.get('name')}")
        if cid.startswith("6aec1fc") or "6aec1fc" in cid:
            print("  *** FOUND MATCHING CAMPAIGN:", cid, c.get("name"))

    print("\n--- Searching for f009d4af8ba1f9a33, b19535e71781335b0, 21d839818c0dc7d4d ---")
    for token in ["f009d4af8ba1f9a33", "b19535e71781335b0", "21d839818c0dc7d4d"]:
        # Search campaigns
        c_match = await db.campaigns.find({"_id": ObjectId(token) if ObjectId.is_valid(token) else None}).to_list(1)
        if c_match:
            print(f"Token {token} matched campaign: {c_match[0].get('name')}")
        # Search scripts
        s_match = await db.scripts.find({"_id": ObjectId(token) if ObjectId.is_valid(token) else None}).to_list(1)
        if s_match:
            print(f"Token {token} matched script: {s_match[0].get('title')}")
        # Search video jobs
        v_match = await db.video_jobs.find({"_id": ObjectId(token) if ObjectId.is_valid(token) else None}).to_list(1)
        if v_match:
            print(f"Token {token} matched video_job: {v_match[0]}")
        # Search creative briefs
        cb_match = await db.creative_briefs.find({"_id": ObjectId(token) if ObjectId.is_valid(token) else None}).to_list(1)
        if cb_match:
            print(f"Token {token} matched creative_brief: {cb_match[0]}")

if __name__ == "__main__":
    asyncio.run(check())


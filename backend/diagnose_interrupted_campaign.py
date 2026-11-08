import asyncio
import pprint
from bson import ObjectId
from database.connection import connect_to_mongo, close_mongo_connection, get_database

async def check():
    await connect_to_mongo()
    db = get_database()
    
    print("=== SEARCHING SCRIPTS WITH 'Signal' IN TITLE ===")
    scripts = await db.scripts.find({"title": {"$regex": "Signal", "$options": "i"}}).to_list(100)
    for s in scripts:
        print(f"ID: {s.get('_id')} | Title: {s.get('title')} | Campaign: {s.get('campaign_id')} (type {type(s.get('campaign_id'))}) | Status: {s.get('status')}")
        print(f"  Hook: {s.get('hook')}")
        for sc in s.get('scenes', []):
            print(f"    Scene {sc.get('scene_number')}: media_type={sc.get('media_type')} | theme={sc.get('chart_theme')} | path={sc.get('visual_asset_path')}")
            print(f"      VO: {sc.get('voiceover')}")
            print(f"      Desc: {sc.get('visual_description')}")

    print("\n=== SEARCHING VIDEO JOBS WITH STATUS 'interrupted' OR 'failed' ===")
    failed_jobs = await db.video_jobs.find({"status": {"$in": ["interrupted", "failed", "processing", "rendering"]}}).to_list(100)
    for j in failed_jobs:
        print(f"Job ID: {j.get('_id')} | Campaign: {j.get('campaign_id')} | Script: {j.get('script_id')} | Status: {j.get('status')} | Progress: {j.get('progress_percent')} | Stage: {j.get('current_stage')}")
        print(f"  Error: {j.get('error_message')}")

    print("\n=== RECENT 10 VIDEO JOBS ===")
    recent_jobs = await db.video_jobs.find().sort("created_at", -1).to_list(10)
    for j in recent_jobs:
        print(f"Job ID: {j.get('_id')} | Campaign: {j.get('campaign_id')} | Script: {j.get('script_id')} | Status: {j.get('status')} | Progress: {j.get('progress_percent')} | Stage: {j.get('current_stage')}")
        print(f"  Error: {j.get('error_message')} | Video: {j.get('video_path')}")

    await close_mongo_connection()

if __name__ == '__main__':
    asyncio.run(check())

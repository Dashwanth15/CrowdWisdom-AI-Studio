import asyncio
import sys
from pathlib import Path
from bson import ObjectId

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from database.connection import connect_to_mongo, get_database

async def main():
    await connect_to_mongo()
    db = get_database()
    script = await db.scripts.find_one({"_id": ObjectId("6aee29a4fadd50fa6e006ce4")})
    print(f"Script: title={script.get('title')}, duration={script.get('duration_seconds')}, scenes count={len(script.get('scenes', []))}")
    for s in script.get("scenes", []):
        print(f"  Scene {s.get('scene_number')}: dur={s.get('duration_seconds')}s, visual_type={s.get('visual_type')}, visual_prompt={s.get('visual_prompt', '')[:60]}, vo={s.get('voiceover', '')[:60]}")
    
    job = await db.video_jobs.find_one({"_id": ObjectId("6aee29fefadd50fa6e006cee")})
    print(f"\nJob details:")
    print(f"  status: {job.get('status')}")
    print(f"  progress: {job.get('progress_percent')}")
    print(f"  stage: {job.get('current_stage')}")
    print(f"  video_url: {job.get('video_url')}")
    print(f"  video_path: {job.get('video_path')}")
    print(f"  error: {job.get('error_message')}")
    print(f"  log: {job.get('production_log')}")

if __name__ == "__main__":
    asyncio.run(main())


import asyncio
import sys
import requests
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from database.connection import connect_to_mongo, get_database
from services.auth_service import create_access_token

async def get_token():
    await connect_to_mongo()
    db = get_database()
    user = await db.users.find_one({"role": "admin"})
    return create_access_token({"sub": str(user["_id"]), "role": "admin"})

token = asyncio.run(get_token())
headers = {"Authorization": f"Bearer {token}"}

res_s = requests.get("http://127.0.0.1:8000/api/scripts?campaign_id=6aedc9fd5891425b46385f05", headers=headers)
res_v = requests.get("http://127.0.0.1:8000/api/videos?campaign_id=6aedc9fd5891425b46385f05", headers=headers)

scripts = res_s.json()
videos = res_v.json()

print(f"Scripts count: {len(scripts)}")
for s in scripts:
    print(f"  Script id: {s.get('id')}, title: {s.get('title')}")

print(f"\nVideos count: {len(videos)}")
for v in videos:
    print(f"  Video id: {v.get('id')}, script_id: {v.get('script_id')}, status: {v.get('status')}")

# Match check:
for s in scripts:
    s_id = s.get("id")
    completed = [v for v in videos if (v.get("script_id") == s_id or (not v.get("script_id") and v.get("campaign_id") == "6aedc9fd5891425b46385f05")) and v.get("status") == "completed"]
    print(f"\nFor script '{s.get('title')}' (id={s_id}): completed matching videos = {len(completed)}")

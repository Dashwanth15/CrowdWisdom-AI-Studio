import asyncio
import os
import json
import urllib.request
from pathlib import Path
from motor.motor_asyncio import AsyncIOMotorClient
import jwt
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / "backend" / ".env")
uri = os.environ.get("MONGODB_URL")
jwt_secret = os.environ.get("JWT_SECRET_KEY", "replace_with_jwt_secret")
client = AsyncIOMotorClient(uri)
db = client["crowdwisdom_ai_studio"]

async def main():
    user = await db.users.find_one()
    if not user:
        print("No user found")
        return
    token = jwt.encode({"sub": str(user["_id"])}, jwt_secret, algorithm="HS256")
    print(f"User: {user.get('email')}, token generated")

    url = "https://crowdwisdom-ai-studio-backend.onrender.com/api/scripts?campaign_id=6aec1fc21d839818c0dc7d4d"
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Origin": "https://crowdwisdom-ai-studio-ads.onrender.com",
            "User-Agent": "Mozilla/5.0"
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as res:
            print("Status:", res.status)
            print("CORS Origin:", res.headers.get("Access-Control-Allow-Origin"))
            data = json.loads(res.read().decode())
            print(f"Scripts returned: {len(data)}")
    except urllib.error.HTTPError as e:
        print("HTTPError:", e.code)
        print("CORS Origin:", e.headers.get("Access-Control-Allow-Origin"))
        print("Body:", e.read().decode()[:400])
    except Exception as e:
        print("Exception:", e)

asyncio.run(main())

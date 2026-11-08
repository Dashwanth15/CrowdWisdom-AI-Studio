import asyncio
import sys
import hashlib
from pathlib import Path

backend_dir = r"c:\Users\dashw\OneDrive\Desktop\my projects\CrowdWisdom AI Studio\backend"
sys.path.insert(0, backend_dir)

from config import settings
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

def md5(p):
    if not p.exists():
        return "NOT_FOUND"
    h = hashlib.md5()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            h.update(chunk)
    return h.hexdigest()

async def inspect_assets():
    client = AsyncIOMotorClient(settings.MONGODB_URL, serverSelectionTimeoutMS=8000)
    try:
        db = client[settings.MONGODB_DB_NAME]
        sid = "6aef772be2a62dd28fae5557"
        script = await db.scripts.find_one({"_id": ObjectId(sid)})
        print("SCRIPT:", script.get("title") if script else "None")
        if not script:
            return
        
        scenes = script.get("scenes", [])
        for sc in scenes:
            sn = sc.get("scene_number")
            m_type = sc.get("media_type")
            vap = sc.get("visual_asset_path")
            desc = sc.get("visual_description")
            print(f"\n--- SCENE {sn} ({m_type}) ---")
            print(f"  Description: {desc}")
            print(f"  Visual Asset Path: {vap}")
            
            p = Path(backend_dir) / vap if vap else None
            if p and p.exists():
                print(f"  File Size: {p.stat().st_size} bytes")
                print(f"  MD5 Hash: {md5(p)}")
            else:
                p2 = Path(vap) if vap else None
                if p2 and p2.exists():
                    print(f"  File Size (direct): {p2.stat().st_size} bytes")
                    print(f"  MD5 Hash: {md5(p2)}")
                else:
                    print("  File: NOT FOUND ON DISK!")

    finally:
        client.close()

if __name__ == '__main__':
    asyncio.run(inspect_assets())


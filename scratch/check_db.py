import asyncio
import sys
from pathlib import Path

backend_dir = r"c:\Users\dashw\OneDrive\Desktop\my projects\CrowdWisdom AI Studio\backend"
sys.path.insert(0, backend_dir)

from config import settings
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

async def inspect():
    client = AsyncIOMotorClient(settings.MONGODB_URL, serverSelectionTimeoutMS=8000)
    try:
        db = client[settings.MONGODB_DB_NAME]
        vj = await db.video_jobs.find_one({'_id': ObjectId('6aef6957547c27366bbc5f33')})
        print('VIDEO JOB:', flush=True)
        if vj:
            for k, v in vj.items():
                print(f'  {k}: {v}', flush=True)
        else:
            print('  None found', flush=True)

        ae = await db.agent_executions.find_one({'_id': ObjectId('6aef6957547c27366bbc5f34')})
        print('\nAGENT EXECUTION:', flush=True)
        if ae:
            for k, v in ae.items():
                print(f'  {k}: {v}', flush=True)
        else:
            print('  None found', flush=True)
    finally:
        client.close()

if __name__ == '__main__':
    asyncio.run(inspect())

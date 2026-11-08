import asyncio
import sys
import os
from pathlib import Path
from bson import ObjectId

sys.path.insert(0, str(Path(__file__).parent.parent))
from database.connection import connect_to_mongo, close_mongo_connection, get_database

async def list_jobs():
    await connect_to_mongo()
    db = get_database()
    jobs = await db.video_jobs.find().sort('created_at', -1).limit(10).to_list(10)
    print(f'Found {len(jobs)} recent video jobs:\n')
    for j in jobs:
        print('=' * 70)
        jid = str(j.get('_id'))
        cid = str(j.get('campaign_id'))
        sid = str(j.get('script_id'))
        vpath = j.get('video_path')
        vurl = j.get('video_url')
        status = j.get('status')
        created = j.get('created_at')
        completed = j.get('completed_at')
        print(f'Job ID: {jid} | Status: {status}')
        print(f'Campaign: {cid} | Script: {sid}')
        print(f'Video Path: {vpath} (exists={os.path.exists(vpath) if vpath else False})')
        print(f'Video URL: {vurl}')
        print(f'Created: {created} | Completed: {completed}')
        
        if sid and ObjectId.is_valid(sid):
            s = await db.scripts.find_one({'_id': ObjectId(sid)})
            if s:
                print(f'Script Title: {s.get("title")}')
                for sc in s.get('scenes', []):
                    snum = sc.get('scene_number')
                    mtype = sc.get('media_type')
                    vtype = sc.get('scene_visual_type')
                    p = sc.get('visual_asset_path')
                    pexists = os.path.exists(p) if p else False
                    print(f'  Scene {snum}: mtype={mtype}, vtype={vtype}, exists={pexists}, path={p}')
            else:
                print('Script not found!')
        print()

    await close_mongo_connection()

if __name__ == '__main__':
    asyncio.run(list_jobs())


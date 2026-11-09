import asyncio, os, sys, json
backend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend")
sys.path.insert(0, backend_dir)
from database.connection import connect_to_mongo, get_database
from bson import ObjectId

async def main():
    await connect_to_mongo()
    db = get_database()
    campaign_ids = ["6aedab3a1d4c801f02794eb7", "6aece05b17af9898fa44c813", "6aec1fc21d839818c0dc7d4d"]
    for cid in campaign_ids:
        print(f"\n================ CAMPAIGN: {cid} ================")
        camp = await db.campaigns.find_one({"_id": ObjectId(cid)})
        if camp:
            print(f"Name: {camp.get('name')}")
        else:
            print("NOT FOUND")
            continue

        scripts = await db.scripts.find({"campaign_id": cid}).to_list(10)
        print(f"Scripts count: {len(scripts)}")
        for s in scripts:
            print(f"  Script {s['_id']}: title='{s.get('title')}', status='{s.get('status')}'")

        vjobs = await db.video_jobs.find({"campaign_id": cid}).to_list(10)
        print(f"Video Jobs count: {len(vjobs)}")
        for vj in vjobs:
            print(f"  Job {vj['_id']}: script_id='{vj.get('script_id')}', status='{vj.get('status')}', progress={vj.get('progress_percent')}%, error='{vj.get('error_message')}'")

        execs = await db.agent_executions.find({"campaign_id": cid}).to_list(10)
        print(f"Agent Executions count: {len(execs)}")
        for ex in execs:
            print(f"  Exec {ex['_id']}: agent_type='{ex.get('agent_type')}', status='{ex.get('status')}', error='{ex.get('error_message')}'")

if __name__ == "__main__":
    asyncio.run(main())


import asyncio
import sys
sys.path.insert(0, 'backend')
from database.connection import connect_to_mongo, get_database
from bson import ObjectId

async def main():
    await connect_to_mongo()
    db = get_database()
    campaign_id = "6aedc9fd5891425b46385f05"
    
    # Delete failed jobs referencing deleted scripts
    res = await db.video_jobs.delete_many({
        "campaign_id": campaign_id,
        "script_id": "6aee29a4fadd50fa6e006ce4"
    })
    print(f"Cleaned up {res.deleted_count} obsolete video jobs for deleted script.")
    
    # Check remaining jobs
    remaining = await db.video_jobs.find({"campaign_id": campaign_id}).to_list(10)
    for r in remaining:
        print("Active job:", r.get("_id"), r.get("status"), r.get("video_url"), r.get("duration_actual"))

if __name__ == '__main__':
    asyncio.run(main())


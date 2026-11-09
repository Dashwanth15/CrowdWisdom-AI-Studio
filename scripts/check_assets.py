import asyncio, os, sys, json
backend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend")
sys.path.insert(0, backend_dir)
from database.connection import connect_to_mongo, get_database

async def main():
    await connect_to_mongo()
    db = get_database()
    assets = await db.assets.find({"campaign_id": "6aec1fc21d839818c0dc7d4d"}).to_list(100)
    print("Assets count:", len(assets))
    for a in assets:
        print(f"Asset: id={a['_id']}, filename={a.get('filename')}, url={a.get('url')}")

if __name__ == "__main__":
    asyncio.run(main())


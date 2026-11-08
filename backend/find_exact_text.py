import asyncio
from database.connection import connect_to_mongo, close_mongo_connection, get_database

async def main():
    await connect_to_mongo()
    db = get_database()
    for col_name in await db.list_collection_names():
        col = db[col_name]
        async for doc in col.find():
            s = str(doc)
            if "starved for clarity" in s or "chrome sphere" in s or "A tidal wave of noise" in s or "Cut through the market's chaos" in s:
                print(f"FOUND IN {col_name}!")
                print("ID:", doc.get("_id"))
                print("Title:", doc.get("title"))
                print("Campaign ID:", doc.get("campaign_id"))
                return
    print("Not found in any MongoDB collection. Checking files...")
    import os
    from pathlib import Path
    for root, dirs, files in os.walk("."):
        if "node_modules" in root or ".git" in root or ".venv" in root:
            continue
        for f in files:
            if f.endswith((".json", ".py", ".ts", ".tsx", ".txt")):
                fp = Path(root) / f
                try:
                    text = fp.read_text(encoding="utf-8", errors="ignore")
                    if "chrome sphere" in text or "starved for clarity" in text:
                        print(f"FOUND IN FILE: {fp}")
                except Exception:
                    pass
    await close_mongo_connection()

if __name__ == '__main__':
    asyncio.run(main())


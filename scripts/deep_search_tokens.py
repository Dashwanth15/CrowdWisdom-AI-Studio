import asyncio
import os
import sys

backend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend")
sys.path.insert(0, backend_dir)

from database.connection import connect_to_mongo, get_database

async def deep_search():
    await connect_to_mongo()
    db = get_database()
    cols = await db.list_collection_names()
    targets = ["f009d4af8ba1f9a3", "b19535e71781335b", "21d839818c0dc7d4d"]
    print("Collections:", cols)
    for col_name in cols:
        col = db[col_name]
        docs = await col.find().to_list(500)
        for doc in docs:
            doc_str = str(doc)
            for t in targets:
                if t in doc_str:
                    print(f"MATCH in {col_name} for '{t}': ID={doc.get('_id')}")
                    if col_name in ["scripts", "video_jobs", "campaigns", "assets"]:
                        print("   Keys:", {k: v for k, v in doc.items() if k in ["_id", "name", "title", "status", "video_url", "video_path", "thumbnail_path", "visual_asset_url", "visual_asset_path"]})

if __name__ == "__main__":
    asyncio.run(deep_search())


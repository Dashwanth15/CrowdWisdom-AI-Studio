import asyncio
import os
import sys

backend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend")
sys.path.insert(0, backend_dir)

from database.connection import connect_to_mongo, get_database

async def find_all_occurrences():
    await connect_to_mongo()
    db = get_database()
    tokens = ["f009d4af8ba1f9a33", "b19535e71781335b0"]
    for col_name in await db.list_collection_names():
        col = db[col_name]
        docs = await col.find().to_list(1000)
        for doc in docs:
            d_str = str(doc)
            for t in tokens:
                if t in d_str:
                    print(f"Collection: {col_name} | Document ID: {doc.get('_id')}")
                    # Find exact key
                    for k, v in doc.items():
                        if t in str(v):
                            print(f"   Field '{k}': {v}")

if __name__ == "__main__":
    asyncio.run(find_all_occurrences())


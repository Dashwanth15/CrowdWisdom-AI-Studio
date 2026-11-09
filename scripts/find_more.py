import asyncio, os, sys, json
backend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend")
sys.path.insert(0, backend_dir)
from database.connection import connect_to_mongo, get_database

async def main():
    await connect_to_mongo()
    db = get_database()
    for col_name in ["assets", "scripts", "creative_briefs"]:
        docs = await db[col_name].find().to_list(100)
        for doc in docs:
            d_str = str(doc)
            if "f009d4af8ba1f9a33" in d_str or "b19535e71781335b0" in d_str:
                print(f"Col {col_name} doc {doc['_id']}:")
                for k, v in doc.items():
                    if "f009d4af8ba1f9a33" in str(v) or "b19535e71781335b0" in str(v):
                        print(f"   {k}: {v}")

if __name__ == "__main__":
    asyncio.run(main())


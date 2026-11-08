import asyncio
from database.connection import connect_to_mongo, close_mongo_connection, get_database

async def main():
    await connect_to_mongo()
    db = get_database()
    for col_name in await db.list_collection_names():
        col = db[col_name]
        count = await col.count_documents({})
        async for doc in col.find():
            s = str(doc)
            if 'chrome sphere' in s.lower() or 'pristine, perfectly balanced' in s.lower():
                print(f"MATCH FOUND in collection '{col_name}'!")
                print("ID:", doc.get("_id"))
                print("Campaign:", doc.get("campaign_id"))
                print("Title:", doc.get("title"))
                print("Hook:", doc.get("hook") or doc.get("visual_hook") or doc.get("opening_hook"))
                print("Full doc keys:", list(doc.keys()))
                if "scenes" in doc:
                    for sc in doc["scenes"]:
                        print(f"  Scene {sc.get('scene_number')}: {sc.get('visual_description')[:80]}")
                        print(f"    VO: {sc.get('voiceover')[:60]}")
                        print(f"    Media: {sc.get('media_type')} | Theme: {sc.get('chart_theme')} | Asset: {sc.get('visual_asset_path')}")
                return
    print("No document found containing 'chrome sphere'.")
    await close_mongo_connection()

if __name__ == '__main__':
    asyncio.run(main())


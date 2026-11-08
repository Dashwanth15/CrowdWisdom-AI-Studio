"""
Migration script: Normalize and persist publication dates for all existing advertisements in MongoDB.
"""
import asyncio
import sys
from pathlib import Path

backend_dir = str(Path(__file__).resolve().parent.parent)
sys.path.insert(0, backend_dir)

from database.connection import connect_to_mongo, get_database, close_mongo_connection
from services.date_normalization import extract_and_normalize_publication_date


async def migrate_advertisements():
    print("[MIGRATION] Connecting to MongoDB...")
    await connect_to_mongo()
    db = get_database()

    ads = await db.advertisements.find().to_list(1000)
    print(f"[MIGRATION] Found {len(ads)} advertisements in db.advertisements.")

    updated_count = 0
    verified_count = 0
    unverified_count = 0

    for ad in ads:
        created_at = ad.get("created_at")
        norm = extract_and_normalize_publication_date(ad, scraped_at=created_at)

        update_fields = {
            "published_at": norm["published_at"],
            "published_at_raw": norm["published_at_raw"],
            "published_date_source": norm["published_date_source"],
            "scraped_at": norm["scraped_at"],
            "date_verification_status": norm["date_verification_status"],
            "age_days": norm["age_days"],
            "meta_ads_url": norm["meta_ads_url"],
        }

        await db.advertisements.update_one(
            {"_id": ad["_id"]},
            {"$set": update_fields}
        )

        updated_count += 1
        if norm["date_verification_status"] == "verified":
            verified_count += 1
        else:
            unverified_count += 1

    print(f"[MIGRATION COMPLETE] Processed: {updated_count} | Verified: {verified_count} | Unverified: {unverified_count}")
    await close_mongo_connection()


if __name__ == "__main__":
    asyncio.run(migrate_advertisements())

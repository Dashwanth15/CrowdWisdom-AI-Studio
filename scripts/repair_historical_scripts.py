"""
Script to repair historical inconsistent scripts in MongoDB.
"""
import asyncio
import sys
import os
from datetime import datetime, timezone
from bson import ObjectId

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from database.connection import get_database
from services.market_intelligence.country_localization_service import country_localization_service


async def run_repair():
    db = get_database()
    target_ids = [
        ObjectId("6af14136285ae7a28dd78ec4"),
        ObjectId("6af17486c494d76c431874b3"),
        ObjectId("6af3f4c181f757afa354a3d1")
    ]
    now = datetime.now(timezone.utc)
    for sc_id in target_ids:
        doc = await db.scripts.find_one({"_id": sc_id})
        if not doc:
            continue
        if "original_unlocalized_copy" not in doc:
            await db.scripts.update_one(
                {"_id": sc_id},
                {"$set": {
                    "original_unlocalized_copy": {
                        "title": doc.get("title") or doc.get("campaign_title"),
                        "visual_hook": doc.get("visual_hook"),
                        "core_message": doc.get("core_message"),
                        "scenes": doc.get("scenes"),
                    }
                }}
            )
        localized = country_localization_service.localize_script_dict(doc, "IN")
        consistency = country_localization_service.validate_script_country_consistency(localized, "IN")
        update_fields = {
            "title": localized.get("title"),
            "campaign_title": localized.get("campaign_title"),
            "visual_hook": localized.get("visual_hook"),
            "core_message": localized.get("core_message"),
            "marketing_angle": localized.get("marketing_angle"),
            "pain_point": localized.get("pain_point"),
            "scenes": localized.get("scenes"),
            "voiceover_full": localized.get("voiceover_full"),
            "on_screen_texts": localized.get("on_screen_texts"),
            "call_to_action": localized.get("call_to_action"),
            "target_country": "IN",
            "consistency_report": consistency,
            "localization_repaired_at": now,
            "updated_at": now,
        }
        await db.scripts.update_one(
            {"_id": sc_id},
            {
                "$set": update_fields,
                "$inc": {"version": 1}
            }
        )
        print(f"Successfully repaired script {str(sc_id)} -> New Version: {doc.get('version', 1) + 1}")


if __name__ == "__main__":
    asyncio.run(run_repair())

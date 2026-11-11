import asyncio
import os
import sys

backend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend")
sys.path.insert(0, backend_dir)

from database.connection import connect_to_mongo, close_mongo_connection, get_database

async def diagnose():
    await connect_to_mongo()
    db = get_database()
    
    print("=== RECENT 15 SCRIPTS IN MONGODB ===")
    scripts = await db.scripts.find().sort([("created_at", -1)]).limit(15).to_list(15)
    for s in scripts:
        sid = str(s.get("_id"))
        title = s.get("title", "")
        country = s.get("target_country", "")
        cid = str(s.get("campaign_id", ""))
        print(f"[{sid}] Country: {country} | Title: {title} | Campaign: {cid}")
        for sc in s.get("scenes", []):
            s_num = sc.get("scene_number")
            ost = sc.get("on_screen_text", "")
            vo = sc.get("voiceover", "")
            if any(term in (ost + vo + title) for term in ["NSE", "SEBI", "BSE", "Nifty", "Sensex", "Dalal"]):
                print(f"   Scene {s_num} Contamination -> OST: '{ost}' | VO: '{vo[:60]}...'")

    print("\n=== SEARCHING FOR SPECIFIC PHRASES FROM SCREENSHOT ===")
    queries = [
        {"title": {"$regex": "Noise Trap", "$options": "i"}},
        {"title": {"$regex": "NSE Blue Chip", "$options": "i"}},
        {"scenes.on_screen_text": {"$regex": "SEBI Compliant", "$options": "i"}},
        {"scenes.voiceover": {"$regex": "Market makers love retail chaos", "$options": "i"}}
    ]
    for q in queries:
        matches = await db.scripts.find(q).to_list(10)
        print(f"Query {q} returned {len(matches)} matches")
        for m in matches:
            print(f"  Match ID: {m.get('_id')} | Title: {m.get('title')} | Country: {m.get('target_country')}")
            for sc in m.get("scenes", []):
                print(f"    Sc {sc.get('scene_number')}: VO: {sc.get('voiceover')[:60]}... | OST: {sc.get('on_screen_text')}")
                print(f"    Visual: {sc.get('visual_description')[:80]}...")

    await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(diagnose())

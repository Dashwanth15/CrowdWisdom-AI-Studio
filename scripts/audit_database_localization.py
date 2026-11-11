"""
Database Localization Audit Script for CrowdWisdom AI Studio.
Audits all existing campaigns and scripts for country and currency consistency.
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from database.connection import get_database
from services.market_intelligence.country_localization_service import country_localization_service


async def audit():
    db = get_database()
    campaigns = await db.campaigns.find({}).to_list(100)
    scripts = await db.scripts.find({}).to_list(100)

    print(f"=== DATABASE AUDIT: {len(campaigns)} CAMPAIGNS, {len(scripts)} SCRIPTS ===")

    # 1. Campaign Target Country Breakdown
    camp_countries = {}
    for c in campaigns:
        tc = c.get("target_country")
        camp_countries[str(tc)] = camp_countries.get(str(tc), 0) + 1
    print("Campaigns target_country breakdown:", camp_countries)

    # 2. Script Target Country Breakdown
    script_countries = {}
    for s in scripts:
        stc = s.get("target_country")
        script_countries[str(stc)] = script_countries.get(str(stc), 0) + 1
    print("Scripts target_country breakdown:", script_countries)

    # 3. Identify Inconsistent Scripts with USD/American references
    inconsistent_scripts = []
    for s in scripts:
        sid = str(s.get("_id"))
        title = s.get("title") or s.get("campaign_title") or "Untitled"
        stc = s.get("target_country") or "IN"

        rep = country_localization_service.validate_script_country_consistency(s, stc)
        if not rep["is_consistent"]:
            inconsistent_scripts.append({
                "id": sid,
                "title": title,
                "country": stc,
                "status": s.get("status"),
                "inconsistencies_count": rep["inconsistencies_count"],
                "first_issue": rep["inconsistencies"][0] if rep["inconsistencies"] else None
            })

    print(f"\nTotal Inconsistent Scripts: {len(inconsistent_scripts)}")
    for item in inconsistent_scripts:
        print(f"- Script ID: {item['id']} | Target Country: {item['country']} | Status: {item['status']}")
        print(f"  Title: {item['title']}")
        if item["first_issue"]:
            print(f"  Issue: [{item['first_issue']['field']}] {item['first_issue']['issue']}: {item['first_issue']['snippet'][:90]}")


if __name__ == "__main__":
    asyncio.run(audit())

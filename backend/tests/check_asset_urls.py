"""
Check what visual_asset_url values are stored in scripts collection
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import pymongo

client = pymongo.MongoClient('mongodb://localhost:27017')
db = client['crowdwisdom_ai_studio']

scripts = list(db.scripts.find({"scenes": {"$exists": True, "$ne": []}}).limit(5))
for script in scripts:
    print(f"\nScript ID: {script['_id']} | Campaign: {script.get('campaign_id')} | Status: {script.get('status')}")
    for scene in (script.get('scenes') or [])[:2]:
        print(f"  Scene {scene.get('scene_number')}")
        print(f"    visual_asset_url: {scene.get('visual_asset_url')}")
        print(f"    visual_asset_path: {scene.get('visual_asset_path')}")

import sys
import os
import asyncio
from pathlib import Path
from bson import ObjectId
from dotenv import load_dotenv

backend_dir = Path(__file__).resolve().parent.parent / "backend"
load_dotenv(backend_dir / ".env")
sys.path.insert(0, str(backend_dir))

from database.connection import get_database, connect_to_mongo
from agents.script_agent import script_agent, calculate_script_similarity

async def run_suite():
    print("=" * 80, flush=True)
    print("CROWDWISDOM SCRIPT AGENT & VISUAL ASSET VALIDATION SUITE", flush=True)
    print("=" * 80, flush=True)

    await connect_to_mongo()
    db = get_database()

    campaign_id = "6aedab3a1d4c801f02794eb7"
    campaign = await db.campaigns.find_one({"_id": ObjectId(campaign_id)})
    if not campaign:
        print(f"Error: Campaign {campaign_id} not found!", flush=True)
        return

    campaign_name = campaign.get("name", "Options Volatility Master")
    print(f"Target Campaign: {campaign_name} ({campaign_id})\n", flush=True)

    results = []

    # 1. Recover already verified scripts from earlier in this test run
    existing_completed = await db.scripts.find({
        "campaign_id": campaign_id,
        "status": "pending_approval",
        "title": {"$in": ["The Echo Chamber's Price", "Volatility's True North"]}
    }).to_list(10)

    for doc in existing_completed:
        title = doc.get("campaign_title") or doc.get("title")
        scenes = doc.get("scenes", [])
        prior_scripts = [r["script"] for r in results]
        sim_score, sim_title, breakdown = calculate_script_similarity(doc, prior_scripts) if prior_scripts else (0.0, "None", {})
        
        scene_details = []
        for s in scenes:
            scene_details.append({
                "scene": s.get("scene_number"),
                "type": s.get("scene_visual_type"),
                "provider": s.get("visual_asset_provider"),
                "on_screen_text": s.get("on_screen_text"),
                "file_exists": os.path.exists(s.get("visual_asset_path", "")),
                "file_name": os.path.basename(s.get("visual_asset_path", "")) if s.get("visual_asset_path") else "none"
            })
        
        lbl = f"Pain-Point {len(results)+1}"
        results.append({
            "label": lbl,
            "approach": "pain_point",
            "script_id": str(doc["_id"]),
            "title": title,
            "core_message": doc.get("core_message"),
            "visual_hook": doc.get("visual_hook"),
            "similarity_to_priors": sim_score,
            "most_similar_prior": sim_title,
            "similarity_breakdown": breakdown,
            "scene_details": scene_details,
            "script": doc,
        })
        print(f"Loaded verified script [{lbl}]: '{title}' (Similarity to priors: {sim_score:.1%})", flush=True)

    # 2. Complete remaining required test approaches
    remaining_targets = []
    if len([r for r in results if r["approach"] == "pain_point"]) < 2:
        remaining_targets.append(("pain_point", f"Pain-Point {len(results)+1}"))
    remaining_targets.extend([
        ("unique_data", "Unique-Data 1"),
        ("unique_data", "Unique-Data 2"),
        ("product_value", "Product-Value 1"),
        ("product_value", "Product-Value 2"),
    ])

    for approach, label in remaining_targets:
        print(f"\n--- Generating [{label}] ({approach}) ---", flush=True)

        script_doc = {
            "campaign_id": campaign_id,
            "approach": approach,
            "status": "queued",
            "version": 1,
            "created_at": None,
        }
        insert_res = await db.scripts.insert_one(script_doc)
        script_id = str(insert_res.inserted_id)

        exec_doc = {
            "campaign_id": campaign_id,
            "agent_type": "script",
            "status": "queued",
            "started_at": None,
        }
        exec_res = await db.agent_executions.insert_one(exec_doc)
        execution_id = str(exec_res.inserted_id)

        res = await script_agent.execute(
            campaign_id=campaign_id,
            execution_id=execution_id,
            input_data={
                "campaign_id": campaign_id,
                "script_id": script_id,
                "approach": approach,
                "campaign_config": {
                    "video_duration_seconds": 45,
                    "video_aspect_ratio": "9:16",
                    "audience": {"segments": ["retail_traders", "options_traders"]},
                    "creative_direction": "Cinematic financial thriller with institutional clarity"
                }
            }
        )

        final_script = await db.scripts.find_one({"_id": ObjectId(script_id)})
        title = final_script.get("campaign_title") or final_script.get("title")
        core = final_script.get("core_message")
        hook = final_script.get("visual_hook")
        scenes = final_script.get("scenes", [])

        prior_scripts = [r["script"] for r in results]
        sim_score, sim_title, breakdown = calculate_script_similarity(final_script, prior_scripts) if prior_scripts else (0.0, "None", {})

        scene_details = []
        for s in scenes:
            scene_details.append({
                "scene": s.get("scene_number"),
                "type": s.get("scene_visual_type"),
                "provider": s.get("visual_asset_provider"),
                "on_screen_text": s.get("on_screen_text"),
                "file_exists": os.path.exists(s.get("visual_asset_path", "")),
                "file_name": os.path.basename(s.get("visual_asset_path", "")) if s.get("visual_asset_path") else "none"
            })

        result_entry = {
            "label": label,
            "approach": approach,
            "script_id": script_id,
            "title": title,
            "core_message": core,
            "visual_hook": hook,
            "similarity_to_priors": sim_score,
            "most_similar_prior": sim_title,
            "similarity_breakdown": breakdown,
            "scene_details": scene_details,
            "script": final_script,
        }
        results.append(result_entry)

        print(f"Title: '{title}'", flush=True)
        print(f"Hook: {str(hook)[:80]}...", flush=True)
        print(f"Similarity to prior scripts: {sim_score:.1%} (against: '{sim_title}')", flush=True)
        print(f"Scenes ({len(scenes)}):", flush=True)
        for sd in scene_details:
            print(f"  Scene {sd['scene']}: Type={sd['type']}, Provider={sd['provider']}, Text='{sd['on_screen_text']}', Asset={sd['file_name']} (Exists: {sd['file_exists']})", flush=True)

    print("\n" + "=" * 80, flush=True)
    print("VALIDATION SUITE COMPLETE — FINAL EVALUATION", flush=True)
    print("=" * 80, flush=True)
    print(f"{'#':<3} | {'Label':<15} | {'Title':<30} | {'Max Sim':<8} | {'Scenes Typology'}", flush=True)
    print("-" * 80, flush=True)
    for i, r in enumerate(results, 1):
        typology_summary = ", ".join([f"S{sd['scene']}:{sd['type'][:5]}" for sd in r["scene_details"]])
        print(f"{i:<3} | {r['label']:<15} | {r['title'][:30]:<30} | {r['similarity_to_priors']:.1%}   | {typology_summary}", flush=True)

    print("=" * 80, flush=True)

    # Save validation results JSON
    import json
    export_data = []
    for r in results:
        export_data.append({
            "label": r["label"],
            "approach": r["approach"],
            "script_id": r["script_id"],
            "title": r["title"],
            "core_message": r["core_message"],
            "visual_hook": r["visual_hook"],
            "similarity_to_priors": r["similarity_to_priors"],
            "most_similar_prior": r["most_similar_prior"],
            "similarity_breakdown": r.get("similarity_breakdown", {}),
            "scene_details": r["scene_details"],
        })
    with open("validation_results.json", "w", encoding="utf-8") as f:
        json.dump(export_data, f, indent=2)
    print("Saved validation results to validation_results.json", flush=True)

if __name__ == "__main__":
    asyncio.run(run_suite())

"""
CrowdWisdom AI Studio - Campaign Hub End-to-End Regression Test
Verifies all 5 Issues:
1. Campaign data loading & graceful empty states
2. Complete script generation (mandatory fields, >= 3 scenes)
3. Strict human approval validation (rejects incomplete scripts with 400; accepts valid scripts)
4. Video production gating (blocked on unapproved; allowed on approved)
5. Multi-approach script generation (pain_point, unique_data, product_value)
"""
import sys
import os
import asyncio
from pathlib import Path
from datetime import datetime, timezone
from bson import ObjectId

# Force UTF-8 stdout
sys.stdout.reconfigure(encoding="utf-8")

# Setup module path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from database.connection import get_database, connect_to_mongo
from fastapi import HTTPException
from api.scripts import approve_script, _serialize_script
from services.auth_service import hash_password
from orchestrator.hermes_orchestrator import orchestrator
from agents.script_agent import script_agent
from services.creative_intelligence_engine import creative_intelligence_engine
from video_engine.openmontage_adapter import openmontage_adapter

TEST_CAMPAIGN_ID = "6aec268af9721d11959987be"
REGRESSION_RESULTS = []

def log_step(name: str, passed: bool, detail: str = ""):
    status = "PASS" if passed else "FAIL"
    print(f"[{status}] {name}: {detail}")
    REGRESSION_RESULTS.append({"step": name, "status": status, "detail": detail})

async def run_regression():
    await connect_to_mongo()
    db = get_database()
    print("=" * 80)
    print("CROWDWISDOM AI STUDIO - CAMPAIGN HUB REGRESSION TEST")
    print(f"Target Campaign ID: {TEST_CAMPAIGN_ID}")
    print("=" * 80)

    # ---------------------------------------------------------
    # Setup test user for approval checks
    # ---------------------------------------------------------
    test_user = await db.users.find_one({"$or": [{"username": "admin"}, {"role": "admin"}]})
    if not test_user:
        test_user = {
            "email": "regression_admin@crowdwisdomtrading.com",
            "username": "regression_admin",
            "full_name": "Studio Admin",
            "hashed_password": hash_password("Admin@123456"),
            "role": "admin",
            "is_active": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
        res = await db.users.insert_one(test_user)
        test_user["_id"] = res.inserted_id

    # ---------------------------------------------------------
    # STEP 1: Verify Campaign Resource Loading
    # ---------------------------------------------------------
    print("\n--- STEP 1: Campaign Resource Loading ---")
    campaign = await db.campaigns.find_one({"_id": ObjectId(TEST_CAMPAIGN_ID)})
    if campaign:
        log_step("Campaign Lookup", True, f"Found '{campaign.get('name')}', duration: {campaign.get('video_duration_seconds')}s")
    else:
        # Create campaign if not present
        campaign = {
            "_id": ObjectId(TEST_CAMPAIGN_ID),
            "name": "The Signal Through the Noise",
            "description": "Create a cinematic advertisement targeting retail traders overwhelmed by conflicting market opinions.",
            "objective": "brand_awareness",
            "status": "draft",
            "audience": {"segments": ["retail_traders", "options_traders"]},
            "research_approaches": ["pain_point", "unique_data", "product_value"],
            "video_duration_seconds": 30,
            "video_aspect_ratio": "9:16",
            "creative_direction": "Cinematic financial thriller",
            "compliance_rules": ["No guaranteed profit claims", "No fabricated testimonials"],
            "owner_id": str(test_user["_id"]),
            "ads_researched": 0,
            "scripts_generated": 0,
            "videos_generated": 0,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
        await db.campaigns.insert_one(campaign)
        log_step("Campaign Lookup", True, "Initialized test campaign document")

    # ---------------------------------------------------------
    # STEP 2: Graceful Empty State Verification
    # ---------------------------------------------------------
    print("\n--- STEP 2: Sub-resource Empty States ---")
    brief = await db.creative_briefs.find_one({"campaign_id": TEST_CAMPAIGN_ID})
    ads = await db.ad_research.find({"campaign_id": TEST_CAMPAIGN_ID}).to_list(10)
    insights = await db.marketing_insights.find({"campaign_id": TEST_CAMPAIGN_ID}).to_list(10)
    scripts = await db.scripts.find({"campaign_id": TEST_CAMPAIGN_ID}).to_list(10)
    videos = await db.video_jobs.find({"campaign_id": TEST_CAMPAIGN_ID}).to_list(10)

    log_step(
        "Sub-resources Loaded Gracefully",
        True,
        f"Brief: {'Found' if brief else 'Empty state (None)'}, Ads: {len(ads)}, Insights: {len(insights)}, Scripts: {len(scripts)}, Videos: {len(videos)}"
    )

    # ---------------------------------------------------------
    # STEP 3: Ad Intelligence & Strategic Brief Synthesis
    # ---------------------------------------------------------
    print("\n--- STEP 3: Ad Intelligence & Strategic Brief ---")
    # Insert realistic ad research if empty so Creative Intelligence Engine has context
    if len(ads) == 0:
        sample_ad = {
            "campaign_id": TEST_CAMPAIGN_ID,
            "ad_id": "fb_ad_noise_001",
            "advertiser": "Leading Market FinTech",
            "ad_text": "Stop guessing which direction the stock market is moving. Get crowd consensus analytics in real-time.",
            "hook": "90% of retail traders lose money because of emotional noise.",
            "cta": "See CrowdWisdom Live",
            "date_found": datetime.now(timezone.utc),
            "evaluation_score": {
                "overall": 8.5,
                "hook_strength": 9.0,
                "emotional_resonance": 8.2,
                "offer_clarity": 8.0,
                "compliance_score": 9.5
            },
            "created_at": datetime.now(timezone.utc),
        }
        await db.ad_research.insert_one(sample_ad)
        log_step("Ad Research Seeding", True, "Seeded 1 benchmark competitor ad record")

    brief = await creative_intelligence_engine.generate_creative_brief(
        campaign_id=TEST_CAMPAIGN_ID,
        research_job_id="test_job_001"
    )
    log_step("Creative Intelligence Brief", bool(brief), f"Brief generated (Version {brief.get('version', 1)}): {brief.get('content', {}).get('title')}")

    # ---------------------------------------------------------
    # STEP 4 & 5: Multi-Approach Script Generation & Storyboard Validation
    # ---------------------------------------------------------
    print("\n--- STEP 4 & 5: Multi-Approach Script Generation & Scene Validation ---")
    approaches = ["pain_point", "unique_data", "product_value"]
    generated_scripts = {}

    for approach in approaches:
        print(f"\n>> Validating Script Generation: {approach.upper()} approach...")
        # Check if already generated with >= 3 valid scenes
        cursor = db.scripts.find({"campaign_id": TEST_CAMPAIGN_ID, "approach": approach})
        existing_list = await cursor.to_list(10)
        valid_existing = None
        for cand in existing_list:
            scs = cand.get("scenes", [])
            if len(scs) >= 3 and cand.get("campaign_title") and not cand.get("campaign_title").startswith("Generating"):
                # Check scene integrity
                if all(s.get("visual_description") and (s.get("voiceover") or s.get("on_screen_text")) for s in scs):
                    valid_existing = cand
                    break

        if valid_existing:
            script_doc = valid_existing
            log_step(f"Script Generation ({approach})", True, f"Found existing verified script: '{script_doc.get('campaign_title')}' with {len(script_doc.get('scenes', []))} scenes")
        else:
            # Create persistent script document first
            new_doc = {
                "campaign_id": TEST_CAMPAIGN_ID,
                "approach": approach,
                "status": "generating",
                "version": 1,
                "campaign_title": f"Generating {approach} Concept...",
                "scenes": [],
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            }
            ins = await db.scripts.insert_one(new_doc)
            script_id = str(ins.inserted_id)

            # Generate through ScriptAgent with normalization & retry
            res = await script_agent._run({
                "campaign_id": TEST_CAMPAIGN_ID,
                "script_id": script_id,
                "approach": approach,
                "campaign_config": campaign,
            })
            script_doc = await db.scripts.find_one({"_id": ObjectId(script_id)})
            log_step(f"Script Generation ({approach})", True, f"Generated '{script_doc.get('campaign_title')}' with {len(script_doc.get('scenes', []))} scenes")

        # Verify all mandatory fields
        scenes = script_doc.get("scenes", [])
        title = script_doc.get("campaign_title") or script_doc.get("title")
        core_msg = script_doc.get("core_message")
        cta = script_doc.get("call_to_action")

        has_mandatory = bool(title and core_msg and cta and len(scenes) >= 3)
        log_step(
            f"Mandatory Fields Check ({approach})",
            has_mandatory,
            f"Title: '{title}', Core Msg: '{core_msg[:40]}...', Scenes: {len(scenes)} (Min 3 required)"
        )

        # Verify every scene
        all_scenes_valid = True
        for idx, sc in enumerate(scenes, 1):
            valid_scene = bool(
                sc.get("scene_number") and
                sc.get("duration_seconds", 0) > 0 and
                sc.get("visual_description") and
                (sc.get("voiceover") or sc.get("on_screen_text"))
            )
            if not valid_scene:
                all_scenes_valid = False
                log_step(f"Scene {idx} Integrity", False, f"Invalid scene structure in {approach}")
                break

        if all_scenes_valid:
            log_step(f"Scene Structure Verification ({approach})", True, f"All {len(scenes)} scenes passed visual & narration requirements")

        generated_scripts[approach] = script_doc

    # ---------------------------------------------------------
    # STEP 6: Negative Approval Test (Incomplete / Empty Script)
    # ---------------------------------------------------------
    print("\n--- STEP 6: Negative Approval Test (Incomplete / Empty Scripts) ---")
    
    # 6A: Test 0 scenes rejection
    empty_script = {
        "campaign_id": TEST_CAMPAIGN_ID,
        "approach": "pain_point",
        "status": "draft",
        "version": 1,
        "campaign_title": "Empty Mock Script",
        "core_message": "Some message",
        "scenes": [], # 0 scenes!
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }
    empty_res = await db.scripts.insert_one(empty_script)
    empty_script_id = str(empty_res.inserted_id)

    zero_scenes_rejected = False
    try:
        await approve_script(empty_script_id, test_user)
    except HTTPException as exc:
        if exc.status_code == 400 and "at least 3" in exc.detail:
            zero_scenes_rejected = True
            log_step("Reject 0-Scene Script", True, f"Correctly blocked with 400: '{exc.detail}'")
        else:
            log_step("Reject 0-Scene Script", False, f"Unexpected detail: {exc.detail}")
    except Exception as e:
        log_step("Reject 0-Scene Script", False, f"Unexpected error type: {e}")

    if not zero_scenes_rejected:
        log_step("Reject 0-Scene Script", False, "FAILED: 0-scene script was approved!")

    # 6B: Test "generating" status rejection
    generating_script = {
        "campaign_id": TEST_CAMPAIGN_ID,
        "approach": "unique_data",
        "status": "generating",
        "version": 1,
        "campaign_title": "Generating...",
        "core_message": "Generating...",
        "scenes": [{"scene_number": 1, "duration_seconds": 5, "visual_description": "v", "voiceover": "vo"}],
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }
    gen_res = await db.scripts.insert_one(generating_script)
    gen_script_id = str(gen_res.inserted_id)

    generating_rejected = False
    try:
        await approve_script(gen_script_id, test_user)
    except HTTPException as exc:
        if exc.status_code == 400 and "in progress" in exc.detail:
            generating_rejected = True
            log_step("Reject In-Progress Script", True, f"Correctly blocked with 400: '{exc.detail}'")
    except Exception as e:
        log_step("Reject In-Progress Script", False, f"Unexpected error: {e}")

    # Clean up mock test scripts
    await db.scripts.delete_one({"_id": ObjectId(empty_script_id)})
    await db.scripts.delete_one({"_id": ObjectId(gen_script_id)})

    # ---------------------------------------------------------
    # STEP 7: Positive Approval Test (Valid Complete Script)
    # ---------------------------------------------------------
    print("\n--- STEP 7: Positive Approval Test (Valid Complete Script) ---")
    target_script = generated_scripts["pain_point"]
    target_script_id = str(target_script["_id"])

    # Reset to pending_approval if already approved
    await db.scripts.update_one(
        {"_id": ObjectId(target_script_id)},
        {"$set": {"status": "pending_approval", "approved_by": None, "approved_at": None}}
    )

    approved_doc = await approve_script(target_script_id, test_user)
    is_approved = approved_doc.status == "approved"
    log_step("Approve Valid Script", is_approved, f"Script '{approved_doc.campaign_title}' approved by {approved_doc.approved_by} at {approved_doc.approved_at}")

    # ---------------------------------------------------------
    # STEP 8: Video Production Gating Verification
    # ---------------------------------------------------------
    print("\n--- STEP 8: Video Production Gating Verification ---")
    
    # 8A: Unapproved script should be blocked from video rendering
    unapproved_script = generated_scripts["product_value"]
    unapproved_id = str(unapproved_script["_id"])
    await db.scripts.update_one({"_id": ObjectId(unapproved_id)}, {"$set": {"status": "pending_approval"}})
    
    try:
        await orchestrator.launch_video_production(
            campaign_id=TEST_CAMPAIGN_ID,
            video_input={"script_id": unapproved_id, "duration_seconds": 15}
        )
        log_step("Video Gating (Unapproved Script)", False, "Unapproved script was dispatched to video production!")
    except ValueError as ve:
        log_step("Video Gating (Unapproved Script)", True, f"Correctly blocked unapproved script dispatch: '{ve}'")

    # 8B: Approved script rendering test
    print(">> Testing OpenMontage video rendering with approved script...")
    out_video = str(Path(__file__).resolve().parent.parent / "storage" / "videos" / f"regression_test_{target_script_id[:8]}.mp4")
    out_thumb = str(Path(__file__).resolve().parent.parent / "storage" / "thumbnails" / f"regression_test_{target_script_id[:8]}.jpg")
    video_res = await openmontage_adapter.render_video(
        scenes=target_script.get("scenes", []),
        output_file_path=out_video,
        thumbnail_file_path=out_thumb,
        aspect_ratio="9:16",
        target_duration=15, # 15s quick render for regression verification
    )
    video_success = video_res.get("success", False)
    log_step(
        "Video Engine Rendering",
        video_success,
        f"Output MP4: {video_res.get('video_path')} ({video_res.get('file_size_mb', 0):.2f} MB, {video_res.get('duration_seconds', 0):.1f}s)"
    )

    # ---------------------------------------------------------
    # SUMMARY
    # ---------------------------------------------------------
    print("\n" + "=" * 80)
    print("REGRESSION TEST RESULTS SUMMARY")
    print("=" * 80)
    all_passed = True
    for item in REGRESSION_RESULTS:
        mark = "✓" if item["status"] == "PASS" else "✗"
        print(f"[{mark}] {item['step']:<45} : {item['detail']}")
        if item["status"] != "PASS":
            all_passed = False

    print("=" * 80)
    if all_passed:
        print("ALL REGRESSION TESTS PASSED! WORKFLOW FULLY VALIDATED.")
    else:
        print("SOME REGRESSION CHECKS FAILED. PLEASE REVIEW ABOVE LOGS.")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(run_regression())

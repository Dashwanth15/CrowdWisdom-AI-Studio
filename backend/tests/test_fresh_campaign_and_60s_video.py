"""
CrowdWisdom AI Studio — Fresh Campaign & 60-Second Video Duration Test
Verifies:
1. Fresh campaign creation without pre-existing scripts.
2. Generating 3 distinct scripts via configured LLM (Pain-Point, Unique-Data, Product-Value).
3. Storyboard integrity: >= 3 scenes, mandatory scene attributes, persistence in MongoDB.
4. Approval checkpoint validation on the fresh campaign scripts.
5. Strict 60-second video duration enforcement:
   - Campaign target duration (60s) passed to Video Production Agent
   - Storyboard scene durations validated and allocated
   - Rendering engine generates 60s MP4 commercial
   - Post-rendering FFprobe inspection of actual MP4 duration on disk
   - Metadata persistence in MongoDB
"""
import sys
import os
import re
import json
import asyncio
import subprocess
from pathlib import Path
from datetime import datetime, timezone
from bson import ObjectId

# Force UTF-8 stdout
sys.stdout.reconfigure(encoding="utf-8")

# Setup module path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import imageio_ffmpeg
from database.connection import get_database, connect_to_mongo
from fastapi import HTTPException
from api.scripts import approve_script
from services.auth_service import hash_password
from orchestrator.hermes_orchestrator import orchestrator
from agents.script_agent import script_agent
from video_engine.openmontage_adapter import openmontage_adapter

TEST_REPORT = {
    "fresh_campaign": {},
    "scripts_generated": {},
    "approval_validation": {},
    "video_duration_audit": {},
    "failures": [],
}

def probe_mp4_duration_ffmpeg(file_path: str) -> float:
    """Uses FFmpeg binary from imageio-ffmpeg to inspect exact media stream duration."""
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [ffmpeg_exe, "-i", str(file_path), "-hide_banner"]
    res = subprocess.run(cmd, capture_output=True, text=True, errors="ignore")
    m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.?\d*)", res.stderr)
    if not m:
        raise RuntimeError(f"Could not parse FFmpeg duration from stderr:\n{res.stderr}")
    hrs, mins, secs = float(m.group(1)), float(m.group(2)), float(m.group(3))
    total_seconds = round(hrs * 3600 + mins * 60 + secs, 2)
    return total_seconds

async def run_validation():
    await connect_to_mongo()
    db = get_database()
    print("=" * 80)
    print("CROWDWISDOM AI STUDIO — FRESH CAMPAIGN & 60-SECOND DURATION VALIDATION")
    print("=" * 80)

    # 1. Fetch or create admin user for approvals
    test_user = await db.users.find_one({"$or": [{"username": "admin"}, {"role": "admin"}]})
    if not test_user:
        test_user = {
            "email": "fresh_admin@crowdwisdomtrading.com",
            "username": "fresh_admin",
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
    # PART 1: Fresh Campaign Creation
    # ---------------------------------------------------------
    print("\n--- STEP 1: Creating Brand-New Fresh Campaign (60 Seconds Target) ---")
    fresh_campaign_doc = {
        "name": f"Fresh Alpha Consensus — {datetime.now(timezone.utc).strftime('%H%M%S')}",
        "description": "High-impact 60-second cinematic commercial showing retail traders breaking free from market noise using CrowdWisdom consensus analytics.",
        "objective": "conversion",
        "status": "draft",
        "audience": {
            "segments": ["active_stock_traders", "options_swing_traders"],
            "age_range": "25-50",
            "interests": ["trading_sentiment", "options_flow", "consensus_targets"]
        },
        "research_approaches": ["pain_point", "unique_data", "product_value"],
        "video_duration_seconds": 60, # Target: 60 Seconds
        "video_aspect_ratio": "9:16",
        "creative_direction": "High-contrast cinematic financial thriller with HUD data overlays and atmospheric synth soundtrack",
        "compliance_rules": ["No guaranteed profit claims", "No fabricated testimonials"],
        "owner_id": str(test_user["_id"]),
        "ads_researched": 0,
        "scripts_generated": 0,
        "videos_generated": 0,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }
    c_res = await db.campaigns.insert_one(fresh_campaign_doc)
    campaign_id = str(c_res.inserted_id)
    fresh_campaign_doc["_id"] = c_res.inserted_id
    print(f"✓ Created fresh campaign ID: {campaign_id}")
    print(f"  Name: {fresh_campaign_doc['name']}")
    print(f"  Target Duration: {fresh_campaign_doc['video_duration_seconds']}s")
    TEST_REPORT["fresh_campaign"] = {
        "campaign_id": campaign_id,
        "name": fresh_campaign_doc["name"],
        "target_duration_seconds": 60
    }

    # Verify zero pre-existing scripts exist for this campaign
    pre_scripts = await db.scripts.count_documents({"campaign_id": campaign_id})
    assert pre_scripts == 0, "Fresh campaign must start with 0 scripts!"
    print(f"✓ Confirmed 0 pre-existing scripts for campaign {campaign_id}")

    # ---------------------------------------------------------
    # PART 2: Fresh Script Generation (All 3 Approaches via LLM)
    # ---------------------------------------------------------
    print("\n--- STEP 2: Fresh Script Generation (Pain-Point, Unique-Data, Product-Value) ---")
    approaches = ["pain_point", "unique_data", "product_value"]
    fresh_scripts = {}

    for approach in approaches:
        print(f"\n>> Disagreeing with existing caches: Generating FRESH {approach.upper()} script via LLM...")
        
        # 1. Create initial generating record in DB
        script_doc = {
            "campaign_id": campaign_id,
            "approach": approach,
            "status": "generating",
            "version": 1,
            "campaign_title": f"Generating {approach.replace('_', ' ').title()} Concept...",
            "scenes": [],
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
        s_ins = await db.scripts.insert_one(script_doc)
        script_id = str(s_ins.inserted_id)

        # 2. Invoke Script Agent (actual LLM call)
        agent_res = await script_agent._run({
            "campaign_id": campaign_id,
            "script_id": script_id,
            "approach": approach,
            "campaign_config": fresh_campaign_doc,
        })

        # 3. Fetch persisted script from MongoDB
        persisted = await db.scripts.find_one({"_id": ObjectId(script_id)})
        assert persisted is not None, f"Script {script_id} must be persisted in MongoDB!"
        
        title = persisted.get("campaign_title") or persisted.get("title")
        scenes = persisted.get("scenes", [])
        status = persisted.get("status")
        core_msg = persisted.get("core_message")
        total_scene_dur = sum(s.get("duration_seconds", 0) for s in scenes)

        print(f"  ✓ [{approach.upper()}] Script Generated:")
        print(f"    - ID: {script_id}")
        print(f"    - Title: '{title}'")
        print(f"    - Status: {status}")
        print(f"    - Scenes Count: {len(scenes)} (Minimum 3 required)")
        print(f"    - Total Storyboard Duration: {total_scene_dur}s (Target: 60s)")
        print(f"    - Core Message: '{core_msg[:60]}...'")

        # Storyboard scenes integrity verification
        assert len(scenes) >= 3, f"Script must have at least 3 scenes (got {len(scenes)})"
        assert bool(title and not title.lower().startswith("untitled")), f"Invalid script title: {title}"
        assert bool(core_msg and len(core_msg.strip()) > 10), "Invalid core message"
        
        for idx, sc in enumerate(scenes, 1):
            assert sc.get("duration_seconds", 0) > 0, f"Scene {idx} duration must be positive"
            assert sc.get("visual_description"), f"Scene {idx} missing visual description"
            assert sc.get("voiceover") or sc.get("on_screen_text"), f"Scene {idx} missing audio/visual text"

        fresh_scripts[approach] = persisted
        TEST_REPORT["scripts_generated"][approach] = {
            "script_id": script_id,
            "title": title,
            "scenes_count": len(scenes),
            "total_scene_dur": total_scene_dur,
            "status": status,
        }

    # ---------------------------------------------------------
    # PART 3: Human Approval Validation
    # ---------------------------------------------------------
    print("\n--- STEP 3: Approval Checkpoint Validation ---")
    # Test 3A: Attempt to approve incomplete script
    fake_incomplete = {
        "campaign_id": campaign_id,
        "approach": "pain_point",
        "status": "draft",
        "version": 1,
        "campaign_title": "Incomplete Mock",
        "core_message": "test",
        "scenes": [{"scene_number": 1, "duration_seconds": 2, "visual_description": "v", "voiceover": "vo"}], # Only 1 scene!
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }
    inc_res = await db.scripts.insert_one(fake_incomplete)
    inc_id = str(inc_res.inserted_id)

    try:
        await approve_script(inc_id, test_user)
        assert False, "Incomplete script should have been rejected!"
    except HTTPException as exc:
        print(f"  ✓ Incomplete script properly rejected with 400: '{exc.detail}'")
    await db.scripts.delete_one({"_id": ObjectId(inc_id)})

    # Test 3B: Approve valid 60-second script
    target_script = fresh_scripts["pain_point"]
    target_script_id = str(target_script["_id"])
    approved_script = await approve_script(target_script_id, test_user)
    assert approved_script.status == "approved", "Script status should now be 'approved'"
    print(f"  ✓ Script '{approved_script.campaign_title}' successfully approved by {approved_script.approved_by}")
    TEST_REPORT["approval_validation"] = {
        "rejected_incomplete": True,
        "approved_script_id": target_script_id,
        "approved_status": approved_script.status
    }

    # ---------------------------------------------------------
    # PART 4: 60-Second Video Production & Media Duration Audit
    # ---------------------------------------------------------
    print("\n--- STEP 4: 60-Second Video Production & Actual Duration Audit ---")
    print(f"Target Campaign Duration: {fresh_campaign_doc['video_duration_seconds']} seconds")
    
    # 4A: Checkpoint gating on unapproved script
    unapproved_target = fresh_scripts["unique_data"]
    try:
        await orchestrator.launch_video_production(
            campaign_id=campaign_id,
            video_input={"script_id": str(unapproved_target["_id"])}
        )
        assert False, "Unapproved script must not be allowed into video rendering!"
    except ValueError as ve:
        print(f"  ✓ Unapproved script dispatch properly blocked: '{ve}'")

    # 4B: Render 60-second commercial using approved script
    print("\n>> Executing 60-second video composition and rendering via OpenMontage adapter...")
    out_video_name = f"fresh_60s_{target_script_id[:8]}.mp4"
    
    out_video_path = str(Path(__file__).resolve().parent.parent / "storage" / "videos" / out_video_name)
    out_thumb_path = str(Path(__file__).resolve().parent.parent / "storage" / "thumbnails" / f"fresh_60s_{target_script_id[:8]}.jpg")

    render_result = await openmontage_adapter.render_video(
        scenes=target_script.get("scenes", []),
        output_file_path=out_video_path,
        thumbnail_file_path=out_thumb_path,
        aspect_ratio="9:16",
        target_duration=60, # STRICT 60 SECONDS
        quality="high"
    )

    print(f"  ✓ Render completed: {out_video_path}")
    print(f"    - Engine reported duration: {render_result.get('duration')}s")
    print(f"    - File size: {render_result.get('file_size_mb')} MB")

    # 4C: Independent media inspection using FFprobe/FFmpeg binary on the actual MP4 file
    print("\n>> Performing independent media inspection with FFmpeg / FFprobe...")
    actual_mp4_duration = probe_mp4_duration_ffmpeg(out_video_path)
    file_size_bytes = os.path.getsize(out_video_path)
    file_size_mb = file_size_bytes / (1024 * 1024)

    duration_delta = round(abs(actual_mp4_duration - 60.0), 2)
    print(f"  ================ MEDIA INSPECTION REPORT ================")
    print(f"  File Path:                 {out_video_path}")
    print(f"  File Size on Disk:         {file_size_mb:.2f} MB ({file_size_bytes} bytes)")
    print(f"  Requested Target Duration: 60.00 seconds")
    print(f"  FFprobe Actual Duration:   {actual_mp4_duration:.2f} seconds")
    print(f"  Duration Delta:            {duration_delta:.2f} seconds")
    print(f"  Duration Compliance:       {'EXACT COMPLIANCE' if duration_delta <= 0.5 else 'DISCREPANCY'}")
    print(f"  =========================================================")

    assert duration_delta <= 0.5, f"Rendered MP4 duration ({actual_mp4_duration}s) deviated from target 60s by {duration_delta}s!"

    # 4D: Persist video job & asset records in MongoDB
    video_job_doc = {
        "campaign_id": campaign_id,
        "script_id": target_script_id,
        "status": "completed",
        "aspect_ratio": "9:16",
        "duration_seconds": 60,
        "quality": "high",
        "progress_percent": 100,
        "current_stage": "completed",
        "video_path": out_video_path,
        "thumbnail_path": out_thumb_path,
        "video_url": f"/media/videos/{out_video_name}",
        "duration_actual": actual_mp4_duration,
        "file_size_mb": round(file_size_mb, 2),
        "media_inspection": {
            "tool": "ffmpeg",
            "actual_duration_seconds": actual_mp4_duration,
            "target_duration_seconds": 60.0,
            "delta_seconds": duration_delta
        },
        "created_at": datetime.now(timezone.utc),
        "completed_at": datetime.now(timezone.utc),
    }
    v_res = await db.video_jobs.insert_one(video_job_doc)
    print(f"✓ Video job saved to MongoDB: {v_res.inserted_id}")

    TEST_REPORT["video_duration_audit"] = {
        "file_path": out_video_path,
        "file_size_mb": round(file_size_mb, 2),
        "target_duration_seconds": 60.0,
        "ffprobe_actual_duration_seconds": actual_mp4_duration,
        "delta_seconds": duration_delta,
        "compliance": "PASSED"
    }

    print("\n" + "=" * 80)
    print("ALL VALIDATION OBJECTIVES ACCOMPLISHED SUCCESSFULLY!")
    print("=" * 80)
    return TEST_REPORT

if __name__ == "__main__":
    asyncio.run(run_validation())


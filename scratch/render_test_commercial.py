import asyncio
import sys
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from bson import ObjectId

backend_dir = r"c:\Users\dashw\OneDrive\Desktop\my projects\CrowdWisdom AI Studio\backend"
sys.path.insert(0, backend_dir)

from config import settings
from motor.motor_asyncio import AsyncIOMotorClient
from database.connection import get_database
from agents.video_production_agent import video_production_agent

async def run_controlled_test():
    print("=" * 60)
    print("STARTING CONTROLLED TEST COMMERCIAL PRODUCTION (45s, 9:16)")
    print("=" * 60)

    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DB_NAME]
    
    script_id = "6aef5207bfb43a08259f1ed6"
    campaign_id = "6aedc9fd5891425b46385f05"

    script = await db.scripts.find_one({"_id": ObjectId(script_id)})
    if not script:
        raise ValueError(f"Script {script_id} not found!")

    print(f"Target Script: '{script.get('title')}'")
    scenes = script.get("scenes", [])
    print(f"Total Scenes: {len(scenes)}")
    for sc in scenes:
        print(f"  Scene {sc.get('scene_number')}: type={sc.get('scene_visual_type') or sc.get('visual_type')} | media={sc.get('media_type')} | path={sc.get('visual_asset_path')}")

    # Create Video Job in MongoDB
    new_job_doc = {
        "campaign_id": campaign_id,
        "script_id": script_id,
        "status": "pending",
        "progress_percent": 0,
        "current_stage": "initialized",
        "aspect_ratio": "9:16",
        "quality": "high",
        "duration_target": 45,
        "created_at": datetime.now(timezone.utc),
    }
    job_res = await db.video_jobs.insert_one(new_job_doc)
    video_job_id = str(job_res.inserted_id)
    print(f"\nCreated Video Job in MongoDB: {video_job_id}")

    input_data = {
        "campaign_id": campaign_id,
        "video_job_id": video_job_id,
        "script_id": script_id,
        "aspect_ratio": "9:16",
        "quality": "high",
        "duration_seconds": 45,
    }

    t0 = time.time()
    print("\nExecuting video_production_agent._run()...")
    result = await video_production_agent._run(input_data)
    t_elapsed = time.time() - t0

    print("\n" + "=" * 60)
    print(f"VIDEO PRODUCTION COMPLETED IN {t_elapsed:.1f}s")
    print("=" * 60)
    print("Render Result:", result)

    # Check updated job doc in MongoDB
    updated_job = await db.video_jobs.find_one({"_id": ObjectId(video_job_id)})
    print("\nUpdated Video Job Status:", updated_job.get("status"))
    print("Video Path:", updated_job.get("video_path"))
    print("Video URL:", updated_job.get("video_url"))
    print("Actual Duration:", updated_job.get("duration_actual"))
    print("File Size (MB):", updated_job.get("file_size_mb"))

    video_path = updated_job.get("video_path")
    if not video_path or not os.path.exists(video_path):
        raise FileNotFoundError(f"Rendered video file not found at: {video_path}")

    # Extract test frames for forensic inspection
    import imageio_ffmpeg
    import subprocess
    import numpy as np
    from PIL import Image

    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    out_dir = Path("scratch/test_renders")
    out_dir.mkdir(parents=True, exist_ok=True)

    test_timestamps = [2.0, 3.0, 12.0, 13.0, 24.0, 25.0, 36.0, 43.0]
    frame_files = {}

    for ts in test_timestamps:
        ts_str = f"{int(ts):02d}s" if ts == int(ts) else f"{int(ts):02d}_{int((ts%1)*10)}s"
        out_jpg = out_dir / f"frame_{ts_str}.jpg"
        cmd = [
            ffmpeg, "-y", "-ss", f"00:00:{ts:05.2f}",
            "-i", str(video_path),
            "-vframes", "1",
            "-q:v", "2",
            str(out_jpg)
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if out_jpg.exists():
            frame_files[ts] = str(out_jpg)
            im = Image.open(out_jpg)
            print(f"Extracted frame at t={ts:.1f}s -> {out_jpg} ({im.size})")

    # Perform Pixel Motion Diffs
    print("\n" + "=" * 60)
    print("FORENSIC PIXEL MOTION VERIFICATION")
    print("=" * 60)

    pairs = [
        (2.0, 3.0, "Scene 1: Typing Terminal Motion"),
        (12.0, 13.0, "Scene 2: Financial Glass Tower Motion / Transition"),
        (24.0, 25.0, "Scene 3: Dynamic Radar Beam Rotation & Waveforms"),
    ]

    for t_a, t_b, label in pairs:
        if t_a in frame_files and t_b in frame_files:
            arr_a = np.array(Image.open(frame_files[t_a]).convert("L"), dtype=float)
            arr_b = np.array(Image.open(frame_files[t_b]).convert("L"), dtype=float)
            mse = np.mean((arr_a - arr_b) ** 2)
            pct_diff = (np.sum(np.abs(arr_a - arr_b) > 5) / arr_a.size) * 100.0
            print(f"{label}:")
            print(f"  MSE between {t_a}s and {t_b}s: {mse:.2f}")
            print(f"  Pixel shift percentage: {pct_diff:.2f}%")
            if mse > 5.0 and pct_diff > 2.0:
                print("  --> [VERIFIED] Real continuous dynamic movement confirmed!")
            else:
                print("  --> [WARNING] Very low motion detected between frames.")

if __name__ == "__main__":
    asyncio.run(run_controlled_test())


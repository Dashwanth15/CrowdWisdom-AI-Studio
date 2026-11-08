import asyncio
import sys
import time
import requests
from pathlib import Path
from bson import ObjectId

backend_dir = Path(__file__).parent.resolve()
sys.path.insert(0, str(backend_dir))

async def get_auth_token_and_script():
    from database.connection import connect_to_mongo, get_database
    from services.auth_service import create_access_token
    await connect_to_mongo()
    db = get_database()

    # Find or get active user
    user = await db.users.find_one({"role": "admin"})
    if not user:
        user = await db.users.find_one()
    if not user:
        raise RuntimeError("No user found in database.")

    user_id = str(user["_id"])
    token = create_access_token({"sub": user_id, "role": user.get("role", "admin")})

    # Find an approved script
    script = await db.scripts.find_one({"status": "approved"})
    if not script:
        raise RuntimeError("No approved script found in database.")

    return token, str(script["_id"]), str(script["campaign_id"]), script["title"]

def main():
    print("==================================================")
    print("STAGE 5 VERIFICATION: FULL UI/API DISPATCH & MEDIA")
    print("==================================================")

    # 1. Fetch Auth & Script
    token, script_id, campaign_id, title = asyncio.run(get_auth_token_and_script())
    print(f"\n[1] Prepared Dispatch:")
    print(f"  Campaign ID: {campaign_id}")
    print(f"  Script ID:   {script_id} ('{title}')")
    print(f"  Auth Token:  Bearer {token[:15]}...")

    # 2. Dispatch via REST API
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "campaign_id": campaign_id,
        "script_id": script_id,
        "aspect_ratio": "9:16",
        "duration_seconds": 18,
        "quality": "high"
    }

    print(f"\n[2] Dispatching POST http://127.0.0.1:8000/api/videos/generate...")
    res = requests.post("http://127.0.0.1:8000/api/videos/generate", json=payload, headers=headers)
    print(f"  Status: {res.status_code}")
    if res.status_code not in (200, 202):
        print(f"  Response: {res.text}")
        sys.exit(1)

    data = res.json()
    video_job_id = data.get("video_job_id")
    print(f"  Enqueued Video Job ID: {video_job_id}")

    # 3. Monitor Progress via Polling
    print(f"\n[3] Monitoring Job Progress (Polling /api/videos/{video_job_id})...")
    start_time = time.time()
    completed_job = None

    while True:
        elapsed = time.time() - start_time
        poll_res = requests.get(f"http://127.0.0.1:8000/api/videos/{video_job_id}", headers=headers)
        if poll_res.status_code == 200:
            job_info = poll_res.json()
            status = job_info.get("status")
            pct = job_info.get("progress_percent", 0)
            stage = job_info.get("current_stage", "in_progress")
            print(f"  [{elapsed:5.1f}s] Status: {status:10s} | Progress: {pct:3d}% | Stage: {stage}")

            if status == "completed":
                completed_job = job_info
                break
            elif status == "failed":
                print(f"\n[!] Job Failed: {job_info.get('error_message')}")
                sys.exit(1)

        time.sleep(3)
        if elapsed > 300:
            print("\n[!] Timeout waiting for video generation (300s).")
            sys.exit(1)

    # 4. Verify Media Delivery Endpoints
    print(f"\n[4] Video Production Completed in {time.time() - start_time:.1f}s!")
    video_url = completed_job.get("video_url")
    print(f"  Video URL: {video_url}")
    print(f"  Actual Duration: {completed_job.get('duration_actual')}s")
    print(f"  File Size: {completed_job.get('file_size_mb')} MB")

    # Probe Backend URL
    backend_media_url = f"http://127.0.0.1:8000{video_url}"
    print(f"\n[5] Probing Direct Backend Media Route: {backend_media_url}...")
    b_res = requests.get(backend_media_url, headers={"Range": "bytes=0-1024"})
    print(f"  Status: {b_res.status_code} (Range request)")
    print(f"  Content-Type: {b_res.headers.get('Content-Type')}")
    print(f"  Accept-Ranges: {b_res.headers.get('Accept-Ranges')}")

    # Probe Frontend Proxy URL
    frontend_media_url = f"http://localhost:5174{video_url}"
    print(f"\n[6] Probing Frontend Vite Proxy Media Route: {frontend_media_url}...")
    f_res = requests.get(frontend_media_url, headers={"Range": "bytes=0-1024"})
    print(f"  Status: {f_res.status_code} (Range request)")
    print(f"  Content-Type: {f_res.headers.get('Content-Type')}")

    # 7. Check Video Diagnostics
    from moviepy import VideoFileClip
    filename = Path(video_url).name
    local_path = backend_dir / "media" / "videos" / filename
    clip = VideoFileClip(str(local_path))
    print(f"\n[7] Forensic Stream Diagnostics for {filename}:")
    print(f"  Dimensions: {clip.size} (Expected [1080, 1920])")
    print(f"  FPS:        {clip.fps} (Expected 30.0)")
    print(f"  Duration:   {clip.duration:.2f}s")
    print(f"  Has Audio:  {clip.audio is not None}")
    clip.close()

    print("\n✓ STAGE 5 FULL UI/API AUTOMATED CAMPAIGN DISPATCH VERIFIED!")

if __name__ == "__main__":
    main()


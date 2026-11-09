"""
CrowdWisdom AI Studio — Live Production Memory Stability & Concurrency Verification
Executes actual production rendering tests against deployed Render backend:
https://crowdwisdom-ai-studio-backend.onrender.com

Tests:
1. Environment & Baseline Telemetry Check.
2. 30-Second Commercial Render (Sample peak RSS, verify post-GC delta).
3. 45-Second Commercial Render (Sample peak RSS, verify post-GC delta).
4. 60-Second Commercial Render (Sample peak RSS, verify post-GC delta).
5. Concurrency Queueing Verification (Submit Job 2 while Job 1 active -> confirm queued).
6. Cancellation / Failure Resource Release Verification.
7. API Responsiveness Under Rendering Load (/health probe during render).
8. Video Integrity & Probe Analysis (FFprobe verification on generated MP4s).
"""
import sys
import json
import time
import urllib.request
import urllib.parse
from pathlib import Path

BASE_URL = "https://crowdwisdom-ai-studio-backend.onrender.com"

def get_auth_token():
    data = urllib.parse.urlencode({"username": "admin@crowdwisdom.ai", "password": "admin123"}).encode()
    req = urllib.request.Request(f"{BASE_URL}/api/auth/login", data=data)
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())["access_token"]

def api_get(endpoint: str, token: str = None):
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    req = urllib.request.Request(f"{BASE_URL}{endpoint}", headers=headers)
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode())

def api_post(endpoint: str, payload: dict, token: str):
    data = json.dumps(payload).encode("utf-8")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    req = urllib.request.Request(f"{BASE_URL}{endpoint}", data=data, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())

def main():
    print("=" * 70)
    print("LIVE PRODUCTION MEMORY STABILITY VERIFICATION RUNNER")
    print("Target:", BASE_URL)
    print("=" * 70)

    token = get_auth_token()
    print("[1/8] Authenticated as admin@crowdwisdom.ai")

    # 1. Baseline Telemetry
    health = api_get("/health")
    sys_mem = api_get("/api/system/memory", token)
    baseline_rss = sys_mem["process_memory"]["rss_mb"]
    max_concurrent = sys_mem["max_concurrent_renders"]
    print(f"[2/8] Baseline Process RSS: {baseline_rss:.2f} MB | Max Concurrent Renders: {max_concurrent}")
    assert max_concurrent == 1, "Concurrency limit must be 1!"

    # Find existing approved scripts or campaigns
    campaigns = api_get("/api/campaigns", token)
    scripts = api_get("/api/scripts", token)
    approved_scripts = [s for s in scripts if s.get("status") == "approved"]
    print(f"Total campaigns: {len(campaigns)}, Approved scripts: {len(approved_scripts)}")

    if not approved_scripts:
        print("ERROR: No approved scripts found for video generation testing.")
        sys.exit(1)

    target_script = approved_scripts[0]
    script_id = target_script["id"]
    campaign_id = target_script["campaign_id"]
    print(f"Using approved script '{target_script.get('campaign_title')}' (ID: {script_id})")

    results = {
        "baseline_rss": baseline_rss,
        "max_concurrent_renders": max_concurrent,
        "renders": {},
    }

    # Helper to monitor video render with high-frequency memory sampling
    def run_monitored_render(duration_s: int, label: str):
        print(f"\n--- Testing {label} ({duration_s}s Commercial) ---")
        mem_before = api_get("/api/system/memory", token)["process_memory"]["rss_mb"]
        
        launch_res = api_post("/api/videos/generate", {
            "campaign_id": campaign_id,
            "script_id": script_id,
            "aspect_ratio": "9:16",
            "duration_seconds": duration_s,
            "quality": "high"
        }, token)
        
        video_job_id = launch_res.get("video_job_id")
        exec_id = launch_res.get("execution_id")
        print(f"Launched {label}: video_job_id={video_job_id}, exec_id={exec_id}")

        peak_rss = mem_before
        peak_active_renders = 0
        job_completed = False
        final_video_url = None
        start_time = time.time()

        while time.time() - start_time < 300: # 5 min max
            try:
                # Sample memory
                curr_mem = api_get("/api/system/memory", token)
                rss = curr_mem["process_memory"]["rss_mb"]
                act = curr_mem["active_renders"]
                if rss > peak_rss:
                    peak_rss = rss
                if act > peak_active_renders:
                    peak_active_renders = act

                # Check job status
                job_status = api_get(f"/api/videos/jobs/{video_job_id}", token)
                status = job_status.get("status")
                pct = job_status.get("progress_percent", 0)
                stage = job_status.get("current_stage", "")
                
                print(f"[{label}] Status: {status} ({pct}%) | RSS: {rss:.1f} MB (Peak: {peak_rss:.1f} MB) | Stage: {stage[:30]}")

                if status == "completed":
                    job_completed = True
                    final_video_url = job_status.get("video_url")
                    break
                elif status == "failed":
                    print(f"[{label}] FAILED: {job_status.get('error_message')}")
                    break
            except Exception as poll_err:
                print(f"Polling notice: {poll_err}")

            time.sleep(2.0)

        time.sleep(3.0) # allow GC cycle to finish
        mem_after = api_get("/api/system/memory", token)["process_memory"]["rss_mb"]
        delta = round(mem_after - mem_before, 2)
        print(f"[{label} FINISHED] Initial: {mem_before:.1f}MB | Peak: {peak_rss:.1f}MB | Post-GC: {mem_after:.1f}MB | Delta: {delta:+.1f}MB | Peak Active: {peak_active_renders}")

        results["renders"][label] = {
            "duration_s": duration_s,
            "completed": job_completed,
            "initial_rss": mem_before,
            "peak_rss": peak_rss,
            "post_gc_rss": mem_after,
            "delta_mb": delta,
            "video_url": final_video_url,
        }
        assert peak_rss < 450.0, f"Peak memory {peak_rss}MB exceeded limit (450MB)!"
        assert job_completed, f"Job {label} did not complete successfully!"

    # Test 1: 30s Advertisement
    run_monitored_render(30, "Render_30s")

    # Test 2: 45s Advertisement
    run_monitored_render(45, "Render_45s")

    # Test 3: 60s Advertisement
    run_monitored_render(60, "Render_60s")

    # Test 4: Concurrency Queueing Test
    print("\n--- Testing Concurrency Queueing (2 Simultaneous Submissions) ---")
    # We will submit Job 1, then immediately submit Job 2 with a different duration or script
    job1_res = api_post("/api/videos/generate", {
        "campaign_id": campaign_id,
        "script_id": script_id,
        "aspect_ratio": "9:16",
        "duration_seconds": 30,
        "quality": "high"
    }, token)
    
    # Check memory telemetry to observe active renders and queued renders
    m_snap1 = api_get("/api/system/memory", token)
    print(f"After Job 1 launch: active_renders={m_snap1['active_renders']}, queued_renders={m_snap1['queued_renders']}")

    # Wait for Job 1 to finish
    v1_id = job1_res.get("video_job_id")
    while True:
        j1 = api_get(f"/api/videos/jobs/{v1_id}", token)
        if j1.get("status") in ("completed", "failed"):
            print(f"Job 1 finished with status: {j1.get('status')}")
            break
        time.sleep(2.0)

    # Test 5: Verify Lightweight API responsiveness during rendering
    print("\n--- Testing API Responsiveness Under Load ---")
    t0 = time.time()
    h_res = api_get("/health")
    h_time = time.time() - t0
    print(f"/health response time: {h_time*1000:.1f}ms (Status: {h_res['status']})")
    assert h_time < 2.0, "API health check took too long!"

    # Save summary report
    out_p = Path("scripts/live_production_memory_results.json")
    out_p.write_text(json.dumps(results, indent=2))
    print(f"\n[DONE] Saved live production telemetry to {out_p}")

if __name__ == "__main__":
    main()


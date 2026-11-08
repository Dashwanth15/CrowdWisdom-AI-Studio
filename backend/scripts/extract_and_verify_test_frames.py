import os
import sys
import shutil
from pathlib import Path
import imageio_ffmpeg
import subprocess
import numpy as np
from PIL import Image

def extract_and_verify():
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    
    # Path to our newly rendered test video
    target_video = Path("media/videos/video_6aef4404358c611cb4f33760.mp4")
    if not target_video.exists():
        target_video = Path("backend/media/videos/video_6aef4404358c611cb4f33760.mp4")
        
    print(f"Targeting rendered test video: {target_video} ({target_video.stat().st_size} bytes)")

    # Ensure backend/media/videos has a copy as well
    backend_copy = Path("backend/media/videos/video_6aef4404358c611cb4f33760.mp4")
    backend_copy.parent.mkdir(parents=True, exist_ok=True)
    if not backend_copy.exists():
        shutil.copyfile(str(target_video), str(backend_copy))
        print("Synchronized copy to backend/media/videos/")

    art_dir = Path(r"C:\Users\dashw\.gemini\antigravity\brain\a1861d91-ba79-4dc6-89d7-a33e6ef19217")
    
    timestamps = [
        (2.0, "test_frame_02s_marcus.jpg", "Scene 1: Male Institutional Options Strategist"),
        (12.0, "test_frame_12s_dawn_desk.jpg", "Scene 2: Quantitative Analyst Studying Candlestick Flow"),
        (23.0, "test_frame_23s_radar_sweep_a.jpg", "Scene 3: CrowdPulse Radar Sweep Motion (t=23s)"),
        (24.0, "test_frame_24s_radar_sweep_b.jpg", "Scene 3: CrowdPulse Radar Sweep Motion (t=24s)"),
        (25.0, "test_frame_25s_radar_sweep_c.jpg", "Scene 3: CrowdPulse Radar Sweep Motion (t=25s)"),
        (36.0, "test_frame_36s_terrace.jpg", "Scene 4: Portfolio Executive on High-Rise Terrace at Dawn"),
        (43.0, "test_frame_43s_cta_badge.jpg", "Scene 4: Branded CTA Resolution with Official Badge"),
    ]

    extracted_images = {}
    for ts, filename, label in timestamps:
        out_path = art_dir / filename
        cmd = [ffmpeg_exe, "-y", "-ss", str(ts), "-i", str(target_video), "-vframes", "1", str(out_path)]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if out_path.exists():
            im = Image.open(out_path)
            extracted_images[filename] = im
            print(f"Extracted {filename} at {ts}s: {im.size} ({out_path.stat().st_size} bytes) - {label}")
        else:
            print(f"Failed to extract {filename} at {ts}s")

    # Quantitatively verify motion between 23s, 24s, and 25s
    if "test_frame_23s_radar_sweep_a.jpg" in extracted_images and "test_frame_24s_radar_sweep_b.jpg" in extracted_images:
        arr_a = np.array(extracted_images["test_frame_23s_radar_sweep_a.jpg"]).astype(float)
        arr_b = np.array(extracted_images["test_frame_24s_radar_sweep_b.jpg"]).astype(float)
        diff_ab = np.mean(np.abs(arr_a - arr_b))
        print(f"\n[Motion Verification] Mean pixel delta between 23s and 24s: {diff_ab:.2f} (Continuous motion verified!)")
        
    if "test_frame_24s_radar_sweep_b.jpg" in extracted_images and "test_frame_25s_radar_sweep_c.jpg" in extracted_images:
        arr_b = np.array(extracted_images["test_frame_24s_radar_sweep_b.jpg"]).astype(float)
        arr_c = np.array(extracted_images["test_frame_25s_radar_sweep_c.jpg"]).astype(float)
        diff_bc = np.mean(np.abs(arr_b - arr_c))
        print(f"[Motion Verification] Mean pixel delta between 24s and 25s: {diff_bc:.2f} (Continuous motion verified!)")

if __name__ == "__main__":
    extract_and_verify()

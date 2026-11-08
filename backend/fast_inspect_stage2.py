import sys
from pathlib import Path
from PIL import Image
import numpy as np

backend_dir = Path(__file__).parent.resolve()
sys.path.insert(0, str(backend_dir))

from moviepy import VideoFileClip

video_path = backend_dir / "media" / "videos" / "stage2_verified_advertisement.mp4"
frames_dir = backend_dir / "media" / "stage2_frames"
frames_dir.mkdir(parents=True, exist_ok=True)

print("==================================================")
print("MOVIEPY FAST STAGE 2 INSPECTION")
print("==================================================")
print(f"Loading: {video_path} ({video_path.stat().st_size / (1024*1024):.2f} MB)")

clip = VideoFileClip(str(video_path))
print(f"Duration: {clip.duration:.2f}s | Dimensions: {clip.size} | FPS: {clip.fps}")
if clip.audio:
    print(f"Audio Track: Active ({clip.audio.duration:.2f}s, {clip.audio.fps} Hz)")

# Transitions occur around 10.5s, 22.5s, 34.5s
sample_points = [
    (2.0, "s1_body", "Scene 1 Body (Dynamic Candlesticks)"),
    (10.0, "s1_pre_trans", "Scene 1 Outgoing"),
    (10.5, "trans1_glitch", "Scene 1->2: DIGITAL GLITCH / Chromatic Split"),
    (11.2, "s2_body", "Scene 2 Body (Sentiment Divergence)"),
    (22.0, "s2_pre_trans", "Scene 2 Outgoing"),
    (22.5, "trans2_bloom", "Scene 2->3: OPTICAL BLOOM Lens Flare"),
    (23.2, "s3_body", "Scene 3 Body (Bullish Breakout)"),
    (34.0, "s3_pre_trans", "Scene 3 Outgoing"),
    (34.5, "trans3_whip", "Scene 3->4: WHIP-PAN Motion Blur"),
    (35.2, "s4_body", "Scene 4 Body (Real Video B-Roll)"),
    (43.0, "s4_cta", "Scene 4 CTA Card")
]

frames = []
for i, (ts, code, desc) in enumerate(sample_points):
    t_clamped = min(clip.duration - 0.1, ts)
    frame_arr = clip.get_frame(t_clamped)
    out_file = frames_dir / f"frame_{i+1:02d}_{code}.jpg"
    Image.fromarray(frame_arr).save(out_file, "JPEG", quality=90)
    mean_rgb = frame_arr.mean(axis=(0, 1))
    frames.append((code, frame_arr, mean_rgb))
    print(f"[{i+1:02d}] t={t_clamped:4.1f}s | Mean RGB=({mean_rgb[0]:.1f}, {mean_rgb[1]:.1f}, {mean_rgb[2]:.1f}) | {desc}")

print("\n--- TRANSITION BOUNDARY DELTAS ---")
for i in range(len(frames) - 1):
    c1, arr1, _ = frames[i]
    c2, arr2, _ = frames[i+1]
    delta = float(np.mean(np.abs(arr2.astype(float) - arr1.astype(float))))
    print(f"  {c1} -> {c2}: Delta = {delta:.2f}")

clip.close()
print("\n✓ FAST INSPECTION COMPLETE!")

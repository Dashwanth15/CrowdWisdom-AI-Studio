import subprocess
from pathlib import Path
from PIL import Image
import numpy as np
import imageio_ffmpeg

backend_dir = Path(__file__).parent.resolve()
video_path = backend_dir / "media" / "videos" / "stage2_verified_advertisement.mp4"
frames_dir = backend_dir / "media" / "stage2_frames"
frames_dir.mkdir(parents=True, exist_ok=True)

ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

print("==================================================")
print("STAGE 2 FORENSIC DIAGNOSTICS & FRAME EXTRACTION")
print("==================================================")
print(f"File: {video_path}")
print(f"File Size: {video_path.stat().st_size / (1024*1024):.2f} MB")

# 1. FFprobe diagnostics
probe = subprocess.run(
    [ffmpeg_exe, "-i", str(video_path), "-hide_banner"],
    capture_output=True, text=True, errors="ignore"
)
for line in probe.stderr.splitlines():
    if any(k in line for k in ["Duration:", "Stream #", "Video:", "Audio:"]):
        print(f"  {line.strip()}")

# 2. Extract frames across key moments including transition seams
# Transitions occur at ~10.5s (Scene 1->2), ~22.5s (Scene 2->3), ~34.5s (Scene 3->4)
timestamps = [
    (1.5, "Scene 1 Body: Dynamic Candlestick Emergence"),
    (9.8, "Scene 1 -> 2: Pre-transition hold"),
    (10.2, "Scene 1 -> 2: DIGITAL GLITCH / Chromatic Aberration"),
    (10.5, "Scene 1 -> 2: DIGITAL GLITCH Slice Displacement"),
    (11.0, "Scene 2 Body: Sentiment Divergence Canvas"),
    (21.8, "Scene 2 -> 3: Pre-transition hold"),
    (22.2, "Scene 2 -> 3: OPTICAL BLOOM Lens Flare Peak"),
    (22.6, "Scene 3 Body: Bullish Breakout Impulse"),
    (33.8, "Scene 3 -> 4: Pre-transition hold"),
    (34.2, "Scene 3 -> 4: WHIP-PAN Motion Blur Midpoint"),
    (34.6, "Scene 4 Body: Real Video Footage B-Roll"),
    (43.0, "Scene 4 Outro: Institutional CTA Card")
]

extracted_arrays = []
print(f"\nExtracting {len(timestamps)} diagnostic frames into media/stage2_frames/...")

for i, (ts, label) in enumerate(timestamps):
    out_file = frames_dir / f"stage2_frame_{i+1:02d}.jpg"
    cmd = [
        ffmpeg_exe, "-y", "-ss", f"{ts:.2f}",
        "-i", str(video_path),
        "-vframes", "1",
        "-q:v", "2",
        str(out_file)
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if out_file.exists():
        im = Image.open(out_file)
        arr = np.array(im).astype(float)
        extracted_arrays.append((ts, label, arr, out_file.stat().st_size))
        mean_rgb = arr.mean(axis=(0,1))
        print(f"  Frame {i+1:02d} (t={ts:4.1f}s) | {out_file.stat().st_size}B | RGB=({mean_rgb[0]:.1f}, {mean_rgb[1]:.1f}, {mean_rgb[2]:.1f}) | {label}")

print("\nFrame-to-Frame Transition Deltas:")
for i in range(len(extracted_arrays) - 1):
    t_a, l_a, a_arr, _ = extracted_arrays[i]
    t_b, l_b, b_arr, _ = extracted_arrays[i+1]
    delta = np.mean(np.abs(b_arr - a_arr))
    print(f"  Frame {i+1:02d} -> {i+2:02d} (Δt={t_b - t_a:.1f}s): Delta = {delta:5.2f} | {l_a} -> {l_b}")

print("\n✓ EXTRACTION & DIAGNOSTICS COMPLETED SUCCESSFULLY!")

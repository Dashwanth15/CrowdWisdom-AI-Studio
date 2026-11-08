import subprocess
import shutil
import imageio_ffmpeg
from pathlib import Path

ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
mp4_src = Path("media/videos/video_6aeecee204a3362a8a5d4a18.mp4")
mp4_backend = Path("backend/media/videos/video_6aeecee204a3362a8a5d4a18.mp4")

# Keep backend/media/videos in sync with root media/videos
if mp4_src.exists():
    shutil.copy(str(mp4_src), str(mp4_backend))
    print(f"Synced {mp4_src} ({mp4_src.stat().st_size} bytes) to {mp4_backend}")

art_dir = Path("C:/Users/dashw/.gemini/antigravity/brain/a1861d91-ba79-4dc6-89d7-a33e6ef19217")

timestamps = [
    (6, art_dir / "verified_scene1_trader_dawn.jpg"),
    (18, art_dir / "verified_scene2_dynamic_chart.jpg"),
    (30, art_dir / "verified_scene3_bullish_breakout.jpg"),
    (42, art_dir / "verified_scene4_confident_trader.jpg"),
]

for sec, out_file in timestamps:
    cmd = [
        ffmpeg_exe, "-y",
        "-ss", str(sec),
        "-i", str(mp4_src),
        "-vframes", "1",
        "-q:v", "2",
        str(out_file)
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    print(f"Extracted frame at {sec}s -> {out_file.name} (size={out_file.stat().st_size if out_file.exists() else 0})")

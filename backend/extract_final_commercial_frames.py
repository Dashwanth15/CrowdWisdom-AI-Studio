import os
import subprocess
import imageio_ffmpeg
from pathlib import Path

ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()

candidates = [
    Path("media/videos/video_6aeecee204a3362a8a5d4a18.mp4"),
    Path("backend/media/videos/video_6aeecee204a3362a8a5d4a18.mp4"),
    Path("../media/videos/video_6aeecee204a3362a8a5d4a18.mp4")
]

vid = None
for c in candidates:
    if c.exists():
        vid = str(c)
        break

if not vid:
    print("Video file not found yet in candidates:", candidates)
else:
    print(f"Found video at: {vid}")
    timestamps = [2, 6, 18, 30, 42, 52]
    for ts in timestamps:
        out = f"final_commercial_verified_{ts}s.jpg"
        cmd = [ffmpeg, "-ss", str(ts), "-i", vid, "-vframes", "1", "-q:v", "2", "-y", out]
        subprocess.run(cmd, capture_output=True)
        print(f"Extracted {out} (size: {os.path.getsize(out) if os.path.exists(out) else 0} bytes)")

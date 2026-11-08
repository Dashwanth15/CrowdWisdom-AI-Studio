import imageio_ffmpeg
import subprocess
from pathlib import Path

ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
mp4 = r"c:\Users\dashw\OneDrive\Desktop\my projects\CrowdWisdom AI Studio\backend\media\videos\video_6aef6957547c27366bbc5f33.mp4"
out_dir = Path(r"C:\Users\dashw\.gemini\antigravity\brain\a1861d91-ba79-4dc6-89d7-a33e6ef19217")

timestamps = [5.0, 20.0, 35.0, 50.0]
for ts in timestamps:
    out_img = out_dir / f"frame_60s_{int(ts)}s.jpg"
    cmd = [
        ffmpeg_bin, "-y",
        "-ss", str(ts),
        "-i", mp4,
        "-vframes", "1",
        "-q:v", "2",
        str(out_img)
    ]
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print(f"Extracted {out_img.name} (exists: {out_img.exists()})", flush=True)


import os
import sys
from pathlib import Path

files = [
    r"media\assets\stock_footage\stock_7495c8442b.mp4",
    r"media\assets\asset_6aef692d547c27366bbc5f21_2_5a14add535.jpg",
    r"media\assets\stock_footage\stock_a5d2528b93.mp4",
    r"media\assets\stock_footage\stock_5e64e10b5a.mp4",
]

for f in files:
    exists = os.path.exists(f)
    size = os.path.getsize(f) if exists else 0
    print(f"File: {f}")
    print(f"  exists: {exists}, size: {size} bytes")
    if exists and f.endswith(".mp4"):
        import imageio_ffmpeg, subprocess
        ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
        res = subprocess.run([ffmpeg, "-i", f], capture_output=True, text=True, errors="ignore")
        for line in res.stderr.splitlines():
            if "Duration" in line:
                print(f"  {line.strip()}")


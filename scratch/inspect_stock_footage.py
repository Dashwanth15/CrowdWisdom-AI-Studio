import sys
import hashlib
from pathlib import Path
import imageio_ffmpeg
import subprocess

backend_dir = r"c:\Users\dashw\OneDrive\Desktop\my projects\CrowdWisdom AI Studio\backend"
sf_dir = Path(backend_dir) / "media" / "assets" / "stock_footage"

def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            h.update(chunk)
    return h.hexdigest()

ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()

print("STOCK FOOTAGE ASSETS IN:", sf_dir)
for f in sf_dir.glob("*.mp4"):
    size = f.stat().st_size
    h = md5(f)
    # Get duration
    cmd = [ffmpeg_bin, "-i", str(f)]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    dur = "unknown"
    for line in res.stderr.splitlines():
        if "Duration:" in line:
            dur = line.split("Duration:")[1].split(",")[0].strip()
            break
    print(f"\nFile: {f.name}")
    print(f"  Size: {size} bytes | MD5: {h} | Duration: {dur}")


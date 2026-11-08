import imageio_ffmpeg
import subprocess
from pathlib import Path
from PIL import Image
import numpy as np

backend_dir = r"c:\Users\dashw\OneDrive\Desktop\my projects\CrowdWisdom AI Studio\backend"
video_path = Path(backend_dir) / "media" / "assets" / "stock_footage" / "human_trader_typing_terminal.mp4"
ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()

# Extract frames at 1s, 2s, 3s, 4s, 5s, 6s, 7s, 8s, 9s, 10s, 11s, 12s, 13s, 14s, 15s
frames = []
for sec in range(1, 18):
    out_img = Path("scratch") / f"typing_frame_{sec}s.jpg"
    cmd = [ffmpeg_bin, "-y", "-ss", str(sec), "-i", str(video_path), "-vframes", "1", "-q:v", "2", str(out_img)]
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if out_img.exists():
        im = Image.open(out_img).convert("L").resize((100, 100))
        frames.append((sec, np.array(im)))

# Compute MSE between frame 1s and other frames to see if there is periodicity/repetition in the source file itself!
print(f"Extracted {len(frames)} frames. Comparing MSE with frame 1s:")
f1 = frames[0][1]
for sec, f in frames:
    mse = np.mean((f1.astype(float) - f.astype(float)) ** 2)
    print(f"  Frame at {sec}s vs 1s: MSE = {mse:.2f}")

# Also compare consecutive frames (sec vs sec-1)
print("\nConsecutive frame difference (sec vs sec-1):")
for i in range(1, len(frames)):
    sec = frames[i][0]
    prev_sec = frames[i-1][0]
    diff = np.mean(np.abs(frames[i][1].astype(float) - frames[i-1][1].astype(float)))
    print(f"  Diff {sec}s vs {prev_sec}s: {diff:.2f}")


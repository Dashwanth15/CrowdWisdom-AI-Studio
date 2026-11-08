from moviepy import VideoFileClip
from pathlib import Path

p = Path("media/videos/test_fast_swarm.mp4")
clip = VideoFileClip(str(p))
print(f"File: {p.name} ({p.stat().st_size / (1024*1024):.2f} MB)")
print(f"Dimensions: {clip.size}")
print(f"FPS: {clip.fps}")
print(f"Duration: {clip.duration:.2f}s")
print(f"Has Audio: {clip.audio is not None}")
clip.close()


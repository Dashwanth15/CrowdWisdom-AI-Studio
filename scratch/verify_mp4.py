import sys
import imageio_ffmpeg
import subprocess

mp4 = r"c:\Users\dashw\OneDrive\Desktop\my projects\CrowdWisdom AI Studio\backend\media\videos\video_6aef6957547c27366bbc5f33.mp4"
ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()

cmd = [ffmpeg_bin, "-v", "error", "-i", mp4, "-f", "null", "-"]
print(f"Testing {mp4} with ffmpeg...", flush=True)
res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
print("FFMPEG Exit Code:", res.returncode, flush=True)
if res.stderr:
    print("FFMPEG STDERR:", res.stderr, flush=True)
else:
    print("Video integrity check passed with ZERO errors!", flush=True)


import imageio_ffmpeg
import subprocess

mp4 = r"c:\Users\dashw\OneDrive\Desktop\my projects\CrowdWisdom AI Studio\backend\media\videos\video_6aef6957547c27366bbc5f33.mp4"
ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()

cmd = [ffmpeg_bin, "-i", mp4]
res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
for line in res.stderr.splitlines():
    if "Duration" in line or "Stream #" in line:
        print(line.strip())

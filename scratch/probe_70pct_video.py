import imageio_ffmpeg
import subprocess

mp4 = r"c:\Users\dashw\OneDrive\Desktop\my projects\CrowdWisdom AI Studio\backend\media\videos\video_6aef776fe2a62dd28fae5564.mp4"
ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()

cmd = [ffmpeg_bin, "-v", "error", "-i", mp4, "-f", "null", "-"]
res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
print("FFMPEG Exit Code:", res.returncode, flush=True)
if res.stderr:
    print("FFMPEG STDERR:", res.stderr, flush=True)

cmd_i = [ffmpeg_bin, "-i", mp4]
res_i = subprocess.run(cmd_i, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
for line in res_i.stderr.splitlines():
    if "Duration" in line or "Stream #" in line:
        print(line.strip())


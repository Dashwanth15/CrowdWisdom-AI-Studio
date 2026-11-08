import subprocess
import imageio_ffmpeg

ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
vid = "media/videos/video_6aee329ffadd50fa6e006d2b.mp4"

for t in [5, 22, 33]:
    out = f"extracted_frame_{t}s.jpg"
    cmd = [ffmpeg_exe, "-ss", str(t), "-i", vid, "-vframes", "1", "-q:v", "2", "-y", out]
    subprocess.run(cmd, capture_output=True)
    print(f"Extracted {out}")


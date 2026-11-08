import subprocess
from pathlib import Path
import imageio_ffmpeg

backend_dir = Path(__file__).parent.resolve()
video_path = backend_dir / "media" / "videos" / "stage2_verified_advertisement.mp4"
out_jpg = backend_dir / "media" / "stage2_frames" / "test_frame.jpg"
out_jpg.parent.mkdir(parents=True, exist_ok=True)

ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
cmd = [
    ffmpeg_exe, "-y", "-ss", "00:00:05",
    "-i", str(video_path),
    "-vframes", "1",
    "-q:v", "2",
    str(out_jpg)
]
res = subprocess.run(cmd, capture_output=True, text=True)
print("FFmpeg returncode:", res.returncode)
print("FFmpeg stderr:\n", res.stderr[-500:] if res.stderr else "None")
print("Output file exists:", out_jpg.exists(), out_jpg.stat().st_size if out_jpg.exists() else 0)

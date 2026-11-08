import subprocess
import imageio_ffmpeg

ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
subprocess.run([ffmpeg, "-ss", "2.0", "-i", "media/videos/test_verify_out.mp4", "-vframes", "1", "-q:v", "2", "-y", "verify_scene1.jpg"], capture_output=True)
subprocess.run([ffmpeg, "-ss", "5.5", "-i", "media/videos/test_verify_out.mp4", "-vframes", "1", "-q:v", "2", "-y", "verify_scene2.jpg"], capture_output=True)
print("Extracted verification frames successfully.")


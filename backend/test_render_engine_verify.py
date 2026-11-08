import os
import time
from PIL import Image
from video_engine.openmontage_adapter import openmontage_adapter

# Test scenes: 1 FLUX/AI image scene, 1 dynamic chart scene
scenes = [
    {
        "scene_number": 1,
        "voiceover": "Ten analysts. A thousand tweets. Infinite noise. You're not lacking data—you're drowning in it.",
        "on_screen_text": "The Information Overload Trap",
        "camera_motion": "slow_zoom_in",
        "duration_seconds": 4,
        "media_type": "ai_image",
        "visual_asset_path": "test_scene1_flux.jpg"
    },
    {
        "scene_number": 2,
        "voiceover": "When every chart contradicts the last, hesitation costs you.",
        "on_screen_text": "Conflicting Signals Analysis Paralysis",
        "camera_motion": "pan_right",
        "duration_seconds": 4,
        "media_type": "animated_chart",
        "chart_theme": "sentiment_divergence"
    }
]

out_mp4 = "media/videos/test_verify_out.mp4"
out_thumb = "media/thumbnails/test_verify_thumb.jpg"
os.makedirs("media/videos", exist_ok=True)
os.makedirs("media/thumbnails", exist_ok=True)

t0 = time.time()
print("Starting verification render...")
res = openmontage_adapter._render_scenes_moviepy(
    scenes=scenes,
    out_path=out_mp4,
    thumb_path=out_thumb,
    width=1080,
    height=1920,
    target_duration=8,
    quality="high"
)
dt = time.time() - t0
print(f"Render completed in {dt:.2f}s! File size: {res['file_size_mb']} MB, duration: {res['duration']}s")


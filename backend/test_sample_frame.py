import os
from PIL import Image
from video_engine.openmontage_adapter import openmontage_adapter, render_dynamic_chart_canvas

# Test render a single scene frame from the current adapter
scenes = [
    {
        "scene_number": 1,
        "voiceover": "Ten analysts. A thousand tweets. Infinite noise. You're not lacking data—you're drowning in it.",
        "on_screen_text": "The Information Overload Trap",
        "camera_motion": "slow_zoom_in",
        "duration": 8,
        "media_type": "stock_video",
        "visual_asset_path": "media/stock_footage/stock_b34267646a.mp4"
    },
    {
        "scene_number": 2,
        "voiceover": "When every chart contradicts the last and every headline screams a different direction, hesitation costs you.",
        "on_screen_text": "Conflicting Signals Analysis Paralysis",
        "camera_motion": "pan_right",
        "duration": 14,
        "media_type": "animated_chart",
        "chart_theme": "sentiment_divergence"
    }
]

# Let's inspect what render_dynamic_chart_canvas produces
chart_frame = render_dynamic_chart_canvas(2.0, 14.0, 1080, 1920, "sentiment_divergence", scene_num=2)
chart_im = Image.fromarray(chart_frame)
chart_im.save("test_chart_1080.jpg", quality=95)
print("Saved test_chart_1080.jpg")

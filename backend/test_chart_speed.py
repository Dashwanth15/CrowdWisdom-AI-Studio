import time
import numpy as np
from PIL import Image
from video_engine.openmontage_adapter import render_dynamic_chart_canvas

t0 = time.time()
for f in range(60):
    t = f / 30.0
    arr = render_dynamic_chart_canvas(t, 8.0, 1080, 1920, "sentiment_divergence", 2)
dt = time.time() - t0
fps = 60.0 / dt
print(f"60 frames at 1080x1920 rendered in {dt:.2f}s ({fps:.1f} FPS)")


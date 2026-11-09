import asyncio
import sys
import os
import time

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, backend_dir)

import pytest
from database.connection import get_database, connect_to_mongo
from bson import ObjectId
from video_engine.openmontage_adapter import openmontage_adapter

@pytest.mark.asyncio
async def test_fast_render():
    await connect_to_mongo()
    db = get_database()

    # Find the approved script
    script = await db.scripts.find_one({"status": "approved"})
    if not script:
        script = await db.scripts.find_one({"scenes": {"$exists": True, "$ne": []}})
    if not script or not script.get("scenes"):
        pytest.skip("No script with scenes found in database for fast render test.")

    try:
        import imageio_ffmpeg
        ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
        if not ffmpeg_bin or not os.path.exists(ffmpeg_bin):
            pytest.skip("FFmpeg binary not available on host system.")
    except Exception as ff_err:
        pytest.skip(f"FFmpeg binary not available on host system: {ff_err}")
    
    print(f"Testing fast video rendering on script: '{script.get('title')}' with {len(script.get('scenes', []))} scenes...")

    out_file = os.path.join(backend_dir, "media", "videos", "test_fast_render.mp4")
    thumb_file = os.path.join(backend_dir, "media", "thumbnails", "test_fast_thumb.jpg")

    async def _progress(pct, msg):
        print(f"  [Progress {pct}%] {msg}")

    t0 = time.time()
    res = await openmontage_adapter.render_video(
        scenes=script["scenes"],
        output_file_path=out_file,
        thumbnail_file_path=thumb_file,
        aspect_ratio="9:16",
        target_duration=45,
        quality="high",
        progress_callback=_progress
    )
    t1 = time.time()

    print(f"\n✓ Video rendering completed in {t1 - t0:.1f} seconds!")
    print(f"  Output path: {res['output_path']}")
    print(f"  Duration: {res['duration']}s")
    print(f"  File size: {res['file_size_mb']} MB")
    print(f"  Resolution: {res['resolution']}")

if __name__ == "__main__":
    asyncio.run(test_fast_render())

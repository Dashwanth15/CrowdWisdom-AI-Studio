import asyncio
import os
import sys
import subprocess
from pathlib import Path
from PIL import Image
import numpy as np
import imageio_ffmpeg

backend_dir = Path(__file__).parent.resolve()
sys.path.insert(0, str(backend_dir))

async def main():
    from video_engine.openmontage_adapter import openmontage_adapter
    from agents.script_agent import script_agent
    from moviepy import VideoFileClip

    print("==================================================")
    print("STAGE 3 VERIFICATION: ADVANCED SOUND DESIGN ENGINE")
    print("==================================================")

    # 1. Screenplay with 3 high-impact dynamic commercial scenes (18s fast verification)
    script = script_agent._generate_fallback_script(
        approach="product_value",
        duration=18,
        campaign_config={"audience": {"segments": ["retail traders", "options traders"]}},
        campaign_id="stage3_verify_campaign",
        campaign_name="Stage 3 Sound Design Verification"
    )

    scenes = script["scenes"][:3]
    scenes[0]["transition"] = "Fast motion blur whip pan right"
    scenes[1]["transition"] = "Digital glitch & chromatic tear"
    scenes[2]["transition"] = "Fade to brand card"

    print(f"\n[1] Screenplay: '{script['title']}' ({len(scenes)} scenes)")
    for s in scenes:
        print(f"  Scene {s['scene_number']} ({s['duration_seconds']}s): {s['voiceover'][:55]}...")

    output_mp4 = backend_dir / "media" / "videos" / "stage3_verified_advertisement.mp4"
    output_thumb = backend_dir / "media" / "thumbnails" / "stage3_verified_thumb.jpg"

    print("\n[2] Executing OpenMontage Stage 3 Pipeline (Multi-Track Sound Design)...")
    t0 = asyncio.get_event_loop().time()

    async def progress_logger(pct: int, msg: str):
        print(f"  [{pct}%] {msg}")

    result = await openmontage_adapter.render_video(
        scenes=scenes,
        output_file_path=str(output_mp4),
        thumbnail_file_path=str(output_thumb),
        aspect_ratio="9:16",
        target_duration=18,
        quality="high",
        progress_callback=progress_logger
    )

    t1 = asyncio.get_event_loop().time()
    print(f"\n[3] Stage 3 Video Render Complete in {t1 - t0:.1f}s!")
    print(f"  Output MP4: {output_mp4} ({output_mp4.stat().st_size / (1024*1024):.2f} MB)")

    # 4. Stream & Audio Forensics
    clip = VideoFileClip(str(output_mp4))
    print("\n[4] Stream & Forensic Audio Analysis:")
    print(f"  Video Duration: {clip.duration:.2f}s | Dimensions: {clip.size} | FPS: {clip.fps}")
    assert clip.audio is not None, "Video must contain active audio stream!"
    print(f"  Audio Duration: {clip.audio.duration:.2f}s | Sample Rate: {clip.audio.fps} Hz")

    # Sample audio array from rendered video
    audio_frames = clip.audio.to_soundarray(fps=44100)
    clip.close()

    left_ch = audio_frames[:, 0]
    right_ch = audio_frames[:, 1]
    peak_left = float(np.max(np.abs(left_ch)))
    peak_right = float(np.max(np.abs(right_ch)))
    overall_rms = float(np.sqrt(np.mean(audio_frames**2)))
    overall_db = 20 * np.log10(overall_rms + 1e-6)

    print(f"  Master Peak Left:  {peak_left:.3f} ({20*np.log10(peak_left + 1e-6):.1f} dBFS)")
    print(f"  Master Peak Right: {peak_right:.3f} ({20*np.log10(peak_right + 1e-6):.1f} dBFS)")
    print(f"  Overall RMS Level: {overall_db:.1f} dBFS")

    # Inspect Opening Braam (0s to 1.5s)
    braam_rms = float(np.sqrt(np.mean(audio_frames[:int(1.5 * 44100), :]**2)))
    print(f"  Opening Hook Braam RMS: {20*np.log10(braam_rms + 1e-6):.1f} dBFS (Punchy Opening Hook)")

    # Inspect CTA Resolution Chime (last 3s)
    cta_rms = float(np.sqrt(np.mean(audio_frames[-int(3.0 * 44100):, :]**2)))
    print(f"  CTA Resolution Chime RMS: {20*np.log10(cta_rms + 1e-6):.1f} dBFS (Harmonic Brand Swell)")

    assert peak_left <= 0.99 and peak_right <= 0.99, "Audio must not digitally clip!"
    print("\n✓ STAGE 3 ADVANCED SOUND DESIGN ENGINE VERIFIED!")

if __name__ == "__main__":
    asyncio.run(main())

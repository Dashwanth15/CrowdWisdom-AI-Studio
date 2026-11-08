import time
import numpy as np
from pathlib import Path
import sys

backend_dir = Path(__file__).parent.resolve()
sys.path.insert(0, str(backend_dir))

from services.sound_design_service import sound_design_service

print("==================================================")
print("TESTING STAGE 3: ADVANCED SOUND DESIGN SERVICE")
print("==================================================")

t0 = time.time()
speech_intervals = [(1.5, 9.8), (11.5, 20.8), (23.2, 32.5), (35.0, 41.5)]
transition_timestamps = [10.5, 22.5, 34.5]
total_dur = 45.0

stereo = sound_design_service.generate_commercial_soundtrack(
    total_duration=total_dur,
    speech_intervals=speech_intervals,
    transition_timestamps=transition_timestamps,
    cta_timestamp=41.8,
    bpm=120.0
)
t1 = time.time()

print(f"Generated 45.0s soundtrack in {t1 - t0:.3f}s!")
print(f"Shape: {stereo.shape} | Dtype: {stereo.dtype}")
print(f"Left Peak: {np.max(np.abs(stereo[:, 0])):.3f} | Right Peak: {np.max(np.abs(stereo[:, 1])):.3f}")
print(f"RMS Energy (dBFS): {20 * np.log10(np.sqrt(np.mean(stereo**2))):.1f} dBFS")

# Verify sidechain ducking in action
speech_sample_idx = int(5.0 * 44100)
pause_sample_idx = int(10.6 * 44100) # During transition
speech_rms = np.sqrt(np.mean(stereo[speech_sample_idx : speech_sample_idx + 4410, :]**2))
pause_rms = np.sqrt(np.mean(stereo[pause_sample_idx : pause_sample_idx + 4410, :]**2))

print(f"Speech Interval RMS: {20 * np.log10(speech_rms + 1e-6):.1f} dBFS")
print(f"Transition Interval RMS (Music Swell + Whoosh): {20 * np.log10(pause_rms + 1e-6):.1f} dBFS")
assert pause_rms > speech_rms, "Transition pause should swell louder than speech interval!"

print("\n✓ SOUND DESIGN SERVICE VALIDATED SUCCESSFULLY!")

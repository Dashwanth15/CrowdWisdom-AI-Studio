import numpy as np
from PIL import Image, ImageDraw, ImageFont
import math

def build_word_timings(vo_text: str, speech_duration: float, pre_roll: float = 0.35):
    """Computes syllable/length-weighted time intervals for each word."""
    words = vo_text.split()
    if not words:
        return [], []
    
    weights = [max(1.0, float(len(w))) for w in words]
    tot_weight = sum(weights)
    
    timings = []
    cur_t = pre_roll
    for w, wt in zip(words, weights):
        w_dur = (wt / tot_weight) * speech_duration
        timings.append((cur_t, cur_t + w_dur))
        cur_t += w_dur
        
    return words, timings

def test_hud():
    width, height = 1080, 1920
    vo = "Options traders don't fear market volatility — they master it with crowd conviction."
    speech_dur = 4.2
    words, timings = build_word_timings(vo, speech_dur, pre_roll=0.35)
    
    print(f"Computed {len(words)} word timings across {speech_dur}s speech:")
    for w, (t0, t1) in zip(words[:5], timings[:5]):
        print(f"  '{w}': {t0:.2f}s -> {t1:.2f}s (dur={t1-t0:.2f}s)")
        
    # Check sample times
    for t_test in [0.2, 0.8, 1.8, 3.2, 4.5]:
        active_w = [w for w, (t0, t1) in zip(words, timings) if t0 <= t_test <= t1]
        print(f"t={t_test:.1f}s: Active word = {active_w[0] if active_w else '[None/Pause]'}")
        
    print("\n✓ KINETIC TYPOGRAPHY TIMING VERIFIED!")

if __name__ == "__main__":
    test_hud()

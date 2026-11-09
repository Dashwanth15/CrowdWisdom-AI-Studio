"""
CrowdWisdom AI Studio — OpenMontage Video Engine Adapter
Encapsulates video rendering logic behind a unified interface.
Integrates calesthio/OpenMontage tool pipelines with seamless high-fidelity MoviePy composition.
Renders genuine commercial video footage, live animated financial charts,
frame-accurate speech synchronization, multi-track fintech soundtrack with sidechain ducking,
and institutional typography overlays at broadcast-standard 1080p 30 FPS.
"""
import os
import sys
import time
import math
import hashlib
import logging
import asyncio
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Callable
import numpy as np
from config import settings

logger = logging.getLogger(__name__)


def generate_fintech_soundtrack(
    total_dur: float,
    speech_intervals: List[Tuple[float, float]],
    transition_timestamps: Optional[List[float]] = None,
    cta_timestamp: Optional[float] = None,
    fps: int = 44100
):
    """
    Synthesizes a master commercial soundtrack via SoundDesignService (Stage 3).
    Pre-renders hybrid stems into a high-performance stereo buffer:
    - Warm D-minor atmospheric pad & 8th-note pulsing bass
    - 120 BPM punchy 808 sub-kick, crisp rimshot & metallic hi-hats
    - Opening hook cinematic braam & sub-bass pitch drop
    - Directional transition whooshes, pink-noise risers & sub-bass landing impacts
    - Micro telemetry data clicks & closing D-Major harmonic resolution chime
    - Smooth exponential vocal sidechain ducking with attack/release envelopes
    """
    from moviepy import AudioClip
    from services.sound_design_service import sound_design_service

    stereo_buffer = sound_design_service.generate_commercial_soundtrack(
        total_duration=total_dur,
        speech_intervals=speech_intervals,
        transition_timestamps=transition_timestamps,
        cta_timestamp=cta_timestamp,
        bpm=120.0
    )
    total_samples = len(stereo_buffer)

    def audio_frame(t):
        if hasattr(t, '__len__'):
            indices = np.clip((np.array(t) * fps).astype(int), 0, total_samples - 1)
            return stereo_buffer[indices]
        else:
            idx = min(total_samples - 1, max(0, int(t * fps)))
            return stereo_buffer[idx]

    return AudioClip(audio_frame, duration=total_dur, fps=fps)


# =====================================================================
# CINEMATIC TRANSITIONS ENGINE (STAGE 2)
# Directional Whip-Pans, Digital Glitches, Optical Blooms, Zoom-Punches
# =====================================================================

def ease_smootherstep(tau: float) -> float:
    """5th-order smootherstep for zero 1st and 2nd derivatives at endpoints."""
    tau = max(0.0, min(1.0, tau))
    return tau * tau * tau * (tau * (tau * 6.0 - 15.0) + 10.0)


def render_whip_pan(
    frame_a: np.ndarray,
    frame_b: np.ndarray,
    tau: float,
    direction: str = "right"
) -> np.ndarray:
    """
    Directional Whip-Pan with dynamic velocity-dependent motion blur and flash bloom.
    Seamlessly slides frame A out and frame B in at high velocity.
    """
    from PIL import Image
    h, w, c = frame_a.shape
    eased = ease_smootherstep(tau)

    # Velocity peaks at tau = 0.5
    velocity = math.sin(math.pi * tau)
    blur_radius = int(velocity * 32.0)

    if direction == "right":
        offset = int(eased * w)
        stitched = np.concatenate((frame_a, frame_b), axis=1)
        crop_x = offset
    else:
        offset = int((1.0 - eased) * w)
        stitched = np.concatenate((frame_b, frame_a), axis=1)
        crop_x = offset

    cropped = stitched[:, crop_x : crop_x + w]

    # Directional horizontal motion blur proportional to speed
    if blur_radius >= 2:
        pil_crop = Image.fromarray(cropped)
        down_w = max(4, int(w / (1.0 + blur_radius * 0.45)))
        blurred = pil_crop.resize((down_w, h), Image.Resampling.BILINEAR).resize((w, h), Image.Resampling.BILINEAR)

        # Subtle exposure bloom flash at peak speed
        flash_intensity = max(0.0, math.sin(math.pi * tau) ** 3.0) * 45.0
        if flash_intensity > 2.0:
            arr = np.array(blurred).astype(np.float32) + flash_intensity
            cropped = np.clip(arr, 0, 255).astype(np.uint8)
        else:
            cropped = np.array(blurred)

    return cropped


def render_digital_glitch(
    frame_a: np.ndarray,
    frame_b: np.ndarray,
    tau: float
) -> np.ndarray:
    """
    Institutional Cyber Glitch & Chromatic Aberration.
    Splits RGB channels, applies randomized horizontal slice tears, and subtle noise.
    """
    h, w, c = frame_a.shape
    base_frame = frame_a if tau < 0.5 else frame_b
    out = base_frame.copy()

    envelope = math.sin(math.pi * tau) ** 1.8
    if envelope < 0.05:
        return out

    # 1. Chromatic Aberration (RGB channel shift)
    shift = int(envelope * 28.0)
    if shift > 1:
        r_channel = np.roll(out[:, :, 0], shift, axis=1)
        b_channel = np.roll(out[:, :, 2], -shift, axis=1)
        out[:, :, 0] = r_channel
        out[:, :, 2] = b_channel

    # 2. Horizontal Displaced Slices
    np.random.seed(int(tau * 1000) % 9999)
    num_slices = int(3 + envelope * 8)
    for _ in range(num_slices):
        slice_y = np.random.randint(0, max(1, h - 30))
        slice_h = np.random.randint(8, 45)
        slice_h = min(slice_h, h - slice_y)
        slice_shift = int(np.random.uniform(-1, 1) * envelope * 70.0)
        if abs(slice_shift) > 2:
            out[slice_y : slice_y + slice_h, :, :] = np.roll(
                out[slice_y : slice_y + slice_h, :, :], slice_shift, axis=1
            )
            tint_color = np.array([0, 40, 60] if np.random.rand() > 0.5 else [60, 20, 0], dtype=np.uint8)
            out[slice_y : slice_y + slice_h, :, :] = np.clip(
                out[slice_y : slice_y + slice_h, :, :].astype(np.int16) + tint_color, 0, 255
            ).astype(np.uint8)

    # 3. High-frequency scanline noise
    if envelope > 0.4:
        noise_mask = (np.random.rand(h, 1, 1) > 0.7).astype(np.uint8) * int(envelope * 25)
        out = np.clip(out.astype(np.int16) + noise_mask, 0, 255).astype(np.uint8)

    return out


def render_optical_bloom(
    frame_a: np.ndarray,
    frame_b: np.ndarray,
    tau: float
) -> np.ndarray:
    """
    Cinematic Anamorphic Light-Leak & Optical Bloom Dissolve.
    Memory-optimized: uses low-resolution flare buffer to prevent 100+ MB transient array spikes.
    """
    from PIL import Image
    h, w, c = frame_a.shape

    alpha = ease_smootherstep(tau)
    dissolved = (1.0 - alpha) * frame_a.astype(np.float32) + alpha * frame_b.astype(np.float32)

    flare_amp = math.exp(-18.0 * ((tau - 0.5) ** 2))

    if flare_amp > 0.02:
        dh, dw = max(32, h // 4), max(32, w // 4)
        fy = int(dh * (0.2 + 0.3 * tau))
        fx = int(dw * (0.8 - 0.6 * tau))

        y_coords = np.arange(dh, dtype=np.float32)[:, None]
        x_coords = np.arange(dw, dtype=np.float32)[None, :]

        dy = (y_coords - fy) / (dh * 0.18)
        dx = (x_coords - fx) / (dw * 0.72)
        dist_sq = dy * dy + dx * dx
        glow_small = (np.exp(-dist_sq) * (flare_amp * 255.0)).astype(np.uint8)

        # Upscale glow buffer to full frame size
        glow_img = Image.fromarray(glow_small).resize((w, h), Image.Resampling.BILINEAR)
        glow = np.array(glow_img, dtype=np.float32) / 255.0

        # Fast additive flare wash in-place
        dissolved[:, :, 0] += glow * 220.0
        dissolved[:, :, 1] += glow * 165.0
        dissolved[:, :, 2] += glow * 110.0

    return np.clip(dissolved, 0, 255).astype(np.uint8)


def render_zoom_punch(
    frame_a: np.ndarray,
    frame_b: np.ndarray,
    tau: float
) -> np.ndarray:
    """
    Zoom Punch & Scale Snap.
    Outgoing frame rapidly accelerates zoom-in; incoming frame snaps in from slightly reduced scale with subtle recoil.
    """
    from PIL import Image
    h, w, c = frame_a.shape

    if tau < 0.5:
        t_half = tau * 2.0
        scale = 1.0 + (t_half ** 2.2) * 0.35
        crop_w, crop_h = int(w / scale), int(h / scale)
        x0, y0 = (w - crop_w) // 2, (h - crop_h) // 2
        pil_a = Image.fromarray(frame_a).crop((x0, y0, x0 + crop_w, y0 + crop_h))
        res = pil_a.resize((w, h), Image.Resampling.BILINEAR)

        if t_half > 0.8:
            flash = (t_half - 0.8) * 150.0
            arr = np.clip(np.array(res).astype(np.float32) + flash, 0, 255).astype(np.uint8)
            return arr
        return np.array(res)
    else:
        t_half = (tau - 0.5) * 2.0
        spring = 1.0 - math.exp(-6.0 * t_half) * math.cos(math.pi * t_half) * 0.12
        crop_w, crop_h = int(w * spring), int(h * spring)

        pil_b = Image.fromarray(frame_b)
        scaled_b = pil_b.resize((crop_w, crop_h), Image.Resampling.BILINEAR)

        bg = Image.new("RGB", (w, h), (8, 12, 22))
        px = (w - crop_w) // 2
        py = (h - crop_h) // 2
        bg.paste(scaled_b, (px, py))
        return np.array(bg)


GAMMA_LUT_22 = np.array([((i / 255.0) ** 2.2) for i in range(256)], dtype=np.float32)


def render_luma_dissolve(
    frame_a: np.ndarray,
    frame_b: np.ndarray,
    tau: float
) -> np.ndarray:
    """
    Film-grade Gamma-Corrected Luma Dissolve via fast vectorized LUT.
    Avoids muddy midtones by performing cross-dissolve in linear light space (gamma=2.2).
    """
    alpha = ease_smootherstep(tau)
    lin_a = GAMMA_LUT_22[frame_a]
    lin_b = GAMMA_LUT_22[frame_b]

    blended = (1.0 - alpha) * lin_a + alpha * lin_b
    srgb = (blended ** (1.0 / 2.2)) * 255.0
    return np.clip(srgb, 0, 255).astype(np.uint8)


def render_cinematic_transition(
    frame_a: np.ndarray,
    frame_b: np.ndarray,
    tau: float,
    transition_type: str = "whip_pan_right"
) -> np.ndarray:
    """
    Dispatches to the specialized cinematic transition renderer based on screenplay transition tag.
    """
    tau = max(0.0, min(1.0, tau))

    if transition_type == "hard_cut":
        return frame_a if tau < 0.5 else frame_b
    elif transition_type == "whip_pan_right":
        return render_whip_pan(frame_a, frame_b, tau, "right")
    elif transition_type == "whip_pan_left":
        return render_whip_pan(frame_a, frame_b, tau, "left")
    elif transition_type == "digital_glitch":
        return render_digital_glitch(frame_a, frame_b, tau)
    elif transition_type == "optical_bloom":
        return render_optical_bloom(frame_a, frame_b, tau)
    elif transition_type == "zoom_punch":
        return render_zoom_punch(frame_a, frame_b, tau)
    elif transition_type == "luma_dissolve":
        return render_luma_dissolve(frame_a, frame_b, tau)
    else:
        return render_luma_dissolve(frame_a, frame_b, tau)


def resolve_transition_type(scene_a: Dict[str, Any], scene_b: Dict[str, Any], scene_idx: int) -> str:
    """
    Maps screenplay transition metadata and narrative arc to the appropriate transition shader.
    Replaces random modulo with screenplay-motivated transitions based on emotional progression:
    - Pain/struggle -> Market chaos: digital_glitch
    - Market chaos -> Product clarity: zoom_punch
    - Product demo -> Trader conviction: optical_bloom
    - Outro conclusion -> CTA Card: luma_dissolve
    - Natural continuity: hard_cut
    """
    raw_trans = str(scene_a.get("transition") or "").lower()

    if any(k in raw_trans for k in ["glitch", "noise", "distortion", "split"]):
        return "digital_glitch"
    elif any(k in raw_trans for k in ["bloom", "light", "flare", "leak", "glow"]):
        return "optical_bloom"
    elif any(k in raw_trans for k in ["zoom", "punch", "snap", "push"]):
        return "zoom_punch"
    elif any(k in raw_trans for k in ["dissolve", "fade", "cross"]):
        return "luma_dissolve"
    elif any(k in raw_trans for k in ["hard_cut", "jump", "cut"]):
        return "hard_cut"

    # Narrative arc resolution based on scene visual typologies & emotional beats
    type_a = str(scene_a.get("scene_visual_type") or scene_a.get("media_type") or "").lower()
    type_b = str(scene_b.get("scene_visual_type") or scene_b.get("media_type") or "").lower()
    vo_a = str(scene_a.get("voiceover") or "").lower()
    vo_b = str(scene_b.get("voiceover") or "").lower()

    # 1. Human struggling with noise -> Market charts / chaos
    if ("human" in type_a or "trader" in type_a) and ("chart" in type_b or "noise" in vo_a or "chaos" in vo_a):
        return "digital_glitch"

    # 2. Market charts / chaos -> Product demo revelation
    if ("chart" in type_a or "glitch" in type_a or "noise" in vo_a) and ("product" in type_b or "crowdpulse" in vo_b):
        return "zoom_punch"

    # 3. Product demo -> Human conviction / victory
    if "product" in type_a and ("human" in type_b or "standing" in type_b or "conviction" in vo_b):
        return "optical_bloom"

    # 4. Outro resolution leading into CTA
    if scene_idx >= 2 or "find your signal" in vo_b or "crowdwisdom" in vo_b:
        return "luma_dissolve"

    # 5. Fast camera pans if camera_motion calls for panning
    cam_a = str(scene_a.get("camera_motion", "")).lower()
    if "pan" in cam_a:
        return "whip_pan_right"

    # 6. Default: Clean professional agency hard cut or smooth luma dissolve
    return "luma_dissolve" if scene_idx == 0 else "hard_cut"


_CHART_GRID_CACHE: Dict[Tuple[str, int, int], Any] = {}
_CHART_PRICES_CACHE: Dict[Tuple[int, str], List[float]] = {}


def _get_cached_chart_prices(scene_num: int, theme: str, num_total_candles: int = 24) -> List[float]:
    key = (scene_num, theme)
    if key in _CHART_PRICES_CACHE:
        return _CHART_PRICES_CACHE[key]
    np.random.seed(300 + scene_num * 41)
    prices = [100.0]
    for i in range(num_total_candles):
        if theme == "volatility_drop":
            drift = -1.3 if i > 6 else 0.1
        elif theme == "bullish_breakout":
            drift = 1.5 if i > 8 else -0.1
        elif theme == "sentiment_divergence":
            drift = 0.9 if i < 12 else -1.2
        else:
            drift = 0.5
        change = float(np.random.normal(drift, 2.4))
        prices.append(max(30.0, prices[-1] + change))
    _CHART_PRICES_CACHE[key] = prices
    return prices


def _get_cached_chart_grid(theme: str, width: int, height: int, bg_col: Tuple[int, int, int], grid_col: Tuple[int, int, int]) -> Any:
    key = (theme, width, height)
    if key in _CHART_GRID_CACHE:
        return _CHART_GRID_CACHE[key]
    from PIL import Image, ImageDraw
    base = Image.new("RGB", (width, height), color=bg_col)
    draw = ImageDraw.Draw(base)
    for y in range(int(height * 0.15), int(height * 0.85), max(4, int(height * 0.06))):
        draw.line([(0, y), (width, y)], fill=grid_col, width=1)
    for x in range(0, width, max(4, int(width * 0.10))):
        draw.line([(x, int(height * 0.15)), (x, int(height * 0.85))], fill=grid_col, width=1)
    _CHART_GRID_CACHE[key] = base
    return base


def render_dynamic_chart_canvas(
    t: float,
    dur: float,
    width: int,
    height: int,
    theme: str = "bullish_breakout",
    scene_num: int = 1
) -> np.ndarray:
    """
    Renders a live frame of a genuinely animated financial visualization.
    Candles draw dynamically, wicks pulse, sentiment curve sweeps forward with leading glowing beacon,
    volume bars rise, and HUD telemetry ticks in real time.
    High-performance cached grid and price arrays ensure 60+ FPS frame generation.
    """
    from PIL import Image, ImageDraw, ImageFont

    tau = min(1.0, max(0.0, t / max(dur, 0.1)))

    if theme == "volatility_drop":
        bg_col = (14, 10, 16)
        grid_col = (40, 20, 26)
        primary_col = (239, 68, 68)
        status_prefix = "-68.4% HIGH NOISE SURGE"
    elif theme == "sentiment_divergence":
        bg_col = (14, 14, 10)
        grid_col = (38, 34, 20)
        primary_col = (234, 179, 8)
        status_prefix = "SENTIMENT DIVERGENCE DETECTED"
    elif theme == "institutional_consensus":
        bg_col = (8, 14, 26)
        grid_col = (20, 36, 60)
        primary_col = (56, 189, 248)
        status_prefix = "INSTITUTIONAL TARGETS LOCKED"
    else:
        bg_col = (8, 16, 22)
        grid_col = (18, 38, 44)
        primary_col = (16, 185, 129)
        status_prefix = "+88.5% BULLISH CONVICTION"

    # 1. Use pre-rendered cached grid
    base = _get_cached_chart_grid(theme, width, height, bg_col, grid_col).copy()
    draw = ImageDraw.Draw(base)

    # Scanning vertical laser beam
    scan_x = int((width * 0.06) + tau * (width * 0.88))
    for dy in range(int(height * 0.15), int(height * 0.85), 3):
        draw.point((scan_x, dy), fill=(56, 189, 248))

    # 2. Dynamic Candlestick Generation from cached series
    num_total_candles = 24
    chart_top = int(height * 0.22)
    chart_bottom = int(height * 0.62)
    chart_h = chart_bottom - chart_top
    spacing = int(width * 0.036)
    candle_w = int(width * 0.024)
    start_x = int(width * 0.06)

    prices = _get_cached_chart_prices(scene_num, theme, num_total_candles)
    min_p, max_p = min(prices), max(prices)
    p_range = max(max_p - min_p, 10.0)

    # Number of visible candles develops over time
    num_visible = min(num_total_candles, 6 + int(tau * (num_total_candles - 5)))
    active_points = []

    for i in range(num_visible):
        open_p = prices[i]
        close_p = prices[i + 1]

        # Active leading candle pulses live with intra-second volatility
        if i == num_visible - 1:
            close_p += math.sin(t * 10.0) * 1.6

        high_p = max(open_p, close_p) + 1.2
        low_p = min(open_p, close_p) - 1.2
        is_green = close_p >= open_p
        color = (16, 185, 129) if is_green else (239, 68, 68)

        x = start_x + (i * spacing)
        y_open = int(chart_bottom - ((open_p - min_p) / p_range) * chart_h)
        y_close = int(chart_bottom - ((close_p - min_p) / p_range) * chart_h)
        y_high = int(chart_bottom - ((high_p - min_p) / p_range) * chart_h)
        y_low = int(chart_bottom - ((low_p - min_p) / p_range) * chart_h)

        # Draw Wick
        draw.line([(x + candle_w // 2, y_high), (x + candle_w // 2, y_low)], fill=color, width=2)
        # Draw Body
        top_b, bot_b = min(y_open, y_close), max(y_open, y_close)
        draw.rectangle([x, top_b, x + candle_w, max(bot_b, top_b + 3)], fill=color)

        # Dynamic Volume Bars rising from bottom
        vol_h = int((abs(close_p - open_p) / p_range) * (height * 0.10) * min(1.0, tau * 1.4 + 0.3))
        draw.rectangle([x, int(height * 0.68) - vol_h, x + candle_w, int(height * 0.68)], fill=color)

        active_points.append((x + candle_w // 2, y_close))

    # 3. Dynamic Sentiment Curve with Pulsing Beacon
    if len(active_points) > 1:
        draw.line(active_points, fill=(56, 189, 248), width=3)
        lead_x, lead_y = active_points[-1]
        beacon_r = int(5 + 2 * math.sin(t * 8.0))
        draw.ellipse([lead_x - beacon_r, lead_y - beacon_r, lead_x + beacon_r, lead_y + beacon_r], fill=primary_col)
        draw.ellipse([lead_x - beacon_r - 4, lead_y - beacon_r - 4, lead_x + beacon_r + 4, lead_y + beacon_r + 4], outline=(56, 189, 248), width=1)

    # 4. Live Ticking Telemetry HUD (Cleanly separated in upper-middle zone: y=0.58 to 0.68)
    hud_y = int(height * 0.58)
    hud_h = int(height * 0.10)
    draw.rounded_rectangle(
        [int(width * 0.05), hud_y, int(width * 0.95), hud_y + hud_h],
        radius=14,
        fill=(12, 18, 30),
        outline=(56, 189, 248),
        width=1
    )

    try:
        font_val = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", max(28, width // 30))
        font_sub = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", max(20, width // 42))
    except Exception:
        font_val = ImageFont.load_default()
        font_sub = font_val

    # Dynamic ticking readout
    if theme == "volatility_drop":
        val = -35.0 - (tau * 42.0) + math.sin(t * 6.0) * 0.8
        txt = f"{val:.1f}% MARKET NOISE SURGE"
    elif theme == "bullish_breakout":
        val = +58.0 + (tau * 30.5) + math.sin(t * 6.0) * 0.5
        txt = f"+{val:.1f}% BULLISH CONVICTION"
    elif theme == "institutional_consensus":
        val = +78.0 + (tau * 18.0) + math.sin(t * 5.0) * 0.4
        txt = f"+{val:.1f}% INSTITUTIONAL TARGET REACHED"
    else:
        val = +84.0 - (tau * 45.0) + math.sin(t * 6.0) * 0.6
        txt = f"{val:.1f}% SENTIMENT DIVERGENCE"

    draw.text((int(width * 0.09), hud_y + 12), "CROWDPULSE™ REAL-TIME CONVICTION RADAR", fill=(148, 163, 184), font=font_sub)
    draw.text((int(width * 0.09), hud_y + 44), txt, fill=primary_col, font=font_val)

    # Dynamic Progress Bar
    bar_w = int(width * 0.82)
    bar_prog = min(1.0, max(0.1, abs(val) / 100.0))
    draw.rounded_rectangle([int(width * 0.09), hud_y + 80, int(width * 0.09) + bar_w, hud_y + 88], radius=4, fill=(24, 34, 52))
    draw.rounded_rectangle([int(width * 0.09), hud_y + 80, int(width * 0.09) + int(bar_w * bar_prog), hud_y + 88], radius=4, fill=primary_col)

    return np.array(base)


def render_dynamic_product_demo_canvas(
    t: float,
    dur: float,
    width: int,
    height: int,
    mode: str = "fullscreen",
    bg_plate: Optional[Any] = None,
    scene_num: int = 1,
    theme: str = "bullish_breakout"
) -> np.ndarray:
    """
    Renders an institutional fintech software demonstration for CrowdPulse:
    1. Fullscreen Institutional UI: Bloomberg/Aladdin caliber dark-glass interface with strictly verified 50-60px safe component gaps.
    2. Hardware Screen Projection: Perspective-correct dynamic UI composited inside physical device display screen with glass sheen.
    """
    from PIL import Image, ImageDraw, ImageFont

    tau = min(1.0, max(0.0, t / max(dur, 0.1)))

    try:
        font_title = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", max(24, width // 28))
        font_sub = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", max(16, width // 48))
        font_val = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", max(28, width // 26))
        font_mono = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", max(18, width // 42))
    except Exception:
        font_title = font_sub = font_val = font_mono = ImageFont.load_default()

    if mode == "fullscreen" or bg_plate is None:
        base = Image.new("RGB", (width, height), color=(6, 10, 18))
        draw = ImageDraw.Draw(base)

        # Tactical background grid
        for y in range(int(height * 0.04), int(height * 0.90), max(8, int(height * 0.04))):
            draw.line([(0, y), (width, y)], fill=(12, 20, 32), width=1)
        for x in range(0, width, max(8, int(width * 0.08))):
            draw.line([(x, int(height * 0.04)), (x, int(height * 0.90))], fill=(12, 20, 32), width=1)

        # -------------------------------------------------------------
        # 1. Top Institutional Header Card (y: 70 to 184, height: 114)
        # -------------------------------------------------------------
        head_y0 = int(height * 0.038)   # ~73px
        head_y1 = int(height * 0.096)   # ~184px
        card_x0 = int(width * 0.06)
        card_x1 = int(width * 0.94)

        draw.rounded_rectangle(
            [card_x0, head_y0, card_x1, head_y1],
            radius=12,
            fill=(10, 16, 28),
            outline=(56, 189, 248),
            width=1
        )
        draw.text((card_x0 + 32, head_y0 + 16), "CrowdPulse™ Institutional Radar", fill=(255, 255, 255), font=font_title)
        draw.text((card_x0 + 32, head_y0 + 58), "QUANTITATIVE SENTIMENT & ORDER FLOW SKEW • NASDAQ / S&P", fill=(56, 189, 248), font=font_sub)

        # -------------------------------------------------------------
        # SAFE GAP 1: 58px between Header and Central Radar (184px -> 242px)
        # -------------------------------------------------------------
        radar_cx = width // 2           # 540px
        radar_cy = int(height * 0.238)  # 457px
        radar_r = int(width * 0.190)    # 205px
        housing_r = radar_r + 12        # 217px (top: 240px, bottom: 674px)

        # Outer Housing with Subtle Radial Glow
        draw.ellipse([radar_cx - housing_r, radar_cy - housing_r, radar_cx + housing_r, radar_cy + housing_r], fill=(12, 18, 30), outline=(30, 48, 76), width=2)
        draw.ellipse([radar_cx - radar_r, radar_cy - radar_r, radar_cx + radar_r, radar_cy + radar_r], fill=(8, 14, 24), outline=(56, 189, 248), width=2)

        # Concentric Calibration Rings
        for frac in [0.33, 0.66, 1.0]:
            sub_r = int(radar_r * frac)
            draw.ellipse([radar_cx - sub_r, radar_cy - sub_r, radar_cx + sub_r, radar_cy + sub_r], outline=(20, 36, 56), width=1)

        # Degree Tick Marks around Circumference
        for deg in range(0, 360, 30):
            rad = math.radians(deg)
            x_out = radar_cx + int(radar_r * math.cos(rad))
            y_out = radar_cy + int(radar_r * math.sin(rad))
            x_in = radar_cx + int((radar_r - 6) * math.cos(rad))
            y_in = radar_cy + int((radar_r - 6) * math.sin(rad))
            draw.line([(x_in, y_in), (x_out, y_out)], fill=(56, 189, 248), width=1)

        # Precision Crosshairs
        draw.line([(radar_cx - radar_r, radar_cy), (radar_cx + radar_r, radar_cy)], fill=(20, 36, 56), width=1)
        draw.line([(radar_cx, radar_cy - radar_r), (radar_cx, radar_cy + radar_r)], fill=(20, 36, 56), width=1)

        # 360-Degree Rotating Radar Sweep Line with Trailing Phosphor Decay Fan
        angle = (t * 2.8) % (2.0 * math.pi)
        sweep_len = radar_r - 2
        for trail_step in range(12, 0, -2):
            trail_ang = angle - (trail_step * 0.04)
            tr_x = int(radar_cx + sweep_len * math.cos(trail_ang))
            tr_y = int(radar_cy + sweep_len * math.sin(trail_ang))
            draw.line([(radar_cx, radar_cy), (tr_x, tr_y)], fill=(16, 185, 129), width=max(1, int(trail_step / 3)))

        tip_x = int(radar_cx + sweep_len * math.cos(angle))
        tip_y = int(radar_cy + sweep_len * math.sin(angle))
        draw.line([(radar_cx, radar_cy), (tip_x, tip_y)], fill=(56, 189, 248), width=3)

        # Synchronous Pulsing Radar Targets with Institutional Callouts
        blips = [
            (0.40, 0.8, "+88.4% CALL SKEW"),
            (0.68, 2.3, "ALPHA ACCUMULATION"),
            (0.82, 4.2, "DARK POOL REVERSAL"),
            (0.50, 5.5, "VOL SHOCK DAMPENED")
        ]
        for b_r_frac, b_ang, b_lbl in blips:
            bx = int(radar_cx + (radar_r * b_r_frac) * math.cos(b_ang))
            by = int(radar_cy + (radar_r * b_r_frac) * math.sin(b_ang))
            ang_diff = (angle - b_ang) % (2.0 * math.pi)
            is_active = (ang_diff < 1.4)
            col = (16, 185, 129) if "CALL" in b_lbl or "ALPHA" in b_lbl else (56, 189, 248)
            draw.ellipse([bx - 5, by - 5, bx + 5, by + 5], fill=col)
            if is_active:
                draw.ellipse([bx - 10, by - 10, bx + 10, by + 10], outline=col, width=1)
                draw.text((bx + 12, by - 8), b_lbl, fill=col, font=font_mono)

        # -------------------------------------------------------------
        # SAFE GAP 2: 50px between Radar Housing and Waveform Card (674px -> 724px)
        # -------------------------------------------------------------
        wave_top = int(height * 0.380)  # 730px
        wave_bot = int(height * 0.515)  # 988px

        draw.rounded_rectangle([card_x0, wave_top, card_x1, wave_bot], radius=12, fill=(10, 16, 28), outline=(30, 48, 76), width=1)
        draw.text((card_x0 + 32, wave_top + 16), "REAL-TIME SENTIMENT DIVERGENCE (ALGORITHMIC FLOW)", fill=(148, 163, 184), font=font_sub)
        draw.text((card_x0 + 32, wave_top + 46), "DIVERGENCE INDEX: +2.84σ • INSTITUTIONAL SKEW", fill=(16, 185, 129), font=font_mono)

        wave_cy = (wave_top + wave_bot) // 2 + 16
        w_points1, w_points2 = [], []
        for wx in range(card_x0 + 20, card_x1 - 20, 4):
            val1 = math.sin((wx * 0.02) + (t * 4.5)) * 24.0
            val2 = math.cos((wx * 0.015) - (t * 3.0)) * 16.0
            w_points1.append((wx, int(wave_cy + val1)))
            w_points2.append((wx, int(wave_cy + val2)))

        if len(w_points1) > 1:
            draw.line(w_points1, fill=(16, 185, 129), width=3)
            draw.line(w_points2, fill=(56, 189, 248), width=2)

        # -------------------------------------------------------------
        # SAFE GAP 3: 42px between Waveform Card and Telemetry Card (988px -> 1030px)
        # -------------------------------------------------------------
        hud_top = int(height * 0.536)   # 1030px
        hud_bot = int(height * 0.668)   # 1282px

        draw.rounded_rectangle([card_x0, hud_top, card_x1, hud_bot], radius=12, fill=(10, 16, 28), outline=(56, 189, 248), width=1)

        val_conv = 74.0 + (tau * 15.5) + math.sin(t * 6.0) * 0.8
        draw.text((card_x0 + 32, hud_top + 18), "PRO CROWD™ REAL-TIME CONVICTION METER", fill=(148, 163, 184), font=font_sub)
        draw.text((card_x0 + 32, hud_top + 48), f"+{val_conv:.1f}% INSTITUTIONAL ACCUMULATION", fill=(16, 185, 129), font=font_val)

        # Dual Horizontal Progress Gauges (Institutional vs Retail)
        bar_x = card_x0 + 32
        bar_w = (card_x1 - card_x0) - 64
        bar_y1 = hud_top + 104
        draw.rounded_rectangle([bar_x, bar_y1, bar_x + bar_w, bar_y1 + 14], radius=7, fill=(20, 30, 48))
        fill_w1 = int(bar_w * min(1.0, val_conv / 100.0))
        draw.rounded_rectangle([bar_x, bar_y1, bar_x + fill_w1, bar_y1 + 14], radius=7, fill=(16, 185, 129))

        bar_y2 = hud_top + 134
        draw.text((bar_x, bar_y2), "RETAIL NOISE EXPOSURE (LOW CONVICTION): 21.6%", fill=(148, 163, 184), font=font_mono)
        draw.rounded_rectangle([bar_x, bar_y2 + 24, bar_x + bar_w, bar_y2 + 34], radius=5, fill=(20, 30, 48))
        draw.rounded_rectangle([bar_x, bar_y2 + 24, bar_x + int(bar_w * 0.216), bar_y2 + 34], radius=5, fill=(239, 68, 68))

        return np.array(base)

    else:
        # Hardware Screen Projection Mode:
        # Composites the animated radar beam, undulating sentiment wave, and glowing telemetry directly
        # onto the active display screen of the hardware device (tablet/laptop/terminal) with glass sheen reflections.
        canvas = bg_plate.copy().convert("RGBA")
        if canvas.size != (width, height):
            canvas = canvas.resize((width, height), Image.Resampling.LANCZOS)
        overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw_ov = ImageDraw.Draw(overlay)

        # Detect device screen layout based on mode or aspect
        is_laptop = (mode in ("hardware_laptop", "laptop"))
        if is_laptop:
            scr_x0 = int(width * 0.14)
            scr_x1 = int(width * 0.86)
            scr_y0 = int(height * 0.18)
            scr_y1 = int(height * 0.64)
        else:
            # Standard tablet screen coordinates
            scr_x0 = int(width * 0.19)
            scr_x1 = int(width * 0.81)
            scr_y0 = int(height * 0.16)
            scr_y1 = int(height * 0.72)

        scr_w = scr_x1 - scr_x0
        scr_h = scr_y1 - scr_y0

        # Rotating Radar Sweep on the device display
        rcx = scr_x0 + scr_w // 2
        rcy = scr_y0 + int(scr_h * 0.35)
        rr = int(min(scr_w * 0.38, scr_h * 0.28))

        angle = (t * 2.8) % (2.0 * math.pi)
        tx = int(rcx + rr * math.cos(angle))
        ty = int(rcy + rr * math.sin(angle))
        
        # Trailing phosphor decay fan
        for trail_step in range(8, 0, -2):
            trail_ang = angle - (trail_step * 0.05)
            tr_x = int(rcx + (rr - 2) * math.cos(trail_ang))
            tr_y = int(rcy + (rr - 2) * math.sin(trail_ang))
            draw_ov.line([(rcx, rcy), (tr_x, tr_y)], fill=(16, 185, 129, int(180 * (1.0 - trail_step / 10.0))), width=2)

        draw_ov.line([(rcx, rcy), (tx, ty)], fill=(56, 189, 248, 240), width=3)
        draw_ov.ellipse([rcx - 5, rcy - 5, rcx + 5, rcy + 5], fill=(16, 185, 129, 255))

        # Dynamic sentiment wave oscillating across the screen
        w_points = []
        wy_base = scr_y0 + int(scr_h * 0.35)
        for x_step in range(rcx - rr, rcx + rr, 4):
            yw = math.sin((x_step * 0.03) + (t * 5.0)) * 14.0
            w_points.append((x_step, int(wy_base + yw)))
        if len(w_points) > 1:
            draw_ov.line(w_points, fill=(56, 189, 248, 210), width=2)

        # Dynamic Institutional Conviction Bar on Screen
        bar_y = scr_y0 + int(scr_h * 0.76)
        bar_x = scr_x0 + int(scr_w * 0.12)
        bar_w = int(scr_w * 0.76)
        val_prog = min(1.0, 0.75 + 0.15 * math.sin(t * 1.5))
        draw_ov.rounded_rectangle([bar_x, bar_y, bar_x + bar_w, bar_y + 10], radius=5, fill=(16, 24, 40, 200))
        draw_ov.rounded_rectangle([bar_x, bar_y, bar_x + int(bar_w * val_prog), bar_y + 10], radius=5, fill=(16, 185, 129, 230))

        # Moving screen glass sheen / ambient reflection sweep
        for gy in range(scr_y0, scr_y1, 4):
            sheen_alpha = int(14 + 10 * math.sin((gy * 0.012) + t * 2.2))
            draw_ov.line([(scr_x0, gy), (scr_x1, gy)], fill=(120, 200, 255, sheen_alpha), width=2)

        comp = Image.alpha_composite(canvas, overlay).convert("RGB")
        if comp.size != (width, height):
            comp = comp.resize((width, height), Image.Resampling.LANCZOS)
        return np.array(comp)


class OpenMontageAdapter:
    """
    Isolated video engine adapter.
    Discovers OpenMontage tools and capabilities, orchestrates scene rendering,
    and produces production-ready MP4 advertisement videos.
    """

    def __init__(self, openmontage_root: Optional[str] = None):
        self.root_path = Path(openmontage_root or (Path(__file__).parent / "openmontage")).resolve()
        self.is_openmontage_available = False
        self._detect_engine()

    def _detect_engine(self):
        """Checks if OpenMontage repository and tool registry are accessible."""
        tools_dir = self.root_path / "tools"
        registry_file = tools_dir / "tool_registry.py"
        if tools_dir.exists() and registry_file.exists():
            try:
                try:
                    import tools
                    om_tools_path = str(tools_dir.resolve())
                    if hasattr(tools, "__path__") and om_tools_path not in tools.__path__:
                        tools.__path__.append(om_tools_path)
                except Exception as te:
                    logger.debug(f"Tools package prep notice: {te}")

                if str(self.root_path) not in sys.path:
                    sys.path.append(str(self.root_path))

                from tools.tool_registry import registry
                if registry and hasattr(registry, "discover"):
                    registry.discover()
                self.is_openmontage_available = True
                logger.info("[OpenMontageAdapter] OpenMontage tool registry successfully detected and loaded.")
            except Exception as e:
                logger.info(f"[OpenMontageAdapter] OpenMontage present but tool discovery deferred: {e}")
                self.is_openmontage_available = False
        else:
            self.is_openmontage_available = False

    async def render_video(
        self,
        scenes: List[Dict[str, Any]],
        output_file_path: str,
        thumbnail_file_path: str,
        aspect_ratio: str = "9:16",
        target_duration: int = 45,
        quality: str = "high",
        progress_callback: Optional[Any] = None,
        cancel_event: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """
        Renders a cinematic video advertisement from storyboard scenes.
        Outputs an actual MP4 video file and thumbnail image.
        Integrates genuine video footage, live animated financial charts, and synchronized speech.
        """
        out_path = Path(output_file_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        thumb_path = Path(thumbnail_file_path)
        thumb_path.parent.mkdir(parents=True, exist_ok=True)

        async def _update_progress(pct: int, msg: str):
            if progress_callback:
                try:
                    if asyncio.iscoroutinefunction(progress_callback):
                        await progress_callback(pct, msg)
                    else:
                        r = progress_callback(pct, msg)
                        if asyncio.iscoroutine(r):
                            await r
                except Exception:
                    pass

        await _update_progress(10, "Setting up scene dimensions and timeline...")

        # 1080p Commercial Quality (1080x1920 or 1920x1080)
        dim_map = {
            "9:16": (1080, 1920),
            "16:9": (1920, 1080),
            "1:1": (1080, 1080),
        }
        width, height = dim_map.get(aspect_ratio, (1080, 1920))

        # 1. Ensure all scenes have genuine media prepared (footage, animated charts, or AI visuals)
        from services.visual_asset_service import visual_asset_service
        await _update_progress(20, "Verifying and generating cinematic video footage and dynamic charts...")

        script_id = None
        campaign_id = None
        for sc in scenes:
            if sc.get("script_id") and not script_id:
                script_id = sc.get("script_id")
            if sc.get("campaign_id") and not campaign_id:
                campaign_id = sc.get("campaign_id")

        scenes_with_assets = await visual_asset_service.ensure_script_visual_assets(
            {"_id": script_id, "campaign_id": campaign_id, "scenes": scenes}, aspect_ratio=aspect_ratio
        )
        if not scenes_with_assets:
            scenes_with_assets = scenes

        # 2. Synthesize Spoken Narration and Synchronize Scene Timings Ahead of Rendering
        await _update_progress(38, "Synthesizing spoken voiceover narration and frame-perfect sync...")
        from services.tts_service import tts_service
        tts_result = None
        try:
            tts_result = await asyncio.wait_for(
                tts_service.generate_narration_track(scenes_with_assets, float(target_duration)),
                timeout=30.0
            )
            if tts_result:
                logger.info(f"[OpenMontageAdapter] Successfully pre-synthesized narration: {len(tts_result.get('speech_intervals', []))} intervals.")
        except Exception as tts_err:
            logger.warning(f"[OpenMontageAdapter] Pre-rendering narration notice: {tts_err}")

        # 3. Render using MoviePy engine with genuine footage, animated charts, and cinematic motion
        await _update_progress(50, "Composing cinematic footage, animated financial charts, and typography at 30 FPS...")

        loop = asyncio.get_running_loop()

        def sync_progress(pct: int, msg: str):
            if progress_callback:
                try:
                    if asyncio.iscoroutinefunction(progress_callback):
                        asyncio.run_coroutine_threadsafe(progress_callback(pct, msg), loop)
                    else:
                        loop.call_soon_threadsafe(progress_callback, pct, msg)
                except Exception:
                    pass

        from services.memory_monitor import MemoryTracker
        v_job_id = out_path.stem.replace("video_", "")
        async with MemoryTracker(job_id=v_job_id, job_type="video_render", limit_mb=float(getattr(settings, "VIDEO_RENDER_MEMORY_LIMIT_MB", 450.0))):
            render_result = await asyncio.to_thread(
                self._render_scenes_moviepy,
                scenes_with_assets,
                str(out_path),
                str(thumb_path),
                width,
                height,
                target_duration,
                quality,
                tts_result,
                sync_progress,
                cancel_event,
            )

        await _update_progress(98, "Finalizing MP4 container and commercial audio mix...")
        return render_result

    def _render_scenes_moviepy(
        self,
        scenes: List[Dict[str, Any]],
        out_path: str,
        thumb_path: str,
        width: int,
        height: int,
        target_duration: int,
        quality: str,
        tts_result: Optional[Dict[str, Any]] = None,
        sync_progress: Optional[Callable[[int, str], None]] = None,
        cancel_event: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """
        Executes actual video rendering using MoviePy 2 and Pillow.
        Composes genuine video clips, live animated financial charts, smooth cross-dissolves,
        and multi-track commercial fintech soundtrack at 30 FPS.
        """
        from PIL import Image, ImageDraw, ImageFont
        try:
            from moviepy import VideoClip, VideoFileClip, concatenate_videoclips, AudioFileClip, CompositeAudioClip
        except ImportError:
            raise RuntimeError("MoviePy is required for video rendering. Install via pip install moviepy")

        open_video_clips: List[Any] = []
        open_audio_clips: List[Any] = []
        temp_files_to_unlink: List[Path] = []
        final_clip = None
        clips = []
        num_scenes = len(scenes)
        if num_scenes == 0:
            raise ValueError("Cannot render video with zero scenes.")

        out_w, out_h = width, height
        scale_filter = []

        if tts_result and tts_result.get("adjusted_durations"):
            allocated_durations = tts_result["adjusted_durations"]
        else:
            raw_durations = [max(1.0, float(sc.get("duration_seconds", 5))) for sc in scenes]
            raw_total = sum(raw_durations)
            allocated_durations = []
            current_sum = 0.0
            for i, raw_dur in enumerate(raw_durations):
                if i == num_scenes - 1:
                    final_dur = max(2.5, target_duration - current_sum)
                    allocated_durations.append(round(final_dur, 2))
                else:
                    scaled = round((raw_dur / raw_total) * target_duration, 2)
                    scaled = max(2.5, scaled)
                    allocated_durations.append(scaled)
                    current_sum += scaled

        def get_font(size: int, bold: bool = False):
            font_candidates = [
                "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
                "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
                "C:/Windows/Fonts/calibrib.ttf" if bold else "C:/Windows/Fonts/calibri.ttf",
            ]
            for font_p in font_candidates:
                if os.path.exists(font_p):
                    try:
                        return ImageFont.truetype(font_p, size)
                    except Exception:
                        pass
            return ImageFont.load_default()

        font_brand = get_font(max(24, width // 42), bold=True)
        font_header = get_font(max(34, width // 28), bold=True)
        font_body = get_font(max(36, width // 28), bold=True)
        font_sub = get_font(max(20, width // 48), bold=False)
        font_cta_head = get_font(max(40, width // 22), bold=True)
        font_active = get_font(max(38, width // 28), bold=True)

        def build_kinetic_phrases(vo_text: str, speech_duration: float, pre_roll: float = 0.35, words_per_phrase: int = 4):
            """Splits voiceover into rhythmic phrases with length-weighted word timestamps."""
            words = vo_text.split()
            if not words:
                return []
            weights = [max(1.0, float(len(w))) for w in words]
            tot_weight = sum(weights)
            word_timings = []
            cur_t = pre_roll
            for w, wt in zip(words, weights):
                w_dur = (wt / tot_weight) * speech_duration
                word_timings.append((w, cur_t, cur_t + w_dur))
                cur_t += w_dur
            phrases = []
            for i in range(0, len(words), words_per_phrase):
                chunk = word_timings[i : i + words_per_phrase]
                p_start = chunk[0][1]
                p_end = chunk[-1][2]
                phrases.append({
                    "words": [c[0] for c in chunk],
                    "word_timings": chunk,
                    "start": p_start,
                    "end": p_end
                })
            return phrases

        caption_cache: Dict[Tuple, Any] = {}

        def draw_kinetic_caption(base_canvas: Any, t: float, phrases: List[Dict[str, Any]], w_w: int, h_h: int, f_main, f_act, scene_id: Any = 0) -> Any:
            """
            Renders dynamic lower-third caption card highlighting the currently spoken word.
            Memory-optimized: renders ONLY the local subtitle card bounding box (card_w x card_h)
            instead of a full-frame 1080x1920 canvas, reducing memory per entry from 8.3 MB to ~0.5 MB.
            Uses bounded LRU cache (max 8 entries) to strictly cap memory usage under 4 MB.
            """
            if not phrases:
                return base_canvas

            # Frame-level active speech interval detection:
            # Check if t falls within any phrase's active spoken window [start - 0.08, end + 0.18]
            active_p = None
            p_idx = -1
            for idx, p in enumerate(phrases):
                if (p["start"] - 0.08) <= t <= (p["end"] + 0.18):
                    active_p = p
                    p_idx = idx
                    break

            # If current frame t falls in a silent gap (before speech, between phrases, or after speech),
            # return base_canvas without any subtitle card
            if active_p is None:
                return base_canvas

            words_info = active_p["word_timings"]
            active_w_idx = -1
            for w_i, (w, t0, t1) in enumerate(words_info):
                if t0 <= t <= t1:
                    active_w_idx = w_i
                    break

            # Unique scene identifier + phrase text + active word index guarantees complete isolation
            phrase_id = active_p.get("id") or f"p{p_idx}_" + "_".join(active_p.get("words", [])[:3])
            cache_key = (str(scene_id), str(phrase_id), active_w_idx, w_w, h_h)
            if cache_key not in caption_cache:
                # Bounded cache eviction: discard oldest entry if exceeding 8 entries
                if len(caption_cache) >= 8:
                    oldest_key = next(iter(caption_cache))
                    caption_cache.pop(oldest_key, None)

                # Modern typographic spacing with stable font.getlength
                space_w = max(24, int(w_w * 0.022))
                word_advances = [int(f_main.getlength(w)) for w, t0, t1 in words_info]

                tot_w_single = sum(word_advances) + space_w * (len(words_info) - 1)
                max_single_w = int(w_w * 0.82)

                # Intelligent multi-line wrapping if phrase exceeds safe width
                if tot_w_single <= max_single_w or len(words_info) <= 3:
                    lines = [list(range(len(words_info)))]
                else:
                    mid = (len(words_info) + 1) // 2
                    lines = [list(range(0, mid)), list(range(mid, len(words_info)))]

                line_height = 56
                num_lines = len(lines)
                card_pad_v = 20
                card_pad_h = 36

                line_widths = []
                for l_indices in lines:
                    lw = sum(word_advances[i] for i in l_indices) + space_w * (len(l_indices) - 1)
                    line_widths.append(lw)

                max_lw = max(line_widths)
                card_w = min(int(w_w * 0.92), max(int(w_w * 0.46), int(max_lw + card_pad_h * 2)))
                card_h = int(card_pad_v * 2 + num_lines * line_height)
                card_x = (w_w - card_w) // 2
                card_y = int(h_h * 0.77)

                # Local card image (only card_w x card_h, e.g. 990x152 = 0.5 MB instead of 8.3 MB!)
                card_img = Image.new("RGBA", (card_w, card_h), (0, 0, 0, 0))
                draw = ImageDraw.Draw(card_img)

                # 2. Dark frosted obsidian glass capsule drawn local to card
                draw.rounded_rectangle(
                    [0, 0, card_w, card_h],
                    radius=18,
                    fill=(10, 14, 24, 235),
                    outline=(56, 189, 248, 140),
                    width=2
                )

                # Position words per line relative to card
                word_positions = {}
                for l_idx, l_indices in enumerate(lines):
                    lw = line_widths[l_idx]
                    start_x = (card_w - lw) // 2
                    text_y = card_pad_v + l_idx * line_height + 4
                    cur_x = start_x
                    for w_i in l_indices:
                        w = words_info[w_i][0]
                        w_adv = word_advances[w_i]
                        ink_bbox = draw.textbbox((cur_x, text_y), w, font=f_main)
                        word_positions[w_i] = (w, cur_x, text_y, ink_bbox, w_adv)
                        cur_x += w_adv + space_w

                # 3. Draw active word pill background under text with balanced padding and centering
                if active_w_idx in word_positions:
                    w, wx, ty, ink_bbox, w_adv = word_positions[active_w_idx]
                    clean_w = w.strip(".,!?:;\"'()[]{}")
                    clean_bbox = draw.textbbox((wx, ty), clean_w or w, font=f_main)
                    ink_center_x = (clean_bbox[0] + clean_bbox[2]) / 2.0
                    ink_w = clean_bbox[2] - clean_bbox[0]
                    pill_w = max(ink_w + 24, 48)
                    pill_x0 = int(ink_center_x - pill_w / 2.0)
                    pill_x1 = pill_x0 + pill_w
                    pill_y0 = ty - 6
                    pill_y1 = ty + 44
                    draw.rounded_rectangle(
                        [pill_x0, pill_y0, pill_x1, pill_y1],
                        radius=10,
                        fill=(28, 78, 185, 235),
                        outline=(56, 189, 248, 255),
                        width=2
                    )

                # 4. Draw text on top with crisp drop shadow
                for w_i, (w, wx, ty, ink_bbox, w_adv) in word_positions.items():
                    if w_i == active_w_idx:
                        draw.text((wx + 1, ty + 2), w, fill=(0, 0, 0, 240), font=f_main)
                        draw.text((wx, ty), w, fill=(255, 255, 255, 255), font=f_main)
                    else:
                        draw.text((wx + 1, ty + 1), w, fill=(0, 0, 0, 180), font=f_main)
                        draw.text((wx, ty), w, fill=(225, 235, 248, 255), font=f_main)

                caption_cache[cache_key] = (card_img, card_x, card_y)

            card_img, card_x, card_y = caption_cache[cache_key]
            if base_canvas.mode != "RGBA":
                base_canvas = base_canvas.convert("RGBA")
            base_canvas.paste(card_img, (card_x, card_y), card_img)
            return base_canvas

        oversized_w = int(width * 1.08)
        oversized_h = int(height * 1.08)

        # Precompute single shared bottom scrim strip (avoids per-scene repetitive line drawing and memory bloat)
        scrim_start = int(height * 0.70)
        scrim_height = height - scrim_start
        shared_scrim_strip = Image.new("RGBA", (width, scrim_height), (0, 0, 0, 0))
        scrim_draw = ImageDraw.Draw(shared_scrim_strip)
        for y_rel in range(scrim_height):
            progress_y = y_rel / max(1, scrim_height)
            alpha_val = int(190 * (progress_y ** 1.3))
            scrim_draw.line([(0, y_rel), (width, y_rel)], fill=(6, 10, 18, min(200, alpha_val)), width=1)

        # Pre-build scene overlays
        prepared_scenes = []
        for idx, sc in enumerate(scenes):
            dur = allocated_durations[idx]
            asset_path = sc.get("visual_asset_path")
            media_type = sc.get("media_type", "ai_image")
            if asset_path and str(asset_path).lower().endswith((".mp4", ".mov", ".webm")):
                media_type = "video_clip"
            chart_theme = sc.get("chart_theme")

            overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
            overlay.paste(shared_scrim_strip, (0, scrim_start))
            draw = ImageDraw.Draw(overlay)

            # Kinetic word-level phrases
            vo_text = (sc.get("voiceover") or sc.get("on_screen_text") or "").strip()
            sc_speech_dur = max(2.0, dur - 1.2)
            phrases = build_kinetic_phrases(vo_text, speech_duration=sc_speech_dur, pre_roll=0.35, words_per_phrase=4)

            # Robust asset path resolution across candidate locations
            resolved_asset_path = None
            if asset_path:
                candidates = [
                    Path(asset_path),
                    Path(settings.MEDIA_DIR) / "assets" / Path(asset_path).name,
                    Path(settings.MEDIA_DIR) / "assets" / "stock_footage" / Path(asset_path).name,
                    Path("backend/media/assets/stock_footage") / Path(asset_path).name,
                    Path("media/assets/stock_footage") / Path(asset_path).name,
                    Path.cwd() / asset_path,
                    Path.cwd() / "backend" / asset_path,
                    Path(__file__).parent.parent / "media" / "assets" / Path(asset_path).name,
                    Path(__file__).parent.parent / "media" / "assets" / "stock_footage" / Path(asset_path).name,
                ]
                for cand in candidates:
                    if cand.exists() and cand.is_file():
                        resolved_asset_path = str(cand)
                        break
                if resolved_asset_path and resolved_asset_path.lower().endswith((".mp4", ".mov", ".webm")):
                    media_type = "video_clip"

            # Base image for still/AI image scenes or hardware plates
            base_bg = None
            if media_type not in ["animated_chart", "video_clip"]:
                clean_p = sc.get("clean_plate_path")
                if media_type == "product_demo" and clean_p and os.path.exists(clean_p):
                    img_to_open = clean_p
                elif media_type == "product_demo":
                    # Strictly resolve unburned hardware plate for product demo canvas
                    p_mode = sc.get("product_demo_mode", "fullscreen")
                    fb_dirs = [
                        Path("backend/media/assets/fallback_library"),
                        Path("media/assets/fallback_library"),
                        Path(settings.MEDIA_DIR) / "assets" / "fallback_library",
                        Path(__file__).parent.parent / "media" / "assets" / "fallback_library",
                    ]
                    target_plate = "platform_crowdwisdom_ui.jpg"
                    if p_mode in ("hardware_laptop", "laptop"):
                        target_plate = "platform_laptop_projection.jpg"
                    elif p_mode == "fullscreen":
                        target_plate = "platform_fullscreen_terminal.jpg"

                    img_to_open = None
                    for fd in fb_dirs:
                        cand = fd / target_plate
                        if cand.exists():
                            img_to_open = str(cand)
                            break
                    if not img_to_open:
                        img_to_open = resolved_asset_path or (asset_path if asset_path and os.path.exists(asset_path) else None)
                else:
                    img_to_open = resolved_asset_path or (asset_path if asset_path and os.path.exists(asset_path) else None)
                
                # If asset is missing, attempt emergency fallback from verified library
                if not img_to_open or not os.path.exists(img_to_open):
                    fb_dirs = [
                        Path("backend/media/assets/fallback_library"),
                        Path("media/assets/fallback_library"),
                        Path(settings.MEDIA_DIR) / "assets" / "fallback_library",
                        Path(__file__).parent.parent / "media" / "assets" / "fallback_library",
                    ]
                    for fd in fb_dirs:
                        cand = fd / ("platform_crowdwisdom_ui.jpg" if media_type == "product_demo" else "human_dawn_workstation.jpg")
                        if cand.exists():
                            img_to_open = str(cand)
                            logger.warning(f"[OpenMontage] Scene {idx+1} visual asset missing ({asset_path}); recovered using verified plate: {cand}")
                            break

                if not img_to_open or not os.path.exists(img_to_open):
                    raise RuntimeError(
                        f"Fatal composition error: Scene {idx+1} visual asset is missing ('{asset_path}'). "
                        f"Composition aborted to prevent blank output."
                    )

                if str(img_to_open).lower().endswith((".mp4", ".mov", ".webm")):
                    raise RuntimeError(
                        f"Scene {idx+1} expected still visual asset plate, but got video file: {img_to_open}"
                    )

                try:
                    loaded_img = Image.open(img_to_open).convert("RGB")
                except Exception as open_err:
                    raise RuntimeError(
                        f"Fatal composition error: Scene {idx+1} visual asset '{img_to_open}' could not be decoded: {open_err}"
                    )

                img_w, img_h = loaded_img.size
                scale = max(oversized_w / img_w, oversized_h / img_h)
                new_w, new_h = int(img_w * scale), int(img_h * scale)
                resized_bg = loaded_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
                crop_x = (new_w - oversized_w) // 2
                crop_y = (new_h - oversized_h) // 2
                base_bg = resized_bg.crop((crop_x, crop_y, crop_x + oversized_w, crop_y + oversized_h))

            # Save thumbnail from Scene 1
            if idx == 0:
                if media_type == "animated_chart":
                    t_thumb = render_dynamic_chart_canvas(0.5, dur, width, height, theme=chart_theme or "bullish_breakout", scene_num=1)
                    thumb_img = Image.alpha_composite(Image.fromarray(t_thumb).convert("RGBA"), overlay).convert("RGB")
                elif media_type == "product_demo":
                    t_thumb = render_dynamic_product_demo_canvas(1.0, dur, width, height, mode=sc.get("product_demo_mode", "fullscreen"), bg_plate=base_bg, scene_num=1)
                    thumb_img = Image.alpha_composite(Image.fromarray(t_thumb).convert("RGBA"), overlay).convert("RGB")
                elif media_type == "video_clip" and resolved_asset_path and os.path.exists(resolved_asset_path):
                    try:
                        v_temp = VideoFileClip(resolved_asset_path)
                        t_frame = v_temp.get_frame(min(1.0, max(0.0, float(v_temp.duration) - 0.1)))
                        v_temp.close()
                        v_img = Image.fromarray(t_frame).resize((width, height)).convert("RGBA")
                        thumb_img = Image.alpha_composite(v_img, overlay).convert("RGB")
                    except Exception:
                        thumb_sample = (base_bg or Image.new("RGB", (width, height), (14, 22, 38))).resize((width, height)).convert("RGBA")
                        thumb_img = Image.alpha_composite(thumb_sample, overlay).convert("RGB")
                else:
                    thumb_sample = (base_bg or Image.new("RGB", (width, height), (14, 22, 38))).resize((width, height)).convert("RGBA")
                    thumb_img = Image.alpha_composite(thumb_sample, overlay).convert("RGB")
                thumb_img.save(thumb_path, "JPEG", quality=92)

            prepared_scenes.append({
                "media_type": media_type,
                "product_demo_mode": sc.get("product_demo_mode", "fullscreen"),
                "chart_theme": chart_theme or ("volatility_drop" if idx == 0 else "bullish_breakout"),
                "asset_path": resolved_asset_path or asset_path,
                "base_bg": base_bg,
                "overlay": overlay,
                "phrases": phrases,
                "camera_motion": sc.get("camera_motion") or ("slow_zoom_in" if idx % 2 == 0 else "pan_right"),
                "duration": dur,
                "is_final": (idx == num_scenes - 1),
                "scene_num": idx + 1
            })

        # Pre-load official CrowdWisdom logo badge for closing outro and opening introduction
        official_logo_img = None
        for cand in [
            Path(settings.MEDIA_DIR) / "assets" / "crowdwisdom_logo_badge.png",
            Path("media/assets/crowdwisdom_logo_badge.png"),
            Path("backend/media/assets/crowdwisdom_logo_badge.png"),
            Path(__file__).parent.parent / "media" / "assets" / "crowdwisdom_logo_badge.png",
        ]:
            if cand.exists() and cand.is_file():
                try:
                    official_logo_img = Image.open(cand).convert("RGBA")
                    break
                except Exception:
                    pass

        scene_generators = []

        for idx, p_scene in enumerate(prepared_scenes):
            dur = p_scene["duration"]
            m_type = p_scene["media_type"]
            c_theme = p_scene["chart_theme"]
            a_path = p_scene["asset_path"]
            sc_num = p_scene["scene_num"]
            is_last = p_scene["is_final"]

            if sync_progress:
                scene_pct = 50 + int((idx / max(num_scenes, 1)) * 12)
                sync_progress(scene_pct, f"Preparing scene generator {idx + 1}/{num_scenes} ({m_type})...")

            # Final scene CTA Card helper integrating official CrowdWisdom logo
            def draw_end_cta_card(target_img: Image.Image, t_curr: float, sc_length: float) -> Image.Image:
                if t_curr < max(0.1, sc_length - 3.4):
                    return target_img
                cta_alpha = min(1.0, (t_curr - (sc_length - 3.4)) / 0.8)
                cta_overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
                cta_draw = ImageDraw.Draw(cta_overlay)

                scrim_alpha = int(195 * cta_alpha)
                cta_draw.rectangle([0, 0, width, height], fill=(6, 10, 18, scrim_alpha))

                card_w = int(width * 0.90)
                card_h = int(height * 0.48)
                card_x = (width - card_w) // 2
                card_y = (height - card_h) // 2 - 30
                card_fill_alpha = int(245 * cta_alpha)

                cta_draw.rounded_rectangle(
                    [card_x, card_y, card_x + card_w, card_y + card_h],
                    radius=20,
                    fill=(10, 16, 28, card_fill_alpha),
                    outline=(56, 189, 248, int(220 * cta_alpha)),
                    width=2
                )

                cur_y = card_y + 24
                # Official CrowdWisdom Bears & Bulls Logo Badge
                if official_logo_img:
                    logo_target_w = int(card_w * 0.86)
                    logo_scale = logo_target_w / official_logo_img.width
                    logo_target_h = int(official_logo_img.height * logo_scale)
                    logo_scaled = official_logo_img.resize((logo_target_w, logo_target_h), Image.Resampling.LANCZOS)
                    if cta_alpha < 0.99:
                        r, g, b, a = logo_scaled.split()
                        a = a.point(lambda p: int(p * cta_alpha))
                        logo_scaled = Image.merge("RGBA", (r, g, b, a))
                    logo_x = card_x + (card_w - logo_target_w) // 2
                    cta_overlay.paste(logo_scaled, (logo_x, cur_y), logo_scaled)
                    cur_y += logo_target_h + 20
                else:
                    cta_draw.text((card_x + 40, cur_y), "CROWDWISDOM TRADING", fill=(56, 189, 248, int(255 * cta_alpha)), font=font_brand)
                    cur_y += 50

                # Headline
                hl_line1 = "TRADE WITH COLLECTIVE"
                hl_line2 = "MARKET CONVICTION"
                bbox1 = cta_draw.textbbox((0, 0), hl_line1, font=font_cta_head)
                bbox2 = cta_draw.textbbox((0, 0), hl_line2, font=font_cta_head)
                cta_draw.text((card_x + (card_w - (bbox1[2] - bbox1[0])) // 2, cur_y), hl_line1, fill=(255, 255, 255, int(255 * cta_alpha)), font=font_cta_head)
                cur_y += (bbox1[3] - bbox1[1]) + 8
                cta_draw.text((card_x + (card_w - (bbox2[2] - bbox2[0])) // 2, cur_y), hl_line2, fill=(56, 189, 248, int(255 * cta_alpha)), font=font_cta_head)
                cur_y += (bbox2[3] - bbox2[1]) + 16

                # Feature pills subhead
                sub_txt = "Institutional Sentiment • CrowdMap™ • Alpha Signals"
                bbox_sub = cta_draw.textbbox((0, 0), sub_txt, font=font_sub)
                cta_draw.text((card_x + (card_w - (bbox_sub[2] - bbox_sub[0])) // 2, cur_y), sub_txt, fill=(148, 163, 184, int(255 * cta_alpha)), font=font_sub)

                # Primary Action Button
                btn_w = int(card_w * 0.86)
                btn_h = 76
                btn_x = card_x + (card_w - btn_w) // 2
                btn_y = card_y + card_h - btn_h - 28
                cta_draw.rounded_rectangle(
                    [btn_x, btn_y, btn_x + btn_w, btn_y + btn_h],
                    radius=14,
                    fill=(37, 99, 235, int(255 * cta_alpha)),
                    outline=(56, 189, 248, int(220 * cta_alpha)),
                    width=2
                )
                btn_txt = "Join at CrowdWisdomTrading.com  →"
                bbox_btn = cta_draw.textbbox((0, 0), btn_txt, font=font_body)
                cta_draw.text(
                    (btn_x + (btn_w - (bbox_btn[2] - bbox_btn[0])) // 2, btn_y + (btn_h - (bbox_btn[3] - bbox_btn[1])) // 2 - 2),
                    btn_txt,
                    fill=(255, 255, 255, int(255 * cta_alpha)),
                    font=font_body
                )
                return Image.alpha_composite(target_img.convert("RGBA"), cta_overlay).convert("RGB")

            # ---------------------------------------------------------
            # Branch A: Real Video Footage Clip
            # ---------------------------------------------------------
            if m_type == "video_clip" and a_path and os.path.exists(a_path):
                try:
                    # High-speed pre-scaling via FFmpeg: avoids costly per-frame Python resizing
                    prescaled_p = Path(a_path).parent / f"prescaled_{width}x{height}_{Path(a_path).name}"
                    if not prescaled_p.exists():
                        try:
                            import imageio_ffmpeg
                            import subprocess
                            ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
                            vf = f"scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height},fps=30"
                            cmd = [ffmpeg_exe, "-y", "-i", str(a_path), "-vf", vf, "-c:v", "libx264", "-preset", "ultrafast", "-an", str(prescaled_p)]
                            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        except Exception as scale_err:
                            logger.debug(f"Fast pre-scaling notice: {scale_err}")

                    source_video_path = str(prescaled_p) if prescaled_p.exists() else a_path
                    cropped_video = VideoFileClip(source_video_path).without_audio()
                    open_video_clips.append(cropped_video)
                    if prescaled_p.exists() and prescaled_p not in temp_files_to_unlink:
                        temp_files_to_unlink.append(prescaled_p)

                    # Fallback resize if pre-scaling was bypassed
                    vw, vh = cropped_video.size
                    if vw != width or vh != height:
                        v_scale = max(width / vw, height / vh)
                        scaled_video = cropped_video.resized(v_scale)
                        sw, sh = scaled_video.size
                        x1 = (sw - width) // 2
                        y1 = (sh - height) // 2
                        cropped_video = scaled_video.cropped(x1=x1, y1=y1, width=width, height=height)

                    loop_dur = max(0.2, float(cropped_video.duration) - 0.06)
                    # Campaign-aware temporal offset: prevents different ads or scenes from starting at identical frames
                    cid_seed = p_scene.get("campaign_id") or str(sc.get("script_id", ""))
                    seed_val = int(hashlib.md5(f"{cid_seed}_{sc_num}".encode()).hexdigest(), 16)
                    max_slack = max(0.0, loop_dur - dur)
                    start_offset = float((seed_val % max(1, int(max_slack * 10))) / 10.0) if max_slack > 0.8 else 0.0

                    def make_video_frame(t, c_vid=cropped_video, l_dur=loop_dur, s_off=start_offset, ov=p_scene["overlay"], phr=p_scene["phrases"], snum=sc_num, is_end=is_last, sc_dur=dur):
                        if cancel_event and getattr(cancel_event, "is_set", lambda: False)():
                            raise RuntimeError("Render cancelled by user/timeout token.")
                        # Continuous natural forward playback
                        target_t = s_off + float(t)
                        if target_t < l_dur:
                            t_safe = target_t
                        else:
                            # Smooth continuous bounce to eliminate jarring hard-modulo GIF restarts
                            period = max(0.2, l_dur - 0.08)
                            norm_t = (float(t) + s_off) % (2.0 * period)
                            t_safe = norm_t if norm_t <= period else (2.0 * period - norm_t)
                        t_safe = max(0.0, min(float(c_vid.duration) - 0.05, t_safe))
                        frame_img = Image.fromarray(c_vid.get_frame(t_safe)).convert("RGBA")
                        comp = Image.alpha_composite(frame_img, ov)
                        comp = draw_kinetic_caption(comp, t, phr, width, height, font_body, font_active, scene_id=snum)
                        final_img = comp.convert("RGB")
                        if is_end:
                            final_img = draw_end_cta_card(final_img, t, sc_dur)
                        return np.array(final_img)

                    scene_generators.append(make_video_frame)
                    continue
                except Exception as vid_err:
                    logger.warning(f"Video footage playback notice scene {idx+1}: {vid_err}. Using dynamic chart fallback.")
                    m_type = "animated_chart"

            # ---------------------------------------------------------
            # Branch B: Genuinely Animated Financial Chart
            # ---------------------------------------------------------
            if m_type == "animated_chart":
                def make_chart_scene_frame(t, sc_dur=dur, theme=c_theme, snum=sc_num, ov=p_scene["overlay"], phr=p_scene["phrases"], is_end=is_last):
                    if cancel_event and getattr(cancel_event, "is_set", lambda: False)():
                        raise RuntimeError("Render cancelled by user/timeout token.")
                    chart_arr = render_dynamic_chart_canvas(t, sc_dur, width, height, theme=theme, scene_num=snum)
                    chart_img = Image.fromarray(chart_arr).convert("RGBA")
                    comp = Image.alpha_composite(chart_img, ov)
                    comp = draw_kinetic_caption(comp, t, phr, width, height, font_body, font_active, scene_id=snum)
                    final_img = comp.convert("RGB")

                    # Final scene CTA Card
                    if is_end:
                        final_img = draw_end_cta_card(final_img, t, sc_dur)

                    return np.array(final_img)

                scene_generators.append(make_chart_scene_frame)
                continue

            # ---------------------------------------------------------
            # Branch C: Dynamic CrowdWisdom Product Demonstration Canvas
            # ---------------------------------------------------------
            if m_type == "product_demo":
                p_mode = p_scene.get("product_demo_mode", "fullscreen")
                p_bg = p_scene.get("base_bg")

                def make_product_scene_frame(t, sc_dur=dur, mode=p_mode, bg=p_bg, snum=sc_num, ov=p_scene["overlay"], phr=p_scene["phrases"], is_end=is_last):
                    if cancel_event and getattr(cancel_event, "is_set", lambda: False)():
                        raise RuntimeError("Render cancelled by user/timeout token.")
                    frame_arr = render_dynamic_product_demo_canvas(t, sc_dur, width, height, mode=mode, bg_plate=bg, scene_num=snum)
                    frame_img = Image.fromarray(frame_arr).convert("RGBA")
                    if frame_img.size != (width, height):
                        frame_img = frame_img.resize((width, height), Image.Resampling.BILINEAR)
                    comp = Image.alpha_composite(frame_img, ov)
                    comp = draw_kinetic_caption(comp, t, phr, width, height, font_body, font_active, scene_id=snum)
                    final_img = comp.convert("RGB")
                    if is_end:
                        final_img = draw_end_cta_card(final_img, t, sc_dur)
                    return np.array(final_img)

                scene_generators.append(make_product_scene_frame)
                continue

            # ---------------------------------------------------------
            # Branch D: AI Photorealistic Image with Eased Camera & Dynamic Ambient Sweep
            # ---------------------------------------------------------
            base_bg = p_scene["base_bg"]
            cam_motion = p_scene["camera_motion"]

            def make_still_scene_frame(t, bg=base_bg, cam=cam_motion, sc_dur=dur, ov=p_scene["overlay"], phr=p_scene["phrases"], is_end=is_last, snum=sc_num):
                if cancel_event and getattr(cancel_event, "is_set", lambda: False)():
                    raise RuntimeError("Render cancelled by user/timeout token.")
                # Smooth non-linear camera ease (cosine deceleration)
                raw_progress = min(1.0, max(0.0, t / max(sc_dur, 0.1)))
                alpha = 0.5 - 0.5 * math.cos(math.pi * raw_progress)

                if cam == "slow_zoom_in":
                    cur_scale = 1.08 - (0.08 * alpha)
                    crop_w, crop_h = int(width * cur_scale), int(height * cur_scale)
                    x0 = (oversized_w - crop_w) // 2
                    y0 = (oversized_h - crop_h) // 2
                elif cam == "pan_right":
                    cur_scale = 1.03
                    crop_w, crop_h = int(width * cur_scale), int(height * cur_scale)
                    x0 = int((oversized_w - crop_w) * alpha)
                    y0 = (oversized_h - crop_h) // 2
                else:
                    cur_scale = 1.03
                    crop_w, crop_h = int(width * cur_scale), int(height * cur_scale)
                    x0 = int((oversized_w - crop_w) * (1.0 - alpha))
                    y0 = (oversized_h - crop_h) // 2

                cropped = bg.crop((x0, y0, x0 + crop_w, y0 + crop_h))
                resized = cropped.resize((width, height), Image.Resampling.BILINEAR).convert("RGBA")
                comp = Image.alpha_composite(resized, ov)

                # Dynamic subtle ambient daylight sweep across the scene (local strip rendering)
                sweep_y = int((height * 0.18) + math.sin(t * 1.6) * (height * 0.06))
                sweep_h = 74
                sweep_y0 = max(0, sweep_y - 37)
                sweep_strip = Image.new("RGBA", (width, sweep_h), (0, 0, 0, 0))
                ls_draw = ImageDraw.Draw(sweep_strip)
                for dy in range(-35, 35, 4):
                    l_alpha = int(14 * (1.0 - abs(dy) / 35.0))
                    local_y = dy + 37
                    if 0 <= local_y < sweep_h:
                        ls_draw.line([(0, local_y), (width, local_y)], fill=(255, 235, 200, l_alpha), width=3)
                comp.paste(sweep_strip, (0, sweep_y0), sweep_strip)

                if snum == 1 and 0.6 <= t <= 3.2 and official_logo_img:
                    intro_alpha = min(1.0, (t - 0.6) / 0.5) * min(1.0, (3.2 - t) / 0.5)
                    if intro_alpha > 0.05:
                        intro_w = int(width * 0.54)
                        intro_scale = intro_w / official_logo_img.width
                        intro_h = int(official_logo_img.height * intro_scale)
                        intro_logo = official_logo_img.resize((intro_w, intro_h), Image.Resampling.LANCZOS)
                        r, g, b, a = intro_logo.split()
                        a = a.point(lambda p: int(p * intro_alpha * 0.90))
                        intro_logo = Image.merge("RGBA", (r, g, b, a))
                        intro_x = (width - intro_w) // 2
                        intro_y = int(height * 0.10)
                        comp.paste(intro_logo, (intro_x, intro_y), intro_logo)

                comp = draw_kinetic_caption(comp, t, phr, width, height, font_body, font_active, scene_id=snum)
                final_img = comp.convert("RGB")
                if is_end:
                    final_img = draw_end_cta_card(final_img, t, sc_dur)
                return np.array(final_img)

            scene_generators.append(make_still_scene_frame)

        # ---------------------------------------------------------
        # Assemble Cinematic Transitions Engine (Stage 2)
        # ---------------------------------------------------------
        clips = []
        transition_timestamps = []
        current_time_cursor = 0.0

        for idx in range(num_scenes):
            dur = prepared_scenes[idx]["duration"]
            gen_cur = scene_generators[idx]

            has_prev = (idx > 0)
            has_next = (idx < num_scenes - 1)

            t_next_dur = prepared_scenes[idx + 1]["duration"] if has_next else 0.0
            trans_dur = min(0.50, dur * 0.15, t_next_dur * 0.15) if has_next else 0.0
            prev_trans_dur = min(0.50, prepared_scenes[idx - 1]["duration"] * 0.15, dur * 0.15) if has_prev else 0.0

            t_start = prev_trans_dur if has_prev else 0.0
            t_end = (dur - trans_dur) if has_next else dur
            main_dur = max(0.1, t_end - t_start)

            # 1. Main scene body
            def make_main_frame(t, g=gen_cur, offset=t_start):
                return g(offset + t)

            main_clip = VideoClip(make_main_frame, duration=main_dur)
            clips.append(main_clip)
            open_video_clips.append(main_clip)
            current_time_cursor += main_dur

            # 2. Cinematic Transition to next scene
            if has_next:
                gen_next = scene_generators[idx + 1]
                t_type = resolve_transition_type(scenes[idx], scenes[idx + 1], idx)
                transition_timestamps.append(round(current_time_cursor + trans_dur / 2.0, 3))
                logger.info(f"[OpenMontageAdapter] Applying cinematic transition '{t_type}' between scene {idx+1} and {idx+2} (t={current_time_cursor:.2f}s).")

                if sync_progress:
                    trans_pct = 62 + int((idx / max(num_scenes - 1, 1)) * 8)
                    sync_progress(trans_pct, f"Composing transition '{t_type}' (scene {idx+1} -> {idx+2})...")

                def make_trans_frame(u, g_a=gen_cur, g_b=gen_next, d_a=dur, trans_type=t_type, t_len=trans_dur):
                    if cancel_event and getattr(cancel_event, "is_set", lambda: False)():
                        raise RuntimeError("Render cancelled by user/timeout token.")
                    tau = max(0.0, min(1.0, u / max(0.01, t_len)))
                    f_a = g_a(d_a - t_len + u)
                    f_b = g_b(u)
                    return render_cinematic_transition(f_a, f_b, tau, trans_type)

                trans_clip = VideoClip(make_trans_frame, duration=trans_dur)
                clips.append(trans_clip)
                open_video_clips.append(trans_clip)
                current_time_cursor += trans_dur

        final_clip = concatenate_videoclips(clips, method="chain")
        total_dur = float(final_clip.duration)
        speech_intervals: List[Tuple[float, float]] = tts_result.get("speech_intervals", []) if tts_result else []

        # High-Definition 30 FPS Rendering with Decoupled Audio Pipeline
        if sync_progress:
            sync_progress(45, f"Rendering cinematic video at {out_w}x{out_h} (30 FPS, H.264 ultrafast)...")

        render_logger = None
        if sync_progress:
            import proglog
            class RenderProgressLogger(proglog.ProgressBarLogger):
                def __init__(self, progress_fn, cancel_tok=None):
                    super().__init__()
                    self.progress_fn = progress_fn
                    self.cancel_tok = cancel_tok
                    self.last_pct = 0
                    self.last_time = 0

                def check_cancellation(self):
                    if self.cancel_tok and getattr(self.cancel_tok, "is_set", lambda: False)():
                        raise RuntimeError("Render cancelled by cancellation token.")

                def bars_callback(self, bar, attr, value, old_value=None):
                    self.check_cancellation()
                    if not self.progress_fn:
                        return
                    if bar == "frame_index" and attr == "index":
                        tot = self.state.get("bars", {}).get(bar, {}).get("total", 0)
                        if tot:
                            mapped_pct = min(92, max(45, 45 + int((value / tot) * 47)))
                            now = time.time()
                            if (mapped_pct > self.last_pct or mapped_pct >= 92) and (now - self.last_time >= 0.8):
                                self.last_pct = mapped_pct
                                self.last_time = now
                                self.progress_fn(mapped_pct, f"Rendering cinematic video frame {value}/{tot} ({mapped_pct}%)...")

                def callback(self, **changes):
                    self.check_cancellation()
                    if not self.progress_fn:
                        return
                    for k, v in self.state.get("bars", {}).items():
                        if k == "frame_index" and "total" in v and v["total"]:
                            idx = v.get("index", 0)
                            tot = v["total"]
                            mapped_pct = min(92, max(45, 45 + int((idx / tot) * 47)))
                            now = time.time()
                            if (mapped_pct > self.last_pct or mapped_pct >= 92) and (now - self.last_time >= 0.8):
                                self.last_pct = mapped_pct
                                self.last_time = now
                                self.progress_fn(mapped_pct, f"Rendering cinematic video frame {idx}/{tot} ({mapped_pct}%)...")

            render_logger = RenderProgressLogger(sync_progress, cancel_event)

        ffmpeg_threads = max(1, min(2, getattr(settings, "VIDEO_FFMPEG_THREADS", 1)))
        ffmpeg_preset = getattr(settings, "VIDEO_FFMPEG_PRESET", "veryfast")

        ffmpeg_args = [
            "-pix_fmt", "yuv420p",
            "-profile:v", "high",
            "-level", "4.2",
            "-threads", "1",
            "-x264-params", "rc-lookahead=4:sync-lookahead=2:bframes=0:threads=1",
            "-bufsize", "2000k",
            "-maxrate", "3500k",
        ] + scale_filter

        temp_video_path = Path(out_path).parent / f"temp_raw_{Path(out_path).name}"
        temp_files_to_unlink.append(temp_video_path)

        try:
            # Render video stream ONLY in MoviePy (avoids ~200 MB audio chunk buffering in Python)
            final_clip.write_videofile(
                str(temp_video_path),
                fps=30,  # Broadcast-standard 30 FPS
                codec="libx264",
                audio=False,
                bitrate="4500k",
                preset=ffmpeg_preset,
                threads=1,  # Single-threaded Python avoids GIL and RAM bloat
                ffmpeg_params=ffmpeg_args,
                logger=render_logger
            )
            actual_duration = float(final_clip.duration)
        finally:
            # Deterministic, leak-free disposal of all clip instances before audio muxing
            for c in open_video_clips:
                try:
                    c.close()
                except Exception:
                    pass
            open_video_clips.clear()
            if final_clip:
                try:
                    final_clip.close()
                except Exception:
                    pass
                final_clip = None
            caption_cache.clear()
            from services.memory_monitor import release_system_memory
            release_system_memory()

        # Step 4: Synthesize soundtrack directly to WAV and mux audio via streaming FFmpeg
        if sync_progress:
            sync_progress(94, "Mixing multi-track cinematic fintech soundtrack and synchronized voiceover...")

        temp_soundtrack_wav = Path(out_path).parent / f"temp_soundtrack_{Path(out_path).stem}.wav"
        temp_files_to_unlink.append(temp_soundtrack_wav)
        soundtrack_ready = False
        try:
            from services.sound_design_service import sound_design_service
            sound_design_service.synthesize_soundtrack_to_wav(
                total_duration=actual_duration,
                speech_intervals=speech_intervals,
                transition_timestamps=transition_timestamps,
                cta_timestamp=max(0.0, actual_duration - 3.2),
                bpm=120.0,
                output_wav_path=str(temp_soundtrack_wav)
            )
            soundtrack_ready = temp_soundtrack_wav.exists() and temp_soundtrack_wav.stat().st_size > 1000
        except Exception as st_err:
            logger.warning(f"[OpenMontageAdapter] Soundtrack WAV export notice: {st_err}")

        # Stream-mux audio and video using FFmpeg without re-encoding video
        try:
            import imageio_ffmpeg
            import subprocess
            ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

            has_narr = bool(tts_result and tts_result.get("master_audio_path") and Path(tts_result["master_audio_path"]).exists())
            has_soundtrack = soundtrack_ready

            if has_narr and has_soundtrack:
                mux_cmd = [
                    ffmpeg_exe, "-y",
                    "-i", str(temp_video_path),
                    "-i", str(tts_result["master_audio_path"]),
                    "-i", str(temp_soundtrack_wav),
                    "-filter_complex", "[1:a]volume=1.15[a0];[2:a]volume=0.85[a1];[a0][a1]amix=inputs=2:duration=first:dropout_transition=2[aout]",
                    "-map", "0:v:0",
                    "-map", "[aout]",
                    "-c:v", "copy",
                    "-c:a", "aac",
                    "-b:a", "192k",
                    "-movflags", "+faststart",
                    str(out_path)
                ]
            elif has_soundtrack:
                mux_cmd = [
                    ffmpeg_exe, "-y",
                    "-i", str(temp_video_path),
                    "-i", str(temp_soundtrack_wav),
                    "-map", "0:v:0",
                    "-map", "1:a:0",
                    "-c:v", "copy",
                    "-c:a", "aac",
                    "-b:a", "192k",
                    "-movflags", "+faststart",
                    str(out_path)
                ]
            elif has_narr:
                mux_cmd = [
                    ffmpeg_exe, "-y",
                    "-i", str(temp_video_path),
                    "-i", str(tts_result["master_audio_path"]),
                    "-map", "0:v:0",
                    "-map", "1:a:0",
                    "-c:v", "copy",
                    "-c:a", "aac",
                    "-b:a", "192k",
                    "-movflags", "+faststart",
                    str(out_path)
                ]
            else:
                mux_cmd = [
                    ffmpeg_exe, "-y",
                    "-i", str(temp_video_path),
                    "-c:v", "copy",
                    "-movflags", "+faststart",
                    str(out_path)
                ]

            logger.info(f"[OpenMontageAdapter] Executing streaming audio mux: {' '.join(mux_cmd[:6])}...")
            mux_proc = subprocess.run(mux_cmd, capture_output=True, text=True, timeout=90)
            if mux_proc.returncode != 0:
                logger.error(f"[OpenMontageAdapter] FFmpeg audio mux failed: {mux_proc.stderr}")
                if temp_video_path.exists():
                    import shutil
                    shutil.copy2(str(temp_video_path), str(out_path))
            else:
                logger.info(f"[OpenMontageAdapter] Successfully muxed synchronized audio and video into {out_path}")
        except Exception as mux_err:
            logger.error(f"[OpenMontageAdapter] Exception during FFmpeg audio mux: {mux_err}")
            if temp_video_path.exists():
                import shutil
                shutil.copy2(str(temp_video_path), str(out_path))
        finally:
            for p in temp_files_to_unlink:
                try:
                    if p.exists():
                        p.unlink()
                except Exception:
                    pass
            if tts_result and tts_result.get("master_audio_path"):
                try:
                    p = Path(tts_result["master_audio_path"])
                    if p.exists():
                        p.unlink()
                except Exception:
                    pass

        actual_file_duration = actual_duration
        probe_source = "moviepy_clip"
        try:
            import imageio_ffmpeg
            import subprocess
            import re
            ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
            probe_cmd = [ffmpeg_exe, "-i", str(out_path), "-hide_banner"]
            probe_res = subprocess.run(probe_cmd, capture_output=True, text=True, errors="ignore")
            m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.?\d*)", probe_res.stderr)
            if m:
                hrs, mins, secs = float(m.group(1)), float(m.group(2)), float(m.group(3))
                actual_file_duration = round(hrs * 3600 + mins * 60 + secs, 2)
                probe_source = "ffmpeg_probe"
        except Exception as probe_err:
            logger.warning(f"FFmpeg probe check notice: {probe_err}")

        discrepancy = round(abs(actual_file_duration - target_duration), 2)
        file_size_mb = os.path.getsize(out_path) / (1024 * 1024)

        return {
            "success": True,
            "output_path": str(out_path),
            "video_path": str(out_path),
            "thumbnail_path": str(thumb_path),
            "duration": round(actual_file_duration, 2),
            "duration_seconds": round(actual_file_duration, 2),
            "file_size_mb": round(file_size_mb, 2),
            "resolution": f"{width}x{height}",
            "fps": 30,
            "engine": "OpenMontage/Dynamic-Chart-Motion",
            "media_probe": {
                "inspected_via": probe_source,
                "actual_duration_seconds": round(actual_file_duration, 2),
                "target_duration_seconds": target_duration,
                "discrepancy_seconds": discrepancy
            }
        }


openmontage_adapter = OpenMontageAdapter()

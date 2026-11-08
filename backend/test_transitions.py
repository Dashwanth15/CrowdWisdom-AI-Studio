import numpy as np
from PIL import Image, ImageFilter, ImageDraw, ImageFont
import math
import os

def ease_in_out_cubic(tau: float) -> float:
    """Standard smooth cubic Hermite acceleration curve."""
    tau = max(0.0, min(1.0, tau))
    return tau * tau * (3.0 - 2.0 * tau)

def ease_smootherstep(tau: float) -> float:
    """5th-order smootherstep for zero 1st and 2nd derivatives at endpoints."""
    tau = max(0.0, min(1.0, tau))
    return tau * tau * tau * (tau * (tau * 6.0 - 15.0) + 10.0)

# =====================================================================
# CINEMATIC TRANSITION SHADERS (STAGE 2)
# =====================================================================

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
    h, w, c = frame_a.shape
    eased = ease_smootherstep(tau)
    
    # Velocity curve peaks at tau = 0.5
    velocity = math.sin(math.pi * tau)
    blur_radius = int(velocity * 32.0)  # Up to 32px blur at peak velocity
    
    # Create side-by-side stitch
    if direction == "right":
        # Frame A exits left, Frame B enters from right
        offset = int(eased * w)
        stitched = np.concatenate((frame_a, frame_b), axis=1) # Shape: (h, 2w, 3)
        crop_x = offset
    else:
        # Frame A exits right, Frame B enters from left
        offset = int((1.0 - eased) * w)
        stitched = np.concatenate((frame_b, frame_a), axis=1)
        crop_x = offset

    cropped = stitched[:, crop_x : crop_x + w]
    
    # Apply directional horizontal motion blur proportional to speed
    if blur_radius >= 2:
        pil_crop = Image.fromarray(cropped)
        # Horizontal motion blur simulation via BoxBlur(radius_x, 0)
        # Pillow BoxBlur is isotropic; to do directional blur, resize horizontally down & back up:
        down_w = max(4, int(w / (1.0 + blur_radius * 0.45)))
        blurred = pil_crop.resize((down_w, h), Image.Resampling.BILINEAR).resize((w, h), Image.Resampling.BILINEAR)
        
        # Add subtle exposure bloom flash at peak speed (tau around 0.5)
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
    
    # Base frame switches at tau = 0.5
    base_frame = frame_a if tau < 0.5 else frame_b
    out = base_frame.copy()
    
    # Glitch envelope peaks at tau = 0.5
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
            # Add subtle color tint to the torn slice
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
    Smooth gamma-corrected dissolve washed over by an expanding amber/cyan optical flare.
    """
    h, w, c = frame_a.shape
    
    # 1. Non-linear smooth cross-dissolve
    alpha = ease_smootherstep(tau)
    dissolved = (1.0 - alpha) * frame_a.astype(np.float32) + alpha * frame_b.astype(np.float32)
    
    # 2. Flare envelope: Gaussian peak centered at tau = 0.5
    flare_amp = math.exp(-18.0 * ((tau - 0.5) ** 2)) # in [0, 1]
    
    if flare_amp > 0.02:
        # Generate anamorphic horizontal flare streak entering from top-right
        # Y center moves smoothly downwards
        fy = int(h * (0.2 + 0.3 * tau))
        fx = int(w * (0.8 - 0.6 * tau))
        
        # Fast meshgrid flare
        y_coords = np.arange(h, dtype=np.float32)[:, None]
        x_coords = np.arange(w, dtype=np.float32)[None, :]
        
        # Anamorphic aspect ratio (horizontal streak is 4x wider than tall)
        dy = (y_coords - fy) / (h * 0.18)
        dx = (x_coords - fx) / (w * 0.72)
        dist_sq = dy * dy + dx * dx
        
        # Glow mask
        glow = np.exp(-dist_sq) * flare_amp
        
        # Premium champagne/cyan tint: [R, G, B] = [245, 175, 80] / [56, 189, 248]
        flare_layer = np.zeros((h, w, 3), dtype=np.float32)
        flare_layer[:, :, 0] = glow * 240.0  # Warm amber-gold
        flare_layer[:, :, 1] = glow * 180.0
        flare_layer[:, :, 2] = glow * 120.0
        
        # Screen blend: 255 - (255 - base)*(255 - flare)/255
        inv_base = 255.0 - dissolved
        inv_flare = np.clip(255.0 - flare_layer, 0, 255.0)
        screened = 255.0 - (inv_base * inv_flare / 255.0)
        return np.clip(screened, 0, 255).astype(np.uint8)
        
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
    h, w, c = frame_a.shape
    
    if tau < 0.5:
        # First half: Frame A zooms in from 1.0 to 1.35
        t_half = tau * 2.0  # 0 to 1
        scale = 1.0 + (t_half ** 2.2) * 0.35
        crop_w, crop_h = int(w / scale), int(h / scale)
        x0, y0 = (w - crop_w) // 2, (h - crop_h) // 2
        pil_a = Image.fromarray(frame_a).crop((x0, y0, x0 + crop_w, y0 + crop_h))
        res = pil_a.resize((w, h), Image.Resampling.BILINEAR)
        
        # Subtle flash at the punch point
        if t_half > 0.8:
            flash = (t_half - 0.8) * 150.0
            arr = np.clip(np.array(res).astype(np.float32) + flash, 0, 255).astype(np.uint8)
            return arr
        return np.array(res)
    else:
        # Second half: Frame B snaps in from 0.92 to 1.0 with subtle overshoot
        t_half = (tau - 0.5) * 2.0  # 0 to 1
        # Spring-like curve
        spring = 1.0 - math.exp(-6.0 * t_half) * math.cos(math.pi * t_half) * 0.12
        crop_w, crop_h = int(w * spring), int(h * spring)
        
        pil_b = Image.fromarray(frame_b)
        scaled_b = pil_b.resize((crop_w, crop_h), Image.Resampling.BILINEAR)
        
        # Composite centered onto dark background
        bg = Image.new("RGB", (w, h), (8, 12, 22))
        px = (w - crop_w) // 2
        py = (h - crop_h) // 2
        bg.paste(scaled_b, (px, py))
        return np.array(bg)


def render_luma_dissolve(
    frame_a: np.ndarray,
    frame_b: np.ndarray,
    tau: float
) -> np.ndarray:
    """
    Film-grade Gamma-Corrected Luma Dissolve.
    Avoids muddy midtones by performing cross-dissolve in linear light space (gamma=2.2).
    """
    alpha = ease_smootherstep(tau)
    # Convert from sRGB to Linear space
    lin_a = (frame_a.astype(np.float32) / 255.0) ** 2.2
    lin_b = (frame_b.astype(np.float32) / 255.0) ** 2.2
    
    blended = (1.0 - alpha) * lin_a + alpha * lin_b
    # Back to sRGB
    srgb = (blended ** (1.0 / 2.2)) * 255.0
    return np.clip(srgb, 0, 255).astype(np.uint8)

if __name__ == "__main__":
    print("Testing Cinematic Transition Shaders...")
    # Create two synthetic 1080x1920 test frames
    f_a = np.zeros((1920, 1080, 3), dtype=np.uint8)
    f_a[:, :, 0] = 180  # Crimson
    f_a[:, :, 1] = 20
    f_a[:, :, 2] = 40
    
    f_b = np.zeros((1920, 1080, 3), dtype=np.uint8)
    f_b[:, :, 0] = 20
    f_b[:, :, 1] = 180  # Emerald Cyan
    f_b[:, :, 2] = 220
    
    taus = [0.1, 0.3, 0.5, 0.7, 0.9]
    for name, fn in [
        ("WhipPan", lambda a, b, t: render_whip_pan(a, b, t, "right")),
        ("Glitch", render_digital_glitch),
        ("Bloom", render_optical_bloom),
        ("ZoomPunch", render_zoom_punch),
        ("LumaDissolve", render_luma_dissolve),
    ]:
        print(f"Testing {name} across timeline...")
        for t in taus:
            res = fn(f_a, f_b, t)
            assert res.shape == (1920, 1080, 3), f"Invalid shape: {res.shape}"
            assert res.dtype == np.uint8, f"Invalid dtype: {res.dtype}"
            print(f"  tau={t:.1f}: Mean RGB={res.mean(axis=(0,1))}")
    print("\n✓ ALL 5 CINEMATIC TRANSITION SHADERS VERIFIED!")

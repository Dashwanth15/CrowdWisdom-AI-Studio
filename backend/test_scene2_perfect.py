import os
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont

def render_scene2_test():
    width = 1080
    height = 1920

    # 1. Base dark background
    base = Image.new("RGBA", (width, height), (8, 12, 20, 255))
    draw = ImageDraw.Draw(base)

    # Subtle grid lines
    grid_col = (20, 30, 45)
    for x in range(0, width, 80):
        draw.line([(x, 0), (x, height)], fill=grid_col, width=1)
    for y in range(0, height, 80):
        draw.line([(0, y), (width, y)], fill=grid_col, width=1)

    # 2. Dynamic Candlestick Chart (placed cleanly in middle: y=0.18 to 0.52)
    chart_top = int(height * 0.18)
    chart_bottom = int(height * 0.52)
    chart_h = chart_bottom - chart_top

    # Simulated prices
    prices = [100 + 15 * math.sin(i * 0.3) + (i * 1.2) for i in range(24)]
    min_p, max_p = min(prices) - 5, max(prices) + 5
    p_range = max(1.0, max_p - min_p)

    candle_w = int(width * 0.024)
    space = int(width * 0.014)
    start_x = int(width * 0.06)

    curve_pts = []
    for i in range(20):
        x = start_x + i * (candle_w + space)
        open_p = prices[i]
        close_p = prices[i+1] if i+1 < len(prices) else open_p + 1
        high_p = max(open_p, close_p) + 2.5
        low_p = min(open_p, close_p) - 2.0

        is_bull = close_p >= open_p
        col = (16, 185, 129) if is_bull else (239, 68, 68)

        y_open = int(chart_bottom - ((open_p - min_p) / p_range) * chart_h)
        y_close = int(chart_bottom - ((close_p - min_p) / p_range) * chart_h)
        y_high = int(chart_bottom - ((high_p - min_p) / p_range) * chart_h)
        y_low = int(chart_bottom - ((low_p - min_p) / p_range) * chart_h)

        # Wick
        draw.line([(x + candle_w // 2, y_high), (x + candle_w // 2, y_low)], fill=col, width=2)
        # Body
        draw.rectangle([x, min(y_open, y_close), x + candle_w, max(y_open, y_close) + 2], fill=col)

        # Volume bar (y=0.52 to 0.56)
        vol_h = int((abs(close_p - open_p) / p_range) * (height * 0.04)) + 4
        draw.rectangle([x, int(height * 0.56) - vol_h, x + candle_w, int(height * 0.56)], fill=col)

        curve_pts.append((x + candle_w // 2, y_close))

    # Glow curve
    if len(curve_pts) > 1:
        draw.line(curve_pts, fill=(56, 189, 248), width=3)
        lx, ly = curve_pts[-1]
        draw.ellipse([lx - 6, ly - 6, lx + 6, ly + 6], fill=(56, 189, 248))

    # 3. Telemetry HUD (Cleanly separated at y=0.60 to 0.70)
    hud_y = int(height * 0.60)
    hud_h = int(height * 0.10)
    hud_overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    h_draw = ImageDraw.Draw(hud_overlay)
    h_draw.rounded_rectangle(
        [int(width * 0.06), hud_y, int(width * 0.94), hud_y + hud_h],
        radius=14,
        fill=(12, 18, 30, 230),
        outline=(56, 189, 248, 160),
        width=1
    )
    base = Image.alpha_composite(base, hud_overlay)
    draw = ImageDraw.Draw(base)

    font_hud_title = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 26)
    font_hud_val = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 36)
    draw.text((int(width * 0.10), hud_y + 14), "CROWDPULSE™ REAL-TIME CONVICTION RADAR", fill=(148, 163, 184), font=font_hud_title)
    draw.text((int(width * 0.10), hud_y + 48), "+78.4% INSTITUTIONAL BULLISH CONVICTION", fill=(16, 185, 129), font=font_hud_val)

    # 4. Kinetic Subtitles (Cleanly placed at y=0.76 to 0.84)
    words = ["hesitation", "costs", "you.", "Find"]
    active_idx = 1  # "costs" is active

    font_w = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 38)
    font_a = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 40)

    space_w = 16
    items = []
    for idx, w in enumerate(words):
        f = font_a if idx == active_idx else font_w
        bbox = f.getbbox(w)
        w_len = bbox[2] - bbox[0]
        items.append((w, idx == active_idx, w_len, f))

    tot_w = sum(it[2] for it in items) + (len(items) - 1) * space_w
    card_w = min(int(width * 0.90), max(int(width * 0.65), tot_w + 64))
    card_h = 96
    card_x = (width - card_w) // 2
    card_y = int(height * 0.76)

    card_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    c_draw = ImageDraw.Draw(card_layer)
    c_draw.rounded_rectangle(
        [card_x, card_y, card_x + card_w, card_y + card_h],
        radius=18,
        fill=(10, 16, 28, 235),
        outline=(56, 189, 248, 180),
        width=2
    )

    cur_x = card_x + (card_w - tot_w) // 2
    text_y = card_y + (card_h - 40) // 2 - 2

    for w, is_act, w_l, f in items:
        if is_act:
            c_draw.rounded_rectangle(
                [cur_x - 12, text_y - 6, cur_x + w_l + 12, text_y + 42],
                radius=8,
                fill=(37, 99, 235, 200),
                outline=(56, 189, 248, 255),
                width=2
            )
        cur_x += w_l + space_w

    base = Image.alpha_composite(base, card_layer)
    draw = ImageDraw.Draw(base)

    cur_x = card_x + (card_w - tot_w) // 2
    for w, is_act, w_l, f in items:
        if is_act:
            draw.text((cur_x + 1, text_y + 2), w, fill=(0, 0, 0, 240), font=f)
            draw.text((cur_x, text_y), w, fill=(255, 255, 255, 255), font=f)
        else:
            draw.text((cur_x + 1, text_y + 1), w, fill=(0, 0, 0, 180), font=f)
            draw.text((cur_x, text_y), w, fill=(225, 235, 248, 255), font=f)
        cur_x += w_l + space_w

    # 5. Top Header HUD (y=0.04)
    top_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    t_draw = ImageDraw.Draw(top_layer)
    # Brand Chip
    t_draw.rounded_rectangle([int(width * 0.06), int(height * 0.04), int(width * 0.46), int(height * 0.075)], radius=10, fill=(10, 16, 26, 220), outline=(56, 189, 248, 140), width=1)
    t_draw.ellipse([int(width * 0.08), int(height * 0.053), int(width * 0.08) + 14, int(height * 0.053) + 14], fill=(16, 185, 129))
    font_brand = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 24)
    t_draw.text((int(width * 0.11), int(height * 0.048)), "CROWDWISDOM TRADING", fill=(240, 246, 255), font=font_brand)

    # Scene Chip
    t_draw.rounded_rectangle([int(width * 0.70), int(height * 0.04), int(width * 0.94), int(height * 0.075)], radius=10, fill=(10, 16, 26, 220), outline=(71, 85, 105, 140), width=1)
    font_scene = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 22)
    t_draw.text((int(width * 0.74), int(height * 0.049)), "SCENE 02 / 04", fill=(148, 163, 184), font=font_scene)

    base = Image.alpha_composite(base, top_layer)
    draw = ImageDraw.Draw(base)

    # Footer
    font_foot = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 22)
    draw.text((int(width * 0.06), int(height * 0.94)), "CrowdWisdomTrading.com • Collective Market Intelligence", fill=(120, 140, 165), font=font_foot)

    base.convert("RGB").save("test_scene2_perfect.jpg", quality=95)
    print("Saved test_scene2_perfect.jpg")

if __name__ == "__main__":
    render_scene2_test()


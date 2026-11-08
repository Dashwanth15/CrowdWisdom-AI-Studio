import os
from PIL import Image, ImageDraw, ImageFont

def test_caption():
    width = 1080
    height = 1920
    canvas = Image.new("RGBA", (width, height), (15, 20, 30, 255))
    draw = ImageDraw.Draw(canvas)

    # Gradient backdrop simulation
    for y in range(int(height * 0.6), height):
        a = int(220 * ((y - height * 0.6) / (height * 0.4)))
        draw.line([(0, y), (width, y)], fill=(8, 12, 20, a))

    # Load bold fonts
    font_word = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 40)
    font_active = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 42)

    words = ["tweets.", "Infinite", "noise.", "You're"]
    active_idx = 2  # "noise." is active

    # Measure words
    space_w = 16
    items = []
    for idx, w in enumerate(words):
        f = font_active if idx == active_idx else font_word
        bbox = f.getbbox(w)
        w_len = bbox[2] - bbox[0]
        h_len = bbox[3] - bbox[1]
        items.append((w, idx == active_idx, w_len, h_len, f))

    tot_w = sum(it[2] for it in items) + (len(items) - 1) * space_w
    card_w = min(int(width * 0.90), max(int(width * 0.65), tot_w + 64))
    card_h = 100
    card_x = (width - card_w) // 2
    card_y = int(height * 0.78)

    # 1. Sleek Lower-Third Card Backdrop
    card_overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    c_draw = ImageDraw.Draw(card_overlay)
    c_draw.rounded_rectangle(
        [card_x, card_y, card_x + card_w, card_y + card_h],
        radius=20,
        fill=(10, 15, 25, 230),
        outline=(56, 189, 248, 160),
        width=2
    )

    # 2. Draw Active Word Pill Background (FIRST, BEFORE TEXT!)
    cur_x = card_x + (card_w - tot_w) // 2
    cur_y = card_y + (card_h - 48) // 2

    for w, is_act, w_l, h_l, f in items:
        if is_act:
            pill_pad_x = 12
            pill_pad_y = 6
            c_draw.rounded_rectangle(
                [cur_x - pill_pad_x, cur_y - pill_pad_y, cur_x + w_l + pill_pad_x, cur_y + 44 + pill_pad_y],
                radius=10,
                fill=(37, 99, 235, 180),  # Royal blue glow pill
                outline=(56, 189, 248, 255),  # Electric cyan stroke
                width=2
            )
        cur_x += w_l + space_w

    # Composite card overlay onto canvas
    canvas = Image.alpha_composite(canvas, card_overlay)
    draw = ImageDraw.Draw(canvas)

    # 3. Draw Text ON TOP of everything with dark drop-shadow for 100% clarity
    cur_x = card_x + (card_w - tot_w) // 2
    for w, is_act, w_l, h_l, f in items:
        if is_act:
            # Drop shadow
            draw.text((cur_x + 1, cur_y + 2), w, fill=(0, 0, 0, 240), font=f)
            # Glowing bright text
            draw.text((cur_x, cur_y), w, fill=(255, 255, 255, 255), font=f)
        else:
            # Standard word
            draw.text((cur_x + 1, cur_y + 1), w, fill=(0, 0, 0, 180), font=f)
            draw.text((cur_x, cur_y), w, fill=(210, 225, 245, 255), font=f)
        cur_x += w_l + space_w

    canvas.convert("RGB").save("test_perfect_caption.jpg", quality=95)
    print("Saved test_perfect_caption.jpg")

if __name__ == "__main__":
    test_caption()


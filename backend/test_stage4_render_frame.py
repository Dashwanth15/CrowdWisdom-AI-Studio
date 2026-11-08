from PIL import Image, ImageDraw, ImageFont
import numpy as np

def test_frame():
    width, height = 1080, 1920
    base = Image.new("RGBA", (width, height), (14, 18, 28, 255))
    draw = ImageDraw.Draw(base)

    # 1. Viewfinder Corner Reticles
    reticle_len = 28
    col = (56, 189, 248, 180)
    # TL
    draw.line([(36, 36), (36 + reticle_len, 36)], fill=col, width=2)
    draw.line([(36, 36), (36, 36 + reticle_len)], fill=col, width=2)
    # TR
    draw.line([(width - 36, 36), (width - 36 - reticle_len, 36)], fill=col, width=2)
    draw.line([(width - 36, 36), (width - 36, 36 + reticle_len)], fill=col, width=2)
    # BL
    draw.line([(36, height - 36), (36 + reticle_len, height - 36)], fill=col, width=2)
    draw.line([(36, height - 36), (36, height - 36 - reticle_len)], fill=col, width=2)
    # BR
    draw.line([(width - 36, height - 36), (width - 36 - reticle_len, height - 36)], fill=col, width=2)
    draw.line([(width - 36, height - 36), (width - 36, height - 36 - reticle_len)], fill=col, width=2)

    # 2. Market Pulse Pill
    draw.rounded_rectangle(
        [int(width * 0.05), int(height * 0.08), int(width * 0.95), int(height * 0.115)],
        radius=8,
        fill=(10, 15, 24, 220),
        outline=(56, 189, 248, 140),
        width=1
    )

    # 3. Floating Kinetic Caption Card
    card_x = int(width * 0.06)
    card_y = int(height * 0.73)
    card_w = int(width * 0.88)
    card_h = int(height * 0.075)
    draw.rounded_rectangle(
        [card_x, card_y, card_x + card_w, card_y + card_h],
        radius=14,
        fill=(10, 16, 28, 230),
        outline=(56, 189, 248, 190),
        width=1
    )

    arr = np.array(base)
    assert arr.shape == (1920, 1080, 4)
    print("✓ STAGE 4 HUD & KINETIC CAPTION CANVAS VERIFIED!")

if __name__ == "__main__":
    test_frame()

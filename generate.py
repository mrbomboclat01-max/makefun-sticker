#!/usr/bin/env python3
"""Local-only sticker generator — produces entry.png using Pillow.
   main.py (stdlib only) just copies entry.png into /output."""

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math, os

SIZE = 1024
CX = CY = SIZE // 2

# Solana brand palette
S_GREEN  = (20, 241, 149)   # #14F195
S_PURPLE = (153, 69, 255)   # #9945FF
S_TEAL   = (0, 194, 220)
DARK     = (8, 9, 26)
WHITE    = (255, 255, 255)
CREAM    = (220, 230, 240)


def load_font(size, bold=False):
    for path in [
        "C:/Windows/Fonts/consolab.ttf" if bold else "C:/Windows/Fonts/consola.ttf",
        "C:/Windows/Fonts/ariblk.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/impact.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
    ]:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            pass
    return ImageFont.load_default()


def horiz_gradient(w, h, c1, c2):
    img = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(img)
    for x in range(w):
        t = x / max(w - 1, 1)
        col = tuple(int(c1[i] * (1 - t) + c2[i] * t) for i in range(3))
        d.line([(x, 0), (x, h)], fill=col)
    return img


def paste_gradient_text(canvas, text, pos, font, c1, c2, anchor="mm"):
    """Render text with a horizontal gradient fill onto canvas (RGBA)."""
    tmp = Image.new("L", (SIZE, SIZE), 0)
    ImageDraw.Draw(tmp).text(pos, text, fill=255, font=font, anchor=anchor)
    bb = tmp.getbbox()
    if not bb:
        return canvas
    w, h = bb[2] - bb[0], bb[3] - bb[1]
    grad = horiz_gradient(w, h, c1, c2).convert("RGBA")
    grad.putalpha(tmp.crop(bb))
    canvas.paste(grad, (bb[0], bb[1]), grad)
    return canvas


def glow_text(canvas, text, pos, font, color, blur=20, passes=3, anchor="mm"):
    """Add a soft neon glow behind text."""
    layer = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    ImageDraw.Draw(layer).text(pos, text, fill=color + (180,), font=font, anchor=anchor)
    blurred = layer.filter(ImageFilter.GaussianBlur(blur))
    for _ in range(passes):
        canvas = Image.alpha_composite(canvas, blurred)
    return canvas


def create_sticker():
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # 1. Dark circular background
    d.ellipse((0, 0, SIZE - 1, SIZE - 1), fill=DARK + (255,))

    # 2. Radial purple bloom at centre
    bloom = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    bd = ImageDraw.Draw(bloom)
    for r in range(380, 0, -4):
        t = 1 - r / 380
        a = int(60 * t ** 2.2)
        bd.ellipse((CX - r, CY - r, CX + r, CY + r), fill=S_PURPLE + (a,))
    img = Image.alpha_composite(img, bloom)
    d = ImageDraw.Draw(img)

    # 3. Fine dot grid
    for gx in range(0, SIZE, 52):
        for gy in range(0, SIZE, 52):
            dist = math.hypot(gx - CX, gy - CY)
            if dist < 490:
                a = max(0, int(22 - dist * 0.022))
                d.ellipse((gx - 1, gy - 1, gx + 1, gy + 1), fill=S_GREEN + (a,))

    # 4. Load + auto-size font so "make" fits in ~760 px wide
    TARGET_W = 760
    for sz in range(260, 60, -4):
        f_big = load_font(sz, bold=True)
        probe = Image.new("L", (SIZE, SIZE), 0)
        ImageDraw.Draw(probe).text((CX, CY), "make", fill=255, font=f_big, anchor="mm")
        bb = probe.getbbox()
        if bb and (bb[2] - bb[0]) <= TARGET_W:
            break
    f_tag   = load_font(40)
    f_small = load_font(28)

    # 5. Measure text heights for layout
    def text_height(text, font):
        p = Image.new("L", (SIZE, SIZE), 0)
        ImageDraw.Draw(p).text((CX, CY), text, fill=255, font=font, anchor="mm")
        bb = p.getbbox()
        return (bb[3] - bb[1]) if bb else 0

    h_make = text_height("make", f_big)
    h_fun  = text_height(".fun",  f_big)
    gap    = 10
    block_h = h_make + gap + h_fun
    # Centre the text block slightly above centre (room for tagline)
    y_make = CY - 70 - block_h // 2 + h_make // 2
    y_fun  = y_make + h_make // 2 + gap + h_fun // 2

    # 6. Neon glow passes
    img = glow_text(img, "make", (CX, y_make), f_big, S_GREEN,  blur=22, passes=3)
    img = glow_text(img, ".fun",  (CX, y_fun),  f_big, S_PURPLE, blur=22, passes=3)

    # 7. Gradient fills: "make" green→purple, ".fun" purple→green
    img = paste_gradient_text(img, "make", (CX, y_make), f_big, S_GREEN,  S_PURPLE, "mm")
    img = paste_gradient_text(img, ".fun",  (CX, y_fun),  f_big, S_PURPLE, S_GREEN,  "mm")
    d = ImageDraw.Draw(img)

    # 8. Small horizontal accent line between words
    sep_y = (y_make + h_make // 2 + y_fun - h_fun // 2) // 2
    d.line([(CX - 160, sep_y), (CX + 160, sep_y)], fill=CREAM + (35,), width=1)

    # 9. Tagline
    tag_y  = y_fun + h_fun // 2 + 58
    d.text((CX, tag_y),      "ai agents · earn usdc",  fill=S_TEAL  + (220,), font=f_tag,   anchor="mm")
    d.text((CX, tag_y + 50), "build on solana",        fill=CREAM   + (120,), font=f_small, anchor="mm")

    # 10. Glowing ring border
    glow_ring = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    grd = ImageDraw.Draw(glow_ring)
    for step in range(18, 0, -1):
        a = int(100 * step / 18)
        exp = step * 2
        grd.ellipse((exp, exp, SIZE - 1 - exp, SIZE - 1 - exp), outline=S_GREEN + (a,))
    img = Image.alpha_composite(img, glow_ring.filter(ImageFilter.GaussianBlur(6)))
    d = ImageDraw.Draw(img)
    d.ellipse((8, 8, SIZE - 9, SIZE - 9), outline=WHITE + (55,), width=2)

    # 11. Circular sticker mask
    mask = Image.new("L", (SIZE, SIZE), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, SIZE - 1, SIZE - 1), fill=255)
    img.putalpha(mask)
    return img


if __name__ == "__main__":
    os.makedirs("C:/output", exist_ok=True)
    img = create_sticker()
    img.save("C:/output/entry.png", "PNG")
    img.save("C:/Users/Mstr.Erisa/Documents/stickerentry/entry.png", "PNG")
    size = os.path.getsize("C:/output/entry.png")
    print(f"Saved — {size/1024:.1f} KB")

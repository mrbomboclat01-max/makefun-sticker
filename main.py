#!/usr/bin/env python3
"""make.fun sticker: Terminal Agent — 1024×1024 PNG, deterministic"""

import os
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

SIZE = 1024
CX = CY = SIZE // 2

DARK_BG   = (6, 8, 16, 255)
TERM_BG   = (10, 14, 10, 255)
TBAR_BG   = (18, 26, 18, 255)
GREEN     = (0, 255, 65, 255)
GREEN2    = (0, 200, 50, 255)
GREEN_DIM = (0, 100, 30, 200)
CYAN      = (0, 230, 255, 220)
WHITE     = (240, 245, 240, 255)
DIMGRAY   = (60, 80, 60, 200)
YELLOW    = (180, 255, 100, 220)


def load_font(size, bold=False):
    b, r = "Bold", "Regular"
    candidates = [
        # Linux
        f"/usr/share/fonts/truetype/liberation/LiberationMono-{b if bold else r}.ttf",
        f"/usr/share/fonts/truetype/dejavu/DejaVuSansMono{'-Bold' if bold else ''}.ttf",
        f"/usr/share/fonts/truetype/ubuntu/UbuntuMono-{'B' if bold else 'R'}.ttf",
        f"/usr/share/fonts/truetype/freefont/FreeMono{'Bold' if bold else ''}.ttf",
        # Windows
        "C:/Windows/Fonts/consolab.ttf" if bold else "C:/Windows/Fonts/consola.ttf",
        "C:/Windows/Fonts/courbd.ttf"   if bold else "C:/Windows/Fonts/cour.ttf",
        # macOS
        "/System/Library/Fonts/Monaco.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            pass
    return ImageFont.load_default()


def hex_points(cx, cy, r):
    return [
        (cx + r * math.cos(math.pi / 6 + math.pi / 3 * i),
         cy + r * math.sin(math.pi / 6 + math.pi / 3 * i))
        for i in range(6)
    ]


def make_glow_layer(draw_fn, blur_px):
    layer = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw_fn(ImageDraw.Draw(layer))
    return layer.filter(ImageFilter.GaussianBlur(blur_px))


def create_sticker():
    canvas = Image.new("RGBA", (SIZE, SIZE), DARK_BG)
    d = ImageDraw.Draw(canvas)

    # 1 ── Radial purple vignette ─────────────────────────────────────────
    for r in range(480, 0, -4):
        v = int(28 * (1 - r / 480) ** 2)
        d.ellipse((CX - r, CY - r, CX + r, CY + r), outline=(v, v // 2, v * 2))

    # 2 ── Subtle circuit-board grid ──────────────────────────────────────
    for x in range(0, SIZE, 64):
        d.line([(x, 0), (x, SIZE)], fill=(0, 35, 15, 30))
    for y in range(0, SIZE, 64):
        d.line([(0, y), (SIZE, y)], fill=(0, 35, 15, 30))
    for gx in range(0, SIZE, 64):
        for gy in range(0, SIZE, 64):
            if math.hypot(gx - CX, gy - CY) < 490:
                a = max(0, int(50 - math.hypot(gx - CX, gy - CY) * 0.07))
                d.ellipse((gx - 2, gy - 2, gx + 2, gy + 2), fill=(0, 100, 50, a))

    # 3 ── Hexagonal border with glow ─────────────────────────────────────
    for step in range(20, 0, -1):
        a = int(90 * step / 20)
        pts = hex_points(CX, CY, 468 + step * 3)
        gl = make_glow_layer(
            lambda dw, p=pts, al=a: dw.polygon(p, outline=(0, 255, 65, al)),
            blur_px=5,
        )
        canvas = Image.alpha_composite(canvas, gl)
    d = ImageDraw.Draw(canvas)
    d.polygon(hex_points(CX, CY, 468), outline=GREEN, width=4)
    d.polygon(hex_points(CX, CY, 456), outline=GREEN2, width=2)
    for px, py in hex_points(CX, CY, 468):
        d.ellipse((px - 6, py - 6, px + 6, py + 6), fill=GREEN)

    # 4 ── Terminal window ─────────────────────────────────────────────────
    TX0, TY0 = 92, 158
    TX1, TY1 = 932, 630
    TBAR = 42

    d.rectangle((TX0, TY0, TX1, TY1), fill=TERM_BG)
    d.rectangle((TX0, TY0, TX1, TY0 + TBAR), fill=TBAR_BG)
    for i, col in enumerate([(255, 95, 86, 255), (255, 189, 46, 255), (39, 201, 63, 255)]):
        bx = TX0 + 18 + i * 26
        d.ellipse((bx, TY0 + 13, bx + 16, TY0 + 29), fill=col)
    f_title = load_font(18)
    d.text(
        ((TX0 + TX1) // 2, TY0 + TBAR // 2),
        "agent@make.fun:~",
        fill=(90, 160, 90, 220),
        font=f_title,
        anchor="mm",
    )
    d.rectangle((TX0, TY0, TX1, TY1), outline=GREEN_DIM, width=2)

    # 5 ── Terminal content ────────────────────────────────────────────────
    f_code = load_font(31)
    f_bold = load_font(33, bold=True)

    rows = [
        (DIMGRAY, f_code, "  # AI agent · bounty hunter"),
        (GREEN,   f_bold, "  $ make fun"),
        None,
        (CYAN,    f_code, "  > solana connected    [OK]"),
        (CYAN,    f_code, "  > bounty: sticker     [OK]"),
        (YELLOW,  f_code, "  > reward: $250 USDC  [SOL]"),
        None,
        (GREEN,   f_bold, "  > MAKING FUN..."),
    ]

    ty = TY0 + TBAR + 18
    LH = 46
    for row in rows:
        if row is None:
            ty += LH // 2
            continue
        color, font, text = row
        if font is f_bold:
            gl = make_glow_layer(
                lambda dw, t=text, f=font, c=color, y=ty: dw.text((TX0, y), t, fill=c, font=f),
                blur_px=10,
            )
            canvas = Image.alpha_composite(canvas, gl)
            d = ImageDraw.Draw(canvas)
        d.text((TX0, ty), text, fill=color, font=font)
        ty += LH

    # 6 ── make.fun brand with glow ────────────────────────────────────────
    f_brand = load_font(100, bold=True)
    f_sub   = load_font(28)

    brand_x, brand_y = CX, 652
    gl = make_glow_layer(
        lambda dw: dw.text(
            (brand_x, brand_y), "make.fun",
            fill=(0, 255, 65, 230), font=f_brand, anchor="mt"
        ),
        blur_px=18,
    )
    for _ in range(3):
        canvas = Image.alpha_composite(canvas, gl)
    d = ImageDraw.Draw(canvas)
    d.text((brand_x, brand_y), "make.fun", fill=WHITE, font=f_brand, anchor="mt")
    d.text((CX, 772), "earn usdc  ·  build on solana", fill=CYAN, font=f_sub, anchor="mt")

    # 7 ── CRT scan lines ─────────────────────────────────────────────────
    scan = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    sd = ImageDraw.Draw(scan)
    for ys in range(0, SIZE, 3):
        sd.line([(0, ys), (SIZE, ys)], fill=(0, 0, 0, 22))
    canvas = Image.alpha_composite(canvas, scan)

    # 8 ── Circular sticker mask ───────────────────────────────────────────
    mask = Image.new("L", (SIZE, SIZE), 0)
    ImageDraw.Draw(mask).ellipse((4, 4, SIZE - 5, SIZE - 5), fill=255)
    canvas.putalpha(mask)

    return canvas


os.makedirs("/output", exist_ok=True)
img = create_sticker()
img.save("/output/entry.png", "PNG")
print("Saved /output/entry.png")

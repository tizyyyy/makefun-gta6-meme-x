#!/usr/bin/env python3
"""Generate three Vice City style memes for the GTA 6 meme entry.

Everything is drawn with Pillow primitives.  The only picture loaded
from disk is the official make.fun mark that lives in assets/press/.
Output files land in memes/ next to this script.
"""

import math
import os
import random

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
MARK_PATH = os.path.join(HERE, "assets", "press", "mark-1024.png")
OUT_DIR = os.path.join(HERE, "memes")
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

SIZE = 1024
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
MAGENTA = (255, 63, 158)
GOLD = (255, 209, 102)
PALM_INK = (12, 6, 26)
LIGHT_BLUE = (165, 216, 255)


# ---------------------------------------------------------------- helpers

def _mix(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def gradient_image(width, height, stops):
    """Vertical gradient.  stops = [(pos0..1, (r,g,b)), ...] sorted."""
    img = Image.new("RGB", (width, height))
    px = img.load()
    for y in range(height):
        pos = y / max(1, height - 1)
        left = stops[0]
        right = stops[-1]
        for i in range(len(stops) - 1):
            if stops[i][0] <= pos <= stops[i + 1][0]:
                left, right = stops[i], stops[i + 1]
                break
        span = right[0] - left[0]
        t = 0.0 if span == 0 else (pos - left[0]) / span
        colour = _mix(left[1], right[1], t)
        for x in range(width):
            px[x, y] = colour
    return img


def paste_mark(base, centre, size, glow_colour=(255, 63, 158), glow_scale=1.35):
    """Paste the official mark centred at `centre`, over a soft glow.

    The glow is drawn on a full-canvas layer and blurred there, so its
    falloff is a clean disc with no square edge from a small tile.
    """
    cx, cy = centre
    glow_d = int(size * glow_scale)
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(overlay)
    gd.ellipse([cx - glow_d // 2, cy - glow_d // 2,
                cx + glow_d // 2, cy + glow_d // 2],
               fill=glow_colour + (165,))
    overlay = overlay.filter(ImageFilter.GaussianBlur(glow_d // 5))
    base.paste(overlay, (0, 0), overlay)

    mark = Image.open(MARK_PATH).convert("RGBA")
    mark = mark.resize((size, size), Image.LANCZOS)
    base.paste(mark, (cx - size // 2, cy - size // 2), mark)


def draw_palm(draw, base_x, base_y, height, lean):
    """One palm: bent trunk, drooping fronds and two coconuts.

    lean is positive when the crown bends to the right.
    """
    pts = []
    steps = 24
    for i in range(steps + 1):
        t = i / steps
        x = base_x + lean * (t * t)
        y = base_y - height * t
        pts.append((x, y))
    for i in range(len(pts) - 1):
        w = max(3, int(14 * (1 - i / steps) + 3))
        draw.line([pts[i], pts[i + 1]], fill=PALM_INK, width=w)
    top_x, top_y = pts[-1]

    frond_angles = [-165, -125, -85, -45, -10, 25]
    for ang in frond_angles:
        rad = math.radians(ang)
        length = height * 0.42
        frond = []
        for i in range(13):
            t = i / 12
            fx = top_x + math.cos(rad) * length * t
            fy = top_y + math.sin(rad) * length * t + 88 * (t * t)
            frond.append((fx, fy))
        draw.line(frond, fill=PALM_INK, width=6)
    draw.ellipse([top_x - 15, top_y - 4, top_x + 3, top_y + 14], fill=PALM_INK)
    draw.ellipse([top_x + 2, top_y + 2, top_x + 20, top_y + 20], fill=PALM_INK)


def draw_skyline(draw, baseline, seed, max_h=190):
    """Seeded row of dark buildings with a few lit windows."""
    rng = random.Random(seed)
    x = -10
    while x < SIZE + 10:
        w = rng.randint(52, 118)
        h = rng.randint(50, max_h)
        shade = rng.randint(14, 34)
        colour = (shade, shade // 2 + 6, shade + 22)
        draw.rectangle([x, baseline - h, x + w, baseline], fill=colour)
        # windows
        for wy in range(baseline - h + 10, baseline - 12, 18):
            for wx in range(x + 8, x + w - 8, 16):
                if rng.random() < 0.28:
                    wc = (255, 214, 120) if rng.random() < 0.7 else (120, 230, 255)
                    draw.rectangle([wx, wy, wx + 6, wy + 8], fill=wc)
        x += w + rng.randint(4, 18)


def draw_grid_floor(draw, top_y, vp_x=512):
    """Dark ground plus a magenta perspective grid under top_y."""
    draw.rectangle([0, top_y, SIZE, SIZE], fill=(22, 6, 38))
    # horizontal lines, closer together near the horizon
    y = float(top_y)
    gap = 10.0
    while y < SIZE:
        draw.line([(0, y), (SIZE, y)], fill=MAGENTA, width=2)
        y += gap
        gap *= 1.32
    # lines fanning out from the vanishing point
    for bx in range(-SIZE, SIZE * 2 + 1, 128):
        draw.line([(vp_x, top_y), (bx, SIZE)], fill=MAGENTA, width=2)


def _font(px):
    return ImageFont.truetype(FONT_PATH, px)


def _fit(draw, text, max_width, start_px):
    px = start_px
    while px > 12:
        f = _font(px)
        if draw.textlength(text, font=f) <= max_width:
            return f, px
        px -= 2
    return _font(px), px


def caption_line(draw, cx, baseline_y, text, start_px, max_width=940,
                 fill=WHITE):
    """One centred caption line, baseline anchored.  Returns its size."""
    f, px = _fit(draw, text, max_width, start_px)
    draw.text((cx, baseline_y), text, font=f, fill=fill, anchor="ms",
              stroke_width=max(3, px // 11), stroke_fill=BLACK)
    return px


def rich_line(draw, cx, baseline_y, segments, start_px, max_width=940):
    """Centred line built from (text, colour) segments, baseline anchored."""
    plain = "".join(t for t, _ in segments)
    f, px = _fit(draw, plain, max_width, start_px)
    total = draw.textlength(plain, font=f)
    x = cx - total / 2
    sw = max(3, px // 11)
    for text, colour in segments:
        draw.text((x, baseline_y), text, font=f, fill=colour, anchor="ls",
                  stroke_width=sw, stroke_fill=BLACK)
        x += draw.textlength(text, font=f)
    return px


# ---------------------------------------------------------------- scene A

def scene_a():
    img = gradient_image(SIZE, SIZE, [
        (0.0, (38, 8, 74)),
        (0.45, (148, 32, 128)),
        (0.72, (255, 94, 98)),
        (1.0, (255, 158, 64)),
    ])
    paste_mark(img, (512, 392), 428)
    draw = ImageDraw.Draw(img)
    draw_skyline(draw, 716, seed=11)
    draw_grid_floor(draw, 716)
    # redraw skyline silhouette edge over the floor seam is not needed;
    # palms sit on top of everything scenic
    draw_palm(draw, 58, 880, 430, 95)
    draw_palm(draw, 972, 890, 455, -100)

    draw = ImageDraw.Draw(img)
    s = caption_line(draw, 512, 78, "13 YEARS I WAITED", 66)
    caption_line(draw, 512, 78 + s + 14, "FOR GTA 6", 66)
    s = caption_line(draw, 512, 872, "MY AI AGENT ALREADY", 56)
    rich_line(draw, 512, 872 + s + 12,
              [("GOT PAID ON ", WHITE), ("make.fun", MAGENTA)], 56)
    img.save(os.path.join(OUT_DIR, "meme-a.png"))


# ---------------------------------------------------------------- scene B

def scene_b():
    img = Image.new("RGB", (SIZE, SIZE))
    top = gradient_image(SIZE, 560, [
        (0.0, (4, 6, 24)),
        (0.7, (22, 24, 68)),
        (1.0, (44, 36, 102)),
    ])
    img.paste(top, (0, 0))
    bottom = gradient_image(SIZE, SIZE - 560, [
        (0.0, (196, 44, 132)),
        (1.0, (255, 158, 64)),
    ])
    img.paste(bottom, (0, 560))

    draw = ImageDraw.Draw(img)
    rng = random.Random(42)
    for _ in range(200):
        sx, sy = rng.randint(0, SIZE - 1), rng.randint(0, 540)
        r = rng.choice([1, 1, 1, 2])
        draw.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(230, 238, 255))

    paste_mark(img, (806, 168), 288, glow_colour=(190, 215, 255),
               glow_scale=1.3)
    draw = ImageDraw.Draw(img)

    caption_line(draw, 215, 74, "ME AT 3 AM:", 58)
    # sleeping Zs drifting up to the right
    zx, zy, zp = 120, 300, 44
    for i in range(3):
        f = _font(zp)
        draw.text((zx, zy), "Z", font=f, fill=LIGHT_BLUE, anchor="ms",
                  stroke_width=3, stroke_fill=BLACK)
        zx += 74
        zy -= 72
        zp += 26

    # bottom panel
    draw.rectangle([0, 556, SIZE, 564], fill=BLACK)
    draw_skyline(draw, 856, seed=23, max_h=120)
    paste_mark(img, (512, 742), 196, glow_scale=1.25)
    draw = ImageDraw.Draw(img)
    draw_palm(draw, 52, 990, 300, 70)
    draw_palm(draw, 976, 990, 310, -72)

    s = rich_line(draw, 512, 908,
                  [("MY AGENT ON ", WHITE), ("make.fun", MAGENTA),
                   (":", WHITE)], 54)
    caption_line(draw, 512, 908 + s + 10, "STILL WINNING BOUNTIES", 54,
                 fill=GOLD)
    img.save(os.path.join(OUT_DIR, "meme-b.png"))


# ---------------------------------------------------------------- scene C

def _calendar_layer():
    w, h = 330, 372
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle([6, 26, w - 6, h - 6], radius=22,
                        fill=(250, 248, 242, 255), outline=(30, 30, 30, 255),
                        width=4)
    d.rounded_rectangle([6, 26, w - 6, 106], radius=22,
                        fill=(214, 40, 57, 255))
    d.rectangle([6, 76, w - 6, 106], fill=(214, 40, 57, 255))
    f_head = _font(44)
    d.text((w / 2, 88), "NOV", font=f_head, fill=WHITE, anchor="ms")
    f_big = _font(150)
    d.text((w / 2, 268), "19", font=f_big, fill=(24, 20, 32), anchor="ms")
    f_foot = _font(36)
    d.text((w / 2, 344), "GTA 6 DAY", font=f_foot, fill=(214, 40, 57),
           anchor="ms")
    for ring_x in (78, w - 78):
        d.rounded_rectangle([ring_x - 11, 0, ring_x + 11, 52], radius=10,
                            fill=(18, 18, 22, 255))
    return layer


def scene_c():
    img = gradient_image(SIZE, SIZE, [
        (0.0, (16, 24, 84)),
        (0.5, (104, 44, 148)),
        (0.78, (232, 84, 108)),
        (1.0, (255, 158, 64)),
    ])
    paste_mark(img, (726, 356), 372)
    draw = ImageDraw.Draw(img)
    draw_skyline(draw, 724, seed=37)
    draw_grid_floor(draw, 724)
    draw = ImageDraw.Draw(img)
    draw_palm(draw, 966, 900, 430, -92)
    draw_palm(draw, 42, 880, 360, 80)

    cal = _calendar_layer()
    cal = cal.rotate(9, expand=True, resample=Image.BICUBIC)
    img.paste(cal, (36, 356), cal)

    draw = ImageDraw.Draw(img)
    s = caption_line(draw, 512, 76, "GTA 6 RELEASE DAY:", 62)
    caption_line(draw, 512, 76 + s + 14, "EVERYONE CALLED IN SICK", 62)
    s = caption_line(draw, 512, 868, "MY AGENT COULDN'T. IT WAS BUSY", 52)
    rich_line(draw, 512, 868 + s + 12,
              [("EARNING MY COPY ON ", WHITE), ("make.fun", MAGENTA)], 52)
    img.save(os.path.join(OUT_DIR, "meme-c.png"))


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    scene_a()
    scene_b()
    scene_c()
    print("wrote meme-a.png, meme-b.png, meme-c.png")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Compose the front page for THE WORLD TODAY — Friday 20 November 2026.

Build-time only: draws the whole 1024x1024 PNG with PIL and real fonts,
then saves it as entry.png next to this script. No network, no randomness
that is not seeded, so repeated runs are byte-identical apart from nothing
at all — the output file is fully deterministic.
"""

import math
import random
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT = "entry.png"

FONT_DIR = "/usr/share/fonts/truetype/noto/"
SERIF_BLACK = FONT_DIR + "NotoSerifDisplay-Black.ttf"
SERIF_BOLD = FONT_DIR + "NotoSerifDisplay-Bold.ttf"
SERIF = FONT_DIR + "NotoSerif-Bold.ttf"
SANS_BLACK = FONT_DIR + "NotoSans-Black.ttf"
SANS_BOLD = FONT_DIR + "NotoSans-Bold.ttf"
SANS = FONT_DIR + "NotoSans-Regular.ttf"

INK = (17, 17, 17)
PAPER = (247, 242, 232)
NAVY = (11, 31, 58)
NAVY2 = (16, 45, 84)
RED = (178, 34, 34)
GOLD = (201, 162, 39)
TEAL = (14, 92, 96)
AMBER = (232, 164, 65)


def font(path, size):
    return ImageFont.truetype(path, size)


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap returning a list of lines that fit max_w."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def star(draw, cx, cy, r, fill):
    """Five-pointed star centred on (cx, cy)."""
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rad = r if i % 2 == 0 else r * 0.42
        pts.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang)))
    draw.polygon(pts, fill=fill)


def draw_lead_scene(base, box):
    """Layered dusk scene: Shenzhen skyline, lake, three flags.

    Layers, back to front: gradient sky, sun + glow, stars, far hills,
    nearer hills, skyline with lit windows, lake with shimmering
    reflection, foreground terrace with three flagpoles.
    """
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    scene = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(scene)
    rng = random.Random(20261120)

    # --- sky: deep indigo at top melting into amber at the horizon
    horizon = int(h * 0.62)
    for y in range(horizon):
        t = y / max(1, horizon)
        d.line([(0, y), (w, y)], fill=lerp((16, 24, 64), (232, 148, 74), t ** 1.6))

    # --- stars in the upper sky
    for _ in range(70):
        sx = rng.randint(0, w - 1)
        sy = rng.randint(0, int(h * 0.30))
        r = rng.choice([1, 1, 2])
        d.ellipse([sx - r, sy - r, sx + r, sy + r],
                  fill=(255, 255, 255) if rng.random() < 0.7 else (255, 220, 150))

    # --- low sun with a soft glow, sitting just above the horizon
    sun_cx, sun_cy, sun_r = int(w * 0.68), horizon - 34, 36
    glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for rad, alpha in [(105, 22), (76, 34), (54, 50)]:
        gd.ellipse([sun_cx - rad, sun_cy - rad, sun_cx + rad, sun_cy + rad],
                   fill=(255, 190, 90, alpha))
    scene = Image.alpha_composite(scene.convert("RGBA"), glow).convert("RGB")
    d = ImageDraw.Draw(scene)
    d.ellipse([sun_cx - sun_r, sun_cy - sun_r, sun_cx + sun_r, sun_cy + sun_r],
              fill=(255, 205, 110))
    d.ellipse([sun_cx - sun_r + 10, sun_cy - sun_r + 10,
               sun_cx + sun_r - 10, sun_cy + sun_r - 10],
              fill=(255, 226, 150))

    # --- birds, high in the sky
    for bx, by, s in [(120, 70, 9), (170, 52, 7), (820, 88, 8), (880, 60, 6)]:
        d.arc([bx - s, by - s, bx, by + s], 200, 340, fill=(20, 20, 40), width=2)
        d.arc([bx, by - s, bx + s, by + s], 200, 340, fill=(20, 20, 40), width=2)

    # --- far hills, hazy mauve
    d.polygon([(0, horizon), (90, horizon - 62), (210, horizon - 18),
               (340, horizon - 74), (470, horizon - 26), (600, horizon - 58),
               (730, horizon - 20), (860, horizon - 66), (w, horizon - 30),
               (w, horizon), (0, horizon)], fill=(94, 82, 116))
    # --- nearer hills, dark teal
    d.polygon([(0, horizon), (60, horizon - 34), (180, horizon - 8),
               (300, horizon - 44), (430, horizon - 12), (560, horizon - 40),
               (700, horizon - 10), (830, horizon - 38), (w, horizon - 14),
               (w, horizon), (0, horizon)], fill=(30, 52, 84))

    # --- skyline, dark navy towers with lit windows
    base_y = horizon + 6
    skyline = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    sd = ImageDraw.Draw(skyline)
    bx = -6
    towers = []
    while bx < w:
        tw = rng.randint(34, 72)
        th = rng.randint(46, 132)
        towers.append((bx, base_y - th, bx + tw, base_y))
        sd.rectangle([bx, base_y - th, bx + tw, base_y], fill=(13, 24, 46, 255))
        if rng.random() < 0.45:  # antenna / spire on some towers
            sd.line([bx + tw // 2, base_y - th, bx + tw // 2, base_y - th - 18],
                    fill=(13, 24, 46, 255), width=3)
            sd.ellipse([bx + tw // 2 - 2, base_y - th - 22,
                        bx + tw // 2 + 2, base_y - th - 18],
                       fill=(255, 90, 90, 255))
        bx += tw + rng.randint(2, 10)
    # lit windows, warm yellow, scattered
    for (tx0, ty0, tx1, ty1) in towers:
        for wy in range(ty0 + 8, ty1 - 6, 13):
            for wx in range(tx0 + 6, tx1 - 5, 11):
                if rng.random() < 0.30:
                    sd.rectangle([wx, wy, wx + 4, wy + 6],
                                 fill=(255, 205, 110, 255))
    scene = Image.alpha_composite(scene.convert("RGBA"), skyline).convert("RGB")
    d = ImageDraw.Draw(scene)

    # --- lake: dark blue water from the horizon down
    for y in range(horizon + 6, h):
        t = (y - horizon - 6) / max(1, h - horizon - 6)
        d.line([(0, y), (w, y)], fill=lerp((24, 52, 96), (10, 22, 48), t))

    # --- reflection: mirrored skyline, dimmed, then broken into shimmer
    refl = skyline.transpose(Image.FLIP_TOP_BOTTOM)
    refl = refl.crop((0, h - (h - horizon - 6), w, h))
    dim = Image.new("RGBA", refl.size, (0, 0, 0, 0))
    dim_d = ImageDraw.Draw(dim)
    dim_d.rectangle([0, 0, w, h - horizon - 6], fill=(10, 22, 48, 150))
    refl = Image.alpha_composite(refl, dim)
    scene.paste(Image.alpha_composite(scene.convert("RGBA").crop(
        (0, horizon + 6, w, h)), refl).convert("RGB"),
        (0, horizon + 6))
    d = ImageDraw.Draw(scene)
    # horizontal shimmer dashes — amber near the sun, pale elsewhere
    for _ in range(90):
        sy = rng.randint(horizon + 10, h - 8)
        sx = rng.randint(0, w - 90)
        ln = rng.randint(12, 70)
        warm = abs(sx + ln // 2 - sun_cx) < 170
        col = (232, 170, 90) if warm else (140, 170, 210)
        d.line([(sx, sy), (sx + ln, sy)], fill=col, width=2)

    # --- foreground terrace strip
    terrace_y = h - 58
    d.rectangle([0, terrace_y, w, h], fill=(8, 14, 28))
    d.rectangle([0, terrace_y, w, terrace_y + 3], fill=GOLD)

    # --- three flags on poles: USA, China, Russia
    def flag_usa(fx, fy, fw, fh):
        d.rectangle([fx, fy, fx + fw, fy + fh], fill=(255, 255, 255))
        for i in range(7):
            if i % 2 == 0:
                d.rectangle([fx, fy + i * fh // 7, fx + fw, fy + (i + 1) * fh // 7],
                            fill=(178, 34, 52))
        cw, chh = int(fw * 0.42), int(fh * 0.54)
        d.rectangle([fx, fy, fx + cw, fy + chh], fill=(28, 48, 110))
        for r in range(3):
            for c in range(4):
                px = fx + 5 + c * (cw - 8) // 3
                py = fy + 5 + r * (chh - 8) // 2
                d.ellipse([px - 1, py - 1, px + 1, py + 1], fill=(255, 255, 255))

    def flag_china(fx, fy, fw, fh):
        d.rectangle([fx, fy, fx + fw, fy + fh], fill=(222, 41, 16))
        star(d, fx + 13, fy + 11, 7, (255, 222, 0))
        for sx, sy in [(28, 7), (33, 12), (33, 19), (28, 23)]:
            star(d, fx + sx, fy + sy, 3, (255, 222, 0))

    def flag_russia(fx, fy, fw, fh):
        d.rectangle([fx, fy, fx + fw, fy + fh // 3], fill=(255, 255, 255))
        d.rectangle([fx, fy + fh // 3, fx + fw, fy + 2 * fh // 3],
                    fill=(0, 57, 166))
        d.rectangle([fx, fy + 2 * fh // 3, fx + fw, fy + fh], fill=(213, 0, 50))

    flag_w, flag_h = 62, 40
    pole_top = terrace_y - 108
    for i, painter in enumerate([flag_usa, flag_china, flag_russia]):
        px = 150 + i * 340
        d.line([px, pole_top, px, terrace_y], fill=(220, 220, 220), width=3)
        d.ellipse([px - 3, pole_top - 4, px + 3, pole_top + 2], fill=GOLD)
        painter(px + 3, pole_top + 2, flag_w, flag_h)

    # caption tag inside the scene, bottom left
    tag = "SHENZHEN, CHINA — THE THREE NUCLEAR POWERS MEET"
    tf = font(SANS_BOLD, 17)
    tw = d.textlength(tag, font=tf)
    d.rectangle([14, h - 52, 14 + tw + 18, h - 52 + 26], fill=(0, 0, 0))
    d.text((14 + 9, h - 52 + 4), tag, font=tf, fill=(255, 255, 255))
    base.paste(scene, (x0, y0))
    return scene


def column(draw, x, y, w, kicker, kcolor, headline, deck, icon):
    """One secondary-story column: small icon, kicker, headline, deck."""
    icon(draw, x + 2, y, 40)
    kf = font(SANS_BLACK, 19)
    draw.text((x + 52, y + 10), kicker, font=kf, fill=kcolor)
    hy = y + 46
    hf = font(SERIF_BLACK, 28)
    hlines = wrap(draw, headline, hf, w)
    for i, line in enumerate(hlines):
        draw.text((x, hy + i * 31), line, font=hf, fill=INK)
    dy = hy + len(hlines) * 31 + 4
    df = font(SANS, 20)
    for i, line in enumerate(wrap(draw, deck, df, w)):
        draw.text((x, dy + i * 24), line, font=df, fill=(58, 58, 58))


def icon_scales(draw, x, y, s):
    draw.line([x + s // 2, y + 4, x + s // 2, y + s - 6], fill=NAVY, width=3)
    draw.line([x + 4, y + 10, x + s - 4, y + 10], fill=NAVY, width=3)
    draw.line([x + s // 2 - 8, y + s - 4, x + s // 2 + 8, y + s - 4],
              fill=NAVY, width=3)
    for cx in (x + 8, x + s - 8):
        draw.line([cx, y + 10, cx, y + 22], fill=NAVY, width=2)
        draw.arc([cx - 9, y + 18, cx + 9, y + 36], 0, 180, fill=NAVY, width=2)


def icon_storm(draw, x, y, s):
    cx, cy = x + s // 2, y + s // 2
    for r, a0 in [(20, 20), (15, 140), (10, 260)]:
        draw.arc([cx - r, cy - r, cx + r, cy + r], a0, a0 + 250,
                 fill=TEAL, width=4)
    draw.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=TEAL)


def icon_clock(draw, x, y, s):
    cx, cy = x + s // 2, y + s // 2
    draw.ellipse([cx - 20, cy - 20, cx + 20, cy + 20], outline=RED, width=4)
    draw.line([cx, cy, cx, cy - 13], fill=RED, width=3)
    draw.line([cx, cy, cx + 11, cy + 5], fill=RED, width=3)
    draw.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=RED)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    mx = 36  # side margin

    # --- masthead: navy band, white serif display
    d.rectangle([0, 0, W, 118], fill=NAVY)
    d.rectangle([0, 118, W, 122], fill=GOLD)
    mast = font(SERIF_BLACK, 82)
    d.text((W // 2, 14), "THE WORLD TODAY", font=mast, fill=(255, 255, 255),
           anchor="ma")

    # --- dateline strip
    d.text((mx, 136), "FRIDAY, 20 NOVEMBER 2026", font=font(SANS_BLACK, 29),
           fill=RED)
    right = "SHENZHEN  •  THE HAGUE  •  NEW DELHI"
    d.text((W - mx, 141), right, font=font(SANS_BOLD, 20), fill=(90, 90, 90),
           anchor="ra")
    d.line([(mx, 172), (W - mx, 172)], fill=INK, width=2)

    # --- lead scene
    draw_lead_scene(img, (mx, 182, W - mx, 520))
    d = ImageDraw.Draw(img)
    d.rectangle([mx, 182, W - mx, 520], outline=INK, width=2)

    # --- lead kicker, headline, deck (headline auto-shrinks to fit)
    d.text((mx, 532), "SHENZHEN SUMMIT  —  A FIRST IN HISTORY",
           font=font(SANS_BLACK, 24), fill=RED)
    head_text = "THREE POWERS, ONE TABLE"
    head_size = 64
    while head_size > 40:
        hf = font(SERIF_BLACK, head_size)
        if d.textlength(head_text, font=hf) <= W - 2 * mx:
            break
        head_size -= 2
    d.text((mx, 560), head_text, font=hf, fill=INK)
    deck = ("Trump, Xi and Putin sign a “peace declaration” on nuclear risk — "
            "but set no timetable, and say nothing on Ukraine.")
    df = font(SANS, 27)
    for i, line in enumerate(wrap(d, deck, df, W - 2 * mx)):
        d.text((mx, 636 + i * 34), line, font=df, fill=(52, 52, 52))

    # --- rule above the secondary stories
    d.line([(mx, 716), (W - mx, 716)], fill=INK, width=3)
    d.line([(mx, 722), (W - mx, 722)], fill=INK, width=1)

    # --- three secondary columns
    col_w = 304
    gap = (W - 2 * mx - 3 * col_w) // 2
    y0 = 738
    column(d, mx, y0, col_w, "THE HAGUE", RED,
           "GENOCIDE, THE COURT RULES",
           "Myanmar guilty over the 2017 Rohingya crackdown — a first for "
           "the world court.", icon_scales)
    column(d, mx + col_w + gap, y0, col_w, "INDIA", TEAL,
           "STORM HITS INDIA TODAY",
           "Cyclone Akvan hits near Gopalpur at noon; 50,000 evacuated.",
           icon_storm)
    column(d, mx + 2 * (col_w + gap), y0, col_w, "WASHINGTON", RED,
           "TRUMP: NO RUSH ON IRAN",
           "Decision pushed to 2027: “We’ll see what happens after Jan 1.”",
           icon_clock)

    # --- bottom ticker: two more stories of the day
    d.rectangle([0, 938, W, 1006], fill=NAVY)
    d.rectangle([0, 938, W, 942], fill=GOLD)
    tf = font(SANS_BOLD, 21)
    d.text((mx, 952), "ALSO TODAY  —  VOYAGER 1 A LIGHT-DAY FROM HOME",
           font=tf, fill=(255, 205, 110))
    d.text((mx, 978), "NASA confirms the probe 16 billion miles out  •  EUROPE READY FOR RUSSIA TALKS",
           font=tf, fill=(255, 255, 255))

    img.save(OUT, optimize=True)
    print("saved", OUT, img.size)


if __name__ == "__main__":
    main()

"""Generate a consistent set of project banners for the GitHub profile README."""
import math, os, random
from collections import deque
from PIL import Image, ImageDraw, ImageFont, ImageFilter

S = 2                      # supersample factor
W, H = 1280 * S, 320 * S
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "banners")
os.makedirs(OUT, exist_ok=True)

FONTS = r"C:\Windows\Fonts"
def font(name, size):
    return ImageFont.truetype(os.path.join(FONTS, name), size * S)

BG_TOP, BG_BOT = (11, 17, 29), (15, 23, 38)
TEXT, MUTED = (241, 245, 249), (148, 163, 184)


def hexc(h, a=255):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (a,)


def background():
    img = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        d.line([(0, y), (W, y)], fill=tuple(int(BG_TOP[i] + (BG_BOT[i] - BG_TOP[i]) * t) for i in range(3)) + (255,))
    # dotted grid
    dots = Image.new("RGBA", (W, H))
    dd = ImageDraw.Draw(dots)
    for x in range(14 * S, W, 28 * S):
        for y in range(14 * S, H, 28 * S):
            dd.ellipse([x - S, y - S, x + S, y + S], fill=(255, 255, 255, 22))
    img.alpha_composite(dots)
    return img


def fade_mask(x0, x1):
    """Horizontal alpha ramp: 0 left of x0, 1 right of x1."""
    m = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(m)
    for x in range(W):
        v = 0 if x < x0 else 255 if x > x1 else int(255 * (x - x0) / (x1 - x0))
        d.line([(x, 0), (x, H)], fill=v)
    return m


def apply_fade(layer, x0=720 * S, x1=960 * S):
    a = layer.getchannel("A")
    a = Image.composite(a, Image.new("L", a.size, 0), fade_mask(x0, x1))
    layer.putalpha(a)
    return layer


def glow(layer, radius=6):
    g = layer.filter(ImageFilter.GaussianBlur(radius * S))
    out = Image.new("RGBA", layer.size)
    out.alpha_composite(g)
    out.alpha_composite(layer)
    return out


def series(n, fn):
    return [fn(i / (n - 1)) for i in range(n)]


def P(x, y):
    return (x * S, y * S)


def dashed(d, x0, x1, y, color, width=2, dash=10, gap=8):
    x = x0
    while x < x1:
        d.line([P(x, y), P(min(x + dash, x1), y)], fill=color, width=width * S)
        x += dash + gap


# ─────────────────────────── icons (drawn in a 130×130 box) ───────────────────────────
def icon_floodlink(d, cx, cy, c):
    for r in (14, 26, 38):
        d.arc([P(cx - r, cy - 18 - r), P(cx + r, cy - 18 + r)], 220, 320, fill=c, width=5 * S)
    d.ellipse([P(cx - 5, cy - 23), P(cx + 5, cy - 13)], fill=c)
    pts = [P(cx - 42 + i, cy + 20 + 8 * math.sin(i / 84 * 2 * math.pi * 1.5)) for i in range(0, 85, 2)]
    d.line(pts, fill=c, width=6 * S, joint="curve")
    pts = [P(cx - 42 + i, cy + 36 + 6 * math.sin(i / 84 * 2 * math.pi * 1.5 + 1)) for i in range(0, 85, 2)]
    d.line(pts, fill=c[:3] + (140,), width=5 * S, joint="curve")


def icon_monitor(d, cx, cy, c):
    for i, h in enumerate((18, 30, 22, 40)):
        x = cx - 34 + i * 20
        d.rounded_rectangle([P(x, cy + 36 - h), P(x + 12, cy + 36)], radius=3 * S, fill=c[:3] + (110,))
    d.line([P(cx - 40, cy + 6), P(cx - 18, cy - 14), P(cx + 2, cy - 2), P(cx + 22, cy - 30), P(cx + 40, cy - 20)],
           fill=c, width=6 * S, joint="curve")
    dashed(d, cx - 42, cx + 42, cy - 38, c[:3] + (160,), width=2, dash=6, gap=5)


def icon_sync(d, cx, cy, c):
    r = 34
    d.arc([P(cx - r, cy - r), P(cx + r, cy + r)], 200, 340, fill=c, width=7 * S)
    d.arc([P(cx - r, cy - r), P(cx + r, cy + r)], 20, 160, fill=c, width=7 * S)
    for ang, sgn in ((340, 1), (160, 1)):
        a = math.radians(ang)
        x, y = cx + r * math.cos(a), cy + r * math.sin(a)
        t = a + math.pi / 2
        tip = (x + 12 * math.cos(t), y + 12 * math.sin(t))
        b1 = (x + 9 * math.cos(a), y + 9 * math.sin(a))
        b2 = (x - 9 * math.cos(a), y - 9 * math.sin(a))
        d.polygon([P(*tip), P(*b1), P(*b2)], fill=c)
    d.ellipse([P(cx - 9, cy - 9), P(cx + 9, cy + 9)], fill=c)


def icon_nn(d, cx, cy, c):
    layers = [[-28, 0, 28], [-40, -13, 13, 40], [-14, 14]]
    xs = [cx - 36, cx, cx + 36]
    for li in range(2):
        for y1 in layers[li]:
            for y2 in layers[li + 1]:
                d.line([P(xs[li], cy + y1), P(xs[li + 1], cy + y2)], fill=c[:3] + (90,), width=2 * S)
    for li, ys in enumerate(layers):
        for y in ys:
            d.ellipse([P(xs[li] - 7, cy + y - 7), P(xs[li] + 7, cy + y + 7)], fill=c)


def icon_chip(d, cx, cy, c):
    d.rounded_rectangle([P(cx - 26, cy - 26), P(cx + 26, cy + 26)], radius=6 * S, outline=c, width=5 * S)
    d.rounded_rectangle([P(cx - 11, cy - 11), P(cx + 11, cy + 11)], radius=3 * S, fill=c)
    for k in (-15, 0, 15):
        for (x0, y0, x1, y1) in ((cx + k, cy - 26, cx + k, cy - 40), (cx + k, cy + 26, cx + k, cy + 40),
                                 (cx - 26, cy + k, cx - 40, cy + k), (cx + 26, cy + k, cx + 40, cy + k)):
            d.line([P(x0, y0), P(x1, y1)], fill=c, width=5 * S)


def icon_phone(d, cx, cy, c):
    d.rounded_rectangle([P(cx - 24, cy - 42), P(cx + 24, cy + 42)], radius=9 * S, outline=c, width=5 * S)
    d.line([P(cx - 8, cy + 32), P(cx + 8, cy + 32)], fill=c, width=4 * S)
    d.ellipse([P(cx - 10, cy - 22), P(cx + 10, cy - 2)], outline=c, width=4 * S)
    d.polygon([P(cx - 9, cy - 8), P(cx + 9, cy - 8), P(cx, cy + 12)], fill=c)
    d.ellipse([P(cx - 4, cy - 16), P(cx + 4, cy - 8)], fill=c)


def icon_emg(d, cx, cy, c):
    pts = [(-44, 0), (-22, 0), (-16, -6), (-10, 8), (-5, -34), (0, 38), (5, -22), (10, 14), (15, -6), (20, 0), (44, 0)]
    d.line([P(cx + x, cy + y) for x, y in pts], fill=c, width=6 * S, joint="curve")


def icon_maze(d, cx, cy, c):
    s = 24
    x0, y0 = cx - 1.5 * s, cy - 1.5 * s
    walls = [((0, 0), (3, 0)), ((0, 3), (3, 3)), ((0, 0), (0, 2)), ((3, 1), (3, 3)),
             ((1, 0), (1, 1)), ((1, 2), (2, 2)), ((2, 1), (2, 2)), ((1, 2), (1, 3))]
    for (a, b), (e, f) in walls:
        d.line([P(x0 + a * s, y0 + b * s), P(x0 + e * s, y0 + f * s)], fill=c, width=5 * S)
    d.ellipse([P(x0 + 0.5 * s - 7, y0 + 2.5 * s - 7), P(x0 + 0.5 * s + 7, y0 + 2.5 * s + 7)], fill=c)


# ─────────────────────────── right-hand artwork ───────────────────────────
def art_floodlink(L, c, c2):
    d = ImageDraw.Draw(L)
    for k, (amp, off, a) in enumerate(((10, 250, 70), (14, 268, 110), (9, 288, 170))):
        pts = [P(560 + i, off + amp * math.sin(i / 90 + k * 1.7)) for i in range(0, 721, 4)]
        d.polygon(pts + [P(1280, 320), P(560, 320)], fill=c[:3] + (a,))
    for y, col, lab in ((215, "#a78bfa", "ALERT  5.0 m"), (170, "#facc15", "MINOR  7.0 m"), (125, "#f87171", "MAJOR  9.0 m")):
        dashed(d, 700, 1250, y, hexc(col, 150), width=2)
        d.text(P(1250, y - 6), lab, font=font("consola.ttf", 12), fill=hexc(col, 200), anchor="rb")
    # sensor pole with LoRa arcs
    px = 1080
    d.rectangle([P(px - 3, 60), P(px + 3, 280)], fill=(200, 210, 225, 200))
    d.rounded_rectangle([P(px - 22, 70), P(px + 22, 110)], radius=6 * S, fill=(30, 41, 59, 255), outline=c, width=2 * S)
    d.ellipse([P(px - 4, 86), P(px + 4, 94)], fill=c2)
    for r in (22, 40, 58):
        d.arc([P(px - r, 60 - r), P(px + r, 60 + r)], 215, 325, fill=c[:3] + (220 - r * 2,), width=3 * S)
    d.line([P(px, 110), P(px, 250)], fill=(250, 250, 250, 60), width=S)
    d.polygon([P(px - 8, 244), P(px + 8, 244), P(px, 256)], fill=(250, 250, 250, 90))


def art_monitor(L, c, c2):
    d = ImageDraw.Draw(L)
    random.seed(3)
    for i in range(46):
        x = 600 + i * 14
        h = max(0, 40 * math.exp(-((i - 26) / 7) ** 2) + random.uniform(0, 8))
        d.rectangle([P(x, 290 - h), P(x + 9, 290)], fill=hexc("#38bdf8", 70))
    for y, col in ((200, "#a78bfa"), (150, "#facc15"), (105, "#f87171")):
        dashed(d, 600, 1260, y, hexc(col, 130), width=2)
    for base, amp, col in ((245, 150, c), (255, 115, c2)):
        pts = [P(600 + t * 660, base - amp * math.exp(-((t - 0.62) / 0.16) ** 2) - 8 * math.sin(t * 9)) for t in [i / 200 for i in range(201)]]
        d.line(pts, fill=col, width=4 * S, joint="curve")
    d.rounded_rectangle([P(1150, 26), P(1250, 56)], radius=15 * S, fill=hexc("#ef4444", 40), outline=hexc("#ef4444", 200), width=2 * S)
    d.ellipse([P(1162, 36), P(1172, 46)], fill=hexc("#ef4444"))
    d.text(P(1180, 41), "LIVE", font=font("segoeuib.ttf", 14), fill=hexc("#fecaca"), anchor="lm")


def art_hydrosync(L, c, c2):
    d = ImageDraw.Draw(L)
    f = font("consola.ttf", 11)
    for k in range(5):
        x0 = 740 + k * 85
        y = 42 + k * 24
        d.rounded_rectangle([P(x0, y), P(x0 + 170, y + 18)], radius=9 * S, fill=c[:3] + (70 + k * 25,), outline=c[:3] + (200,), width=S)
        d.text(P(x0 + 160, y + 9), f"export {k + 1} · 72 h", font=f, fill=(226, 232, 240, 230), anchor="rm")
    for x in (880, 1050, 1220):
        d.line([P(x, 170), P(x, 196)], fill=c2[:3] + (200,), width=3 * S)
        d.polygon([P(x - 7, 192), P(x + 7, 192), P(x, 202)], fill=c2)
    d.rounded_rectangle([P(620, 210), P(1250, 226)], radius=8 * S, fill=c2[:3] + (200,))
    d.text(P(1250, 240), "1 row / hour / station", font=f, fill=c2[:3] + (220,), anchor="ra")
    pts = [P(620 + t * 630, 292 - 30 * math.exp(-((t - 0.55) / 0.12) ** 2) - 5 * math.sin(t * 14)) for t in [i / 200 for i in range(201)]]
    d.line(pts, fill=c[:3] + (200,), width=3 * S, joint="curve")


def art_model(L, c, c2):
    d = ImageDraw.Draw(L)
    now = 1010
    fn = lambda t: 250 - 150 * math.exp(-((t - 0.58) / 0.14) ** 2) - 10 * math.sin(t * 11)
    xs = [600 + i * 3.25 for i in range(201)]
    obs = [(x, fn((x - 600) / 650)) for x in xs]
    d.rectangle([P(now, 30), P(1250, 295)], fill=c[:3] + (18,))
    band_top = [(x, y - 6 - (x - now) * 0.12) for x, y in obs if x >= now]
    band_bot = [(x, y + 6 + (x - now) * 0.12) for x, y in obs if x >= now]
    d.polygon([P(*p) for p in band_top + band_bot[::-1]], fill=c[:3] + (60,))
    d.line([P(x, y) for x, y in obs if x <= now], fill=(226, 232, 240, 230), width=4 * S, joint="curve")
    pred = [(x, y + 8 * math.sin(x / 40)) for x, y in obs if x >= now]
    for i in range(0, len(pred) - 1, 2):
        d.line([P(*pred[i]), P(*pred[i + 1])], fill=c, width=4 * S)
    d.line([P(now, 30), P(now, 295)], fill=(226, 232, 240, 120), width=2 * S)
    f = font("consola.ttf", 12)
    d.text(P(now - 8, 40), "now", font=f, fill=MUTED + (200,), anchor="ra")
    for i, lab in enumerate(("+1 h", "+3 h", "+6 h")):
        x = now + 40 + i * 75
        d.line([P(x, 290), P(x, 298)], fill=c, width=2 * S)
        d.text(P(x, 304), lab, font=f, fill=c[:3] + (220,), anchor="ma")
    d.text(P(1250, 40), "RMSE 0.14 m · NSE 0.99", font=f, fill=c2[:3] + (230,), anchor="ra")


def plane_poly(cx, cy, s, ang):
    pts = [(0, -40), (5, -30), (6, -6), (46, 4), (46, 12), (6, 8), (4, 28), (16, 36), (16, 41), (0, 38),
           (-16, 41), (-16, 36), (-4, 28), (-6, 8), (-46, 12), (-46, 4), (-6, -6), (-5, -30)]
    a = math.radians(ang)
    return [P(cx + s * (x * math.cos(a) - y * math.sin(a)), cy + s * (x * math.sin(a) + y * math.cos(a))) for x, y in pts]


def art_flyme_hw(L, c, c2):
    d = ImageDraw.Draw(L)
    # artificial horizon
    cx, cy, r = 1150, 140, 95
    hz = Image.new("RGBA", L.size)
    hd = ImageDraw.Draw(hz)
    hd.ellipse([P(cx - r, cy - r), P(cx + r, cy + r)], fill=hexc("#1e3a8a", 110))
    hd.polygon([P(cx - r - 20, cy + 10 + 34), P(cx + r + 20, cy + 10 - 34), P(cx + r + 20, cy + r + 20), P(cx - r - 20, cy + r + 20)], fill=hexc("#78350f", 120))
    m = Image.new("L", L.size, 0)
    ImageDraw.Draw(m).ellipse([P(cx - r, cy - r), P(cx + r, cy + r)], fill=255)
    L.paste(hz, (0, 0), Image.composite(hz.getchannel("A"), Image.new("L", L.size, 0), m))
    d.ellipse([P(cx - r, cy - r), P(cx + r, cy + r)], outline=c[:3] + (200,), width=3 * S)
    d.line([P(cx - 40, cy), P(cx - 12, cy), P(cx, cy + 10), P(cx + 12, cy), P(cx + 40, cy)], fill=hexc("#fde047"), width=4 * S)
    f = font("consola.ttf", 12)
    d.text(P(cx, cy + r + 10), "roll 18°  pitch 4°", font=f, fill=MUTED + (220,), anchor="ma")
    # plane + link
    px, py = 940, 100
    d.polygon(plane_poly(px, py, 1.15, 20), fill=(226, 232, 240, 235))
    for r2 in (34, 54, 74):
        d.arc([P(px - r2, py - r2), P(px + r2, py + r2)], 95, 165, fill=c[:3] + (210 - r2 * 2,), width=3 * S)
    gx, gy = 850, 262
    for i in range(8):
        t = i / 7
        x, y = px - 40 + (gx - px + 40) * t, py + 50 + (gy - py - 70) * t
        d.ellipse([P(x - 3, y - 3), P(x + 3, y + 3)], fill=c2[:3] + (90 + int(160 * (1 - t)),))
    d.line([P(gx, gy - 22), P(gx, gy + 20)], fill=(203, 213, 225, 220), width=3 * S)
    d.polygon([P(gx - 12, gy + 20), P(gx + 12, gy + 20), P(gx, gy + 4)], fill=(203, 213, 225, 220))
    d.text(P(gx + 22, gy + 8), "LoRa 433 MHz · SF7 · 10 Hz · 47 B", font=f, fill=c[:3] + (230,), anchor="lm")


def art_flyme_app(L, c, c2):
    d = ImageDraw.Draw(L)
    for x in range(600, 1281, 40):
        d.line([P(x, 0), P(x, 320)], fill=(255, 255, 255, 12), width=S)
    for y in range(0, 321, 40):
        d.line([P(600, y), P(1280, y)], fill=(255, 255, 255, 12), width=S)
    # phone
    x0, y0, x1, y1 = 1000, 20, 1160, 330
    d.rounded_rectangle([P(x0, y0), P(x1, y1)], radius=22 * S, fill=(15, 23, 42, 255), outline=(203, 213, 225, 200), width=3 * S)
    hx, hy = 1040, 230
    for r in (30, 60, 90):
        d.ellipse([P(hx - r, hy - r), P(hx + r, hy + r)], outline=c[:3] + (70,), width=S)
    trail = [(hx + 90 * t + 20 * math.sin(t * 6), hy - 150 * t) for t in [i / 40 for i in range(41)]]
    for i in range(0, 40, 2):
        d.line([P(*trail[i]), P(*trail[i + 1])], fill=c2, width=3 * S)
    d.polygon(plane_poly(trail[-1][0], trail[-1][1], 0.45, 30), fill=hexc("#fde047"))
    d.ellipse([P(hx - 7, hy - 7), P(hx + 7, hy + 7)], fill=c, outline=(255, 255, 255, 255), width=2 * S)
    d.rounded_rectangle([P(x0 + 10, 272), P(x1 - 10, 310)], radius=8 * S, fill=(30, 41, 59, 255))
    f = font("segoeuib.ttf", 10)
    for i, (v, lab) in enumerate((("412 m", "DIST"), ("86 m", "ALT"), ("54", "KM/H"))):
        cx = x0 + 32 + i * 48
        d.text(P(cx, 285), v, font=f, fill=TEXT, anchor="mm")
        d.text(P(cx, 299), lab, font=font("segoeui.ttf", 8), fill=MUTED, anchor="mm")
    d.rounded_rectangle([P(x0 + 10, 34), P(x1 - 10, 54)], radius=6 * S, fill=(30, 41, 59, 230))
    d.ellipse([P(x0 + 18, 40), P(x0 + 26, 48)], fill=hexc("#22c55e"))
    d.text(P(x0 + 32, 44), "LINK · SAT 12", font=font("segoeuib.ttf", 9), fill=TEXT, anchor="lm")
    # floating chips beside phone
    for i, t in enumerate(("GPX export", "Voice alerts", "Flight replay")):
        y = 90 + i * 50
        d.rounded_rectangle([P(826, y), P(976, y + 32)], radius=16 * S, fill=c[:3] + (40,), outline=c[:3] + (160,), width=2 * S)
        d.text(P(901, y + 16), t, font=font("seguisb.ttf", 13), fill=TEXT, anchor="mm")


def art_emg(L, c, c2):
    d = ImageDraw.Draw(L)
    random.seed(7)
    for k, (y, col) in enumerate(((80, hexc("#2dd4bf")), (170, hexc("#f59e0b")), (255, hexc("#a855f7")))):
        pts = []
        for i in range(0, 661, 2):
            t = i / 660
            env = math.exp(-((t - 0.42 - 0.08 * k) / 0.08) ** 2) * (1.0 - 0.2 * k) + 0.6 * math.exp(-((t - 0.8 + 0.04 * k) / 0.05) ** 2)
            pts.append(P(600 + i, y + (random.gauss(0, 1) * 30 * env + random.gauss(0, 0.8))))
        d.line(pts, fill=col[:3] + (220,), width=2 * S, joint="curve")
        d.text(P(1255, y - 16), f"CH{k}", font=font("consola.ttf", 12), fill=col[:3] + (200,), anchor="rm")


def art_maze(L, c, c2):
    d = ImageDraw.Draw(L)
    cols, rows, s = 12, 8, 34
    ox, oy = 830, 25
    random.seed(11)
    walls = {(x, y): {"N", "S", "E", "W"} for x in range(cols) for y in range(rows)}
    opp = {"N": "S", "S": "N", "E": "W", "W": "E"}
    mv = {"N": (0, -1), "S": (0, 1), "E": (1, 0), "W": (-1, 0)}
    stack, seen = [(0, rows - 1)], {(0, rows - 1)}
    while stack:
        x, y = stack[-1]
        nb = [(dname, (x + dx, y + dy)) for dname, (dx, dy) in mv.items() if (x + dx, y + dy) in walls and (x + dx, y + dy) not in seen]
        if not nb:
            stack.pop(); continue
        dname, n = random.choice(nb)
        walls[(x, y)].discard(dname); walls[n].discard(opp[dname])
        seen.add(n); stack.append(n)
    # extra openings so the centre is reachable in multiple ways
    for x, y in walls:
        for dname, (dx, dy) in mv.items():
            pass
    col = c[:3] + (150,)
    for (x, y), ws in walls.items():
        X, Y = ox + x * s, oy + y * s
        if "N" in ws: d.line([P(X, Y), P(X + s, Y)], fill=col, width=3 * S)
        if "W" in ws: d.line([P(X, Y), P(X, Y + s)], fill=col, width=3 * S)
        if "S" in ws and y == rows - 1: d.line([P(X, Y + s), P(X + s, Y + s)], fill=col, width=3 * S)
        if "E" in ws and x == cols - 1: d.line([P(X + s, Y), P(X + s, Y + s)], fill=col, width=3 * S)
    # BFS to centre
    start, goal = (0, rows - 1), (cols // 2, rows // 2)
    prev, q = {start: None}, deque([start])
    while q:
        cur = q.popleft()
        if cur == goal: break
        for dname, (dx, dy) in mv.items():
            n = (cur[0] + dx, cur[1] + dy)
            if dname not in walls[cur] and n not in prev:
                prev[n] = cur; q.append(n)
    path, cur = [], goal
    while cur:
        path.append(cur); cur = prev[cur]
    path = path[::-1]
    for (x, y) in (goal, (goal[0] - 1, goal[1]), (goal[0], goal[1] - 1), (goal[0] - 1, goal[1] - 1)):
        d.rectangle([P(ox + x * s + 3, oy + y * s + 3), P(ox + (x + 1) * s - 3, oy + (y + 1) * s - 3)], fill=c2[:3] + (45,))
    d.line([P(ox + x * s + s / 2, oy + y * s + s / 2) for x, y in path], fill=c2, width=5 * S, joint="curve")
    sx, sy = ox + s / 2, oy + (rows - 1) * s + s / 2
    d.ellipse([P(sx - 9, sy - 9), P(sx + 9, sy + 9)], fill=(255, 255, 255, 255))


# ─────────────────────────── compose ───────────────────────────
def banner(slug, title, subtitle, chips, accent, accent2, icon, art):
    c, c2 = hexc(accent), hexc(accent2)
    img = background()

    # soft accent glow behind the art
    g = Image.new("RGBA", (W, H))
    ImageDraw.Draw(g).ellipse([P(820, -120), P(1400, 440)], fill=c[:3] + (40,))
    img.alpha_composite(g.filter(ImageFilter.GaussianBlur(90 * S)))

    layer = Image.new("RGBA", (W, H))
    art(layer, c, c2)
    img.alpha_composite(apply_fade(glow(layer, 3)))

    fg = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(fg)
    # icon tile
    ix, iy, isz = 60, 95, 130
    d.rounded_rectangle([P(ix, iy), P(ix + isz, iy + isz)], radius=24 * S, fill=c[:3] + (28,), outline=c[:3] + (210,), width=3 * S)
    icon(d, ix + isz / 2, iy + isz / 2, c)

    tx = 222
    size = 52
    while font("segoeuib.ttf", size).getlength(title) > 560 * S and size > 34:
        size -= 2
    d.text(P(tx, 150), title, font=font("segoeuib.ttf", size), fill=TEXT, anchor="ls")
    d.text(P(tx, 188), subtitle, font=font("segoeui.ttf", 21), fill=MUTED, anchor="ls")

    x = tx
    cf = font("seguisb.ttf", 13)
    for chip in chips:
        w = cf.getlength(chip) / S + 26
        d.rounded_rectangle([P(x, 208), P(x + w, 236)], radius=14 * S, fill=(255, 255, 255, 14), outline=c[:3] + (120,), width=S * 1)
        d.text(P(x + w / 2, 222), chip, font=cf, fill=(203, 213, 225, 255), anchor="mm")
        x += w + 8

    img.alpha_composite(fg)
    d = ImageDraw.Draw(img)
    # bottom accent bar
    for xx in range(W):
        t = xx / W
        col = tuple(int(c[i] + (c2[i] - c[i]) * t) for i in range(3)) + (255,)
        d.line([(xx, H - 5 * S), (xx, H)], fill=col)

    img = img.convert("RGB").resize((W // S, H // S), Image.LANCZOS)
    path = os.path.join(OUT, f"{slug}.png")
    img.save(path, optimize=True)
    print("wrote", path)


BANNERS = [
    ("floodlink", "FloodLink 1.0", "LoRa flood early-warning system · Mahaweli River",
     ["2nd Place · Idea to Invention 2025", "ESP32-C3", "LoRa", "Python"], "#22d3ee", "#3b82f6", icon_floodlink, art_floodlink),
    ("flood-web-monitor", "Flood Web Monitor", "Live water level & rainfall dashboard · Peradeniya · Nawalapitiya",
     ["Live on GitHub Pages", "JavaScript", "Plotly.js", "ArcGIS"], "#4a9eff", "#34d399", icon_monitor, art_monitor),
    ("hydrosync", "HydroSync Studio", "Overlapping gauge exports → one clean hourly dataset",
     ["FloodLink 2.0", "PySide6", "pandas", "Windows .exe"], "#38bdf8", "#22c55e", icon_sync, art_hydrosync),
    ("water-level-model", "Water Level Forecasting", "Predicting Peradeniya from the upstream Nawalapitiya gauge",
     ["9 models", "1–6 h lead", "scikit-learn", "PyTorch"], "#f59e0b", "#fbbf24", icon_nn, art_model),
    ("flyme-hardware", "FlyMe Hardware", "ESP32-C3 flight telemetry & LoRa command link",
     ["200 Hz Mahony AHRS", "MPU6500", "NEO-M8N GPS", "C++"], "#fb923c", "#f43f5e", icon_chip, art_flyme_hw),
    ("flyme-app", "FlyMe Ground Station", "Android live-map tracking for an RC aircraft",
     ["Android", "Java", "Wi-Fi UDP / HTTP", "USB-OTG"], "#a78bfa", "#38bdf8", icon_phone, art_flyme_app),
    ("emg-recorder", "EMG Recorder", "Real-time 3-channel EMG acquisition · NI USB-6009",
     ["PySide6", "NumPy", "NI-DAQmx", "Notch filter"], "#2dd4bf", "#a855f7", icon_emg, art_emg),
    ("micromouse", "MicroMouse", "Autonomous maze-solving robot · STM32F411 BlackPill",
     ["STM32", "PlatformIO", "C/C++", "H-bridge PWM"], "#f43f5e", "#fde047", icon_maze, art_maze),
]

if __name__ == "__main__":
    for b in BANNERS:
        banner(*b)

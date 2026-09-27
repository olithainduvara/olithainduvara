"""Generate the profile header, the About photo and the footer banner.

Source photos are read from scripts/photos/ (suit.jpg, engex.jpg).
"""
import math, os, random
from PIL import Image, ImageDraw, ImageFilter, ImageChops

import make_banners as mb
from make_banners import S, P, font, hexc, TEXT, MUTED

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "..", "assets")
PHOTOS = os.path.join(HERE, "photos")
CYAN, BLUE, VIOLET = hexc("#22d3ee"), hexc("#4a9eff"), hexc("#a78bfa")


def gradient_color(t, stops=(CYAN, BLUE, VIOLET)):
    t = max(0.0, min(1.0, t)) * (len(stops) - 1)
    i = min(int(t), len(stops) - 2)
    f = t - i
    return tuple(int(stops[i][k] + (stops[i + 1][k] - stops[i][k]) * f) for k in range(3)) + (255,)


def canvas(w, h):
    img = Image.new("RGBA", (w * S, h * S))
    d = ImageDraw.Draw(img)
    for y in range(h * S):
        t = y / (h * S)
        d.line([(0, y), (w * S, y)], fill=tuple(int(mb.BG_TOP[i] + (mb.BG_BOT[i] - mb.BG_TOP[i]) * t) for i in range(3)) + (255,))
    dots = Image.new("RGBA", img.size)
    dd = ImageDraw.Draw(dots)
    for x in range(14 * S, w * S, 28 * S):
        for y in range(14 * S, h * S, 28 * S):
            dd.ellipse([x - S, y - S, x + S, y + S], fill=(255, 255, 255, 20))
    img.alpha_composite(dots)
    return img


def blob(img, box, color, blur):
    g = Image.new("RGBA", img.size)
    ImageDraw.Draw(g).ellipse([P(*box[:2]), P(*box[2:])], fill=color)
    img.alpha_composite(g.filter(ImageFilter.GaussianBlur(blur * S)))


def circuit(w, h, x_from, seed=5):
    """PCB-style traces with vias, faded in from the left."""
    L = Image.new("RGBA", (w * S, h * S))
    d = ImageDraw.Draw(L)
    random.seed(seed)
    for _ in range(26):
        x = random.randint(x_from, w - 40)
        y = random.choice(range(30, h - 30, 22))
        pts = [(x, y)]
        for _ in range(random.randint(2, 4)):
            if random.random() < 0.5:
                x += random.choice((-1, 1)) * random.randint(40, 140)
            else:
                dy = random.choice((-1, 1)) * random.randint(20, 60)
                x += abs(dy) * random.choice((-1, 1))
                y += dy
            x, y = max(x_from - 60, min(w - 10, x)), max(16, min(h - 16, y))
            pts.append((x, y))
        col = gradient_color(pts[0][0] / w)[:3]
        d.line([P(*p) for p in pts], fill=col + (70,), width=2 * S, joint="curve")
        for p in (pts[0], pts[-1]):
            d.ellipse([P(p[0] - 4, p[1] - 4), P(p[0] + 4, p[1] + 4)], outline=col + (140,), width=2 * S)
    L.putalpha(ImageChops.multiply(L.getchannel("A"), mb.fade_mask(x_from * S, (x_from + 260) * S).resize(L.size)))
    return L


def circle_photo(path, box, size):
    im = Image.open(path).convert("RGB").crop(box).resize((size * S, size * S), Image.LANCZOS)
    m = Image.new("L", im.size, 0)
    ImageDraw.Draw(m).ellipse([0, 0, im.size[0] - 1, im.size[1] - 1], fill=255)
    out = Image.new("RGBA", im.size)
    out.paste(im, (0, 0), m)
    return out


def gradient_ring(img, cx, cy, r, width):
    ring = Image.new("RGBA", img.size)
    d = ImageDraw.Draw(ring)
    for a in range(0, 360, 1):
        col = gradient_color((math.sin(math.radians(a - 45)) + 1) / 2)
        d.arc([P(cx - r, cy - r), P(cx + r, cy + r)], a, a + 1.6, fill=col, width=width * S)
    img.alpha_composite(ring.filter(ImageFilter.GaussianBlur(10 * S)))
    img.alpha_composite(ring)


def bottom_bar(img):
    d = ImageDraw.Draw(img)
    w, h = img.size
    for x in range(w):
        d.line([(x, h - 5 * S), (x, h)], fill=gradient_color(x / w))


def pin_icon(d, x, y, c):
    d.ellipse([P(x - 6, y - 9), P(x + 6, y + 3)], fill=c)
    d.polygon([P(x - 5, y - 1), P(x + 5, y - 1), P(x, y + 9)], fill=c)
    d.ellipse([P(x - 2.5, y - 5.5), P(x + 2.5, y - 0.5)], fill=mb.BG_TOP + (255,))


def cap_icon(d, x, y, c):
    d.polygon([P(x - 12, y - 3), P(x, y - 9), P(x + 12, y - 3), P(x, y + 3)], fill=c)
    d.polygon([P(x - 7, y), P(x + 7, y), P(x + 7, y + 7), P(x, y + 10), P(x - 7, y + 7)], fill=c)
    d.line([P(x + 10, y - 3), P(x + 10, y + 7)], fill=c, width=2 * S)


def save(img, name, w, h):
    path = os.path.join(ASSETS, name)
    img.convert("RGB").resize((w, h), Image.LANCZOS).save(path, optimize=True, quality=92)
    print("wrote", path)


# ─────────────────────────── header ───────────────────────────
def header():
    w, h = 1280, 400
    img = canvas(w, h)
    blob(img, (-120, -80, 520, 520), CYAN[:3] + (38,), 110)
    blob(img, (860, -160, 1480, 460), VIOLET[:3] + (40,), 120)
    img.alpha_composite(circuit(w, h, 820))

    # photo
    cx, cy, r = 205, 200, 128
    gradient_ring(img, cx, cy, r + 9, 6)
    ph = circle_photo(os.path.join(PHOTOS, "suit.jpg"), (560, 580, 1340, 1360), 2 * r)
    img.alpha_composite(ph, (int((cx - r) * S), int((cy - r) * S)))

    fg = Image.new("RGBA", img.size)
    d = ImageDraw.Draw(fg)
    tx = 395
    f_small = font("seguisb.ttf", 16)
    x = tx
    for ch in "HELLO, I'M":
        d.text(P(x, 92), ch, font=f_small, fill=CYAN, anchor="ls")
        x += f_small.getlength(ch) / S + 3.2
    d.text(P(tx - 3, 162), "Olitha Induvara", font=font("segoeuib.ttf", 66), fill=TEXT, anchor="ls")
    d.text(P(tx, 204), "Electrical & Electronic Engineering Undergraduate", font=font("segoeui.ttf", 25), fill=(203, 213, 225, 255), anchor="ls")

    f_meta = font("segoeui.ttf", 17)
    cap_icon(d, tx + 10, 236, BLUE)
    d.text(P(tx + 30, 243), "University of Peradeniya", font=f_meta, fill=MUTED + (255,), anchor="ls")
    x2 = tx + 30 + f_meta.getlength("University of Peradeniya") / S + 26
    pin_icon(d, x2, 236, BLUE)
    d.text(P(x2 + 16, 243), "Sri Lanka", font=f_meta, fill=MUTED + (255,), anchor="ls")

    cf = font("seguisb.ttf", 15)
    x = tx
    chips = ["Embedded Systems", "IoT & LoRa", "Data & Machine Learning", "Drones & Aerial Media"]
    for i, chip in enumerate(chips):
        cw = cf.getlength(chip) / S + 40
        col = gradient_color(i / (len(chips) - 1))
        d.rounded_rectangle([P(x, 272), P(x + cw, 306)], radius=17 * S, fill=col[:3] + (26,), outline=col[:3] + (170,), width=S)
        d.ellipse([P(x + 14, 286), P(x + 20, 292)], fill=col)
        d.text(P(x + cw / 2 + 8, 289), chip, font=cf, fill=(226, 232, 240, 255), anchor="mm")
        x += cw + 10

    # award ribbon, top-right
    rf = font("seguisb.ttf", 14)
    label = "2nd Place · Idea to Invention 2025"
    rw = rf.getlength(label) / S + 52
    rx = w - 40 - rw
    d.rounded_rectangle([P(rx, 34), P(w - 40, 66)], radius=16 * S, fill=hexc("#f59e0b", 30), outline=hexc("#f59e0b", 190), width=S)
    tx0, ty0 = rx + 20, 50
    d.polygon([P(tx0 - 7, ty0 - 8), P(tx0 + 7, ty0 - 8), P(tx0 + 5, ty0 + 1), P(tx0 - 5, ty0 + 1)], fill=hexc("#fbbf24"))
    d.rectangle([P(tx0 - 1.5, ty0 + 1), P(tx0 + 1.5, ty0 + 5)], fill=hexc("#fbbf24"))
    d.rectangle([P(tx0 - 5, ty0 + 5), P(tx0 + 5, ty0 + 8)], fill=hexc("#fbbf24"))
    d.text(P(rx + 34, 50), label, font=rf, fill=hexc("#fde68a"), anchor="lm")

    img.alpha_composite(fg)
    bottom_bar(img)
    save(img, "header.png", w, h)


# ─────────────────────────── about photo ───────────────────────────
def about_photo():
    w, h = 360, 480
    src = Image.open(os.path.join(PHOTOS, "engex.jpg")).convert("RGB").crop((330, 280, 1030, 1213))
    im = src.resize((w * S, h * S), Image.LANCZOS).convert("RGBA")
    # darken the bottom so the caption reads
    shade = Image.new("RGBA", im.size)
    sd = ImageDraw.Draw(shade)
    for y in range(h * S):
        t = max(0.0, (y / (h * S) - 0.62) / 0.38)
        sd.line([(0, y), (w * S, y)], fill=(8, 12, 22, int(225 * t)))
    im.alpha_composite(shade)
    d = ImageDraw.Draw(im)
    d.text(P(22, h - 50), "EngEx 2025", font=font("segoeuib.ttf", 22), fill=TEXT, anchor="ls")
    d.text(P(22, h - 26), "Media Team Lead", font=font("segoeui.ttf", 16), fill=CYAN, anchor="ls")
    for x in range(w * S):
        d.line([(x, h * S - 5 * S), (x, h * S)], fill=gradient_color(x / (w * S)))
    m = Image.new("L", im.size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, im.size[0] - 1, im.size[1] - 1], radius=22 * S, fill=255)
    out = Image.new("RGBA", im.size)
    out.paste(im, (0, 0), m)
    path = os.path.join(ASSETS, "about-photo.png")
    out.resize((w, h), Image.LANCZOS).save(path, optimize=True)
    print("wrote", path)


# ─────────────────────────── footer ───────────────────────────
def footer():
    w, h = 1280, 170
    img = canvas(w, h)
    blob(img, (380, -140, 900, 300), BLUE[:3] + (40,), 100)
    img.alpha_composite(circuit(w, h, 900, seed=9))
    fg = Image.new("RGBA", img.size)
    d = ImageDraw.Draw(fg)
    d.text(P(w / 2, 72), "Let's build something that matters.", font=font("segoeuib.ttf", 34), fill=TEXT, anchor="ms")
    d.text(P(w / 2, 108), "Open to internships, research collaborations and embedded / IoT projects",
           font=font("segoeui.ttf", 18), fill=MUTED + (255,), anchor="ms")
    img.alpha_composite(fg)
    bottom_bar(img)
    save(img, "footer.png", w, h)


if __name__ == "__main__":
    header()
    about_photo()
    footer()

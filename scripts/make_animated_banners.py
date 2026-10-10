"""Generate the animated SVG header, footer and project banners for the GitHub profile README.

Output goes to assets/animated/. Animations are CSS-only, so they play when GitHub shows the
SVG as an image, and they switch off for visitors who ask their system for reduced motion.

Private projects get a lock tag instead of tech chips, and no technical detail.
"""
import base64, html, io, math, os, random
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "assets", "animated")
PHOTOS = os.path.join(HERE, "photos")
os.makedirs(OUT, exist_ok=True)

W, H = 1280, 320
SANS = "'Segoe UI','Helvetica Neue',Helvetica,Arial,sans-serif"
MONO = "Consolas,'SFMono-Regular',Menlo,'Courier New',monospace"
_measure = ImageFont.truetype(r"C:\Windows\Fonts\seguisb.ttf", 130)


def text_w(s, size):
    return _measure.getlength(s) * size / 130


BASE_CSS = """
  .sans{font-family:%s}
  .mono{font-family:%s}
  .fade-in{animation:fadeIn 1s ease-out both}
  @keyframes fadeIn{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}
  @keyframes shimmer{from{transform:translateX(-400px)}to{transform:translateX(1700px)}}
  @keyframes pulse{0%%,100%%{opacity:.35}50%%{opacity:1}}
  @keyframes blink{0%%,49%%{opacity:1}50%%,100%%{opacity:0}}
  @keyframes spin{to{transform:rotate(360deg)}}
  @media (prefers-reduced-motion: reduce){*{animation:none!important}}
""" % (SANS, MONO)


def defs_common(accent, accent2):
    return f'''
    <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#0b111d"/><stop offset="1" stop-color="#0f1726"/>
    </linearGradient>
    <pattern id="dots" width="28" height="28" patternUnits="userSpaceOnUse">
      <circle cx="14" cy="14" r="1" fill="#fff" fill-opacity="0.09"/>
    </pattern>
    <radialGradient id="glowR" cx="0.78" cy="0.5" r="0.45">
      <stop offset="0" stop-color="{accent}" stop-opacity="0.16"/><stop offset="1" stop-color="{accent}" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="bar" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="{accent}"/><stop offset="1" stop-color="{accent2}"/>
    </linearGradient>
    <linearGradient id="shine" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset="0.5" stop-color="#fff" stop-opacity="0.85"/><stop offset="1" stop-color="#fff" stop-opacity="0"/>
    </linearGradient>
    <linearGradient id="fadeMaskGrad" gradientUnits="userSpaceOnUse" x1="640" y1="0" x2="860" y2="0">
      <stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#fff" stop-opacity="1"/>
    </linearGradient>
    <mask id="fadeMask" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}">
      <rect width="{W}" height="{H}" fill="url(#fadeMaskGrad)"/>
    </mask>
    <filter id="soft" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="4"/></filter>'''


def lock_icon(x, y, color="#cbd5e1"):
    return (f'<g transform="translate({x} {y})" fill="none" stroke="{color}" stroke-width="1.8" stroke-linecap="round">'
            f'<rect x="-6" y="-2" width="12" height="9" rx="2" fill="{color}" fill-opacity="0.15"/>'
            f'<path d="M-3.5 -2 V-5 a3.5 3.5 0 0 1 7 0 V-2"/></g>')


def chips_svg(chips, x, y, accent):
    out, cx = [], x
    for c in chips:
        w = text_w(c, 13) + 26
        out.append(f'<rect x="{cx:.1f}" y="{y}" width="{w:.1f}" height="26" rx="13" fill="#1e293b" stroke="#94a3b8" stroke-opacity="0.28"/>'
                   f'<text x="{cx + w / 2:.1f}" y="{y + 17.5}" text-anchor="middle" class="sans" font-size="13" font-weight="600" fill="#cbd5e1">{html.escape(c)}</text>')
        cx += w + 8
    return "".join(out)


def private_tag(x, y, accent):
    label = "Private project"
    w = text_w(label, 13) + 46
    return (f'<rect x="{x}" y="{y}" width="{w:.1f}" height="26" rx="13" fill="{accent}" fill-opacity="0.12" stroke="{accent}" stroke-opacity="0.55"/>'
            + lock_icon(x + 18, y + 12, accent)
            + f'<text x="{x + 32}" y="{y + 17.5}" class="sans" font-size="13" font-weight="700" fill="#e2e8f0">{label}</text>')


def banner(name, title, tagline, accent, accent2, icon, visual, css="", chips=None, private=False, extra_defs=""):
    title_size = 50 if text_w(title, 50) < 560 else 44
    title, tagline = html.escape(title), html.escape(tagline)
    lower = private_tag(190, 214, accent) if private else chips_svg(chips or [], 190, 214, accent)
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{title}: {tagline}">
  <defs>{defs_common(accent, accent2)}{extra_defs}
    <style>{BASE_CSS}
      .bar-shine{{animation:shimmer 5s ease-in-out infinite}}
      .icon-pulse{{animation:pulse 3s ease-in-out infinite}}
{css}
    </style>
  </defs>
  <rect width="{W}" height="{H}" fill="url(#bg)"/>
  <rect width="{W}" height="{H}" fill="url(#dots)"/>
  <rect width="{W}" height="{H}" fill="url(#glowR)"/>

  <g mask="url(#fadeMask)">
{visual}
  </g>

  <g class="fade-in">
    <rect x="60" y="112" width="100" height="100" rx="22" fill="{accent}" fill-opacity="0.10" stroke="{accent}" stroke-opacity="0.65" stroke-width="2"/>
    <rect x="60" y="112" width="100" height="100" rx="22" fill="none" stroke="{accent}" stroke-width="2" class="icon-pulse" filter="url(#soft)"/>
    <g transform="translate(110 162)" fill="none" stroke="{accent}" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round">{icon}</g>
    <text x="188" y="164" class="sans" font-size="{title_size}" font-weight="700" fill="#f1f5f9">{title}</text>
    <text x="190" y="198" class="sans" font-size="19" fill="#94a3b8">{tagline}</text>
    {lower}
  </g>

  <rect x="0" y="{H - 4}" width="{W}" height="4" fill="url(#bar)"/>
  <rect x="0" y="{H - 4}" width="260" height="4" fill="url(#shine)" class="bar-shine" opacity="0.7"/>
</svg>
'''
    with open(os.path.join(OUT, name + ".svg"), "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"{name}.svg  {len(svg) // 1024} KB")


# ───────────────────────────── helpers for visuals ─────────────────────────────
def jpeg_b64(img, q=82):
    buf = io.BytesIO(); img.convert("RGB").save(buf, "JPEG", quality=q, optimize=True)
    return base64.b64encode(buf.getvalue()).decode()


def wave_path(y, amp, length, x0=600, x1=1300):
    d = f"M{x0} {y}"
    x = x0
    while x < x1 + 2 * length:
        d += f" q{length / 4} {-amp} {length / 2} 0 t{length / 2} 0"
        x += length
    return d


# ───────────────────────────── 1. EMG recorder (public) ─────────────────────────────
def emg():
    random.seed(11)
    cols = ["#2dd4bf", "#f59e0b", "#a78bfa"]
    rows = []
    for i, c in enumerate(cols):
        y = 92 + i * 70
        seg = []
        x = 0
        while x <= 640:
            ph = (x + i * 70) % 213
            burst = 40 < ph < 120
            a = (22 * math.sin(math.pi * (ph - 40) / 80) + 6) if burst else 2.5
            seg.append(f"L{x} {y + random.uniform(-a, a):.1f}")
            x += 3
        tile = f"M0 {y} " + " ".join(seg)
        rows.append(f'''    <g class="emg{i}"><path d="{tile}" fill="none" stroke="{c}" stroke-width="1.6"/>
      <path d="{tile}" transform="translate(640 0)" fill="none" stroke="{c}" stroke-width="1.6"/></g>''')
    labels = "".join(f'<text x="1236" y="{92 + i * 70 - 14}" text-anchor="end" class="mono" font-size="11" fill="{c}" opacity="0.8">CH{i}</text>'
                     for i, c in enumerate(cols))
    visual = '<g transform="translate(600 0)">' + '\n'.join(rows) + '</g>' + labels
    css = "\n".join(f"      .emg{i}{{animation:scroll {6 + i}s linear infinite}}" for i in range(3))
    css += "\n      @keyframes scroll{to{transform:translateX(-640px)}}"
    icon = '<path d="M-30 0 H-16 L-10 -18 L-2 22 L6 -28 L12 14 L17 0 H30"/>'
    banner("emg-recorder", "EMG Recorder", "Real-time 3-channel EMG acquisition · NI USB-6009",
           "#2dd4bf", "#a78bfa", icon, visual, css, chips=["PySide6", "NumPy", "NI-DAQmx", "Notch filter"])


# ───────────────────────────── 2. Flood Web Monitor (public) ─────────────────────────────
def flood_web():
    x0, x1, base = 700, 1240, 270
    def curve(c, amp, phase, n=90):
        pts = []
        for i in range(n + 1):
            t = i / n
            v = c + amp * math.exp(-((t - 0.55 - phase) / 0.16) ** 2) + 6 * math.sin(t * 9 + phase * 10)
            pts.append((x0 + t * (x1 - x0), base - v))
        return "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts)
    thr = "".join(f'<line x1="{x0}" x2="{x1}" y1="{y}" y2="{y}" stroke="{c}" stroke-width="1.4" stroke-dasharray="7 6" opacity="0.75"/>'
                  for y, c in [(92, "#ef4444"), (122, "#fbbf24"), (152, "#c084fc")])
    random.seed(4)
    bars = "".join(f'<rect class="rain" style="animation-delay:{i * 0.07:.2f}s" x="{x0 + 8 + i * 13}" y="{base - h:.0f}" width="9" height="{h:.0f}" rx="2" fill="#4a9eff" fill-opacity="0.35"/>'
                   for i, h in enumerate([max(4, 46 * math.exp(-((j - 22) / 7) ** 2) + random.uniform(0, 10)) for j in range(41)]))
    visual = f'''    {thr}
    {bars}
    <path d="{curve(60, 110, 0)}" class="draw" fill="none" stroke="#4a9eff" stroke-width="3.2" stroke-linejoin="round"/>
    <path d="{curve(40, 70, 0.02)}" class="draw d2" fill="none" stroke="#34d399" stroke-width="2.6" stroke-linejoin="round"/>
    <g class="live"><rect x="1150" y="30" width="74" height="26" rx="13" fill="#ef4444" fill-opacity="0.18" stroke="#ef4444"/>
      <circle cx="1168" cy="43" r="5" fill="#ef4444" class="blinkdot"/>
      <text x="1180" y="48" class="sans" font-size="13" font-weight="700" fill="#fecaca">LIVE</text></g>'''
    css = '''      .draw{stroke-dasharray:900;stroke-dashoffset:900;animation:draw 6s ease-in-out infinite}
      .d2{animation-delay:.4s}
      @keyframes draw{0%{stroke-dashoffset:900}45%,85%{stroke-dashoffset:0}100%{stroke-dashoffset:-900}}
      .rain{transform-box:fill-box;transform-origin:bottom;animation:grow 6s ease-in-out infinite}
      @keyframes grow{0%{transform:scaleY(0)}35%,85%{transform:scaleY(1)}100%{transform:scaleY(0)}}
      .blinkdot{animation:pulse 1.2s ease-in-out infinite}'''
    icon = '<path d="M-28 22 V8 M-14 22 V-2 M0 22 V10 M14 22 V-8 M28 22 V2"/><path d="M-30 -4 L-14 -16 L0 -6 L14 -24 L30 -14" stroke-width="3"/>'
    banner("flood-web-monitor", "Flood Web Monitor", "Live water level & rainfall dashboard · Peradeniya · Nawalapitiya",
           "#4a9eff", "#34d399", icon, visual, css, chips=["Live on GitHub Pages", "JavaScript", "Plotly.js", "ArcGIS"])


# ───────────────────────────── 3. HydroSync Studio (public) ─────────────────────────────
def hydrosync():
    rows = []
    for i in range(5):
        x = 850 + i * 52; y = 58 + i * 24
        rows.append(f'<g class="exp" style="animation-delay:{i * 0.35:.2f}s"><rect x="{x}" y="{y}" width="180" height="18" rx="9" fill="#38bdf8" fill-opacity="{0.3 + i * 0.12:.2f}"/>'
                    f'<text x="{x + 172}" y="{y + 13}" text-anchor="end" class="mono" font-size="11" fill="#e0f2fe">export {i + 1} · 72 h</text></g>')
    arrows = "".join(f'<g class="arr" style="animation-delay:{1.8 + i * 0.25:.2f}s"><path d="M{x} 188 v26 m-7 -8 l7 8 l7 -8" fill="none" stroke="#22c55e" stroke-width="2.4" stroke-linecap="round"/></g>'
                     for i, x in enumerate([920, 1040, 1160]))
    visual = f'''    {''.join(rows)}
    {arrows}
    <rect x="800" y="226" width="440" height="12" rx="6" fill="#22c55e" class="merged"/>
    <text x="1240" y="258" text-anchor="end" class="mono" font-size="11" fill="#86efac">1 row / hour / station</text>
    <path d="{wave_path(290, 9, 160, 700, 1300)}" fill="none" stroke="#38bdf8" stroke-opacity="0.5" stroke-width="2" class="wave"/>'''
    css = '''      .exp{animation:slide 7s ease-in-out infinite;opacity:0}
      @keyframes slide{0%{opacity:0;transform:translateX(80px)}12%,80%{opacity:1;transform:none}100%{opacity:0}}
      .arr{animation:drop 7s ease-in-out infinite;opacity:0}
      @keyframes drop{0%,20%{opacity:0;transform:translateY(-10px)}35%,80%{opacity:1;transform:none}100%{opacity:0}}
      .merged{animation:pulse 3.5s ease-in-out infinite}
      .wave{animation:wv 4s linear infinite}
      @keyframes wv{to{transform:translateX(-160px)}}'''
    icon = '<path d="M-24 -6 A26 26 0 0 1 22 -14 M22 -14 L24 -26 M22 -14 L10 -14"/><path d="M24 6 A26 26 0 0 1 -22 14 M-22 14 L-24 26 M-22 14 L-10 14"/><circle cx="0" cy="0" r="5" fill="currentColor"/>'
    banner("hydrosync", "HydroSync Studio", "Overlapping gauge exports → one clean hourly dataset",
           "#38bdf8", "#22c55e", icon, visual, css, chips=["FloodLink 2.0", "PySide6", "pandas", "Windows .exe"])


# ───────────────────────────── 4. FloodLink 1.0 (private) ─────────────────────────────
def floodlink():
    thr = "".join(f'<line x1="700" x2="1250" y1="{y}" y2="{y}" stroke="{c}" stroke-width="1.3" stroke-dasharray="7 6" opacity="0.7"/>'
                  f'<text x="1250" y="{y - 6}" text-anchor="end" class="mono" font-size="11" fill="{c}">{t}</text>'
                  for y, c, t in [(118, "#ef4444", "MAJOR"), (150, "#fbbf24", "MINOR"), (182, "#c084fc", "ALERT")])
    visual = f'''    {thr}
    <g class="water">
      <path d="{wave_path(214, 10, 180)}  V340 H600 Z" fill="#22d3ee" fill-opacity="0.22" class="w1"/>
      <path d="{wave_path(224, 8, 140)}  V340 H600 Z" fill="#0891b2" fill-opacity="0.45" class="w2"/>
    </g>
    <line x1="1080" y1="70" x2="1080" y2="300" stroke="#cbd5e1" stroke-width="4"/>
    <rect x="1064" y="52" width="32" height="28" rx="6" fill="#0f172a" stroke="#22d3ee" stroke-width="2"/>
    <circle cx="1080" cy="66" r="3.5" fill="#22d3ee"/>
    <g fill="none" stroke="#22d3ee" stroke-width="2.4" stroke-linecap="round">
      <path class="rw r1" d="M1066 40 A20 20 0 0 1 1094 40"/>
      <path class="rw r2" d="M1058 30 A32 32 0 0 1 1102 30"/>
      <path class="rw r3" d="M1050 20 A44 44 0 0 1 1110 20"/>
    </g>'''
    css = '''      .water{animation:rise 8s ease-in-out infinite}
      @keyframes rise{0%,100%{transform:translateY(40px)}50%{transform:translateY(-22px)}}
      .w1{animation:wv 5s linear infinite}.w2{animation:wv 3.6s linear infinite reverse}
      @keyframes wv{to{transform:translateX(-180px)}}
      .rw{animation:pulse 1.8s ease-out infinite}.r2{animation-delay:.3s}.r3{animation-delay:.6s}'''
    icon = '<path d="M-14 -16 A20 20 0 0 1 14 -16 M-7 -8 A10 10 0 0 1 7 -8"/><circle cx="0" cy="-1" r="2" fill="currentColor"/><path d="M-30 14 q7.5 -8 15 0 t15 0 t15 0 t15 0 M-30 26 q7.5 -8 15 0 t15 0 t15 0 t15 0"/>'
    banner("floodlink", "FloodLink 1.0", "Flood early-warning system for the Mahaweli River",
           "#22d3ee", "#0891b2", icon, visual, css, private=True)


# ───────────────────────────── 5. Water level forecasting (private) ─────────────────────────────
def water_level():
    now_x = 1010
    obs = [(700 + t * (now_x - 700), 250 - 150 * math.exp(-((t - 0.78) / 0.22) ** 2)) for t in [i / 60 for i in range(61)]]
    fc = [(now_x + t * 230, obs[-1][1] + 90 * (1 - math.exp(-t * 2.2)) * 0.9) for t in [i / 40 for i in range(41)]]
    p_obs = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in obs)
    p_fc = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in fc)
    band_up = [(x, y - 8 - (x - now_x) * 0.14) for x, y in fc]
    band_dn = [(x, y + 8 + (x - now_x) * 0.14) for x, y in reversed(fc)]
    p_band = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in band_up + band_dn) + " Z"
    ticks = "".join(f'<text x="{now_x + o}" y="300" text-anchor="middle" class="mono" font-size="11" fill="#fbbf24">{l}</text>'
                    for o, l in [(40, "+1 h"), (120, "+3 h"), (220, "+6 h")])
    visual = f'''    <path d="{p_band}" fill="#f59e0b" fill-opacity="0.18"/>
    <path d="{p_obs}" fill="none" stroke="#e2e8f0" stroke-width="3"/>
    <line x1="{now_x}" y1="40" x2="{now_x}" y2="280" stroke="#94a3b8" stroke-width="1.4" stroke-dasharray="4 5"/>
    <text x="{now_x - 8}" y="54" text-anchor="end" class="mono" font-size="11" fill="#94a3b8">now</text>
    <path d="{p_fc}" fill="none" stroke="#f59e0b" stroke-width="3" stroke-dasharray="2 8" stroke-linecap="round" class="march"/>
    <g class="fcdot" style="offset-path:path('{p_fc}')"><circle r="7" fill="#f59e0b" fill-opacity="0.35"/><circle r="4" fill="#fde68a"/></g>
    {ticks}'''
    css = '''      .march{animation:march 1s linear infinite}
      @keyframes march{to{stroke-dashoffset:-10}}
      .fcdot{offset-rotate:0deg;animation:fc 4s ease-in-out infinite}
      @keyframes fc{0%{offset-distance:0%;opacity:0}10%{opacity:1}90%{opacity:1}100%{offset-distance:100%;opacity:0}}'''
    icon = ''.join(f'<circle cx="{x}" cy="{y}" r="4.5" fill="currentColor" stroke="none"/>' for x, y in [(-24, -16), (-24, 16), (0, -24), (0, 0), (0, 24), (24, -8), (24, 8)]) + \
        '<path d="M-24 -16 L0 -24 M-24 -16 L0 0 M-24 -16 L0 24 M-24 16 L0 -24 M-24 16 L0 0 M-24 16 L0 24 M0 -24 L24 -8 M0 0 L24 -8 M0 0 L24 8 M0 24 L24 8" stroke-width="1.6" opacity="0.7"/>'
    banner("water-level-model", "Water Level Forecasting", "Forecasting the river level at Peradeniya hours ahead",
           "#f59e0b", "#ef4444", icon, visual, css, private=True)


# ───────────────────────────── 6. FlyMe hardware (private) ─────────────────────────────
def flyme_hw():
    visual = '''    <g transform="translate(860 86) rotate(28)">
      <path d="M0 -30 L6 -8 L34 4 L34 10 L6 4 L4 22 L13 30 L13 34 L0 30 L-13 34 L-13 30 L-4 22 L-6 4 L-34 10 L-34 4 L-6 -8 Z" fill="#f1f5f9"/>
    </g>
    <g>
      <circle class="pkt" style="animation-delay:0s" cx="0" cy="0" r="4" fill="#fb923c"/>
      <circle class="pkt" style="animation-delay:.33s" cx="0" cy="0" r="4" fill="#fb923c"/>
      <circle class="pkt" style="animation-delay:.66s" cx="0" cy="0" r="4" fill="#fb923c"/>
    </g>
    <path d="M832 120 L768 254" stroke="#fb923c" stroke-opacity="0.25" stroke-width="2" stroke-dasharray="3 6"/>
    <rect x="736" y="272" width="48" height="26" rx="5" fill="#1f2937" stroke="#94a3b8" stroke-width="1.6"/>
    <circle cx="748" cy="285" r="3" fill="#4cd787" class="rw"/><rect x="756" y="282" width="20" height="5" rx="2" fill="#475569"/>
    <path d="M770 272 V254" stroke="#94a3b8" stroke-width="2.4" stroke-linecap="round"/>
    <g fill="none" stroke="#fb923c" stroke-width="2" stroke-linecap="round">
      <path class="rw" d="M760 248 A12 12 0 0 1 780 248"/><path class="rw r2" d="M753 240 A22 22 0 0 1 787 240"/>
    </g>
    <g transform="translate(1110 160)">
      <circle r="92" fill="#1c1917" stroke="#fb923c" stroke-width="3"/>
      <clipPath id="ai"><circle r="88"/></clipPath>
      <g clip-path="url(#ai)"><g class="horizon">
        <rect x="-140" y="-140" width="280" height="140" fill="#1e3a5f"/>
        <rect x="-140" y="0" width="280" height="140" fill="#7c4a1e"/>
        <line x1="-140" x2="140" y1="0" y2="0" stroke="#f1f5f9" stroke-width="2"/>
        <g stroke="#f1f5f9" stroke-width="1.4" opacity="0.8"><line x1="-18" x2="18" y1="-24" y2="-24"/><line x1="-18" x2="18" y1="24" y2="24"/><line x1="-10" x2="10" y1="-48" y2="-48"/><line x1="-10" x2="10" y1="48" y2="48"/></g>
      </g></g>
      <path d="M-46 0 H-16 L-8 10 L0 0 L8 10 L16 0 H46" fill="none" stroke="#fbbf24" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
    </g>'''
    css = '''      .pkt{offset-path:path('M832 120 L768 252');animation:pk 1s linear infinite;opacity:0}
      @keyframes pk{0%{offset-distance:0%;opacity:0}15%{opacity:1}85%{opacity:1}100%{offset-distance:100%;opacity:0}}
      .rw{animation:pulse 1.6s ease-out infinite}.r2{animation-delay:.4s}
      .horizon{animation:roll 6s ease-in-out infinite}
      @keyframes roll{0%,100%{transform:rotate(-14deg) translateY(-8px)}50%{transform:rotate(12deg) translateY(10px)}}'''
    icon = '<rect x="-18" y="-18" width="36" height="36" rx="5"/><rect x="-8" y="-8" width="16" height="16" rx="2" fill="currentColor"/>' + \
        ''.join(f'<path d="M{x} -18 V-28 M{x} 18 V28 M-18 {x} H-28 M18 {x} H28"/>' for x in (-9, 0, 9))
    banner("flyme-hardware", "FlyMe Hardware", "Flight telemetry hardware for an RC aircraft",
           "#fb923c", "#f43f5e", icon, visual, css, private=True)


# ───────────────────────────── 7. FlyMe app (private) ─────────────────────────────
def flyme_app():
    path = "M1010 236 C 940 200, 960 120, 1040 110 S 1150 150, 1120 90"
    visual = f'''    <g transform="translate(0 0)">
      <rect x="930" y="24" width="240" height="280" rx="30" fill="#0b1220" stroke="#94a3b8" stroke-opacity="0.6" stroke-width="2.5"/>
      <rect x="944" y="40" width="212" height="248" rx="20" fill="#111a2b"/>
      <g fill="none" stroke="#a78bfa" stroke-opacity="0.25"><circle cx="1010" cy="236" r="50"/><circle cx="1010" cy="236" r="100"/><circle cx="1010" cy="236" r="150"/></g>
      <path d="{path}" fill="none" stroke="#22d3ee" stroke-width="2.6" stroke-dasharray="3 7" stroke-linecap="round"/>
      <circle cx="1010" cy="236" r="10" fill="#f0b847"/><text x="1010" y="240.5" text-anchor="middle" class="sans" font-size="11" font-weight="800" fill="#0b1220">H</text>
      <g class="plane"><path d="M0 -12 L7 9 L0 4 L-7 9 Z" fill="#f1f5f9" transform="rotate(90)"/></g>
      <rect x="958" y="54" width="92" height="22" rx="11" fill="#0b1220" stroke="#4cd787" stroke-opacity="0.6"/>
      <circle cx="972" cy="65" r="4" fill="#4cd787" class="blink"/>
      <text x="982" y="69.5" class="sans" font-size="11" font-weight="700" fill="#e2e8f0">LIVE</text>
    </g>
    <g class="sans" font-size="13" font-weight="600">
      {''.join(f'<g class="pill" style="animation-delay:{i * 0.6:.1f}s"><rect x="740" y="{100 + i * 46}" width="150" height="30" rx="15" fill="#a78bfa" fill-opacity="0.12" stroke="#a78bfa" stroke-opacity="0.5"/><text x="815" y="{120 + i * 46}" text-anchor="middle" fill="#e9d5ff">{t}</text></g>' for i, t in enumerate(["Live map", "Voice alerts", "Flight replay"]))}
    </g>'''
    css = f'''      .plane{{offset-path:path('{path}');offset-rotate:auto;animation:fly 6s ease-in-out infinite alternate}}
      @keyframes fly{{from{{offset-distance:0%}}to{{offset-distance:100%}}}}
      .blink{{animation:pulse 1.2s ease-in-out infinite}}
      .pill{{animation:fadeIn 1s ease-out both}}'''
    icon = '<rect x="-17" y="-28" width="34" height="56" rx="7"/><path d="M0 -12 a8 8 0 0 1 8 8 c0 7 -8 14 -8 14 s-8 -7 -8 -14 a8 8 0 0 1 8 -8 z" stroke-width="2.6"/><path d="M-5 21 H5"/>'
    banner("flyme-app", "FlyMe Ground Station", "Android app for tracking an RC aircraft live",
           "#a78bfa", "#22d3ee", icon, visual, css, private=True)


# ───────────────────────────── 8. MicroMouse (private) ─────────────────────────────
def micromouse():
    ox, oy, c, n = 900, 30, 32, 8
    random.seed(21)
    # perfect maze (recursive backtracker): open[(cell, neighbour)] = True when there is no wall
    opened, seen, stack = set(), {(0, n - 1)}, [(0, n - 1)]
    while stack:
        x, y = stack[-1]
        nb = [(x + dx, y + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))
              if 0 <= x + dx < n and 0 <= y + dy < n and (x + dx, y + dy) not in seen]
        if not nb:
            stack.pop(); continue
        nx, ny = random.choice(nb)
        opened.add(frozenset(((x, y), (nx, ny)))); seen.add((nx, ny)); stack.append((nx, ny))
    # walls: every grid edge that is not opened
    segs = [f"M{ox} {oy} H{ox + n * c} V{oy + n * c} H{ox} Z"]
    for x in range(n):
        for y in range(n):
            if x + 1 < n and frozenset(((x, y), (x + 1, y))) not in opened:
                segs.append(f"M{ox + (x + 1) * c} {oy + y * c} v{c}")
            if y + 1 < n and frozenset(((x, y), (x, y + 1))) not in opened:
                segs.append(f"M{ox + x * c} {oy + (y + 1) * c} h{c}")
    walls = " ".join(segs)
    # breadth-first search from the start corner to the centre goal
    start, goal = (0, n - 1), (n // 2, n // 2)
    prev, q = {start: None}, [start]
    while q:
        cur = q.pop(0)
        if cur == goal:
            break
        for e in opened:
            if cur in e:
                (nxt,) = e - {cur}
                if nxt not in prev:
                    prev[nxt] = cur; q.append(nxt)
    cells, cur = [], goal
    while cur:
        cells.append(cur); cur = prev[cur]
    cells.reverse()
    sol = "M" + " L".join(f"{ox + x * c + c / 2:.0f} {oy + y * c + c / 2:.0f}" for x, y in cells)
    plen = (len(cells) - 1) * c + 10
    gx, gy = ox + goal[0] * c, oy + goal[1] * c
    visual = f'''    <path d="{walls}" fill="none" stroke="#7f1d1d" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>
    <path d="{walls}" fill="none" stroke="#f43f5e" stroke-opacity="0.6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    <rect x="{gx + 3}" y="{gy + 3}" width="{c - 6}" height="{c - 6}" rx="4" fill="#fbbf24" fill-opacity="0.22" class="goal"/>
    <path d="{sol}" fill="none" stroke="#fbbf24" stroke-width="8" stroke-linejoin="round" stroke-linecap="round" opacity="0.3" filter="url(#soft)" class="solve"/>
    <path d="{sol}" fill="none" stroke="#fde047" stroke-width="3.5" stroke-linejoin="round" stroke-linecap="round" class="solve"/>
    <g class="mouse"><circle r="8" fill="#e2e8f0"/><circle r="2.6" cx="4" fill="#0b111d"/></g>'''
    css = f'''      .solve{{stroke-dasharray:{plen};stroke-dashoffset:{plen};animation:solve 7s linear infinite}}
      @keyframes solve{{0%{{stroke-dashoffset:{plen}}}70%,90%{{stroke-dashoffset:0;opacity:1}}100%{{stroke-dashoffset:0;opacity:0}}}}
      .mouse{{offset-path:path('{sol}');offset-rotate:auto;animation:run 7s linear infinite}}
      @keyframes run{{0%{{offset-distance:0%}}70%,100%{{offset-distance:100%}}}}
      .goal{{animation:pulse 1.6s ease-in-out infinite}}'''
    icon = '<rect x="-26" y="-26" width="52" height="52" rx="6"/><path d="M-26 -6 H2 M12 -26 V12 M-10 12 H26" stroke-width="3"/><circle cx="-14" cy="18" r="5" fill="currentColor"/>'
    banner("micromouse", "MicroMouse", "Autonomous maze-solving robot",
           "#f43f5e", "#fbbf24", icon, visual, css, private=True)


# ───────────────────────────── 9. Sobel on FPGA (private) ─────────────────────────────
def sobel():
    mem = os.path.join(HERE, "..", "..", "Sobel Filter On FPGA Board", "milestone-2-fpga", "mem", "image_320x240.mem")
    import numpy as np
    g = np.array([int(l, 16) for l in open(mem) if l.strip()], dtype=np.uint8).reshape(240, 320).astype(int)
    gx = np.zeros_like(g); gy = np.zeros_like(g)
    gx[1:-1, 1:-1] = (g[:-2, 2:] - g[:-2, :-2]) + 2 * (g[1:-1, 2:] - g[1:-1, :-2]) + (g[2:, 2:] - g[2:, :-2])
    gy[1:-1, 1:-1] = (g[:-2, :-2] - g[2:, :-2]) + 2 * (g[:-2, 1:-1] - g[2:, 1:-1]) + (g[:-2, 2:] - g[2:, 2:])
    e = np.clip(np.abs(gx) + np.abs(gy), 0, 255).astype(float) / 255
    e = np.clip(e * 1.6, 0, 1)[..., None]
    col = np.array([11, 17, 29]) * (1 - e) + np.array([232, 121, 249]) * e
    edge = Image.fromarray(col.clip(0, 255).astype("uint8")).resize((360, 270), Image.LANCZOS)
    gray = Image.fromarray((g * 0.55 + 12).clip(0, 255).astype("uint8")).resize((360, 270), Image.LANCZOS)
    X, Y, IW, IH = 870, 26, 360, 270
    visual = f'''    <rect x="{X - 8}" y="{Y - 8}" width="{IW + 16}" height="{IH + 16}" rx="12" fill="#111827" stroke="#e879f9" stroke-opacity="0.45" stroke-width="2"/>
    <image x="{X}" y="{Y}" width="{IW}" height="{IH}" xlink:href="data:image/jpeg;base64,{jpeg_b64(gray)}"/>
    <image x="{X}" y="{Y}" width="{IW}" height="{IH}" class="edge" xlink:href="data:image/jpeg;base64,{jpeg_b64(edge)}"/>
    <g class="scan"><rect x="{X - 2}" y="{Y}" width="4" height="{IH}" fill="#f5d0fe"/><rect x="{X - 10}" y="{Y}" width="20" height="{IH}" fill="#e879f9" opacity="0.35" filter="url(#soft)"/></g>
    <g class="mono" font-size="13" fill="#f5d0fe" opacity="0.85">
      <text x="720" y="110">[-1  0 +1]</text><text x="720" y="130">[-2  0 +2]</text><text x="720" y="150">[-1  0 +1]</text>
      <text x="720" y="88" fill="#e879f9" font-weight="700">Gx</text>
    </g>'''
    css = f'''      .edge{{animation:reveal 6s ease-in-out infinite}}
      @keyframes reveal{{0%{{clip-path:inset(0 100% 0 0)}}45%,75%{{clip-path:inset(0 0 0 0)}}100%{{clip-path:inset(0 100% 0 0)}}}}
      .scan{{animation:scan 6s ease-in-out infinite}}
      @keyframes scan{{0%{{transform:translateX(0)}}45%,75%{{transform:translateX({IW}px)}}100%{{transform:translateX(0)}}}}'''
    icon = ''.join(f'<rect x="{-27 + i * 19}" y="{-27 + j * 19}" width="16" height="16" rx="3" {"fill=\"currentColor\"" if (i, j) in [(0, 0), (2, 2), (1, 1)] else ""}/>' for i in range(3) for j in range(3))
    banner("sobel-fpga", "Sobel Filter on FPGA", "Real-time edge detection in hardware, shown live on a monitor",
           "#e879f9", "#22d3ee", icon, visual, css, private=True)


# ───────────────────────────── 10. DJI RC video bridge (private) ─────────────────────────────
def dji():
    visual = '''    <g transform="translate(760 120)">
      <rect x="-52" y="-28" width="104" height="56" rx="26" fill="#1f2937" stroke="#64748b" stroke-width="1.5"/>
      <circle cx="-25" cy="0" r="12" fill="#0f172a" stroke="#64748b"/><circle cx="-25" cy="0" r="5" fill="#94a3b8"/>
      <circle cx="25" cy="0" r="12" fill="#0f172a" stroke="#64748b"/><circle cx="25" cy="0" r="5" fill="#94a3b8"/>
    </g>
    <g transform="translate(960 120)">
      <rect x="-58" y="-38" width="116" height="76" rx="7" fill="#14532d" stroke="#22c55e" stroke-opacity="0.6" stroke-width="1.5"/>
      <rect x="-18" y="-14" width="30" height="30" rx="3" fill="#cbd5e1"/>
      <rect x="20" y="-12" width="20" height="16" rx="2" fill="#1f2937"/>
      <g fill="#facc15" fill-opacity="0.85">''' + ''.join(f'<rect x="{-50 + i * 7}" y="-34" width="3.5" height="5" rx="1"/>' for i in range(14)) + '''</g>
    </g>
    <g transform="translate(1160 120)">
      <rect x="-30" y="-54" width="60" height="108" rx="10" fill="#0f172a" stroke="#64748b" stroke-width="1.5"/>
      <rect x="-25" y="-46" width="50" height="88" rx="5" fill="#1e3a5f"/>
      <path d="M-25 24 L-8 4 L4 16 L12 8 L25 20 V42 H-25 Z" fill="#14532d" fill-opacity="0.8"/>
    </g>
    <g transform="translate(960 252)">
      <rect x="-86" y="-40" width="172" height="80" rx="7" fill="#0f172a" stroke="#38bdf8" stroke-opacity="0.7" stroke-width="1.5"/>
      <rect x="-79" y="-33" width="158" height="66" rx="4" fill="#1e3a5f"/>
      <path d="M-79 20 L-48 -2 L-24 12 L4 -10 L40 14 L79 -2 V33 H-79 Z" fill="#14532d" fill-opacity="0.8"/>
      <rect x="-72" y="-27" width="34" height="12" rx="3" fill="#ef4444" class="rec"/>
      <text x="-55" y="-18" text-anchor="middle" class="sans" font-size="8.5" font-weight="800" fill="#fff">LIVE</text>
    </g>
    <g fill="none" stroke-width="3" stroke-linecap="round" stroke-dasharray="2 10">
      <path d="M814 120 H900" stroke="#fb7185" class="flow"/>
      <path d="M1020 120 H1128" stroke="#fb7185" class="flow"/>
      <path d="M960 160 V210" stroke="#7dd3fc" class="flow"/>
    </g>'''
    css = '''      .flow{animation:dash 1.1s linear infinite}
      @keyframes dash{to{stroke-dashoffset:-24}}
      .rec{animation:pulse 1.4s ease-in-out infinite}'''
    icon = '<rect x="-28" y="-20" width="56" height="34" rx="4"/><path d="M-12 24 H12 M0 14 V24"/><path d="M-8 -9 L8 -3 L-8 3 Z" fill="currentColor" stroke-width="2"/>'
    banner("dji-video-bridge", "Drone Video Bridge", "Live drone camera feed on HDMI, straight from the remote",
           "#fb7185", "#38bdf8", icon, visual, css, private=True)


# ───────────────────────────── header & footer ─────────────────────────────
GRAD = ["#22d3ee", "#4a9eff", "#a78bfa"]


def circuit_traces(seed, x_from, x_to, h, n=22):
    random.seed(seed)
    out = []
    for k in range(n):
        x = random.randint(x_from, x_to - 40); y = random.choice(range(30, h - 30, 22))
        d = f"M{x} {y}"
        for _ in range(random.randint(2, 4)):
            if random.random() < 0.5:
                x += random.choice((-1, 1)) * random.randint(40, 140)
            else:
                dy = random.choice((-1, 1)) * random.randint(20, 60); x += abs(dy) * random.choice((-1, 1)); y += dy
            x = max(x_from - 60, min(x_to - 10, x)); y = max(16, min(h - 16, y))
            d += f" L{x} {y}"
        col = GRAD[min(2, int((k / n) * 3))]
        out.append(f'<path d="{d}" fill="none" stroke="{col}" stroke-opacity="0.16" stroke-width="2"/>'
                   f'<path d="{d}" fill="none" stroke="{col}" stroke-opacity="0.8" stroke-width="2.4" stroke-linecap="round" class="pulse-trace" style="animation-delay:{random.uniform(0, 6):.2f}s"/>'
                   f'<circle cx="{x}" cy="{y}" r="4" fill="none" stroke="{col}" stroke-opacity="0.35" stroke-width="2"/>')
    return "".join(out)


HF_CSS = """
      .pulse-trace{stroke-dasharray:26 600;stroke-dashoffset:626;animation:trace 6s linear infinite}
      @keyframes trace{to{stroke-dashoffset:0}}
      .blob1{animation:drift 14s ease-in-out infinite alternate}
      .blob2{animation:drift 18s ease-in-out infinite alternate-reverse}
      @keyframes drift{from{transform:translate(0,0)}to{transform:translate(60px,30px)}}
"""


def header():
    w, h = 1280, 400
    ph = Image.open(os.path.join(PHOTOS, "suit.jpg")).convert("RGB").crop((560, 580, 1340, 1360)).resize((300, 300), Image.LANCZOS)
    cx, cy, r = 205, 200, 128
    tx = 395
    chips = ["Embedded Systems", "IoT &amp; LoRa", "Data &amp; Machine Learning", "Drones &amp; Aerial Media"]
    chip_svg, x = [], tx
    for i, c in enumerate(chips):
        plain = c.replace("&amp;", "&")
        cw = text_w(plain, 15) + 40
        col = GRAD[min(2, round(i / (len(chips) - 1) * 2))]
        chip_svg.append(f'<g class="chip" style="animation-delay:{0.9 + i * 0.15:.2f}s"><rect x="{x:.1f}" y="272" width="{cw:.1f}" height="34" rx="17" fill="{col}" fill-opacity="0.1" stroke="{col}" stroke-opacity="0.7"/>'
                        f'<circle cx="{x + 17:.1f}" cy="289" r="3.5" fill="{col}"/>'
                        f'<text x="{x + cw / 2 + 8:.1f}" y="294" text-anchor="middle" class="sans" font-size="15" font-weight="600" fill="#e2e8f0">{c}</text></g>')
        x += cw + 10
    award = "2nd Place · Idea to Invention 2025"
    aw = text_w(award, 14) + 52
    ax = w - 40 - aw
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="Olitha Induvara, Electrical and Electronic Engineering Undergraduate, University of Peradeniya">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0b111d"/><stop offset="1" stop-color="#0f1726"/></linearGradient>
    <pattern id="dots" width="28" height="28" patternUnits="userSpaceOnUse"><circle cx="14" cy="14" r="1" fill="#fff" fill-opacity="0.08"/></pattern>
    <radialGradient id="b1"><stop offset="0" stop-color="#22d3ee" stop-opacity="0.22"/><stop offset="1" stop-color="#22d3ee" stop-opacity="0"/></radialGradient>
    <radialGradient id="b2"><stop offset="0" stop-color="#a78bfa" stop-opacity="0.24"/><stop offset="1" stop-color="#a78bfa" stop-opacity="0"/></radialGradient>
    <linearGradient id="ring" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#22d3ee"/><stop offset="0.5" stop-color="#4a9eff"/><stop offset="1" stop-color="#a78bfa"/></linearGradient>
    <linearGradient id="bar" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#22d3ee"/><stop offset="0.5" stop-color="#4a9eff"/><stop offset="1" stop-color="#a78bfa"/></linearGradient>
    <linearGradient id="shine" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset="0.5" stop-color="#fff" stop-opacity="0.85"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
    <linearGradient id="tfade" gradientUnits="userSpaceOnUse" x1="760" y1="0" x2="1020" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#fff"/></linearGradient>
    <mask id="tmask" maskUnits="userSpaceOnUse" x="0" y="0" width="{w}" height="{h}"><rect width="{w}" height="{h}" fill="url(#tfade)"/>
      <rect x="{tx - 10}" y="258" width="{x - tx + 20:.0f}" height="62" rx="20" fill="#000" filter="url(#soft)"/>
      <rect x="{ax - 20:.0f}" y="20" width="{aw + 60:.0f}" height="60" rx="20" fill="#000" filter="url(#soft)"/></mask>
    <clipPath id="photo"><circle cx="{cx}" cy="{cy}" r="{r}"/></clipPath>
    <filter id="soft" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="9"/></filter>
    <style>{BASE_CSS}{HF_CSS}
      .ring{{transform-origin:{cx}px {cy}px;animation:spin 12s linear infinite}}
      .caret{{animation:blink 1s step-end infinite}}
      .hello{{animation:fadeIn .8s ease-out both}}
      .name{{animation:fadeIn 1s ease-out .2s both}}
      .role{{animation:fadeIn 1s ease-out .45s both}}
      .meta{{animation:fadeIn 1s ease-out .65s both}}
      .chip{{animation:fadeIn .9s ease-out both}}
      .award-shine{{animation:ashine 4s ease-in-out infinite}}
      @keyframes ashine{{0%,60%{{transform:translateX(-80px)}}100%{{transform:translateX({aw + 80:.0f}px)}}}}
      .bar-shine{{animation:shimmer 5s ease-in-out infinite}}
    </style>
  </defs>
  <rect width="{w}" height="{h}" fill="url(#bg)"/>
  <rect width="{w}" height="{h}" fill="url(#dots)"/>
  <ellipse cx="200" cy="220" rx="330" ry="300" fill="url(#b1)" class="blob1"/>
  <ellipse cx="1170" cy="150" rx="330" ry="300" fill="url(#b2)" class="blob2"/>
  <g mask="url(#tmask)">{circuit_traces(5, 820, w, h, 26)}</g>

  <g class="ring"><circle cx="{cx}" cy="{cy}" r="{r + 9}" fill="none" stroke="url(#ring)" stroke-width="7" filter="url(#soft)" opacity="0.8"/>
    <circle cx="{cx}" cy="{cy}" r="{r + 9}" fill="none" stroke="url(#ring)" stroke-width="6"/></g>
  <image x="{cx - r}" y="{cy - r}" width="{2 * r}" height="{2 * r}" clip-path="url(#photo)" xlink:href="data:image/jpeg;base64,{jpeg_b64(ph, 86)}"/>

  <text x="{tx}" y="92" class="sans hello" font-size="16" font-weight="600" letter-spacing="3.2" fill="#22d3ee">HELLO, I'M</text>
  <g class="name"><text x="{tx - 3}" y="162" class="sans" font-size="66" font-weight="700" fill="#f1f5f9">Olitha Induvara</text>
    <rect x="{tx + text_w('Olitha Induvara', 66) * 1.02 + 6:.0f}" y="112" width="4" height="54" fill="#22d3ee" class="caret"/></g>
  <text x="{tx}" y="204" class="sans role" font-size="25" fill="#cbd5e1">Electrical &amp; Electronic Engineering Undergraduate</text>
  <g class="meta sans" font-size="17" fill="#94a3b8">
    <g transform="translate({tx + 10} 236)" fill="#4a9eff"><path d="M-12 -3 L0 -9 L12 -3 L0 3 Z"/><path d="M-7 0 H7 V7 L0 10 L-7 7 Z"/><rect x="9" y="-3" width="2" height="10"/></g>
    <text x="{tx + 30}" y="243">University of Peradeniya</text>
    <g transform="translate({tx + 30 + text_w('University of Peradeniya', 17) * 0.93 + 26:.0f} 236)" fill="#4a9eff"><circle cx="0" cy="-3" r="6"/><path d="M-5 -1 L5 -1 L0 9 Z"/><circle cx="0" cy="-3" r="2.5" fill="#0b111d"/></g>
    <text x="{tx + 30 + text_w('University of Peradeniya', 17) * 0.93 + 42:.0f}" y="243">Sri Lanka</text>
  </g>
  {''.join(chip_svg)}

  <g class="fade-in">
    <rect x="{ax:.0f}" y="34" width="{aw:.0f}" height="32" rx="16" fill="#f59e0b" fill-opacity="0.12" stroke="#f59e0b" stroke-opacity="0.75"/>
    <clipPath id="ac"><rect x="{ax:.0f}" y="34" width="{aw:.0f}" height="32" rx="16"/></clipPath>
    <g clip-path="url(#ac)"><rect x="{ax:.0f}" y="34" width="60" height="32" fill="url(#shine)" opacity="0.35" class="award-shine"/></g>
    <g transform="translate({ax + 20:.0f} 50)" fill="#fbbf24"><path d="M-7 -8 H7 L5 1 H-5 Z"/><rect x="-1.5" y="1" width="3" height="4"/><rect x="-5" y="5" width="10" height="3"/></g>
    <text x="{ax + 34:.0f}" y="55" class="sans" font-size="14" font-weight="600" fill="#fde68a">{award}</text>
  </g>

  <rect x="0" y="{h - 5}" width="{w}" height="5" fill="url(#bar)"/>
  <rect x="0" y="{h - 5}" width="260" height="5" fill="url(#shine)" class="bar-shine" opacity="0.7"/>
</svg>
'''
    with open(os.path.join(OUT, "header.svg"), "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"header.svg  {len(svg) // 1024} KB")


def footer():
    w, h = 1280, 170
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="Let's build something that matters. Open to internships, research collaborations and embedded / IoT projects.">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0b111d"/><stop offset="1" stop-color="#0f1726"/></linearGradient>
    <pattern id="dots" width="28" height="28" patternUnits="userSpaceOnUse"><circle cx="14" cy="14" r="1" fill="#fff" fill-opacity="0.08"/></pattern>
    <linearGradient id="bar" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#22d3ee"/><stop offset="0.5" stop-color="#4a9eff"/><stop offset="1" stop-color="#a78bfa"/></linearGradient>
    <linearGradient id="shine" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset="0.5" stop-color="#fff" stop-opacity="0.85"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
    <linearGradient id="title" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#f1f5f9"/><stop offset="0.5" stop-color="#bfe9ff"/><stop offset="1" stop-color="#f1f5f9"/></linearGradient>
    <radialGradient id="b1"><stop offset="0" stop-color="#4a9eff" stop-opacity="0.2"/><stop offset="1" stop-color="#4a9eff" stop-opacity="0"/></radialGradient>
    <linearGradient id="tfade" gradientUnits="userSpaceOnUse" x1="980" y1="0" x2="1120" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#fff"/></linearGradient>
    <mask id="tmask" maskUnits="userSpaceOnUse" x="0" y="0" width="{w}" height="{h}"><rect width="{w}" height="{h}" fill="url(#tfade)"/></mask>
    <style>{BASE_CSS}{HF_CSS}
      .bar-shine{{animation:shimmer 5s ease-in-out infinite}}
      .t1{{animation:fadeIn 1s ease-out both}}.t2{{animation:fadeIn 1s ease-out .3s both}}
    </style>
  </defs>
  <rect width="{w}" height="{h}" fill="url(#bg)"/>
  <rect width="{w}" height="{h}" fill="url(#dots)"/>
  <rect x="0" y="0" width="{w}" height="5" fill="url(#bar)"/>
  <rect x="0" y="0" width="260" height="5" fill="url(#shine)" class="bar-shine" opacity="0.7"/>
  <ellipse cx="640" cy="90" rx="420" ry="120" fill="url(#b1)" class="blob1"/>
  <g mask="url(#tmask)">{circuit_traces(9, 900, w, h, 12)}</g>
  <text x="640" y="80" text-anchor="middle" class="sans t1" font-size="34" font-weight="700" fill="url(#title)">Let's build something that matters.</text>
  <text x="640" y="116" text-anchor="middle" class="sans t2" font-size="17" fill="#94a3b8">Open to internships, research collaborations and embedded / IoT projects</text>
</svg>
'''
    with open(os.path.join(OUT, "footer.svg"), "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"footer.svg  {len(svg) // 1024} KB")


# ───────────────────────────── about-me card ─────────────────────────────
ICONS = {
    "wave": '<path d="M-11 -4 q2.75 -4 5.5 0 t5.5 0 t5.5 0 t5.5 0 M-11 4 q2.75 -4 5.5 0 t5.5 0 t5.5 0 t5.5 0"/>',
    "plane": '<path d="M0 -11 L2.5 -3 L11 1 V3.5 L2.5 1.5 L1.5 7 L4.5 9.5 V11 L0 10 L-4.5 11 V9.5 L-1.5 7 L-2.5 1.5 L-11 3.5 V1 L-2.5 -3 Z" fill="currentColor" stroke="none"/>',
    "spark": '<path d="M-10 8 L-4 -1 L1 4 L10 -8"/><circle cx="10" cy="-8" r="2" fill="currentColor"/>',
    "trophy": '<path d="M-6 -9 H6 V-3 a6 6 0 0 1 -12 0 Z M-6 -6 H-10 a3.5 3.5 0 0 0 4 5 M6 -6 H10 a3.5 3.5 0 0 1 -4 5 M0 3 V7 M-5 9 H5"/>',
    "camera": '<rect x="-10" y="-6" width="20" height="14" rx="3"/><circle cx="0" cy="1" r="4"/><path d="M-4 -6 L-2 -9 H2 L4 -6"/>',
    "people": '<circle cx="-4" cy="-4" r="3.5"/><circle cx="6" cy="-3" r="2.8"/><path d="M-11 9 a7 7 0 0 1 14 0 M4 9 a5.5 5.5 0 0 1 8 -5"/>',
}

ABOUT_TILES = [
    ("wave", "#22d3ee", "NOW BUILDING", "FloodLink", "Flood early warning · Mahaweli River"),
    ("plane", "#a78bfa", "ALSO BUILDING", "FlyMe", "RC aircraft telemetry & ground station"),
    ("spark", "#4a9eff", "EXPLORING", "River-level forecasting", "Classical ML & neural networks"),
    ("trophy", "#fbbf24", "RECOGNITION", "2nd Place", "Idea to Invention 2025"),
    ("camera", "#fb7185", "BEYOND CODE", "EngEx 2025 Media Lead", "Drone pilot · photographer · astronomy"),
    ("people", "#34d399", "COMMUNITY", "IEEE PES & IEEE MTT-S", "Former President, Buddhist Society (FoE)"),
]


def about():
    w, h = 1280, 470
    ph = Image.open(os.path.join(PHOTOS, "engex.jpg")).convert("RGB").crop((330, 280, 1030, 1213)).resize((480, 640), Image.LANCZOS)
    PX, PY, PW, PHH = 52, 36, 300, 400
    TX, TY, TW, TH, GX, GY = 392, 222, 270, 98, 14, 14
    tile_svg = []
    for k, (ic, col, lab, main, sub) in enumerate(ABOUT_TILES):
        x = TX + (k % 3) * (TW + GX)
        y = TY + (k // 3) * (TH + GY)
        sub_size = 13 if text_w(sub, 13) < TW - 32 else 12
        tile_svg.append(
            f'<g class="tile" style="animation-delay:{0.5 + k * 0.12:.2f}s">'
            f'<rect x="{x}" y="{y}" width="{TW}" height="{TH}" rx="16" fill="#131c2e" stroke="{col}" stroke-opacity="0.32"/>'
            f'<rect x="{x}" y="{y + 18}" width="3" height="{TH - 36}" rx="1.5" fill="{col}"/>'
            f'<circle cx="{x + 34}" cy="{y + 32}" r="17" fill="{col}" fill-opacity="0.13"/>'
            f'<circle cx="{x + 34}" cy="{y + 32}" r="17" fill="none" stroke="{col}" stroke-opacity="0.6" class="ring-pulse" style="animation-delay:{k * 0.5:.1f}s"/>'
            f'<g transform="translate({x + 34} {y + 32})" fill="none" stroke="{col}" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" color="{col}">{ICONS[ic]}</g>'
            f'<text x="{x + 62}" y="{y + 28}" class="sans" font-size="11" font-weight="700" letter-spacing="1.6" fill="{col}">{lab}</text>'
            f'<text x="{x + 62}" y="{y + 47}" class="sans" font-size="16" font-weight="700" fill="#f1f5f9">{html.escape(main)}</text>'
            f'<text x="{x + 18}" y="{y + 78}" class="sans" font-size="{sub_size}" fill="#94a3b8">{html.escape(sub)}</text></g>')
    cxp, cyp = PX + PW / 2, PY + PHH / 2
    pill = "Open to internships &amp; collaborations"
    pill_w = text_w("Open to internships & collaborations", 14) + 46
    aria = ("About me. Third-year Electrical and Electronic Engineering undergraduate at the University of Peradeniya, Sri Lanka, "
            "building systems end to end. Now building FloodLink, a flood early-warning system for the Mahaweli River. "
            "Also building FlyMe, RC aircraft telemetry and a ground station. Exploring river-level forecasting with classical ML "
            "and neural networks. 2nd Place, Idea to Invention 2025. EngEx 2025 Media Lead, drone pilot, photographer and astronomy "
            "enthusiast. IEEE PES and IEEE MTT-S member, former President of the Buddhist Society (FoE).")
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{aria}">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0b111d"/><stop offset="1" stop-color="#0f1726"/></linearGradient>
    <pattern id="dots" width="28" height="28" patternUnits="userSpaceOnUse"><circle cx="14" cy="14" r="1" fill="#fff" fill-opacity="0.08"/></pattern>
    <radialGradient id="b1"><stop offset="0" stop-color="#22d3ee" stop-opacity="0.18"/><stop offset="1" stop-color="#22d3ee" stop-opacity="0"/></radialGradient>
    <radialGradient id="b2"><stop offset="0" stop-color="#a78bfa" stop-opacity="0.18"/><stop offset="1" stop-color="#a78bfa" stop-opacity="0"/></radialGradient>
    <linearGradient id="frame" gradientUnits="userSpaceOnUse" x1="{PX}" y1="{PY}" x2="{PX + PW}" y2="{PY + PHH}">
      <stop offset="0" stop-color="#22d3ee"/><stop offset="0.5" stop-color="#4a9eff"/><stop offset="1" stop-color="#a78bfa"/>
      <animateTransform attributeName="gradientTransform" type="rotate" values="0 {cxp} {cyp};360 {cxp} {cyp}" dur="10s" repeatCount="indefinite"/>
    </linearGradient>
    <linearGradient id="shade" x1="0" y1="0" x2="0" y2="1"><stop offset="0.6" stop-color="#080c16" stop-opacity="0"/><stop offset="1" stop-color="#080c16" stop-opacity="0.9"/></linearGradient>
    <linearGradient id="bar" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#22d3ee"/><stop offset="0.5" stop-color="#4a9eff"/><stop offset="1" stop-color="#a78bfa"/></linearGradient>
    <linearGradient id="shine" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset="0.5" stop-color="#fff" stop-opacity="0.85"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
    <linearGradient id="title" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#f1f5f9"/><stop offset="1" stop-color="#bfe9ff"/></linearGradient>
    <clipPath id="photoClip"><rect x="{PX}" y="{PY}" width="{PW}" height="{PHH}" rx="22"/></clipPath>
    <filter id="soft" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="10"/></filter>
    <style>{BASE_CSS}{HF_CSS}
      .tile{{animation:fadeIn .9s ease-out both}}
      .ring-pulse{{animation:pulse 3s ease-in-out infinite}}
      .h1{{animation:fadeIn 1s ease-out .1s both}}
      .p1{{animation:fadeIn 1s ease-out .25s both}}
      .photo-shine{{animation:pshine 6s ease-in-out infinite}}
      @keyframes pshine{{0%,70%{{transform:translateX(-200px)}}100%{{transform:translateX(520px)}}}}
      .bar-shine{{animation:shimmer 5s ease-in-out infinite}}
    </style>
  </defs>
  <rect width="{w}" height="{h}" fill="url(#bg)"/>
  <rect width="{w}" height="{h}" fill="url(#dots)"/>
  <ellipse cx="200" cy="240" rx="320" ry="300" fill="url(#b1)" class="blob1"/>
  <ellipse cx="1150" cy="200" rx="360" ry="300" fill="url(#b2)" class="blob2"/>

  <rect x="{PX - 4}" y="{PY - 4}" width="{PW + 8}" height="{PHH + 8}" rx="25" fill="none" stroke="url(#frame)" stroke-width="8" filter="url(#soft)" opacity="0.6"/>
  <g clip-path="url(#photoClip)">
    <image x="{PX}" y="{PY}" width="{PW}" height="{PHH}" preserveAspectRatio="xMidYMid slice" xlink:href="data:image/jpeg;base64,{jpeg_b64(ph, 84)}"/>
    <rect x="{PX}" y="{PY}" width="{PW}" height="{PHH}" fill="url(#shade)"/>
    <g class="photo-shine"><rect x="{PX}" y="{PY}" width="70" height="{PHH}" fill="url(#shine)" opacity="0.18" transform="skewX(-12)"/></g>
  </g>
  <rect x="{PX - 3}" y="{PY - 3}" width="{PW + 6}" height="{PHH + 6}" rx="24" fill="none" stroke="url(#frame)" stroke-width="3"/>
  <text x="{PX + 22}" y="{PY + PHH - 44}" class="sans" font-size="21" font-weight="700" fill="#f1f5f9">EngEx 2025</text>
  <text x="{PX + 22}" y="{PY + PHH - 21}" class="sans" font-size="15" fill="#22d3ee">Media Team Lead</text>

  <g class="h1">
    <rect x="{w - 48 - pill_w:.0f}" y="44" width="{pill_w:.0f}" height="30" rx="15" fill="#34d399" fill-opacity="0.1" stroke="#34d399" stroke-opacity="0.55"/>
    <circle cx="{w - 48 - pill_w + 18:.0f}" cy="59" r="7" fill="#34d399" opacity="0.3" class="ring-pulse"/>
    <circle cx="{w - 48 - pill_w + 18:.0f}" cy="59" r="4" fill="#34d399"/>
    <text x="{w - 48 - pill_w + 32:.0f}" y="64" class="sans" font-size="14" font-weight="600" fill="#d1fae5">{pill}</text>
  </g>
  <text x="{TX}" y="62" class="sans h1" font-size="14" font-weight="700" letter-spacing="3.5" fill="#22d3ee">ABOUT ME</text>
  <text x="{TX - 2}" y="104" class="sans h1" font-size="34" font-weight="700" fill="url(#title)">I build systems end to end.</text>
  <g class="p1 sans" font-size="17.5" fill="#cbd5e1">
    <text x="{TX}" y="142">Third-year <tspan font-weight="700" fill="#f1f5f9">Electrical &amp; Electronic Engineering</tspan> undergraduate at the</text>
    <text x="{TX}" y="166"><tspan font-weight="700" fill="#f1f5f9">University of Peradeniya</tspan>, Sri Lanka. From sensor hardware and firmware to</text>
    <text x="{TX}" y="190">radio links and the software that turns data into decisions.</text>
  </g>
  {''.join(tile_svg)}

  <rect x="0" y="{h - 4}" width="{w}" height="4" fill="url(#bar)"/>
  <rect x="0" y="{h - 4}" width="260" height="4" fill="url(#shine)" class="bar-shine" opacity="0.7"/>
</svg>
'''
    with open(os.path.join(OUT, "about.svg"), "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"about.svg  {len(svg) // 1024} KB")


if __name__ == "__main__":
    header(); footer(); about()
    emg(); flood_web(); hydrosync(); floodlink(); water_level(); flyme_hw(); flyme_app(); micromouse(); sobel(); dji()

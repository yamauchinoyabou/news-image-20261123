"""Render a one-page front of the world's news for Monday, 23 November 2026.

Writes assets/entry.png (1024x1024). Build-time only: Pillow + the system Noto fonts.
Deterministic: no timestamps, no randomness, no PNG metadata. Every scene, icon and the
world map are drawn here from code (the map from a coarse hand-made 7.5-degree land grid).
"""
import math
import os

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
FONT_DIR = "/usr/share/fonts/truetype/noto"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "entry.png")

PAPER = (247, 244, 236)
CARD = (255, 255, 255)
INK = (22, 26, 34)
MUTED = (88, 94, 106)
FAINT = (150, 154, 162)
RULE = (212, 206, 194)
RED = (168, 36, 30)

REGION = {
    "EUROPE": (36, 76, 156),
    "MIDDLE EAST": (160, 52, 40),
    "AFRICA": (156, 92, 10),
    "ASIA": (0, 112, 122),
    "AMERICAS": (108, 58, 150),
    "OCEANIA": (18, 122, 84),
    "WORLD": (70, 72, 84),
}
SURE = {  # certainty tag -> (colour, short code, legend text)
    "CONFIRMED": ((24, 118, 70), "C", "2+ independent outlets"),
    "OFFICIAL": ((36, 76, 156), "O", "on the record"),
    "REPORTED": ((96, 100, 112), "R", "one outlet"),
    "CLAIM": ((150, 88, 0), "CL", "one side's account"),
}

_fonts = {}


def F(name, size):
    key = (name, size)
    if key not in _fonts:
        _fonts[key] = ImageFont.truetype(os.path.join(FONT_DIR, f"{name}.ttf"), size)
    return _fonts[key]


def wrap(d, text, fnt, width):
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if d.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit(d, text, name, sizes, width, max_lines):
    """Largest size from `sizes` whose wrap fits in max_lines lines."""
    for s in sizes:
        lines = wrap(d, text, F(name, s), width)
        if len(lines) <= max_lines and all(d.textlength(l, font=F(name, s)) <= width for l in lines):
            return F(name, s), s, lines
    raise AssertionError(f"text does not fit: {text!r}")


def text_lines(d, x, y, lines, fnt, fill, lead):
    for line in lines:
        d.text((x, y), line, font=fnt, fill=fill)
        y += lead
    return y


def chip(d, x, y, label, fill, fnt, fg=(255, 255, 255), padx=5, h=None):
    w = d.textlength(label, font=fnt) + 2 * padx
    h = h or fnt.size + 6
    d.rounded_rectangle([x, y, x + w, y + h], radius=3, fill=fill)
    d.text((x + w / 2, y + h / 2), label, font=fnt, fill=fg, anchor="mm")
    return x + w


def num_badge(d, cx, cy, r, n, colour):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=colour)
    d.text((cx, cy), str(n), font=F("NotoSans-Bold", int(r * 1.15)), fill=(255, 255, 255), anchor="mm")


# ------------------------------------------------------------------ scenes (large)
def scene_warship(d, b):
    x0, y0, x1, y1 = b
    w, h = x1 - x0, y1 - y0
    sea = y0 + h * 0.58
    d.rectangle(b, fill=(226, 234, 244))
    d.rectangle([x0, sea, x1, y1], fill=(178, 202, 228))
    d.rectangle([x0, sea - h * 0.12, x0 + w * 0.23, y1], fill=(150, 146, 138))      # quay
    d.text((x0 + 5, y1 - 5), "BENGHAZI", font=F("NotoSans-Bold", 10), fill=(255, 255, 255), anchor="ld")
    cx = x0 + w * 0.47
    d.polygon([(cx - w * 0.20, sea - h * 0.20), (cx + w * 0.16, sea + h * 0.02),
               (cx + w * 0.12, sea + h * 0.13), (cx - w * 0.17, sea - h * 0.05)], fill=(84, 88, 98))
    d.polygon([(cx - w * 0.09, sea - h * 0.23), (cx + w * 0.05, sea - h * 0.13),
               (cx + w * 0.04, sea - h * 0.04), (cx - w * 0.10, sea - h * 0.12)], fill=(108, 112, 122))
    d.line([(cx - w * 0.03, sea - h * 0.19), (cx + w * 0.01, sea - h * 0.45)], fill=(84, 88, 98), width=3)
    d.rectangle([cx + w * 0.02, sea, x1, y1], fill=(178, 202, 228))                  # stern under water
    for i in range(6):
        rx = cx - w * 0.22 + i * w * 0.08
        d.arc([rx, sea - 4, rx + w * 0.08, sea + 4], 180, 360, fill=(70, 120, 175), width=2)
    for t, r in [(0.0, 0.05), (0.33, 0.07), (0.66, 0.09)]:                           # smoke from deck
        px, py, rr = cx - w * 0.04 + w * 0.08 * t, sea - h * 0.18 - h * 0.42 * t, h * r
        d.ellipse([px - rr, py - rr, px + rr, py + rr], fill=(136, 138, 146))
    for dx, dy in [(0.66, 0.12), (0.75, 0.24), (0.82, 0.34)]:                        # sea drones + wakes
        bx, by = x0 + w * dx, sea + h * dy
        bl, bh, wl = w * 0.075, h * 0.07, w * 0.09
        assert bx + bl + wl <= x1
        for s in (-1, 1):
            d.polygon([(bx + bl, by + s * bh * 0.2), (bx + bl + wl, by + s * bh * 1.3),
                       (bx + bl + wl, by + s * bh * 0.8), (bx + bl, by - s * bh * 0.1)], fill=(255, 255, 255))
        d.polygon([(bx, by), (bx + w * 0.02, by - bh * 0.5), (bx + bl, by - bh * 0.5),
                   (bx + bl, by + bh * 0.5), (bx + w * 0.02, by + bh * 0.5)], fill=(30, 34, 42))
    chip(d, x1 - 108, y0 + 6, "CORVETTE MERKURY", RED, F("NotoSans-Bold", 10))


def scene_rally(d, b):
    x0, y0, x1, y1 = b
    w, h = x1 - x0, y1 - y0
    d.rectangle(b, fill=(20, 40, 34))
    for i in range(1, 4):                                                            # grid
        gy = y0 + h * i / 4
        d.line([(x0, gy), (x1, gy)], fill=(40, 70, 60), width=1)
    pts = [(0.04, 0.55), (0.16, 0.62), (0.28, 0.70), (0.40, 0.74), (0.52, 0.80), (0.60, 0.78), (0.64, 0.30), (0.76, 0.22)]
    xy = [(x0 + w * px, y0 + h * py) for px, py in pts]
    d.line(xy, fill=(90, 220, 140), width=4, joint="curve")
    ax, ay = xy[-1]
    d.polygon([(ax + 12, ay - 6), (ax - 2, ay - 12), (ax + 2, ay + 4)], fill=(90, 220, 140))
    label_box = d.textbbox((x0 + w * 0.06, y0 + 8), "NVDA", font=F("NotoSans-Bold", 13))
    d.text((x0 + w * 0.06, y0 + 8), "NVDA", font=F("NotoSans-Bold", 13), fill=(170, 230, 190))
    d.text((x1 - 8, y1 - 8), "+31%", font=F("NotoSans-Black", 34), fill=(255, 255, 255), anchor="rd")
    # a chip outline with pins (generic processor, not a logo), in the empty
    # upper-middle area: right of the NVDA label and above the chart line
    cx, cy, s = x0 + w * 0.42, y0 + h * 0.30, h * 0.12
    cb = (cx - s - 5, cy - s - 5, cx + s + 5, cy + s + 5)                            # incl. pins
    assert cb[0] > label_box[2] + 4 or cb[1] > label_box[3] + 4, "chip overlaps NVDA label"
    line_top = min(py for px, py in xy if cb[0] - 20 <= px <= cb[2] + 20)
    assert cb[3] + 4 < line_top, "chip overlaps chart line"
    d.rectangle([cx - s, cy - s, cx + s, cy + s], outline=(170, 230, 190), width=2)
    for k in range(-2, 3):
        o = k * s * 0.4
        d.line([(cx + o, cy - s - 5), (cx + o, cy - s)], fill=(170, 230, 190), width=2)
        d.line([(cx + o, cy + s), (cx + o, cy + s + 5)], fill=(170, 230, 190), width=2)
        d.line([(cx - s - 5, cy + o), (cx - s, cy + o)], fill=(170, 230, 190), width=2)
        d.line([(cx + s, cy + o), (cx + s + 5, cy + o)], fill=(170, 230, 190), width=2)
    chip(d, x0 + 8, y1 - 24, "CEO REINSTATED", (24, 118, 70), F("NotoSans-Bold", 10))


def scene_nato(d, b):
    x0, y0, x1, y1 = b
    w, h = x1 - x0, y1 - y0
    d.rectangle(b, fill=(222, 230, 244))
    # round council table, seen from above, with seats
    cx, cy, rx, ry = x0 + w * 0.30, y0 + h * 0.60, w * 0.20, h * 0.26
    for k in range(12):
        a = k * math.pi / 6
        sx, sy = cx + (rx + 9) * math.cos(a), cy + (ry + 9) * math.sin(a)
        d.ellipse([sx - 5, sy - 5, sx + 5, sy + 5], fill=(36, 76, 156))
    d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=(150, 120, 90))
    d.ellipse([cx - rx + 8, cy - ry + 6, cx + rx - 8, cy + ry - 6], fill=(222, 230, 244))
    d.text((cx, cy), "BRUSSELS", font=F("NotoSans-Bold", 10), fill=(36, 76, 156), anchor="mm")
    # three cruise missiles heading down-right
    for i in range(3):
        mx, my = x0 + w * (0.60 + 0.10 * i), y0 + h * (0.20 + 0.14 * i)
        L = w * 0.14
        d.line([(mx, my), (mx + L, my + L * 0.35)], fill=(60, 64, 74), width=5)
        d.polygon([(mx + L, my + L * 0.35 - 4), (mx + L + 9, my + L * 0.35 + 3), (mx + L, my + L * 0.35 + 5)], fill=(60, 64, 74))
        d.polygon([(mx + 2, my - 2), (mx - 6, my - 8), (mx + 8, my + 1)], fill=(60, 64, 74))
    chip(d, x1 - 96, y1 - 24, "3 × Kh-101", RED, F("NotoSans-Bold", 11))


# ------------------------------------------------------------------ icons (medium)
def ico_bars(d, x, y, s, c):
    base = y + s
    for i, hgt in enumerate([0.35, 0.25, 0.2, 0.9]):
        bx = x + i * s * 0.26
        d.rectangle([bx, base - s * hgt, bx + s * 0.2, base], fill=c if i == 3 else (170, 176, 186))


def ico_virus(d, x, y, s, c):
    cx, cy, r = x + s / 2, y + s / 2, s * 0.27
    for k in range(8):
        a = k * math.pi / 4
        ex, ey = cx + (r + s * 0.13) * math.cos(a), cy + (r + s * 0.13) * math.sin(a)
        d.line([(cx, cy), (ex, ey)], fill=c, width=3)
        d.ellipse([ex - s * 0.07, ey - s * 0.07, ex + s * 0.07, ey + s * 0.07], fill=c)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=c)


def ico_person(d, x, y, s, c):
    d.ellipse([x + s * 0.30, y, x + s * 0.66, y + s * 0.36], fill=c)
    d.pieslice([x + s * 0.12, y + s * 0.42, x + s * 0.84, y + s * 1.14], 180, 360, fill=c)
    d.ellipse([x + s * 0.60, y + s * 0.46, x + s * 0.92, y + s * 0.78], outline=INK, width=3)
    d.line([(x + s * 0.88, y + s * 0.74), (x + s, y + s * 0.9)], fill=INK, width=3)


def ico_scales(d, x, y, s, c):
    cx = x + s / 2
    d.line([(cx, y + s * 0.08), (cx, y + s * 0.88)], fill=c, width=3)
    d.rectangle([x + s * 0.28, y + s * 0.88, x + s * 0.72, y + s * 0.96], fill=c)
    d.line([(x + s * 0.1, y + s * 0.2), (x + s * 0.9, y + s * 0.2)], fill=c, width=3)
    for px in (0.2, 0.8):
        d.line([(x + s * px, y + s * 0.2), (x + s * (px - 0.12), y + s * 0.55)], fill=c, width=2)
        d.line([(x + s * px, y + s * 0.2), (x + s * (px + 0.12), y + s * 0.55)], fill=c, width=2)
        d.pieslice([x + s * (px - 0.16), y + s * 0.42, x + s * (px + 0.16), y + s * 0.68], 0, 180, fill=c)


def ico_satellite(d, x, y, s, c):
    cx, cy = x + s / 2, y + s / 2
    for sg in (-1, 1):
        xa, xb = cx + sg * s * 0.18, cx + sg * s * 0.5
        d.line([(cx, cy), (xa, cy)], fill=INK, width=2)
        d.rectangle([min(xa, xb), cy - s * 0.16, max(xa, xb), cy + s * 0.16], fill=(60, 90, 150))
    d.rectangle([cx - s * 0.14, cy - s * 0.22, cx + s * 0.14, cy + s * 0.22], fill=c)
    d.ellipse([cx - s * 0.07, cy - s * 0.07, cx + s * 0.07, cy + s * 0.07], fill=(255, 205, 60))


def ico_cricket(d, x, y, s, c):
    for i in range(3):                                                                # stumps
        sx = x + s * (0.12 + i * 0.14)
        d.rectangle([sx, y + s * 0.2, sx + s * 0.07, y + s], fill=(200, 170, 120))
    d.rectangle([x + s * 0.08, y + s * 0.14, x + s * 0.48, y + s * 0.19], fill=(200, 170, 120))
    d.polygon([(x + s * 0.62, y + s * 0.95), (x + s * 0.72, y + s * 0.95), (x + s * 0.95, y + s * 0.2), (x + s * 0.85, y + s * 0.18)], fill=(222, 196, 140))
    d.ellipse([x + s * 0.55, y + s * 0.1, x + s * 0.72, y + s * 0.27], fill=(180, 30, 30))


def ico_ball_door(d, x, y, s, c):
    d.rectangle([x + s * 0.5, y, x + s * 0.95, y + s], fill=(120, 90, 60))           # door
    d.rectangle([x + s * 0.55, y + s * 0.06, x + s * 0.9, y + s], fill=(160, 124, 86))
    d.ellipse([x + s * 0.8, y + s * 0.5, x + s * 0.86, y + s * 0.56], fill=INK)
    d.ellipse([x, y + s * 0.5, x + s * 0.46, y + s * 0.96], fill=(255, 255, 255), outline=INK, width=2)
    cx, cy = x + s * 0.23, y + s * 0.73
    d.regular_polygon((cx, cy, s * 0.08), 5, fill=INK)


def ico_podium(d, x, y, s, c):
    d.polygon([(x + s * 0.2, y + s * 0.45), (x + s * 0.8, y + s * 0.45), (x + s * 0.7, y + s), (x + s * 0.3, y + s)], fill=c)
    d.line([(x + s * 0.5, y + s * 0.45), (x + s * 0.5, y + s * 0.12)], fill=INK, width=3)
    d.ellipse([x + s * 0.42, y, x + s * 0.58, y + s * 0.2], fill=INK)
    for k in (1, 2):
        d.arc([x + s * (0.5 - 0.16 * k), y - s * 0.06 * k, x + s * (0.5 + 0.16 * k), y + s * (0.26 + 0.06 * k)], 300, 60, fill=FAINT, width=2)


def medium_scene(d, b, icon, label, colour):
    x0, y0, x1, y1 = b
    tint = tuple(int(c + (255 - c) * 0.86) for c in colour)
    d.rectangle(b, fill=tint)
    s = (y1 - y0) - 12
    icon(d, x0 + 10, y0 + 6, s, colour)
    lf, _, _ = fit(d, label, "NotoSans-Black", (26, 24, 22, 20, 18), (x1 - x0) - s - 34, 1)
    d.text((x1 - 10, (y0 + y1) / 2), label, font=lf, fill=colour, anchor="rm")


# ------------------------------------------------------------------ world map (own grid)
# 7.5-degree cells: column c covers lon -180+7.5c .. +7.5; row r covers lat 82.5-7.5r .. -7.5.
LAND = {
    0: [(9, 13), (14, 21), (26, 26), (30, 30), (37, 37)],
    1: [(3, 6), (7, 13), (15, 21), (26, 47)],
    2: [(1, 11), (13, 15), (17, 19), (21, 21), (25, 47)],
    3: [(7, 11), (13, 15), (23, 23), (25, 43), (45, 45)],
    4: [(8, 15), (24, 42)],
    5: [(8, 14), (22, 24), (25, 27), (28, 41), (42, 42)],
    6: [(8, 13), (23, 28), (28, 33), (34, 40), (41, 42)],
    7: [(9, 12), (22, 28), (29, 31), (32, 35), (36, 39), (40, 40)],
    8: [(10, 12), (21, 29), (30, 30), (33, 34), (37, 38), (40, 40)],
    9: [(12, 13), (14, 15), (22, 30), (34, 34), (37, 38), (40, 40)],
    10: [(14, 17), (23, 29), (37, 39)],
    11: [(13, 18), (25, 29), (38, 42), (43, 43)],
    12: [(14, 18), (25, 29), (41, 43)],
    13: [(15, 18), (25, 28), (30, 30), (39, 43)],
    14: [(15, 17), (26, 28), (39, 43)],
    15: [(15, 16), (26, 26), (39, 43)],
    16: [(15, 15), (43, 43), (46, 47)],
    17: [(15, 15)],
}
MAP_ROWS, MAP_COLS = 19, 48


def draw_map(d, b, pins):
    x0, y0, x1, y1 = b
    d.rectangle(b, fill=(232, 238, 246))
    cw, rh = (x1 - x0) / MAP_COLS, (y1 - y0) / MAP_ROWS
    for r, spans in LAND.items():
        for c0, c1 in spans:
            for c in range(c0, c1 + 1):
                cx, cy = x0 + (c + 0.5) * cw, y0 + (r + 0.5) * rh
                rr = min(cw, rh) * 0.42
                d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=(178, 186, 198))

    def proj(lat, lon):
        return x0 + (lon + 180) / 360 * (x1 - x0), y0 + (82.5 - lat) / 142.5 * (y1 - y0)

    for n, lat, lon, colour, dx, dy in pins:
        px, py = proj(lat, lon)
        bx, by = px + dx, py + dy
        if dx or dy:
            d.line([(px, py), (bx, by)], fill=colour, width=1)
        d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=colour)
        num_badge(d, bx, by, 7, n, colour)


# ------------------------------------------------------------------ stories
# (n, region, sure, place/field, headline, summary, sources, scene, label, lat, lon, pin offset)
LARGE = [
    (1, "AFRICA", "CONFIRMED", "LIBYA · UKRAINE · WAR",
     "Ukraine sinks Russian warship in Libya",
     "Zelenskyy confirms Ukrainian sea drones hit the corvette Merkury at Benghazi; it lies capsized. Kremlin: \"terrorist activity\".",
     "CNBC · CBC · NBC · RFE/RL · Euronews · Reuters", scene_warship, 32.1, 20.1, (0, -12)),
    (2, "AMERICAS", "OFFICIAL", "SANTA CLARA, US · BUSINESS",
     "Nvidia brings back Jensen Huang as CEO",
     "Board votes unanimously to reinstate him; shares close about 31% higher. Colette Kress returns to CFO.",
     "Nvidia/SEC filing · CNBC · NBC · PBS · Axios", scene_rally, 37.4, -122.0, (-8, -10)),
    (3, "EUROPE", "CONFIRMED", "BRUSSELS · SECURITY",
     "NATO meets over Russian missiles in Poland",
     "Emergency council after Polish prosecutors say all three objects that fell in Poland were Kh-101 missiles.",
     "Notes from Poland · Reuters · EU Today", scene_nato, 50.8, 4.4, (-10, -10)),
]
MEDIUM = [
    (4, "AMERICAS", "CONFIRMED", "NEW YORK · MARKETS", "Wall Street's big rebound",
     "Dow +1,448; Nasdaq +6.5%, best day since April 2025.", "AP · CNBC", ico_bars, "+1,448", 40.7, -74.0, (10, 2)),
    (5, "AFRICA", "REPORTED", "BUNIA, DR CONGO · HEALTH", "Ebola deaths undercounted",
     "Reuters satellite study finds far more new graves than official tallies.", "Reuters · TimesLive · TBS", ico_virus, "EBOLA", 1.6, 30.2, (8, 8)),
    (6, "ASIA", "OFFICIAL", "SEOUL · POLITICS", "First woman picked as spy chief",
     "Lee nominates Kang Kum-sil for the NIS and a new foreign minister.", "Korea Times · SBS · Reuters", ico_person, "NIS", 37.6, 127.0, (0, -11)),
    (7, "ASIA", "CONFIRMED", "BANGKOK · LAW", "Thai MP's royal-insult term halved",
     "Appeal court cuts Rukchanok Srinork's sentence; she is bailed.", "AP · Bangkok Post · Khaosod", ico_scales, "6 TO 3 YRS", 13.8, 100.5, (-9, 8)),
    (8, "WORLD", "REPORTED", "RUSSIA · SPACE", "Report: Russian nuclear satellite",
     "German media cite NATO intelligence; the Kremlin dismisses it.", "Reuters · J. Post · Hromadske", ico_satellite, "REPORT", 55.7, 37.6, (6, -12)),
    (9, "OCEANIA", "CONFIRMED", "WELLINGTON · CRICKET", "First Test ends in a draw",
     "New Zealand bat out day five after India's 720/9 declared.", "ESPNcricinfo · ICC · RNZ", ico_cricket, "720/9", -41.3, 174.8, (-8, -10)),
    (10, "MIDDLE EAST", "OFFICIAL", "TEHRAN · POLITICS", "Iran's leaders defy US pressure",
     "Pezeshkian says the US can't topple Iran; Araghchi eyes trade with neighbours.", "Reuters · Tehran Times", ico_podium, "TEHRAN", 35.7, 51.4, (8, 6)),
    (11, "EUROPE", "CONFIRMED", "SWINDON, UK · FOOTBALL", "Swindon sack Ian Holloway",
     "League Two club parts ways with its manager after a winless run.", "BBC Sport · Yahoo Sports", ico_ball_door, "SACKED", 51.6, -1.8, (-11, 0)),
]
LIST = [
    (12, "MIDDLE EAST", "CONFIRMED", "Gaza:", "UNRWA worker killed in Israeli strike", "Reuters, DN"),
    (13, "AFRICA", "REPORTED", "Libya:", "UN mission urges Benghazi attack probe", "Euronews"),
    (14, "EUROPE", "REPORTED", "Poland:", "to summon Russian envoy over missiles", "A. Prague"),
    (15, "EUROPE", "CLAIM", "Germany:", "maker's video: interceptor downs drone", "Euronews"),
    (16, "EUROPE", "REPORTED", "Spain:", "right leads polls before 29 Nov vote", "Reuters"),
    (17, "EUROPE", "REPORTED", "Belgium:", "workers march in Brussels against cuts", "Euronews"),
    (18, "EUROPE", "REPORTED", "Canaries:", "over 10,000 migrants in record month", "Euronews"),
    (19, "ASIA", "REPORTED", "Bangladesh:", "Hasina faces jail if she returns", "Reuters"),
    (20, "ASIA", "REPORTED", "N. Korea:", "Kim stresses security, no Trump talks", "Euronews"),
    (21, "AMERICAS", "REPORTED", "US:", "Clayton named acting cyber director", "Axios"),
    (22, "AMERICAS", "REPORTED", "Iowa:", "Army reschedules explosives detonation", "DN"),
    (23, "AMERICAS", "REPORTED", "NFL:", "Commanders beat Bengals on Monday night", "SI"),
    (24, "AMERICAS", "REPORTED", "Chile:", "poll shows low approval for Kast", "Rio Times"),
    (25, "AFRICA", "REPORTED", "Nigeria:", "Atiku says he stays in the 2027 race", "Nig. Brief"),
    (26, "AFRICA", "REPORTED", "Nigeria:", "election body delays voter-roll clean-up", "Nig. Brief"),
    (27, "OCEANIA", "REPORTED", "Australia:", "Albanese keeps medicine price cap", "ABC"),
    (28, "OCEANIA", "REPORTED", "Australia:", "opposition vows spending \"speed limit\"", "ABC"),
]
NUMBERS = [
    ("31%", "Nvidia's one-day share gain", (24, 118, 70)),
    ("+1,448", "Dow points; Nasdaq +6.5%", (24, 118, 70)),
    ("3", "Kh-101 missiles found in Poland", RED),
    ("6 to 3", "years: Thai MP's sentence, cut", (156, 92, 10)),
    ("720/9", "India's declared total in Wellington", (18, 122, 84)),
]
DATE_CHECK = ("COP31 ends without a deal (Sun 22) · Dymer strike (Sun 22) · Indonesia candy-factory fire (Sat 21) · "
              "Delta outage (Sun 22) · Khartoum UN building hit (Sun 22) · Kenya–DR Congo ties (Sun 22) · "
              "Hormuz ship strikes (21–22) · BepiColombo reaches Mercury (Sat 21) · Nigeria boat capsizing (Fri 20)")


# ------------------------------------------------------------------ panels
def tagline(d, x, y, n, region, place, sure, right, small=False):
    colour = REGION[region]
    r = 7 if small else 8
    num_badge(d, x + r, y + r, r, n, colour)
    pf = F("NotoSans-SemiCondensedBold", 10 if small else 11)
    sf = F("NotoSans-Bold", 9 if small else 10)
    sc = SURE[sure][0]
    sw = d.textlength(sure, font=sf) + 10
    d.text((x + 2 * r + 5, y + r), place, font=pf, fill=colour, anchor="lm")
    assert x + 2 * r + 5 + d.textlength(place, font=pf) <= right - sw - 4, f"tag line too long: {place}"
    chip(d, right - sw, y + r - (sf.size + 6) / 2, sure, sc, sf)


def large_panel(d, b, story):
    n, region, sure, place, head, summary, src, scene = story[:8]
    x0, y0, x1, y1 = b
    d.rectangle(b, fill=CARD, outline=RULE)
    d.rectangle([x0, y0, x1, y0 + 4], fill=REGION[region])
    scene(d, (x0, y0 + 4, x1, y0 + 114))
    pad = 9
    y = y0 + 120
    tagline(d, x0 + pad, y, n, region, place, sure, x1 - pad)
    y += 22
    hf, hs, hl = fit(d, head, "NotoSerif-Bold", (22, 21, 20, 19, 18), x1 - x0 - 2 * pad, 2)
    y = text_lines(d, x0 + pad, y, hl, hf, INK, int(hs * 1.18)) + 3
    bf, bs, bl = fit(d, summary, "NotoSans-Regular", (13, 12), x1 - x0 - 2 * pad, 3)
    y = text_lines(d, x0 + pad, y, bl, bf, MUTED, bs + 4)
    sf = F("NotoSans-SemiCondensed", 10)
    assert y <= y1 - 18, f"large panel overflow: {head}"
    d.text((x0 + pad, y1 - 6), src, font=sf, fill=FAINT, anchor="ld")


def medium_panel(d, b, story):
    n, region, sure, place, head, summary, src, icon, label = story[:9]
    x0, y0, x1, y1 = b
    d.rectangle(b, fill=CARD, outline=RULE)
    d.rectangle([x0, y0, x1, y0 + 3], fill=REGION[region])
    medium_scene(d, (x0, y0 + 3, x1, y0 + 43), icon, label, REGION[region])
    pad = 8
    y = y0 + 48
    tagline(d, x0 + pad, y, n, region, place, sure, x1 - pad, small=True)
    y += 17
    hf, hs, hl = fit(d, head, "NotoSerif-Bold", (18, 17, 16), x1 - x0 - 2 * pad, 2)
    y = text_lines(d, x0 + pad, y, hl, hf, INK, int(hs * 1.18)) + 1
    bf, bs, bl = fit(d, summary, "NotoSans-Regular", (12, 11), x1 - x0 - 2 * pad, 2)
    y = text_lines(d, x0 + pad, y, bl, bf, MUTED, bs + 3)
    assert y <= y1 - 14, f"medium panel overflow: {head}"
    d.text((x0 + pad, y1 - 4), src, font=F("NotoSans-SemiCondensed", 9), fill=FAINT, anchor="ld")


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    M = 12
    all_regions = [s[1] for s in LARGE + MEDIUM + LIST]
    n_stories, n_regions = len(all_regions), len(set(all_regions))
    assert [s[0] for s in LARGE + MEDIUM + LIST] == list(range(1, n_stories + 1))

    # top strip + masthead
    d.rectangle([0, 0, W, 20], fill=INK)
    d.text((M, 10), "THE WORLD IN ONE DAY", font=F("NotoSans-Bold", 11), fill=(255, 255, 255), anchor="lm")
    d.text((W - M, 10), f"{n_stories} STORIES · {n_regions} REGIONS · EVERY ONE DATED MONDAY 23 NOVEMBER 2026 (UTC)",
           font=F("NotoSans-Bold", 11), fill=(255, 214, 120), anchor="rm")
    d.text((W / 2, 56), "Monday, 23 November 2026", font=F("NotoSerif-Black", 62), fill=INK, anchor="mm")
    d.text((W / 2, 102), "Ukraine sinks a Russian warship in Libya · Nvidia brings back Jensen Huang · NATO meets on Poland's missiles",
           font=F("NotoSerif-SemiBold", 16), fill=RED, anchor="mm")
    d.line([(M, 116), (W - M, 116)], fill=INK, width=2)

    # region tally chips
    cf = F("NotoSans-Bold", 11)
    order = ["EUROPE", "MIDDLE EAST", "AFRICA", "ASIA", "AMERICAS", "OCEANIA", "WORLD"]
    labels = [f"{r}  {all_regions.count(r)}" for r in order]
    widths = [d.textlength(l, font=cf) + 16 for l in labels]
    gap = (W - 2 * M - sum(widths)) / (len(labels) - 1)
    x = M
    for r, l, w in zip(order, labels, widths):
        chip(d, x, 122, l, REGION[r], cf, padx=8, h=20)
        x += w + gap

    # row 1: three large panels + day in numbers
    top, bot = 150, 418
    nb_w = 196
    lw = (W - 2 * M - nb_w - 3 * 8) / 3
    for i, st in enumerate(LARGE):
        lx = M + i * (lw + 8)
        large_panel(d, (int(lx), top, int(lx + lw), bot), st)
    nx0 = int(W - M - nb_w)
    d.rectangle([nx0, top, W - M, bot], fill=INK)
    d.text((nx0 + 10, top + 8), "THE DAY IN NUMBERS", font=F("NotoSans-Bold", 13), fill=(255, 214, 120))
    y = top + 32
    for big, cap, colour in NUMBERS:
        bright = tuple(min(255, int(c * 0.45 + 255 * 0.55)) for c in colour)
        d.text((nx0 + 10, y), big, font=F("NotoSans-Black", 27), fill=bright)
        d.text((nx0 + 10, y + 32), cap, font=F("NotoSans-SemiCondensed", 12), fill=(220, 222, 228))
        y += 47
    assert y <= bot + 4

    # rows 2-3: eight medium panels
    mw = (W - 2 * M - 3 * 8) / 4
    for i, st in enumerate(MEDIUM):
        r, c = divmod(i, 4)
        mx, my = M + c * (mw + 8), 426 + r * (156 + 8)
        medium_panel(d, (int(mx), my, int(mx + mw), my + 156), st)

    # bottom band: ALSO ON MONDAY list + map
    by = 752
    d.line([(M, by), (W - M, by)], fill=INK, width=2)
    lx1 = 736
    d.text((M, by + 5), f"ALSO ON MONDAY 23 NOVEMBER — {len(LIST)} MORE STORIES", font=F("NotoSans-Black", 13), fill=INK)
    rows = (len(LIST) + 1) // 2
    colw = (lx1 - M - 10) / 2
    nf, tf, srcf = F("NotoSans-Bold", 12), F("NotoSans-SemiCondensed", 12), F("NotoSans-SemiCondensed", 10)
    tfb = F("NotoSans-SemiCondensedBold", 12)
    lead = 18
    for i, (n, region, sure, where, text, src) in enumerate(LIST):
        col, row = divmod(i, rows)
        x = M + col * (colw + 10)
        y = by + 26 + row * lead
        colour = REGION[region]
        d.text((x, y), f"{n}", font=nf, fill=colour)
        cx = x + 20
        sc, code, _ = SURE[sure]
        cx = chip(d, cx, y + 1, code, sc, F("NotoSans-Bold", 9), padx=3, h=14) + 5
        d.text((cx, y), where, font=tfb, fill=colour)
        cx += d.textlength(where, font=tfb) + 4
        sw = d.textlength(src, font=srcf)
        right = x + colw
        assert cx + d.textlength(text, font=tf) <= right - sw - 6, f"list line too long: {text}"
        d.text((cx, y), text, font=tf, fill=INK)
        d.text((right, y + 2), src, font=srcf, fill=FAINT, anchor="ra")
    list_bottom = by + 26 + rows * lead
    d.line([(lx1, by + 6), (lx1, list_bottom)], fill=RULE, width=1)

    mx0 = lx1 + 10
    d.text((mx0, by + 5), "WHERE IT HAPPENED", font=F("NotoSans-Black", 13), fill=INK)
    d.text((W - M, by + 7), "pins = panel numbers", font=F("NotoSans-SemiCondensed", 10), fill=MUTED, anchor="ra")
    pins = [(s[0], s[-3], s[-2], REGION[s[1]], *s[-1]) for s in LARGE + MEDIUM]
    map_box = (mx0, by + 26, W - M, list_bottom)
    assert (map_box[2] - map_box[0]) / (map_box[3] - map_box[1]) > 1.6
    draw_map(d, map_box, pins)

    # footer: DATE CHECK + HOW SURE
    fy = list_bottom + 8
    d.rounded_rectangle([M, fy, W - M, fy + 52], radius=4, fill=(253, 240, 236), outline=RED)
    chip(d, M + 8, fy + 7, "DATE CHECK", RED, F("NotoSans-Black", 11), padx=6, h=18)
    d.text((M + 104, fy + 16), "Every story here happened, or was first reported, on Monday 23 November 2026. Left out as earlier days' news:",
           font=F("NotoSans-SemiCondensedBold", 12), fill=INK, anchor="lm")
    df, _, dl = fit(d, DATE_CHECK, "NotoSans-SemiCondensed", (11, 10), W - 2 * M - 20, 2)
    text_lines(d, M + 10, fy + 26, dl, df, MUTED, 12)

    hy = fy + 58
    d.text((M, hy + 7), "HOW SURE", font=F("NotoSans-Black", 11), fill=INK, anchor="lm")
    x = M + 66
    hf = F("NotoSans-SemiCondensed", 11)
    for name, (colour, code, desc) in SURE.items():
        x = chip(d, x, hy, f"{code} {name}", colour, F("NotoSans-Bold", 9), padx=4, h=14) + 4
        d.text((x, hy + 7), desc, font=hf, fill=MUTED, anchor="lm")
        x += d.textlength(desc, font=hf) + 12
    d.text((W - M, hy + 7), "Claims are attributed · scenes, icons and map drawn in code", font=hf, fill=MUTED, anchor="rm")
    assert hy + 16 <= H - 2, f"footer overflows: {hy}"

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    img.save(OUT, format="PNG", optimize=True)


if __name__ == "__main__":
    main()

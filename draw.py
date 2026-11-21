"""Draw the Saturday 21 November 2026 front page (1024x1024).

Self-contained: Lexend variable font in fonts/, no network, deterministic.
Run:  python3 draw.py [output.png]
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_PATH = os.path.join(HERE, "fonts", "Lexend-VF.ttf")

W = 1024
H = 1024
M = 16  # page margin

PAPER = (247, 242, 231)
INK = (20, 33, 61)
NAVY = (20, 33, 61)
RED = (178, 34, 22)
GOLD = (201, 162, 39)
TEAL = (14, 107, 107)
SLATE = (70, 84, 110)
LIGHT = (220, 230, 242)
CARD_BG = (255, 253, 247)
RULE = (180, 172, 155)

_FONT_CACHE = {}


def font(size, weight=400):
    key = (size, weight)
    if key not in _FONT_CACHE:
        f = ImageFont.truetype(FONT_PATH, size)
        try:
            f.set_variation_by_axes([weight])
        except Exception:
            pass
        _FONT_CACHE[key] = f
    return _FONT_CACHE[key]


def text_w(draw, text, size, weight=400):
    return draw.textlength(text, font=font(size, weight))


def wrap(draw, text, size, weight, max_w):
    """Greedy word wrap; returns list of lines that fit max_w."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if text_w(draw, trial, size, weight) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_lines(draw, text, size, weight, max_w, max_lines):
    """Wrap and trim to max_lines, adding an ellipsis if trimmed."""
    lines = wrap(draw, text, size, weight, max_w)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        while lines and text_w(draw, lines[-1] + " ...", size, weight) > max_w:
            lines[-1] = lines[-1].rsplit(" ", 1)[0]
        lines[-1] = lines[-1] + " ..."
    return lines


def draw_text_block(draw, x, y, lines, size, weight, color, leading=None):
    lead = leading if leading is not None else int(size * 1.25)
    for line in lines:
        draw.text((x, y), line, font=font(size, weight), fill=color)
        y += lead
    return y


def kicker_bar(draw, x, y, w, text, size=10):
    """Red kicker strip with white bold text; returns height used."""
    h = size + 8
    draw.rectangle([x, y, x + w, y + h], fill=RED)
    draw.text((x + 6, y + 4), text, font=font(size, 700), fill=(255, 255, 255))
    return h


def starburst(draw, cx, cy, r, color, points=8):
    import math
    pts = []
    for i in range(points * 2):
        ang = math.pi * i / points
        rr = r if i % 2 == 0 else r * 0.38
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    draw.polygon(pts, fill=color)


# ---------------------------------------------------------------- map data
# Land drawn as a dot grid; each rect is (x0, y0, x1, y1) in grid cells.
MAP_COLS, MAP_ROWS = 60, 25
LAND_RECTS = [
    (2, 3, 14, 8), (4, 8, 12, 10), (6, 10, 9, 12),      # North America
    (15, 1, 18, 3),                                       # Greenland
    (12, 12, 17, 14), (13, 14, 16, 19), (14, 19, 15, 21),  # South America
    (26, 3, 27, 4),                                       # Britain
    (27, 4, 33, 7),                                       # Europe
    (28, 9, 36, 12), (29, 12, 35, 16), (31, 16, 33, 19),  # Africa
    (34, 3, 56, 6), (36, 6, 52, 9), (40, 9, 48, 11),      # Asia
    (55, 7, 57, 9),                                       # Japan
    (47, 12, 52, 13),                                     # SE Asia islands
    (48, 20, 55, 22),                                     # Australia
    (56, 23, 57, 24),                                     # New Zealand
]


def draw_world_map(draw, x, y, w, h, pins):
    """Dot-grid world map. pins: list of (lon, lat, number, dx, dy)."""
    draw.rectangle([x, y, x + w, y + h], fill=LIGHT, outline=SLATE, width=1)
    cw, ch = w / MAP_COLS, h / MAP_ROWS
    for gx in range(MAP_COLS):
        for gy in range(MAP_ROWS):
            if any(x0 <= gx <= x1 and y0 <= gy <= y1 for x0, y0, x1, y1 in LAND_RECTS):
                cx, cy = x + (gx + 0.5) * cw, y + (gy + 0.5) * ch
                r = 1.6
                draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(51, 80, 122))
    for lon, lat, num, dx, dy in pins:
        px = x + (lon + 180.0) / 360.0 * w + dx
        py = y + (90.0 - lat) / 180.0 * h + dy
        r = 6
        draw.ellipse([px - r, py - r, px + r, py + r], fill=RED, outline=(255, 255, 255), width=1)
        t = str(num)
        tw = draw.textlength(t, font=font(8, 700))
        draw.text((px - tw / 2, py - 5), t, font=font(8, 700), fill=(255, 255, 255))


# ---------------------------------------------------------------- illustrations
# Each draws a flat, simple scene inside box (x, y, w, h). Keys match cards.

def ill_riyadh(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(16, 24, 52))
    draw.ellipse([x + w - 34, y + 8, x + w - 14, y + 28], fill=(240, 230, 180))
    import random
    rnd = random.Random(7)
    for _ in range(26):
        sx, sy = x + rnd.randint(2, w - 2), y + rnd.randint(2, int(h * 0.45))
        draw.point((sx, sy), fill=(255, 255, 255))
    base = y + h
    for bx, bw, bh in [(0, 34, 52), (36, 26, 70), (64, 40, 46), (106, 30, 78),
                       (138, 36, 58), (176, 28, 66), (206, 38, 48), (246, 30, 72)]:
        draw.rectangle([x + bx, base - bh, x + bx + bw, base], fill=(32, 44, 74))
        for wy in range(base - bh + 8, base - 6, 12):
            for wx in range(x + bx + 5, x + bx + bw - 4, 9):
                draw.rectangle([wx, wy, wx + 4, wy + 5], fill=(255, 196, 66))
    for tx, ty in [(52, 26), (150, 18), (238, 30)]:
        pts = [(x + tx - 46, y + 6), (x + tx - 12, y + ty), (x + tx, y + ty + 10)]
        draw.line(pts, fill=(255, 140, 40), width=3)
        starburst(draw, x + tx, y + ty + 10, 9, (255, 196, 66))


def ill_cop31(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(198, 232, 222))
    cx, cy, r = x + w * 0.36, y + h * 0.52, min(w, h) * 0.42
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(46, 139, 87))
    draw.ellipse([cx - r * 0.55, cy - r * 0.7, cx + r * 0.1, cy - r * 0.1], fill=(124, 200, 150))
    draw.ellipse([cx + r * 0.05, cy + r * 0.15, cx + r * 0.6, cy + r * 0.65], fill=(124, 200, 150))
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(20, 33, 61), width=2)
    tx = x + w * 0.78
    draw.rounded_rectangle([tx - 9, y + 12, tx + 9, y + h - 26], radius=9, fill=(255, 255, 255), outline=RED, width=2)
    draw.ellipse([tx - 15, y + h - 40, tx + 15, y + h - 10], fill=RED)
    draw.rectangle([tx - 4, y + h - 58, tx + 4, y + h - 26], fill=RED)
    draw.text((tx - 26, y + 2), "1.5 C", font=font(13, 700), fill=RED)


def ill_mercury(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(8, 10, 24))
    import random
    rnd = random.Random(11)
    for _ in range(30):
        sx, sy = x + rnd.randint(2, w - 2), y + rnd.randint(2, h - 2)
        draw.point((sx, sy), fill=(255, 255, 255))
    cx, cy, r = x + w * 0.30, y + h * 0.55, min(w, h) * 0.40
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(168, 160, 148))
    for ox, oy, orr in [(-0.4, -0.3, 0.16), (0.25, 0.1, 0.12), (-0.1, 0.35, 0.14), (0.45, -0.35, 0.10)]:
        draw.ellipse([cx + ox * r - orr * r, cy + oy * r - orr * r,
                      cx + ox * r + orr * r, cy + oy * r + orr * r], fill=(140, 132, 120))
    sx, sy = x + w * 0.74, y + h * 0.34
    draw.rectangle([sx - 26, sy - 6, sx - 8, sy + 6], fill=(40, 110, 190))
    draw.rectangle([sx + 8, sy - 6, sx + 26, sy + 6], fill=(40, 110, 190))
    draw.rectangle([sx - 8, sy - 10, sx + 8, sy + 10], fill=(210, 210, 210))
    draw.polygon([(sx - 2, sy + 10), (sx + 2, sy + 10), (sx + 8, sy + 26), (sx - 8, sy + 26)], fill=(255, 140, 40))
    draw.text((x + 8, y + h - 18), "8 YEARS  -  10 BILLION KM", font=font(11, 700), fill=(255, 255, 255))


def ill_quake(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(232, 214, 180))
    s = h / 100.0
    for mx, mh, col in [(0, 62, (120, 84, 58)), (70, 84, (96, 66, 44)), (160, 58, (120, 84, 58)), (230, 76, (96, 66, 44))]:
        mh2 = mh * s
        draw.polygon([(x + mx, y + h), (x + mx + 46, y + h - mh2), (x + mx + 92, y + h)], fill=col)
        draw.polygon([(x + mx + 46, y + h - mh2), (x + mx + 60, y + h - mh2 + 14 * s), (x + mx + 34, y + h - mh2 + 12 * s)], fill=(255, 255, 255))
    pts = [(x + 8, y + h * 0.45)]
    import random
    rnd = random.Random(3)
    for i in range(1, 12):
        yy = h * 0.45 + rnd.choice([-10, -3, 3, 11, -6, 6]) * s
        pts.append((x + 8 + i * (w - 16) / 11, y + yy))
    draw.line(pts, fill=RED, width=2)


def ill_warsaw(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(18, 52, 110))
    cx, cy, r = x + w * 0.5, y + h * 0.5, min(w, h) * 0.38
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(255, 255, 255), width=2)
    for ang, ln in [(0, 1.0), (90, 1.0), (45, 0.62), (135, 0.62), (225, 0.62), (315, 0.62)]:
        import math
        a = math.radians(ang)
        draw.line([(cx, cy), (cx + ln * r * math.cos(a), cy - ln * r * math.sin(a))], fill=(255, 255, 255), width=3)
    draw.rectangle([x + 8, y + h - 24, x + w // 2 - 4, y + h - 12], fill=(255, 255, 255))
    draw.rectangle([x + 8, y + h - 12, x + w // 2 - 4, y + h], fill=RED)
    draw.rectangle([x + w // 2 + 4, y + h - 24, x + w - 8, y + h - 12], fill=(255, 255, 255))
    draw.rectangle([x + w // 2 + 4, y + h - 12, x + w - 8, y + h], fill=RED)


def ill_copenhagen(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(178, 34, 22))
    draw.rectangle([x + w * 0.30, y, x + w * 0.42, y + h], fill=(255, 255, 255))
    draw.rectangle([x, y + h * 0.42, x + w, y + h * 0.58], fill=(255, 255, 255))
    for i, cx in enumerate([x + w * 0.72, x + w * 0.82, x + w * 0.92]):
        draw.polygon([(cx - 7, y + 14), (cx, y + 4), (cx + 7, y + 14)], fill=GOLD)
        draw.rectangle([cx - 7, y + 14, cx + 7, y + 18], fill=GOLD)


def ill_kryvyi(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(24, 28, 44))
    draw.rectangle([x, y + h - 8, x + w, y + h], fill=(52, 58, 74))
    draw.line([(x, y + h - 16), (x + w * 0.42, y + h - 16)], fill=(200, 200, 200), width=3)
    draw.line([(x + w * 0.58, y + h - 22), (x + w, y + h - 22)], fill=(200, 200, 200), width=3)
    draw.line([(x + w * 0.42, y + h - 16), (x + w * 0.50, y + h - 28)], fill=(200, 200, 200), width=2)
    starburst(draw, x + w * 0.50, y + h * 0.42, 9, (255, 140, 40))
    starburst(draw, x + w * 0.80, y + h * 0.32, 7, (255, 196, 66))
    draw.line([(x + 10, y + 5), (x + w - 10, y + 5)], fill=(120, 120, 130), width=1)


def ill_hodeidah(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(14, 107, 107))
    draw.rectangle([x, y + h * 0.62, x + w, y + h], fill=(10, 80, 96))
    for cx in [x + 40, x + 130, x + 220]:
        draw.rectangle([cx, y + 18, cx + 6, y + h * 0.62], fill=(30, 30, 34))
        draw.line([(cx, y + 18), (cx + 34, y + 34)], fill=(30, 30, 34), width=4)
        draw.line([(cx + 34, y + 34), (cx + 34, y + 44)], fill=(30, 30, 34), width=2)
    draw.rectangle([x + w * 0.55, y + h * 0.66, x + w * 0.92, y + h * 0.80], fill=(40, 40, 44))
    draw.rectangle([x + w * 0.62, y + h * 0.52, x + w * 0.70, y + h * 0.66], fill=(60, 60, 64))
    for i in range(3):
        draw.ellipse([x + 20 + i * 26, y + 12 + i * 4, x + 44 + i * 26, y + 30 + i * 4], fill=(220, 220, 220))


def ill_brussels(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(0, 51, 153))
    import math
    cx, cy, r = x + w * 0.5, y + h * 0.48, min(w, h) * 0.34
    for i in range(12):
        a = math.radians(i * 30 - 90)
        sx, sy = cx + r * math.cos(a), cy + r * math.sin(a)
        starburst(draw, sx, sy, 5, (255, 204, 0), points=5)
    draw.text((x + w * 0.5 - 12, y + h - 24), "EU", font=font(16, 700), fill=(255, 255, 255))


def ill_cricket(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(56, 130, 62))
    draw.rectangle([x, y + h * 0.55, x + w, y + h], fill=(46, 110, 52))
    draw.rectangle([x + w * 0.62, y + 10, x + w * 0.68, y + h - 14], fill=(210, 180, 120))
    draw.rectangle([x + w * 0.58, y + 10, x + w * 0.72, y + 26], fill=(210, 180, 120))
    for sx in [x + w * 0.18, x + w * 0.24, x + w * 0.30]:
        draw.rectangle([sx, y + h - 34, sx + 4, y + h - 12], fill=(255, 255, 255))
    draw.ellipse([x + w * 0.82, y + 16, x + w * 0.82 + 16, y + 32], fill=RED, outline=(255, 255, 255), width=1)
    draw.text((x + 8, y + 6), "100", font=font(18, 700), fill=(255, 255, 255))


def ill_tennis(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(30, 90, 140))
    draw.rectangle([x + 10, y + 10, x + w - 10, y + h - 10], fill=(52, 130, 90))
    draw.line([(x + 10, y + h // 2), (x + w - 10, y + h // 2)], fill=(255, 255, 255), width=2)
    for lx in [x + w // 2 - 40, x + w // 2 + 40]:
        draw.line([(lx, y + 10), (lx, y + h - 10)], fill=(255, 255, 255), width=1)
    draw.ellipse([x + w - 34, y + 12, x + w - 14, y + 32], fill=(210, 230, 60), outline=(255, 255, 255), width=1)


def ill_washington(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(20, 33, 61))
    draw.ellipse([x + w // 2 - 26, y + 12, x + w // 2 + 26, y + 44], fill=(235, 235, 235))
    draw.rectangle([x + w // 2 - 34, y + 40, x + w // 2 + 34, y + 52], fill=(235, 235, 235))
    for i in range(5):
        px = x + w // 2 - 28 + i * 13
        draw.rectangle([px, y + 52, px + 7, y + h - 12], fill=(220, 220, 220))
    draw.rectangle([x + 10, y + h - 12, x + w - 10, y + h - 6], fill=(235, 235, 235))
    draw.rectangle([x + w - 58, y + 8, x + w - 14, y + 34], fill=(201, 162, 39))
    draw.text((x + w - 52, y + 13), "AI", font=font(13, 700), fill=(20, 33, 61))


ILLUSTRATIONS = {
    "riyadh": ill_riyadh, "cop31": ill_cop31, "mercury": ill_mercury,
    "quake": ill_quake, "warsaw": ill_warsaw, "copenhagen": ill_copenhagen,
    "kryvyi": ill_kryvyi, "hodeidah": ill_hodeidah, "brussels": ill_brussels,
    "cricket": ill_cricket, "tennis": ill_tennis, "washington": ill_washington,
}


# ---------------------------------------------------------------- content
HERO = [
    {"key": "riyadh", "num": 1, "place": "RIYADH, SAUDI ARABIA",
     "beat": "CONFLICT", "src": "Reuters, AP",
     "head": "Coalition downs three Houthi missiles over Riyadh",
     "body": "Air defences destroy three ballistic missiles fired at the capital early on Saturday, the second attack in days. A dawn drone is also downed."},
    {"key": "cop31", "num": 2, "place": "ANTALYA, TURKIYE",
     "beat": "CLIMATE", "src": "Reuters, Guardian",
     "head": "COP31 runs into overtime with no deal",
     "body": "Talks pass their Friday deadline into Saturday. A third draft drops fossil-fuel language and a $120bn adaptation target."},
    {"key": "mercury", "num": 3, "place": "MERCURY",
     "beat": "SPACE", "src": "ESA, JAXA",
     "head": "BepiColombo reaches Mercury after eight years",
     "body": "The European-Japanese craft fires its thrusters at 19:24 CET tonight to enter Mercury orbit, the first dual-orbiter mission there."},
]

MEDIUM = [
    {"key": "quake", "num": 4, "place": "JUNIN, PERU", "beat": "QUAKE", "src": "Reuters",
     "head": "Quake shakes Peru, felt in Lima",
     "body": "Magnitude 6.7 strikes Junin at 00:09 GMT on Saturday, 129 km deep. Felt in Lima; no casualties."},
    {"key": "warsaw", "num": 5, "place": "WARSAW, POLAND", "beat": "NATO", "src": "AP",
     "head": "Rutte in Warsaw as Poland seeks more NATO forces",
     "body": "NATO chief flies in on Saturday after Russian missiles land in Poland. Warsaw calls it a provocation."},
    {"key": "copenhagen", "num": 6, "place": "COPENHAGEN, DENMARK", "beat": "SECURITY", "src": "BBC",
     "head": "Denmark charges two over Russian murder plot",
     "body": "Two Danes charged over a Russian plot to kill a Ukrainian rapper. Denmark expels the defence attache."},
    {"key": "kryvyi", "num": 7, "place": "KRYVYI RIH, UKRAINE", "beat": "WAR", "src": "Kyiv Independent",
     "head": "Overnight strike kills 2, injures 42",
     "body": "Russian double-tap strike kills a child of seven and a paramedic; four children hurt, officials say."},
    {"key": "hodeidah", "num": 8, "place": "HODEIDAH, YEMEN", "beat": "WAR", "src": "Reports",
     "head": "Coalition hits Hodeidah port",
     "body": "Saudi-led jets strike Houthi-held port facilities on Friday. The Houthis threaten Saudi ports."},
    {"key": "brussels", "num": 9, "place": "BRUSSELS, EUROPE", "beat": "AID", "src": "EU",
     "head": "EU sends Ukraine record 7.9bn euros support",
     "body": "The bloc completes its largest-ever support payment to Kyiv, tied to reforms, as winter sets in."},
]

STATS = [
    ("3", "missiles over Riyadh", "Saudi coalition"),
    ("6.7", "Peru quake magnitude", "Peru Geophysics Institute"),
    ("42", "hurt in Kryvyi Rih strike", "Kyiv Independent"),
    ("8 yrs", "BepiColombo voyage", "ESA"),
    ("35%", "clean power by 2035", "Reuters"),
    ("100", "Rahul's Test century", "Reuters"),
]

BRIEFS = [
    ("US declassifies Middle East UFO footage", "BBC"),
    ("Mamdani to close New York's Rikers jail by 2032", "BBC"),
    ("ANC fights to keep South Africa's big cities", "BBC"),
    ("US jails Indian man 19 years over Sikh plot", "BBC"),
    ("French police jailed over Zecler beating", "BBC"),
    ("Myanmar rejects World Court genocide ruling", "NST"),
    ("Bayer $7.25bn Roundup payout approved", "Reports"),
    ("Pentagon memo limits US-Canada military ties", "Reports"),
    ("Estonia closes its border with Russia", "Reports"),
    ("Iraq raids Iran-backed militia oil network", "Reports"),
    ("US sanctions Iranian oil traders, Yemen bank", "Reports"),
    ("Sudan war keeps disabled children from school", "Reports"),
    ("Gaza raid ends; officials say 6,000 displaced", "Reports"),
    ("Israel talks stall; neither bloc holds 61 seats", "Reports"),
    ("Kane out for months with ankle ligament tear", "IANS"),
    ("India U17 qualify for Asian Cup 2027", "IANS"),
    ("Pakistan clinch Test series over Sri Lanka", "Nation"),
    ("UAE Bulls win Abu Dhabi T10 final by 24 runs", "Reports"),
    ("Lauren Price becomes undisputed world champion", "UK press"),
    ("Hazlewood may quit if Cummins loses captaincy", "IANS"),
    ("Cost-of-living protests sweep across Europe", "BBC"),
    ("South Korea catches 111 students in exam cheat", "BBC"),
    ("Nearly 600 women killed in South Africa in 3 months", "BBC"),
    ("Pattinson announced as the next James Bond", "BBC"),
    ("Rahul century puts India on top in Wellington", "Reuters"),
    ("ATP Finals semis: Alcaraz-Shelton, Zverev-Medvedev", "ATP"),
    ("Trump threatens ban on AI data centres abroad", "BBC"),
    ("Guinea bans Burkina Faso state broadcaster", "Night Watch"),
]

DATE_CHECK = ("DATE CHECK  -  Left out: Friday's news, NOT Saturday's: "
               "Kyiv bridges hit  -  Russian missiles land in Poland  -  "
               "Wall Street's AI sell-off  -  UK-EU summit deals  -  "
               "World Court Myanmar ruling  -  Cyclone Akvan landfall  -  "
               "Panama quake 7.7  -  Trump-Xi-Putin Shenzhen summit")

PINS = [
    (46.7, 24.6, 1, 0, 0), (30.7, 36.9, 2, 6, 12),
    (-76.0, -11.2, 4, 0, 0), (21.0, 52.2, 5, 10, -8), (12.6, 55.7, 6, -12, -10),
    (33.4, 47.9, 7, 12, 6), (42.9, 14.8, 8, 2, 4), (4.4, 50.8, 9, -14, 4),
]
PINS = [p for p in PINS if p[2] != 0]


def draw_card(draw, card, x, y, w, h, hero=False):
    draw.rectangle([x, y, x + w, y + h], fill=CARD_BG, outline=SLATE, width=1)
    ill_h = 104 if hero else 34
    ILLUSTRATIONS[card["key"]](draw, x + 1, y + 1, w - 2, ill_h)
    ky = y + ill_h + 1
    kh = kicker_bar(draw, x + 1, ky, w - 2,
                    "%s  -  %s  -  %s" % (card["place"], card["beat"], card["src"]),
                    size=11 if hero else 9)
    ty = ky + kh + 5
    hs = 19 if hero else 14
    hw = 600 if hero else 700
    head_lines = fit_lines(draw, card["head"], hs, hw, w - 14, 2 if hero else 2)
    ty = draw_text_block(draw, x + 7, ty, head_lines, hs, hw, INK, leading=hs + 3)
    bs = 12 if hero else 11
    body_lines = fit_lines(draw, card["body"], bs, 400, w - 14, 3 if hero else 2)
    draw_text_block(draw, x + 7, ty + 2, body_lines, bs, 400, (40, 50, 70), leading=bs + 3)


def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    # masthead
    d.text((M, 8), "THE WORLD IN ONE DAY", font=font(19, 700), fill=RED)
    right = "37 STORIES  -  6 CONTINENTS  -  EVERY ONE DATED"
    d.text((W - M - text_w(d, right, 13, 700), 12), right, font=font(13, 700), fill=NAVY)
    d.line([(M, 34), (W - M, 34)], fill=INK, width=2)
    # giant date
    date = "Saturday 21 November 2026"
    dw = text_w(d, date, 56, 700)
    d.text(((W - dw) / 2, 40), date, font=font(56, 700), fill=INK)
    sub = "Riyadh intercepts three missiles  -  COP31 into overtime  -  BepiColombo at Mercury  -  Rutte in Warsaw"
    sw = text_w(d, sub, 15, 500)
    d.text(((W - sw) / 2, 106), sub, font=font(15, 500), fill=(40, 50, 70))
    d.line([(M, 130), (W - M, 130)], fill=RULE, width=1)
    # stat strip
    y0, y1 = 136, 196
    cw = (W - 2 * M) / 6
    for i, (num, label, src) in enumerate(STATS):
        cx = M + i * cw
        if i:
            d.line([(cx, y0 + 6), (cx, y1 - 6)], fill=RULE, width=1)
        nw = text_w(d, num, 26, 700)
        d.text((cx + (cw - nw) / 2, y0), num, font=font(26, 700), fill=RED if i % 2 == 0 else NAVY)
        lw = text_w(d, label, 11, 500)
        d.text((cx + (cw - lw) / 2, y0 + 32), label, font=font(11, 500), fill=(40, 50, 70))
        sw2 = text_w(d, src, 9, 400)
        d.text((cx + (cw - sw2) / 2, y0 + 47), src, font=font(9, 400), fill=SLATE)
    d.line([(M, y1 + 4), (W - M, y1 + 4)], fill=INK, width=2)
    # hero cards
    hy = 206
    hw = (W - 2 * M - 16) // 3
    for i, card in enumerate(HERO):
        draw_card(d, card, M + i * (hw + 8), hy, hw, 222, hero=True)
    # medium cards: 2 rows x 3
    my = hy + 222 + 8
    mh = 120
    for r in range(2):
        for c in range(3):
            card = MEDIUM[r * 3 + c]
            draw_card(d, card, M + c * (hw + 8), my + r * (mh + 8), hw, mh)
    # map + briefs
    by = my + 2 * mh + 1 * 8 + 8
    bh = 902 - by
    d.text((M, by), "WHERE IT HAPPENED", font=font(13, 700), fill=NAVY)
    map_x, map_y = M, by + 20
    map_w, map_h = 296, bh - 34
    draw_world_map(d, map_x, map_y, map_w, map_h, PINS)
    d.text((map_x, map_y + map_h + 2), "Pins 1-9 mark the card stories. No. 3 is in space: Mercury.",
           font=font(9, 400), fill=SLATE)
    bx = M + 296 + 12
    bw = W - M - bx
    d.text((bx, by), "ALSO ON SATURDAY 21 NOVEMBER  -  28 MORE STORIES", font=font(13, 700), fill=NAVY)
    col_w = (bw - 12) // 2
    ly = by + 22
    for i, (text, src) in enumerate(BRIEFS):
        col = 0 if i < 14 else 1
        row = i if i < 14 else i - 14
        x = bx + col * (col_w + 12)
        yy = ly + row * 14
        line = "- %s (%s)" % (text, src)
        lines = fit_lines(d, line, 11, 400, col_w, 1)
        if lines:
            d.text((x, yy), lines[0], font=font(11, 400), fill=(30, 40, 60))
    # date check
    dy = 908
    d.rectangle([M, dy, W - M, dy + 62], outline=RED, width=2, fill=(253, 238, 234))
    dc = fit_lines(d, DATE_CHECK, 11, 400, W - 2 * M - 20, 3)
    draw_text_block(d, M + 10, dy + 6, dc, 11, 400, (120, 20, 10), leading=15)
    # footer
    foot = ("Every story here happened, or was first reported, on Saturday 21 November 2026 "
            "in at least one time zone. Claims are attributed; forecasts are flagged. Original drawings.")
    fl = fit_lines(d, foot, 10, 400, W - 2 * M, 2)
    draw_text_block(d, M, dy + 68, fl, 10, 400, SLATE, leading=13)
    return img


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "entry.png"
    build().save(out, "PNG", optimize=True)
    print("wrote", out)

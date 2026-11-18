#!/usr/bin/env python3
"""news-image-20261117 v3 — one front page summing up Tuesday 17 November 2026.

Draws entry.png (1024x1024, <=1 MiB) with Pillow only, stdlib only, no network.
Deterministic: no timestamps, no randomness, fixed fonts and geometry.
Every story below was first reported on Tuesday 17 November 2026 and confirmed
by at least two sources. The program counts the stories it draws and prints
the true total; masthead and ALSO counts come from those same counts.
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (247, 242, 231)
CARD = (255, 253, 245)
INK = (22, 24, 29)
NAVY = (22, 40, 63)
RED = (176, 42, 33)
GOLD = (201, 162, 39)
GREY = (120, 118, 110)
LINE = (190, 184, 170)
DOT = (122, 138, 122)

F_SERIF_B = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
F_SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
F_SANS_B = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
F_SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"


def F(path, size):
    return ImageFont.truetype(path, size)


# ---------------------------------------------------------------- data
LEADS = [
    ("EUROPE", "UKRAINE WAR",
     "Ukraine says a Crimea Bridge road span fell into the sea",
     "Second strike in two days; Zelensky hails an \u2018unprecedented operation\u2019. "
     "Russia hits Kyiv\u2019s bridges in reply."),
    ("MIDDLE EAST", "IRAN WAR",
     "Iran sends drones at a US radar in Bahrain; US hits back",
     "Bahrain and the US say all were downed; US jets then strike Qeshm. "
     "Iran says tankers hit mines in Hormuz."),
    ("ASIA", "DIPLOMACY",
     "Trump holds his first Quad summit, in Manila",
     "The four unveil critical-minerals deals; Putin reaches Shenzhen for "
     "Thursday\u2019s talks with Trump and Xi."),
]

MIDS = [
    ("AFRICA", "HEALTH", "Ebola cases in DR Congo top 11,000, WHO says",
     "Cases more than doubled in three months; about 5,400 have died."),
    ("GLOBAL", "CLIMATE", "COP31 divided over a fossil-fuel phase-out",
     "Nations weigh the first draft; the Antalya talks end Friday."),
    ("AMERICAS", "HEALTH", "US, Mexico and Bolivia lose measles-free status",
     "PAHO cites a year of spread; the US has 5,700+ cases in 2026."),
    ("US", "BUSINESS", "Nvidia\u2019s quarterly sales double to $115.8bn",
     "Reported after the close. Earlier the Dow fell 849 points."),
    ("MIDDLE EAST", "GAZA", "Gaza truce at risk of collapse, UN is told",
     "Board of Peace report; UN agencies say 1.4m face acute hunger."),
    ("ASIA", "POLITICS", "Mongolia\u2019s president says he will resign",
     "Khurelsukh denies a $25m bribe claim; parliament must accept."),
    ("EUROPE", "POLITICS", "Serbia\u2019s student-led majority takes its seats",
     "Student List holds 140 of 250; Vu\u010di\u0107\u2019s party goes into opposition."),
    ("ASIA", "LABOUR", "Bangladesh police tear-gas garment workers",
     "They want Tk 30,000 a month, up from 12,500; 37 factories shut."),
    ("RUSSIA", "AIR CRASH", "Russian An-12 crash in Siberia kills all 19",
     "The air force plane came down near Kemerovo; a fault is suspected."),
]

# (number, keyword, rest-of-line) — keyword is bold, rest is regular.
ONES = [
    (13, "RUSSIA", "says it downed a record 1,441 drones overnight"),
    (14, "KYIV", "missiles hit the North and South Dnipro bridges"),
    (15, "UN", "Ukraine\u2019s civilian deaths this year top all of 2025"),
    (16, "PRAGUE", "two trains collide; 46 people injured"),
    (17, "FRANCE", "public-sector strike; 146,000 march"),
    (18, "POLAND", "Tusk\u2019s government survives a no-confidence vote"),
    (19, "GERMANY", "Deutsche Bank shares fall after a huge data leak"),
    (20, "MOLDOVA", "shuts its airspace as a drone nears Chi\u0219in\u0103u"),
    (21, "TURKEY", "police seize opposition broadcaster S\u00f6zc\u00fc TV"),
    (22, "FOOTBALL", "Norway win 3\u20132 in Denmark; Haaland scores twice"),
    (23, "VATICAN", "Pope Leo XIV returns from his South America tour"),
    (24, "UK", "sanctions 8 settlement firms and the group Tzav 9"),
    (25, "ISRAEL", "Eisenkot ally Matan Kahana elected speaker, 66\u201352"),
    (26, "WEST BANK", "settlers kill a woman, 72, near Jericho"),
    (27, "OMAN", "Iran\u2019s Araghchi holds shipping-safety talks"),
    (28, "INDIA", "Cyclone Akvan strengthens; Odisha evacuates"),
    (29, "INDIA", "bus falls into an Uttarakhand gorge; 8 dead"),
    (30, "JAPAN", "protests a Russian airspace intrusion near Fukuoka"),
    (31, "CHINA\u2013CANADA", "more tariff cuts after Carney\u2013Xi talks"),
    (32, "MALAYSIA", "Macron visit seals a strategic partnership"),
    (33, "THAILAND", "pledges to scrap tariffs on US goods"),
    (34, "SOUTH KOREA", "IMF lifts 2026 growth forecast to 3.9%"),
    (35, "FOOTBALL", "India beat Pakistan 2\u20131 in SAFF final"),
    (36, "KENYA", "WFP aids 30,000 who fled Ethiopia clashes"),
    (37, "FOOTBALL", "Togo beat Algeria 3\u20130 in AFCON qualifier"),
    (38, "HAITI", "Aristide\u2019s party will field no candidates"),
    (39, "US SENATE", "Van Hollen challenges Schumer for leader"),
    (40, "AUSTRALIA", "eases planned backpacker visa curbs"),
]

# Numbered map pins (story number, longitude, latitude, display offset dx, dy).
# Offsets only spread the tight Europe / Middle East cluster so no two
# numbered pins overlap; every pin stays next to its true location.
PINS = [
    (1, 36.5, 45.3, 10, -10), (2, 50.5, 26.2, 11, 3), (3, 121.0, 14.6, 0, 0),
    (4, 25.0, -2.0, 0, 0), (5, 30.7, 36.9, -11, 8), (6, -98.0, 39.0, 0, 0),
    (7, -122.0, 37.0, 0, 0), (8, 34.5, 31.5, 9, 10), (9, 106.9, 47.9, 0, 0),
    (10, 20.8, 44.8, -11, -10), (11, 90.4, 23.8, 0, 0), (12, 86.0, 55.4, 0, 0),
]

LEGEND = [
    ("Americas", (176, 42, 33)), ("Europe", (43, 94, 167)),
    ("Middle East", (208, 122, 31)), ("Asia", (122, 79, 163)),
    ("Africa", (61, 139, 79)), ("Oceania", (31, 138, 138)),
    ("Global", (119, 119, 119)),
]

# Coarse ASCII world landmask, 96 columns x 44 rows ('#' = land).
# Longitude -170..190 left to right, latitude 75..-55 top to bottom.
# Rows are normalised to 96 chars at draw time, so small length drift is safe.
LAND_ROWS = [
    "  #######         #############                         ###################################   ",
    " #########   ##################  ####                 ####################################  ",
    "########### ###################  ####   #######       ###################################### ",
    "  #######################       ####   #######       ###################################### ",
    "  #######################            ########        #####################################  ",
    "  #######################  ##        ######         ####################################   ",
    "  ######################   ###  ############        ####################################   ",
    "  ######################        ##############     ###################################     ",
    "  #####################         ###############   ##################################  ##   ",
    "  ####################          ###############  ################################  ###    ",
    "  ###################           ##############  ###############################    ###     ",
    "  ###################   ####   ################ ################################   ##      ",
    "  ################  #####  ##################  #######################  #############      ",
    "   ######  #####   #######################   #################  ########  ############       ",
    "    #####   ######################  #######  ###############  ########  ##########          ",
    "     #####   #####################  ######   ##############  ########  ##########           ",
    "     ####    #####################   #####   #############  ########  ##########             ",
    "     ####     ####################   ####   ############   #######   #########               ",
    "       #########################    ####   ###########    #######   #########  ##            ",
    "       ##########################   ###    #########      #####     ###############          ",
    "       ###########################   ##    #########               #################         ",
    "       ###########################   #     #########              ################          ",
    "       ############################        #########              ###############           ",
    "        ###########################        #########              ##############            ",
    "        ##########################         #########                                            ",
    "        ##########################         #########                                            ",
    "         #########################         #########                                            ",
    "         ########################          #########                                            ",
    "         #######################           ########                                             ",
    "         ######################            #######                                              ",
    "          #####################            #######          ##########                          ",
    "          #####################            #######         ###########                         ",
    "          ####################             ######         ###########                         ",
    "           ###################             ######         ###########                         ",
    "           ###################             #####          ##########                          ",
    "           ##################              ####           ########                           ",
    "           #################               ####           #######                 ##          ",
    "            ################               ###            #####                  ##           ",
    "            ################                            ####                               ",
    "            ################                                                                    ",
    "            ################                                                                    ",
    "            ################                                                                    ",
    "            ################                                                                    ",
    "            ################                                                                    ",
]


# ---------------------------------------------------------------- helpers
def wrap(d, text, font, max_w):
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if d.textlength(t, font=font) <= max_w or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit_lines(d, text, sizes, path, max_w, max_lines):
    """Try font sizes largest-first; return (font, lines) fitting max_lines."""
    for s in sizes:
        f = F(path, s)
        lines = wrap(d, text, f, max_w)
        if len(lines) <= max_lines:
            return f, lines
    f = F(path, sizes[-1])
    return f, wrap(d, text, f, max_w)[:max_lines]


def dashed_line(d, p0, p1, fill, dash=5, gap=4, width=2):
    import math
    x0, y0 = p0
    x1, y1 = p1
    dist = math.hypot(x1 - x0, y1 - y0)
    if dist == 0:
        return
    steps = int(dist / (dash + gap)) + 1
    for i in range(steps):
        t0 = i * (dash + gap) / dist
        t1 = min(1.0, t0 + dash / dist)
        d.line([(x0 + (x1 - x0) * t0, y0 + (y1 - y0) * t0),
                (x0 + (x1 - x0) * t1, y0 + (y1 - y0) * t1)],
               fill=fill, width=width)


def star(d, cx, cy, r, fill):
    import math
    pts = []
    for i in range(16):
        ang = math.pi * i / 8 - math.pi / 2
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    d.polygon(pts, fill=fill)


def small_flag(d, x, y, w, h, kind):
    """Tiny stylised flag on a pole at (x, y); kind selects the design."""
    d.line([(x, y), (x, y - h - 14)], fill=INK, width=2)
    if kind == "us":
        d.rectangle([x, y - h - 14, x + w, y - 14], fill=(255, 255, 255),
                    outline=INK)
        for i in range(0, h, 4):
            if (i // 4) % 2 == 0:
                d.rectangle([x, y - h - 14 + i, x + w, y - h - 14 + i + 2],
                            fill=RED)
        d.rectangle([x, y - h - 14, x + w // 2, y - h - 14 + h // 2],
                    fill=NAVY)
    elif kind == "in":
        d.rectangle([x, y - h - 14, x + w, y - h - 14 + h // 3],
                    fill=(255, 153, 51))
        d.rectangle([x, y - h - 14 + h // 3, x + w, y - h - 14 + 2 * h // 3],
                    fill=(255, 255, 255), outline=INK)
        d.rectangle([x, y - h - 14 + 2 * h // 3, x + w, y - 14],
                    fill=(19, 136, 8))
        d.ellipse([x + w // 2 - 3, y - h - 14 + h // 3 + 1,
                   x + w // 2 + 3, y - h - 14 + 2 * h // 3 - 1],
                  outline=NAVY)
    elif kind == "jp":
        d.rectangle([x, y - h - 14, x + w, y - 14], fill=(255, 255, 255),
                    outline=INK)
        d.ellipse([x + w // 2 - 4, y - h - 14 + h // 2 - 4,
                   x + w // 2 + 4, y - h - 14 + h // 2 + 4], fill=RED)
    else:  # au
        d.rectangle([x, y - h - 14, x + w, y - 14], fill=(0, 40, 104),
                    outline=INK)
        d.ellipse([x + w // 2 - 3, y - h - 14 + h // 2 - 3,
                   x + w // 2 + 3, y - h - 14 + h // 2 + 3],
                  fill=(255, 255, 255))


def num_badge(d, x, y, n, r=10):
    d.ellipse([x - r, y - r, x + r, y + r], fill=RED, outline=(255, 255, 255))
    f = F(F_SANS_B, 12)
    t = str(n)
    d.text((x - d.textlength(t, font=f) / 2, y - 8), t, font=f,
           fill=(255, 255, 255))


# ---------------------------------------------------------------- banners
def banner_bridge(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(220, 233, 242))
    sea_y = y + int(h * 0.62)
    d.rectangle([x, sea_y, x + w, y + h], fill=(111, 158, 196))
    for i in range(3):  # waves
        d.arc([x + 12 + i * 90, sea_y + 8, x + 52 + i * 90, sea_y + 22],
              200, 340, fill=(255, 255, 255), width=2)
    # towers + arch cable above the deck
    for tx in (x + 52, x + w - 52):
        d.line([(tx, y + 14), (tx, sea_y + 6)], fill=INK, width=4)
    d.arc([x + 52, y + 2, x + w - 52, y + 58], 180, 360, fill=INK, width=3)
    # deck in two pieces with a gap in the middle (the fallen span)
    d.line([(x + 8, sea_y - 14), (x + w // 2 - 26, sea_y - 14)], fill=INK,
           width=5)
    d.line([(x + w // 2 + 26, sea_y - 14), (x + w - 8, sea_y - 14)], fill=INK,
           width=5)
    # falling span piece, tilted, dropping into the sea
    d.polygon([(x + w // 2 - 22, sea_y - 12), (x + w // 2 + 6, sea_y + 2),
               (x + w // 2 + 2, sea_y + 12), (x + w // 2 - 26, sea_y - 2)],
              fill=(60, 60, 66))
    # explosion star + smoke over the gap
    star(d, x + w // 2, y + 26, 22, (255, 176, 32))
    star(d, x + w // 2, y + 26, 12, (255, 90, 32))
    for cx, cy, r in ((x + w // 2 - 34, y + 16, 9), (x + w // 2 + 32, y + 12, 8),
                      (x + w // 2 - 44, y + 30, 6)):
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(120, 120, 124))


def banner_gulf(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(188, 216, 232))
    # simplified land: Arabia (left-bottom) and Iran (top-right)
    d.polygon([(x + 8, y + h - 6), (x + 8, y + 34), (x + 92, y + 30),
               (x + 128, y + 52), (x + 118, y + h - 6)], fill=(232, 217, 168))
    d.polygon([(x + 150, y + 6), (x + w - 8, y + 6), (x + w - 8, y + 34),
               (x + 210, y + 44), (x + 168, y + 58), (x + 148, y + 40)],
              fill=(226, 205, 150))
    # strait water gap + radar rings at Bahrain
    bx, by = x + 138, y + 52
    for r in (7, 13, 19):
        d.ellipse([bx - r, by - r, bx + r, by + r], outline=RED, width=2)
    d.ellipse([bx - 3, by - 3, bx + 3, by + 3], fill=RED)
    # dashed drone flight paths + drone dots
    dashed_line(d, (x + 176, y + 12), (bx + 4, by - 2), (40, 40, 46))
    dashed_line(d, (x + 210, y + 66), (bx + 6, by + 6), (40, 40, 46))
    for dx, dy in ((x + 176, y + 12), (x + 196, y + 26), (x + 210, y + 66),
                   (x + 186, y + 70)):
        d.ellipse([dx - 4, dy - 4, dx + 4, dy + 4], fill=INK)
        d.line([(dx - 8, dy), (dx + 8, dy)], fill=INK, width=2)
    # tanker dots in the strait
    for tx, ty in ((x + 128, y + 66), (x + 152, y + 72)):
        d.rectangle([tx - 7, ty - 3, tx + 7, ty + 3], fill=(90, 60, 40))


def banner_summit(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=NAVY)
    d.ellipse([x + 18, y + 8, x + w - 18, y + 34], fill=(201, 162, 39))
    # four flags behind the table
    for fx, kind in ((x + 42, "us"), (x + 108, "in"), (x + 178, "jp"),
                     (x + 244, "au")):
        small_flag(d, fx, y + 46, 30, 16, kind)
    # table + name plates on its front
    d.rectangle([x + 30, y + 46, x + w - 30, y + 66], fill=(122, 82, 52))
    d.rectangle([x + 30, y + 46, x + w - 30, y + 52], fill=(150, 106, 70))
    for cx in (x + 62, x + 128, x + 192, x + 258):
        d.rectangle([cx - 12, y + 54, cx + 12, y + 63],
                    fill=(247, 242, 231), outline=GOLD)


# ---------------------------------------------------------------- mid icons
def icon_panel(d, x, y, s, bg):
    d.rectangle([x, y, x + s, y + s], fill=bg, outline=LINE)


def icon_virus(d, x, y, s, col):
    cx, cy = x + s // 2, y + s // 2
    for k in range(8):
        import math
        a = math.pi * k / 4
        d.line([(cx + 10 * math.cos(a), cy + 10 * math.sin(a)),
                (cx + 17 * math.cos(a), cy + 17 * math.sin(a))],
               fill=col, width=2)
    d.ellipse([cx - 10, cy - 10, cx + 10, cy + 10], fill=col)
    for ox, oy in ((-13, -11), (14, -12), (12, 13)):
        d.ellipse([cx + ox - 3, cy + oy - 3, cx + ox + 3, cy + oy + 3],
                  fill=col)


def draw_icon(d, idx, x, y, s):
    if idx == 4:  # Ebola / virus
        icon_panel(d, x, y, s, (220, 239, 224))
        icon_virus(d, x, y, s, (46, 125, 62))
    elif idx == 5:  # COP31 / thermometer
        icon_panel(d, x, y, s, (253, 238, 205))
        cx = x + s // 2
        d.rectangle([cx - 4, y + 8, cx + 4, y + s - 14], fill=(255, 255, 255),
                    outline=INK)
        d.rectangle([cx - 2, y + 12, cx + 2, y + s - 18], fill=RED)
        d.ellipse([cx - 8, y + s - 20, cx + 8, y + s - 4], fill=RED)
        for ty in (y + 12, y + 20, y + 28):
            d.line([(cx + 4, ty), (cx + 9, ty)], fill=INK, width=1)
    elif idx == 6:  # measles / virus trio
        icon_panel(d, x, y, s, (251, 227, 224))
        icon_virus(d, x + 2, y + 2, s - 18, (176, 42, 33))
        d.ellipse([x + s - 16, y + s - 16, x + s - 6, y + s - 6],
                  fill=(176, 42, 33))
        d.ellipse([x + s - 15, y + 6, x + s - 7, y + 14], fill=(176, 42, 33))
    elif idx == 7:  # Nvidia / rising bars
        icon_panel(d, x, y, s, (15, 46, 26))
        bars = [10, 16, 22, 30]
        for i, bh in enumerate(bars):
            bx = x + 7 + i * 10
            d.rectangle([bx, y + s - 7 - bh, bx + 7, y + s - 7],
                        fill=(118, 200, 90))
        d.line([(x + 6, y + 12), (x + s - 6, y + 6)], fill=(255, 255, 255),
               width=2)
        d.polygon([(x + s - 12, y + 4), (x + s - 4, y + 4), (x + s - 8, y + 12)],
                  fill=(255, 255, 255))
    elif idx == 8:  # Gaza / tents
        icon_panel(d, x, y, s, (242, 227, 194))
        for tx, th in ((x + 6, 18), (x + 24, 24)):
            d.polygon([(tx, y + s - 8 - th), (tx + 16, y + s - 8 - th),
                       (tx + 8, y + s - 8)], fill=(176, 130, 70),
                      outline=INK)
        d.line([(x + s - 8, y + 8), (x + s - 8, y + 26)], fill=INK, width=2)
        d.polygon([(x + s - 8, y + 8), (x + s + 2, y + 12), (x + s - 8, y + 16)],
                  fill=RED)
    elif idx == 9:  # Mongolia / parliament
        icon_panel(d, x, y, s, (220, 230, 245))
        d.polygon([(x + 8, y + 16), (x + s - 8, y + 16), (x + s // 2, y + 6)],
                  fill=NAVY)
        for i in range(4):
            cx = x + 11 + i * 9
            d.rectangle([cx, y + 18, cx + 4, y + s - 10], fill=NAVY)
        d.rectangle([x + 6, y + s - 10, x + s - 6, y + s - 6], fill=NAVY)
    elif idx == 10:  # Serbia / ballot box
        icon_panel(d, x, y, s, (227, 232, 247))
        d.rectangle([x + 10, y + 8, x + s - 14, y + 16], fill=(255, 255, 255),
                    outline=INK)
        d.rectangle([x + 8, y + 18, x + s - 8, y + s - 8], fill=(43, 94, 167))
        d.rectangle([x + 16, y + 22, x + s - 16, y + 26], fill=(22, 24, 29))
        d.line([(x + 14, y + s - 14), (x + 20, y + s - 20), (x + 30, y + s - 28)],
               fill=(255, 255, 255), width=2)
    elif idx == 11:  # Bangladesh / factory
        icon_panel(d, x, y, s, (253, 232, 210))
        d.rectangle([x + 8, y + 22, x + s - 8, y + s - 8], fill=(208, 122, 31))
        d.rectangle([x + 10, y + 12, x + 16, y + 24], fill=(120, 70, 20))
        for cx, cy, r in ((x + 14, y + 6, 3), (x + 20, y + 3, 2)):
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(150, 150, 150))
        for wx in (x + 20, x + 28, x + 36):
            d.rectangle([wx, y + 28, wx + 5, y + 33], fill=(255, 255, 255))
    else:  # 12 — An-12 / plane
        icon_panel(d, x, y, s, (228, 228, 232))
        d.polygon([(x + 6, y + 26), (x + 30, y + 14), (x + s - 6, y + 18),
                   (x + 30, y + 24), (x + 20, y + 30), (x + 8, y + 30)],
                  fill=(90, 90, 96))
        d.line([(x + 30, y + 14), (x + 26, y + 6)], fill=(90, 90, 96), width=3)
        for cx, cy, r in ((x + 8, y + 12, 3), (x + 14, y + 8, 2)):
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(150, 150, 150))
        d.line([(x + 6, y + s - 6), (x + s - 6, y + s - 6)], fill=INK, width=2)


# ---------------------------------------------------------------- build
def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    total = len(LEADS) + len(MIDS) + len(ONES)
    assert total == 40, total

    MX = 22                      # side margin
    CW = W - 2 * MX              # 980 content width

    # ---- 1. masthead (y 0..104)
    f_top = F(F_SANS_B, 13)
    d.text((MX, 12), "THE WORLD\u2019S NEWS IN ONE PICTURE", font=f_top,
           fill=RED)
    right = "%d STORIES \u00b7 6 CONTINENTS \u00b7 ALL FROM TUESDAY" % total
    d.text((W - MX - d.textlength(right, font=f_top), 12), right, font=f_top,
           fill=(150, 118, 20))
    d.text((MX, 34), "Tuesday 17 November 2026", font=F(F_SERIF_B, 60),
           fill=INK)
    d.line([(MX, 106), (W - MX, 106)], fill=RED, width=3)

    # ---- 2. lead row (y 112..317)
    lead_y, lead_h = 112, 205
    lead_w = (CW - 20) // 3
    banners = (banner_bridge, banner_gulf, banner_summit)
    for i, (region, cat, head, desc) in enumerate(LEADS):
        x = MX + i * (lead_w + 10)
        d.rectangle([x, lead_y, x + lead_w, lead_y + lead_h], fill=CARD,
                    outline=LINE)
        banners[i](d, x + 1, lead_y + 1, lead_w - 2, 72)
        ty = lead_y + 72 + 7
        num_badge(d, x + 12, ty + 8, i + 1, r=10)
        f_cat = F(F_SANS_B, 11)
        d.text((x + 28, ty), "%s \u00b7 %s" % (region, cat), font=f_cat,
               fill=RED)
        ty += 20
        f_head, lines = fit_lines(d, head, [23, 22, 21], F_SERIF_B,
                                  lead_w - 16, 3)
        for ln in lines:
            d.text((x + 8, ty), ln, font=f_head, fill=INK)
            ty += f_head.size + 2
        ty += 2
        f_desc = F(F_SERIF, 12)
        for ln in wrap(d, desc, f_desc, lead_w - 16)[:3]:
            d.text((x + 8, ty), ln, font=f_desc, fill=(60, 60, 64))
            ty += 15

    # ---- 3. mid grid (y 325..613), 3 x 3, row height 92
    mid_y, mid_h, mid_gap = 325, 92, 6
    mid_w = (CW - 20) // 3
    for i, (region, cat, head, desc) in enumerate(MIDS):
        r, c = divmod(i, 3)
        x = MX + c * (mid_w + 10)
        y = mid_y + r * (mid_h + mid_gap)
        d.rectangle([x, y, x + mid_w, y + mid_h], fill=CARD, outline=LINE)
        draw_icon(d, i + 4, x + 8, y + 8, 46)
        tx = x + 62
        num_badge(d, tx + 9, y + 12, i + 4, r=9)
        f_cat = F(F_SANS_B, 10)
        d.text((tx + 22, y + 5), "%s \u00b7 %s" % (region, cat), font=f_cat,
               fill=RED)
        ty = y + 24
        f_head, lines = fit_lines(d, head, [17, 16], F_SERIF_B, mid_w - 70, 2)
        for ln in lines:
            d.text((tx, ty), ln, font=f_head, fill=INK)
            ty += f_head.size + 1
        f_desc = F(F_SERIF, 11)
        for ln in wrap(d, desc, f_desc, mid_w - 70)[:2]:
            d.text((tx, ty), ln, font=f_desc, fill=(60, 60, 64))
            ty += 13

    # ---- 4. bottom split (y 621..996)
    bot_y = 621
    map_x, map_w = MX, 460
    d.text((map_x, bot_y), "WHERE IT HAPPENED", font=F(F_SANS_B, 13),
           fill=INK)
    d.line([(map_x, bot_y + 18), (map_x + map_w, bot_y + 18)], fill=RED,
           width=2)
    # dot-matrix world map
    gx, gy = map_x + 14, bot_y + 26
    cell = 4.5
    grid_w, grid_h = 96 * cell, 44 * cell
    for ri, row in enumerate(LAND_ROWS):
        row = (row + " " * 96)[:96]
        for ci, ch in enumerate(row):
            if ch == "#":
                cx = gx + ci * cell + cell / 2
                cy = gy + ri * cell + cell / 2
                d.ellipse([cx - 1.6, cy - 1.6, cx + 1.6, cy + 1.6], fill=DOT)
    f_pin = F(F_SANS_B, 10)
    for n, lon, lat, dx, dy in PINS:
        px = gx + (lon + 170) / 360.0 * grid_w + dx
        py = gy + (75 - lat) / 130.0 * grid_h + dy
        d.ellipse([px - 8, py - 8, px + 8, py + 8], fill=RED,
                  outline=(255, 255, 255), width=1)
        t = str(n)
        d.text((px - d.textlength(t, font=f_pin) / 2, py - 7), t, font=f_pin,
               fill=(255, 255, 255))
    cap_y = gy + int(grid_h) + 8
    d.text((map_x, cap_y),
           "Pins: stories 1\u201312 \u00b7 dots: 13\u201340.",
           font=F(F_SANS, 11), fill=(60, 60, 64))
    # region legend, two rows
    lx, ly = map_x, cap_y + 20
    f_leg = F(F_SANS_B, 10)
    col = 0
    for name, colr in LEGEND:
        wlab = d.textlength(name, font=f_leg) + 16
        if lx + wlab > map_x + map_w and col > 0:
            lx, ly = map_x, ly + 16
            col = 0
        d.rectangle([lx, ly + 2, lx + 9, ly + 11], fill=colr)
        d.text((lx + 12, ly), name, font=f_leg, fill=INK)
        lx += wlab + 8
        col += 1

    # right: ALSO list, 2 columns x 14 rows
    rx, rw = map_x + map_w + 10, W - MX - (map_x + map_w + 10)
    d.text((rx, bot_y),
           "ALSO ON TUESDAY 17 NOVEMBER \u00b7 %d MORE STORIES" % len(ONES),
           font=F(F_SANS_B, 13), fill=INK)
    d.line([(rx, bot_y + 18), (rx + rw, bot_y + 18)], fill=RED, width=2)
    col_w = (rw - 12) // 2
    list_top = bot_y + 26
    list_h = 996 - list_top
    # adaptive font size so 14 rows always fit
    for size in (10.5, 10, 9.5, 9):
        fb, fr = F(F_SANS_B, int(size)), F(F_SANS, int(size))
        lead = int(size) + 2
        rows = []
        ok = True
        for n, kw, rest in ONES:
            toks = [("%d. %s" % (n, kw), fb), ("\u2014", fb)]
            toks += [(w, fr) for w in rest.split()]
            lines, cur, cur_w = [], [], 0.0
            for w, fnt in toks:
                ww = d.textlength(w + " ", font=fnt)
                if cur and cur_w + ww > col_w:
                    lines.append(cur)
                    cur, cur_w = [(w, fnt)], ww
                else:
                    cur.append((w, fnt))
                    cur_w += ww
            if cur:
                lines.append(cur)
            rows.append(lines)
            if len(lines) > 2:
                ok = False
        if ok and max(len(r) for r in rows) * lead * 14 <= list_h:
            break
    y = list_top
    for ci in range(2):
        yy = list_top
        for ri in range(14):
            lines = rows[ci * 14 + ri]
            for toks in lines:
                xx = rx + ci * (col_w + 12)
                for w, fnt in toks:
                    d.text((xx, yy), w + " ", font=fnt, fill=INK)
                    xx += d.textlength(w + " ", font=fnt)
                yy += lead
            yy += 2
        y = max(y, yy)

    # ---- 5. footer
    d.line([(MX, 1000), (W - MX, 1000)], fill=LINE, width=1)
    d.text((MX, 1006),
           "Every story here happened or was first reported on Tuesday 17 November 2026. "
           "Contested claims are marked as claims. Sources: Reuters, AP, AFP, BBC, "
           "Al Jazeera, WHO, UN. Original drawings.",
           font=F(F_SANS, 10), fill=(90, 88, 82))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img.save(out, format="PNG")
    print("STORIES total=%d leads=%d mids=%d oneliners=%d" %
          (total, len(LEADS), len(MIDS), len(ONES)))
    print("WROTE", out)


if __name__ == "__main__":
    main()

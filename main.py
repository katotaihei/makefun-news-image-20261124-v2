#!/usr/bin/env python3
"""Sum up 24 November 2026's world news in one image.

Pure Python 3 standard library only. No network, no clock, no
randomness: every run writes exactly the same bytes.

The picture is a newspaper front page for Tuesday 24 November
2026. Six main stories, each cross-checked against that day's
reporting (Reuters, AP, CNN, Bloomberg, The Guardian, WDR/NDR/
Sueddeutsche Zeitung, UN News, Press Information Bureau of India):

  1. Nvidia reinstates Jensen Huang as chief executive, 11 days
     after he resigned; shares jump 31% in their best day since
     2003, and the Nasdaq leaps 6.5%.
  2. Analyses of hacked Russian civil-registry data count
     460,000-490,000 Russian war dead in Ukraine; researchers
     say the true toll, with the missing, may reach ~700,000.
  3. Western intelligence shared among NATO allies says Russia
     could launch the nuclear-armed Sputnik-S satellite as
     soon as December. Moscow denies it.
  4. Virginia and Oregon sue Musk's SpaceX over Grok: the first
     state lawsuits alleging the chatbot made sexual images of
     real people, including children.
  5. Democrat Jimmy Gomez will resign from the US House on
     1 December after the Ethics Committee found substantial
     evidence of sexual misconduct.
  6. A staffing shortage halts arrivals at Chicago's O'Hare for
     95 minutes as nearly 6 million Americans prepare to fly
     for Thanksgiving.

Ticker: the UN chief urges global AI safety rules within a year;
India pledges 15,000 crore rupees in aid and credit to Nepal;
Burnham calls UK rejoining the EU without a referendum
"unthinkable".
"""

import os
import struct
import zlib

WIDTH = 1024
HEIGHT = 1024

# ---------------------------------------------------------------- palette
PAPER = (248, 243, 232)
CARD = (255, 253, 247)
INK = (22, 32, 58)
NAVY = (24, 44, 84)
RED = (186, 32, 38)
BLUE = (36, 84, 160)
TEAL = (16, 120, 110)
ORANGE = (214, 116, 26)
PURPLE = (96, 60, 164)
GREEN = (42, 118, 48)
GREY = (96, 100, 114)
LIGHT = (226, 219, 200)
WHITE = (255, 255, 255)
GOLD = (176, 132, 30)

# ------------------------------------------------------- 5x7 bitmap font
# Glyphs are seven rows of five pixels, "1" = ink. Written for this
# program; the set covers everything the page needs (ASCII capitals,
# digits and common punctuation).
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11100", "10010", "10001", "10001", "10001", "10010", "11100"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    "X": ("10001", "01010", "00100", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "01010", "00100", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '"': ("01010", "01010", "01010", "00000", "00000", "00000", "00000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    ",": ("00000", "00000", "00000", "00000", "00100", "00100", "01000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "*": ("00000", "10101", "01110", "10101", "00000", "00000", "00000"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "#": ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "@": ("01110", "10001", "10111", "10101", "10110", "10000", "01110"),
    "_": ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    ">": ("10000", "01000", "00100", "00010", "00100", "01000", "10000"),
}

# ------------------------------------------------------------- pixel canvas
class Canvas:
    def __init__(self, width, height, bg):
        self.w = width
        self.h = height
        self.buf = bytearray(bg * (width * height))

    def px(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.buf[i:i + 3] = bytes(color)

    def rect(self, x, y, w, h, color):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.px(xx, yy, color)

    def hline(self, x, y, w, color, thick=1):
        self.rect(x, y, w, thick, color)

    def vline(self, x, y, h, color, thick=1):
        self.rect(x, y, thick, h, color)

    def line(self, x0, y0, x1, y1, color):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.px(x0, y0, color)
            if x0 == x1 and y0 == y1:
                return
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def disc(self, cx, cy, r, color):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    self.px(xx, yy, color)

    def outline(self, cx, cy, r, color):
        # Midpoint circle outline, integer only.
        x, y, d = r, 0, 1 - r
        while x >= y:
            for sx, sy in ((x, y), (y, x), (-x, y), (-y, x),
                           (x, -y), (y, -x), (-x, -y), (-y, -x)):
                self.px(cx + sx, cy + sy, color)
            y += 1
            if d <= 0:
                d += 2 * y + 1
            else:
                x -= 1
                d += 2 * (y - x) + 1

    def half_disc(self, cx, cy, r, color):
        # Filled upper half of a disc (dome shape).
        for yy in range(cy - r, cy + 1):
            half = int((r * r - (cy - yy) ** 2) ** 0.5)
            for xx in range(cx - half, cx + half + 1):
                self.px(xx, yy, color)

    def triangle(self, x0, y0, x1, y1, x2, y2, color):
        # Fill by scanlines over the bounding box.
        top = min(y0, y1, y2)
        bot = max(y0, y1, y2)
        for yy in range(top, bot + 1):
            xs = []
            for (ax, ay), (bx, by) in (((x0, y0), (x1, y1)),
                                       ((x1, y1), (x2, y2)),
                                       ((x2, y2), (x0, y0))):
                if ay == by:
                    continue
                if min(ay, by) <= yy <= max(ay, by):
                    t = (yy - ay) / (by - ay)
                    xs.append(int(ax + t * (bx - ax)))
            if len(xs) >= 2:
                for xx in range(min(xs), max(xs) + 1):
                    self.px(xx, yy, color)

# -------------------------------------------------------------------- text
def text_width(s, scale):
    return len(s) * 6 * scale - scale


def draw_text(cv, x, y, s, scale, color):
    s = s.upper()
    cx = x
    for ch in s:
        glyph = FONT.get(ch, FONT[" "])
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits[col] == "1":
                    cv.rect(cx + col * scale, y + row * scale,
                            scale, scale, color)
        cx += 6 * scale
    return cx


def draw_text_centred(cv, cx, y, s, scale, color):
    draw_text(cv, cx - text_width(s, scale) // 2, y, s, scale, color)


def wrap(s, scale, max_w):
    """Greedy word wrap; returns a list of lines fitting max_w."""
    words = s.split(" ")
    lines = []
    cur = ""
    for w in words:
        trial = w if not cur else cur + " " + w
        if text_width(trial, scale) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

# ------------------------------------------------------------ small icons
# Each icon is drawn inside a square box (bx, by, size) with a tint
# background and one accent colour. All shapes are plain geometry.

def icon_box(cv, bx, by, size, tint):
    cv.rect(bx, by, size, size, tint)
    cv.rect(bx, by, size, 2, INK)
    cv.rect(bx, by + size - 2, size, 2, INK)
    cv.rect(bx, by, 2, size, INK)
    cv.rect(bx + size - 2, by, 2, size, INK)


def icon_document(cv, bx, by, size, accent):
    icon_box(cv, bx, by, size, (232, 226, 210))
    x0, y0 = bx + size // 4, by + size // 5
    w, h = size // 2, size * 3 // 5
    cv.rect(x0, y0, w, h, CARD)
    cv.rect(x0, y0, w, 2, INK)
    cv.rect(x0, y0 + h - 2, w, 2, INK)
    cv.rect(x0, y0, 2, h, INK)
    cv.rect(x0 + w - 2, y0, 2, h, INK)
    for k in range(3):
        cv.rect(x0 + 6, y0 + 8 + k * 9, w - 12, 3, GREY)
    cv.disc(x0 + w - 4, y0 + h - 4, 7, accent)
    draw_text(cv, x0 + w - 7, y0 + h - 10, "?", 1, WHITE)


def icon_satellite(cv, bx, by, size, accent):
    icon_box(cv, bx, by, size, (214, 226, 242))
    cx, cy = bx + size // 2, by + size // 2
    cv.rect(bx + 8, cy - 10, 18, 5, accent)          # left panel
    cv.rect(bx + size - 26, cy - 10, 18, 5, accent)  # right panel
    cv.rect(bx + 8, cy - 6, 18, 2, INK)
    cv.rect(bx + size - 26, cy - 6, 18, 2, INK)
    cv.rect(cx - 9, cy - 12, 18, 24, CARD)           # body
    cv.rect(cx - 9, cy - 12, 18, 2, INK)
    cv.rect(cx - 9, cy + 10, 18, 2, INK)
    cv.rect(cx - 9, cy - 12, 2, 24, INK)
    cv.rect(cx + 7, cy - 12, 2, 24, INK)
    cv.disc(cx, cy, 4, accent)
    cv.line(cx, cy - 12, cx + 12, cy - 24, INK)      # antenna
    cv.disc(cx + 13, cy - 25, 3, RED)
    cv.disc(bx + size - 12, by + 10, 2, GOLD)        # a star


def icon_scales(cv, bx, by, size, accent):
    icon_box(cv, bx, by, size, (226, 220, 240))
    cx = bx + size // 2
    top = by + 10
    cv.rect(cx - 1, top, 3, size - 26, INK)          # post
    cv.rect(bx + 10, top, size - 20, 3, INK)         # beam
    cv.disc(cx, top - 3, 4, accent)
    for sx in (bx + 14, bx + size - 14):
        cv.line(sx, top + 3, sx - 8, top + 22, INK)
        cv.line(sx, top + 3, sx + 8, top + 22, INK)
        cv.triangle(sx - 9, top + 22, sx + 9, top + 22, sx, top + 14, accent)
    cv.rect(bx + size // 2 - 16, by + size - 14, 32, 4, INK)  # base


def icon_capitol(cv, bx, by, size, accent):
    icon_box(cv, bx, by, size, (232, 226, 210))
    cx = bx + size // 2
    base = by + size - 12
    cv.half_disc(cx, by + 26, 16, accent)            # dome
    cv.rect(cx - 2, by + 8, 4, 6, INK)               # finial
    cv.rect(cx - 18, by + 26, 36, 5, CARD)           # entablature
    cv.rect(cx - 18, by + 26, 36, 2, INK)
    for k in range(4):                               # columns
        cv.rect(cx - 18 + k * 10, by + 31, 4, 20, INK)
    cv.rect(cx - 22, base - 6, 44, 6, INK)           # steps


def icon_plane(cv, bx, by, size, accent):
    icon_box(cv, bx, by, size, (214, 232, 226))
    cx, cy = bx + size // 2, by + size // 2
    cv.rect(bx + 8, cy - 4, size - 16, 9, accent)    # fuselage
    cv.triangle(bx + size - 8, cy - 4, bx + size - 8, cy + 5,
                bx + size + 2, cy, accent)           # nose
    cv.triangle(cx - 6, cy - 4, cx + 8, cy - 4, cx + 2, cy - 22, INK)
    cv.triangle(cx - 2, cy + 5, cx + 10, cy + 5, cx + 4, cy + 20, INK)
    cv.triangle(bx + 12, cy - 4, bx + 20, cy - 4, bx + 10, cy - 16, INK)
    for k in range(4):
        cv.disc(bx + 16 + k * 8, cy, 2, WHITE)       # windows


# -------------------------------------------------------------- bar chart
def bar_chart(cv, x, y, w, h, bars, color):
    """bars: list of (label, value, shown_text). Baseline at y + h."""
    base = y + h - 26
    top = y + 22
    span = base - top
    vmax = max(v for _, v, _ in bars)
    n = len(bars)
    slot = w // n
    bw = 34
    for i, (label, value, shown) in enumerate(bars):
        bh = max(6, int(span * value / vmax))
        bx = x + i * slot + (slot - bw) // 2
        cv.rect(bx, base - bh, bw, bh, color)
        cv.rect(bx, base - bh, bw, 3, INK)
        draw_text_centred(cv, bx + bw // 2, base - bh - 16, shown, 2, INK)
        draw_text_centred(cv, bx + bw // 2, base + 6, label, 2, GREY)
    cv.hline(x, base, w, INK, 2)


# ------------------------------------------------------------------- cards
def card(cv, x, y, w, h, accent):
    cv.rect(x, y, w, h, CARD)
    cv.rect(x, y, w, 4, accent)
    cv.rect(x, y, w, 1, INK)
    cv.rect(x, y + h - 1, w, 1, INK)
    cv.rect(x, y, 1, h, INK)
    cv.rect(x + w - 1, y, 1, h, INK)


def kicker(cv, x, y, s, color):
    draw_text(cv, x, y, s, 2, color)


def headline_block(cv, x, y, max_w, text, scale, color, leading=None):
    lines = wrap(text, scale, max_w)
    lh = 7 * scale + (leading if leading is not None else scale * 2)
    for i, ln in enumerate(lines):
        draw_text(cv, x, y + i * lh, ln, scale, color)
    return y + len(lines) * lh


def deck_block(cv, x, y, max_w, text, scale, color):
    lines = wrap(text, scale, max_w)
    lh = 7 * scale + 4
    for i, ln in enumerate(lines):
        draw_text(cv, x, y + i * lh, ln, scale, color)
    return y + len(lines) * lh

# ------------------------------------------------------------------ content
LEAD_HEADLINE = "HUANG IS BACK - AND SO IS THE AI RALLY"
LEAD_DECK = (
    "NVIDIA REINSTATES JENSEN HUANG AS CHIEF EXECUTIVE 11 DAYS AFTER "
    "HE QUIT; SHARES JUMP 31% IN THEIR BEST DAY SINCE 2003. THE NASDAQ "
    "LEAPS 6.5% AND THE S&P 500 4.7% AS AI STOCKS ROAR BACK."
)
LEAD_NOTE = "TRUMP SAYS HE 'CONVINCED' THE BOARD."
LEAD_BARS = [
    ("NVDA", 31.0, "+31%"),
    ("NASDQ", 6.5, "+6.5%"),
    ("S&P", 4.7, "+4.7%"),
    ("DOW", 3.0, "+3.0%"),
]

# (kicker, accent, headline, deck, icon)
STORIES = [
    ("UKRAINE WAR", BLUE,
     "RUSSIA'S WAR DEAD NEAR 500,000, LEAK SHOWS",
     "Hacked registry data counts 460,000-490,000 deaths; "
     "the true toll may reach 700,000.",
     "document"),
    ("SPACE", PURPLE,
     "RUSSIA MAY LAUNCH NUCLEAR SATELLITE",
     "Western intelligence says Sputnik-S could fly as soon as December.",
     "satellite"),
    ("TECHNOLOGY", ORANGE,
     "TWO STATES SUE MUSK OVER GROK SEX IMAGES",
     "Virginia and Oregon say Grok made sexual images of real "
     "people, including children.",
     "scales"),
    ("WASHINGTON", TEAL,
     "CONGRESSMAN QUITS AFTER ETHICS FINDING",
     "Democrat Jimmy Gomez will resign on 1 December after "
     "the panel's finding.",
     "capitol"),
]

BAND_KICKER = "TRAVEL"
BAND_HEADLINE = "O'HARE GROUND STOP SNARLS THANKSGIVING GETAWAY"
BAND_DECK = (
    "A staffing shortage halts arrivals at Chicago's O'Hare for 95 "
    "minutes as nearly 6 million Americans prepare to fly for the holiday."
)

TICKERS = [
    "UN CHIEF URGES NATIONS TO AGREE GLOBAL AI SAFETY RULES WITHIN A YEAR",
    "INDIA PLEDGES 15,000 CRORE RUPEES IN AID AND CREDIT TO NEPAL",
    "BURNHAM: 'UNTHINKABLE' FOR UK TO REJOIN EU WITHOUT A REFERENDUM",
]

FOOTER = [
    "SOURCES: REUTERS, AP, CNN, BLOOMBERG, THE GUARDIAN",
    "WDR / NDR / SUEDDEUTSCHE ZEITUNG, UN NEWS, PRESS INFORMATION BUREAU OF INDIA",
    "FIGURES AS REPORTED ON 24 NOVEMBER 2026.",
]

ICONS = {
    "document": icon_document,
    "satellite": icon_satellite,
    "scales": icon_scales,
    "capitol": icon_capitol,
}


def draw_page():
    cv = Canvas(WIDTH, HEIGHT, PAPER)
    # Outer frame.
    cv.rect(12, 12, 1000, 2, INK)
    cv.rect(12, 1010, 1000, 2, INK)
    cv.rect(12, 12, 2, 1000, INK)
    cv.rect(1010, 12, 2, 1000, INK)

    # Masthead.
    draw_text_centred(cv, WIDTH // 2, 34, "THE WORLD TODAY", 6, INK)
    draw_text_centred(cv, WIDTH // 2, 88, "TUESDAY 24 NOVEMBER 2026",
                      2, RED)
    cv.hline(30, 110, 964, INK, 2)
    cv.hline(30, 114, 964, INK, 1)

    # Lead story.
    card(cv, 30, 126, 964, 262, RED)
    kicker(cv, 46, 140, "MARKETS - LEAD STORY", RED)
    headline_block(cv, 46, 162, 600, LEAD_HEADLINE, 4, INK)
    deck_block(cv, 46, 244, 600, LEAD_DECK, 2, INK)
    draw_text(cv, 46, 348, LEAD_NOTE, 2, GREY)
    cv.vline(662, 140, 234, LIGHT, 2)
    draw_text(cv, 680, 140, "TUESDAY'S MARKET JUMP", 2, GREY)
    bar_chart(cv, 680, 162, 300, 206, LEAD_BARS, GREEN)

    # Four stories in a 2 x 2 grid.
    grid = [(30, 398), (521, 398), (30, 556), (521, 556)]
    for (kicker_s, accent, head, deck, icon), (gx, gy) in zip(STORIES, grid):
        card(cv, gx, gy, 473, 148, accent)
        kicker(cv, gx + 12, gy + 12, kicker_s, accent)
        headline_block(cv, gx + 12, gy + 30, 449, head, 3, INK)
        ICONS[icon](cv, gx + 12, gy + 88, 48, accent)
        deck_block(cv, gx + 72, gy + 90, 389, deck, 2, INK)

    # Full-width travel band.
    card(cv, 30, 714, 964, 116, GREEN)
    icon_plane(cv, 42, 730, 56, GREEN)
    kicker(cv, 112, 726, BAND_KICKER, GREEN)
    headline_block(cv, 112, 744, 860, BAND_HEADLINE, 3, INK)
    deck_block(cv, 112, 778, 860, BAND_DECK, 2, INK)

    # Ticker band.
    cv.rect(30, 840, 964, 106, NAVY)
    draw_text(cv, 46, 852, "ALSO TODAY", 2, GOLD)
    for i, t in enumerate(TICKERS):
        draw_text(cv, 46, 874 + i * 20, ">> " + t, 2, WHITE)

    # Footer.
    for i, line in enumerate(FOOTER):
        draw_text_centred(cv, WIDTH // 2, 954 + i * 18, line, 2, GREY)

    return cv


# ---------------------------------------------------------------- PNG writer
def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def write_png(cv, path):
    raw = bytearray()
    for y in range(cv.h):
        raw.append(0)
        raw += cv.buf[y * cv.w * 3:(y + 1) * cv.w * 3]
    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    data = (b"\x89PNG\r\n\x1a\n"
            + _chunk(b"IHDR", ihdr)
            + _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + _chunk(b"IEND", b""))
    with open(path, "wb") as fh:
        fh.write(data)
    return len(data)


def main():
    cv = draw_page()
    targets = ["entry.png"]
    if os.path.isdir("/output"):
        targets.append("/output/entry.png")
    for path in targets:
        nbytes = write_png(cv, path)
        print("wrote %s (%d bytes, %dx%d)" % (path, nbytes, cv.w, cv.h))


if __name__ == "__main__":
    main()

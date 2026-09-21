# theme.py — OpenCar color themes (openpilot-inspired flat dark design)
import pyray as rl
from pyray import Color

class Theme:
    def __init__(self, dark=True):
        self.dark = dark
        if dark:
            # ── openpilot dark palette ──────────────────────────────
            self.bg        = Color(0,   0,   0,   255)   # pure black
            self.surface   = Color(41,  41,  41,  255)   # #292929 content card
            self.surface2  = Color(57,  57,  57,  255)   # #393939 button/toggle bg
            self.surface3  = Color(74,  74,  74,  255)   # #4A4A4A pressed state
            self.fg        = Color(255, 255, 255, 255)   # #FFFFFF primary text
            self.fg2       = Color(128, 128, 128, 255)   # #808080 secondary/desc
            self.fg3       = Color(170, 170, 170, 255)   # #AAAAAA value labels
            self.border    = Color(128, 128, 128, 100)   # divider lines
            self.accent    = Color(70,  91,  234, 255)   # #465BEA comma blue
            self.accent2   = Color(48,  73,  244, 255)   # #3049F4 pressed blue
            self.warn      = Color(218, 202, 37,  255)   # #DACA25 amber warning
            self.good      = Color(51,  171, 76,  255)   # #33AB4C comma green
            self.danger    = Color(226, 44,  44,  255)   # #E22C2C red
            self.dim_overlay = Color(0, 0, 0, 120)
            # Card/panel colors
            self.card_bg     = Color(41,  41,  41,  255)   # #292929
            self.card_border = Color(50,  50,  50,  255)   # subtle border
            self.toggle_off  = Color(57,  57,  57,  255)   # #393939
            self.toggle_on   = Color(51,  171, 76,  255)   # #33AB4C
            self.btn_bg      = Color(57,  57,  57,  255)   # #393939
            self.btn_pressed = Color(74,  74,  74,  255)   # #4A4A4A
            self.btn_text    = Color(228, 228, 228, 255)   # #E4E4E4
        else:
            # ── Light theme (subtle, not pure white) ───────────────
            self.bg        = Color(240, 242, 248, 255)   # soft white
            self.surface   = Color(255, 255, 255, 255)   # white cards
            self.surface2  = Color(235, 237, 243, 255)   # elevated
            self.surface3  = Color(225, 228, 236, 255)   # pressed
            self.fg        = Color(20,  25,  40,  255)   # dark text
            self.fg2       = Color(100, 108, 128, 255)   # gray secondary
            self.fg3       = Color(130, 138, 158, 255)   # lighter gray
            self.border    = Color(200, 205, 220, 120)   # dividers
            self.accent    = Color(70,  91,  234, 255)   # same blue
            self.accent2   = Color(48,  73,  244, 255)   # pressed blue
            self.warn      = Color(218, 162, 37,  255)   # warm amber
            self.good      = Color(51,  171, 76,  255)   # same green
            self.danger    = Color(226, 44,  44,  255)   # red
            self.dim_overlay = Color(255, 255, 255, 140)
            self.card_bg     = Color(255, 255, 255, 255)
            self.card_border = Color(220, 222, 230, 255)
            self.toggle_off  = Color(210, 212, 220, 255)
            self.toggle_on   = Color(51,  171, 76,  255)
            self.btn_bg      = Color(235, 237, 243, 255)
            self.btn_pressed = Color(225, 228, 236, 255)
            self.btn_text    = Color(40,  45,  60,  255)

DARK  = Theme(dark=True)
LIGHT = Theme(dark=False)
current = DARK  # Default to dark (openpilot style)

def toggle():
    global current
    current = LIGHT if current.dark else DARK
    return current

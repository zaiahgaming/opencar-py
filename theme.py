# theme.py — OpenCar color themes
from pyray import Color

class Theme:
    def __init__(self, dark=True):
        self.dark = dark
        if dark:
            self.bg        = Color(13,  13,  13,  255)   # near-black
            self.surface   = Color(22,  22,  24,  255)   # card bg
            self.surface2  = Color(32,  32,  36,  255)   # elevated card
            self.surface3  = Color(44,  44,  50,  255)   # pressed
            self.fg        = Color(240, 240, 240, 255)   # primary text
            self.fg2       = Color(160, 160, 165, 255)   # secondary text
            self.border    = Color(50,  50,  58,  255)   # dividers
            self.accent    = Color(99,  179, 237, 255)   # sky blue accent
            self.accent2   = Color(66,  153, 225, 255)   # darker accent
            self.warn      = Color(252, 129,  74, 255)   # orange-red warning
            self.good      = Color(104, 211, 145, 255)   # green good state
            self.dim_overlay = Color(0, 0, 0, 120)       # overlay tint
        else:
            self.bg        = Color(245, 245, 248, 255)
            self.surface   = Color(255, 255, 255, 255)
            self.surface2  = Color(235, 235, 240, 255)
            self.surface3  = Color(220, 220, 228, 255)
            self.fg        = Color(15,  15,  20,  255)
            self.fg2       = Color(100, 100, 108, 255)
            self.border    = Color(210, 210, 218, 255)
            self.accent    = Color(49,  130, 206, 255)
            self.accent2   = Color(43,  108, 176, 255)
            self.warn      = Color(221, 107,  32, 255)
            self.good      = Color(56,  161, 105, 255)
            self.dim_overlay = Color(0, 0, 0, 40)

DARK  = Theme(dark=True)
LIGHT = Theme(dark=False)
current = DARK

def toggle():
    global current
    current = LIGHT if current.dark else DARK
    return current

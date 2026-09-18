# surfaces/infotainment.py — OpenCar infotainment surface (Rivian OS 2 layout)
# Apps: 0=Home  1=Nav  2=Music  3=Climate  4=Phone  5=Settings
import math
import time as _time
import pyray as rl

# ──────────────────────────────────────────────────────────────────────────────
# Layout constants
# ──────────────────────────────────────────────────────────────────────────────
W, H            = 1280, 480
SIDEBAR_W       = 64
CONTENT_X       = SIDEBAR_W
CONTENT_W       = W - SIDEBAR_W            # 1216
STRIP_Y         = 444
STRIP_H         = 36
CONTENT_H       = STRIP_Y                  # 444

# Sidebar icon y-positions and app indices
_ICON_YS = [60, 150, 240, 330, 400]

# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

def _col(c: rl.Color, a: int = 255) -> rl.Color:
    """Return a Color with override alpha."""
    return rl.Color(c.r, c.g, c.b, a)


def _lerp_color(a: rl.Color, b: rl.Color, t: float) -> rl.Color:
    t = max(0.0, min(1.0, t))
    return rl.Color(
        int(a.r + (b.r - a.r) * t),
        int(a.g + (b.g - a.g) * t),
        int(a.b + (b.b - a.b) * t),
        255,
    )


def card(x: int, y: int, w: int, h: int, theme, radius: float = 0.12) -> None:
    rl.draw_rectangle_rounded(rl.Rectangle(x, y, w, h), radius, 8, theme.surface)


def card2(x: int, y: int, w: int, h: int, theme, radius: float = 0.12) -> None:
    rl.draw_rectangle_rounded(rl.Rectangle(x, y, w, h), radius, 8, theme.surface2)


def pill_button(x: int, y: int, w: int, h: int, label: str, font, theme,
                active: bool = False, sz: int = 16) -> None:
    color = theme.accent if active else theme.surface2
    txt_color = rl.Color(20, 20, 20, 255) if active else theme.fg2
    rl.draw_rectangle_rounded(rl.Rectangle(x, y, w, h), 1.0, 8, color)
    v = rl.measure_text_ex(font, label, sz, 1)
    rl.draw_text_ex(font, label, rl.Vector2(x + w / 2 - v.x / 2, y + h / 2 - v.y / 2),
                    sz, 1, txt_color)


def _artist_color(artist: str) -> rl.Color:
    """Deterministic hue from artist name hash."""
    h_val = abs(hash(artist)) % 360
    r_f, g_f, b_f = _hsv_to_rgb(h_val / 360.0, 0.60, 0.55)
    return rl.Color(int(r_f * 255), int(g_f * 255), int(b_f * 255), 255)


def _hsv_to_rgb(h: float, s: float, v: float):
    if s == 0:
        return v, v, v
    i = int(h * 6)
    f = h * 6 - i
    p, q, t2 = v * (1 - s), v * (1 - s * f), v * (1 - s * (1 - f))
    i %= 6
    return [(v, t2, p), (q, v, p), (p, v, t2), (p, q, v), (t2, p, v), (v, p, q)][i]


def _draw_text_centered(font, text: str, cx: float, cy: float, sz: int, color: rl.Color) -> None:
    v = rl.measure_text_ex(font, text, sz, 1)
    rl.draw_text_ex(font, text, rl.Vector2(cx - v.x / 2, cy - v.y / 2), sz, 1, color)


def _draw_text_right(font, text: str, rx: float, y: float, sz: int, color: rl.Color) -> None:
    v = rl.measure_text_ex(font, text, sz, 1)
    rl.draw_text_ex(font, text, rl.Vector2(rx - v.x, y), sz, 1, color)


def _eta_string(seconds: int) -> str:
    h = seconds // 3600
    m = (seconds % 3600) // 60
    if h > 0:
        return f"ETA {h}h {m:02d}m"
    return f"ETA {m}m"


# ──────────────────────────────────────────────────────────────────────────────
# InfoSurface
# ──────────────────────────────────────────────────────────────────────────────

class InfoSurface:
    # Tracks within 'music' app
    _TRACKS = [
        ("The Midnight",  "Los Angeles"),
        ("Tycho",         "Awake"),
        ("Bonobo",        "Kong"),
        ("Polo & Pan",    "Canopée"),
        ("Washed Out",    "Feel It All Around"),
    ]

    # Contacts for 'phone' app
    _CONTACTS = [
        ("Mom",         "+1 (555) 234-0011", "2m ago",  "incoming"),
        ("Alex R.",     "+1 (555) 019-3872", "14m ago", "missed"),
        ("Tesla Svc",   "+1 (800) 882-0000", "1h ago",  "outgoing"),
        ("Sarah K.",    "+1 (555) 741-2255", "3h ago",  "incoming"),
        ("Jake M.",     "+1 (555) 303-9988", "Yesterday","missed"),
    ]

    # Settings rows
    _SETTINGS_LABELS = [
        "Vehicle Profile",
        "Theme",
        "Units",
        "Brightness",
        "About",
    ]

    def __init__(self, fonts: dict):
        self.fonts = fonts
        # App-level focus state
        self._climate_focus = 0    # 0=driver temp, 1=pass temp, 2=ac, 3=heated, 4=defrost, 5=sync, 6=fan
        self._phone_row    = 0
        self._phone_keypad = False
        self._dial_buf     = ""
        self._keypad_focus = 0     # 0-11 on 4×3 grid
        self._settings_row = 0
        self._home_tile    = 0     # focused tile 0-3 in home 2×2
        self._nav_dir      = 0     # 0=straight, 1=left, 2=right (cycles with time)

    # ──────────────────────────────────────────────────────────────────────────
    # Key handler
    # ──────────────────────────────────────────────────────────────────────────

    def handle_key(self, key: int, state, theme) -> None:
        app = state.infotainment_app

        # Global sidebar shortcuts
        if key == rl.KeyboardKey.KEY_N:
            state.infotainment_app = 1; return
        if key == rl.KeyboardKey.KEY_M:
            state.infotainment_app = 2; return
        if key == rl.KeyboardKey.KEY_C:
            state.infotainment_app = 3; return
        if key == rl.KeyboardKey.KEY_P:
            state.infotainment_app = 4; return
        if key == rl.KeyboardKey.KEY_S:
            state.infotainment_app = 5; return
        if key == rl.KeyboardKey.KEY_H:
            state.infotainment_app = 0; return

        # ── Music (app 2)
        if app == 2:
            if key == rl.KeyboardKey.KEY_SPACE:
                state.music_playing = not state.music_playing
            elif key == rl.KeyboardKey.KEY_LEFT:
                state.music_track = (state.music_track - 1) % len(self._TRACKS)
                artist, title = self._TRACKS[state.music_track]
                state.music_artist = artist
                state.music_title  = title
                state.music_progress = 0.0
            elif key == rl.KeyboardKey.KEY_RIGHT:
                state.music_track = (state.music_track + 1) % len(self._TRACKS)
                artist, title = self._TRACKS[state.music_track]
                state.music_artist = artist
                state.music_title  = title
                state.music_progress = 0.0

        # ── Climate (app 3)
        elif app == 3:
            focus = self._climate_focus
            if key == rl.KeyboardKey.KEY_TAB:
                self._climate_focus = (focus + 1) % 7
            elif key in (rl.KeyboardKey.KEY_UP, rl.KeyboardKey.KEY_KP_ADD,
                         ord('+')):
                if focus == 0:
                    state.driver_temp_f = min(90.0, state.driver_temp_f + 1.0)
                elif focus == 1:
                    state.pass_temp_f   = min(90.0, state.pass_temp_f  + 1.0)
                elif focus == 6:
                    state.fan_level = min(5, state.fan_level + 1)
            elif key in (rl.KeyboardKey.KEY_DOWN, rl.KeyboardKey.KEY_KP_SUBTRACT,
                         ord('-')):
                if focus == 0:
                    state.driver_temp_f = max(60.0, state.driver_temp_f - 1.0)
                elif focus == 1:
                    state.pass_temp_f   = max(60.0, state.pass_temp_f  - 1.0)
                elif focus == 6:
                    state.fan_level = max(0, state.fan_level - 1)
            elif key == rl.KeyboardKey.KEY_ENTER:
                if focus == 2:
                    state.ac_on          = not state.ac_on
                elif focus == 3:
                    state.heated_seats   = not state.heated_seats
                elif focus == 4:
                    state.rear_defrost   = not state.rear_defrost

        # ── Phone (app 4)
        elif app == 4:
            if self._phone_keypad:
                if key == rl.KeyboardKey.KEY_BACKSPACE:
                    self._dial_buf = self._dial_buf[:-1]
                elif key == rl.KeyboardKey.KEY_ENTER:
                    self._dial_buf = ""
                    self._phone_keypad = False
                else:
                    ch = _keycode_to_digit(key)
                    if ch:
                        self._dial_buf += ch
            else:
                if key == rl.KeyboardKey.KEY_UP:
                    self._phone_row = max(0, self._phone_row - 1)
                elif key == rl.KeyboardKey.KEY_DOWN:
                    self._phone_row = min(len(self._CONTACTS) - 1, self._phone_row + 1)
                elif key == rl.KeyboardKey.KEY_ENTER:
                    self._phone_keypad = True

        # ── Settings (app 5)
        elif app == 5:
            if key == rl.KeyboardKey.KEY_UP:
                self._settings_row = max(0, self._settings_row - 1)
            elif key == rl.KeyboardKey.KEY_DOWN:
                self._settings_row = min(4, self._settings_row + 1)
            elif key == rl.KeyboardKey.KEY_ENTER:
                row = self._settings_row
                if row == 1:
                    state.theme_dark = not state.theme_dark
                elif row == 2:
                    state.units_mph = not state.units_mph
            elif key in (rl.KeyboardKey.KEY_LEFT, rl.KeyboardKey.KEY_RIGHT):
                row = self._settings_row
                delta = -1 if key == rl.KeyboardKey.KEY_LEFT else 1
                if row == 0:
                    profiles = ["toyota", "honda", "gm", "ford"]
                    idx = profiles.index(state.car_profile) if state.car_profile in profiles else 0
                    state.car_profile = profiles[(idx + delta) % len(profiles)]
                elif row == 3:
                    state.brightness = max(10, min(100, state.brightness + delta * 5))

        # ── Home tile navigation (app 0)
        elif app == 0:
            if key == rl.KeyboardKey.KEY_RIGHT:
                self._home_tile = min(3, self._home_tile + 1)
            elif key == rl.KeyboardKey.KEY_LEFT:
                self._home_tile = max(0, self._home_tile - 1)

    # ──────────────────────────────────────────────────────────────────────────
    # Main render
    # ──────────────────────────────────────────────────────────────────────────

    def render(self, state, theme) -> None:
        # Background fill for whole screen
        rl.draw_rectangle(0, 0, W, H, theme.bg)

        self._render_sidebar(state, theme)
        self._render_status_strip(state, theme)
        self._render_content(state, theme)

    # ──────────────────────────────────────────────────────────────────────────
    # Sidebar
    # ──────────────────────────────────────────────────────────────────────────

    def _render_sidebar(self, state, theme) -> None:
        rl.draw_rectangle(0, 0, SIDEBAR_W, H, theme.surface)
        # Right border
        rl.draw_rectangle(SIDEBAR_W - 1, 0, 1, H, theme.border)

        app = state.infotainment_app
        icons = [
            self._icon_nav,
            self._icon_music,
            self._icon_climate,
            self._icon_phone,
            self._icon_settings,
        ]
        icon_apps = [1, 2, 3, 4, 5]

        for idx, (iy, draw_fn) in enumerate(zip(_ICON_YS, icons)):
            active = (app == icon_apps[idx])
            color  = theme.accent if active else theme.fg2
            draw_fn(32, iy, color)
            if active:
                # Pill indicator dot below icon
                rl.draw_rectangle_rounded(rl.Rectangle(24, iy + 18, 16, 4), 1.0, 4, theme.accent)

        # Handle mouse clicks on sidebar
        mouse = rl.get_mouse_position()
        if rl.is_mouse_button_pressed(rl.MouseButton.MOUSE_BUTTON_LEFT):
            if mouse.x < SIDEBAR_W:
                my = mouse.y
                # Home if above first icon
                if my < (_ICON_YS[0] + _ICON_YS[1]) / 2:
                    state.infotainment_app = 0
                else:
                    for idx, iy in enumerate(_ICON_YS):
                        if idx < len(_ICON_YS) - 1:
                            mid = (_ICON_YS[idx] + _ICON_YS[idx + 1]) / 2
                        else:
                            mid = H
                        prev = (_ICON_YS[idx - 1] + iy) / 2 if idx > 0 else 0
                        if prev <= my < mid:
                            state.infotainment_app = icon_apps[idx]
                            break

    def _icon_nav(self, cx: int, cy: int, color: rl.Color) -> None:
        """Triangle pointing up."""
        rl.draw_triangle(
            rl.Vector2(cx,      cy - 12),
            rl.Vector2(cx - 10, cy + 8),
            rl.Vector2(cx + 10, cy + 8),
            color,
        )

    def _icon_music(self, cx: int, cy: int, color: rl.Color) -> None:
        """Stem + note head."""
        rl.draw_rectangle(cx + 3, cy - 12, 4, 20, color)
        rl.draw_circle(cx, cy + 8, 6, color)

    def _icon_climate(self, cx: int, cy: int, color: rl.Color) -> None:
        """6-spoke snowflake via draw_line_ex."""
        for angle_deg in range(0, 360, 60):
            rad = math.radians(angle_deg)
            ex  = cx + math.cos(rad) * 13
            ey  = cy + math.sin(rad) * 13
            rl.draw_line_ex(
                rl.Vector2(cx, cy),
                rl.Vector2(ex, ey),
                2.0,
                color,
            )

    def _icon_phone(self, cx: int, cy: int, color: rl.Color) -> None:
        """Rounded rect body + small earpiece circle."""
        rl.draw_rectangle_rounded(rl.Rectangle(cx - 7, cy - 13, 14, 22), 0.4, 6, color)
        rl.draw_circle(cx, cy - 8, 2, theme_bg_approx(color))

    def _icon_settings(self, cx: int, cy: int, color: rl.Color) -> None:
        """Outer ring + 4 small knob circles (N/S/E/W)."""
        rl.draw_circle_lines(cx, cy, 10, color)
        for angle_deg in [0, 90, 180, 270]:
            rad = math.radians(angle_deg)
            kx  = int(cx + math.cos(rad) * 10)
            ky  = int(cy + math.sin(rad) * 10)
            rl.draw_circle(kx, ky, 3, color)

    # ──────────────────────────────────────────────────────────────────────────
    # Status strip
    # ──────────────────────────────────────────────────────────────────────────

    def _render_status_strip(self, state, theme) -> None:
        rl.draw_rectangle(0, STRIP_Y, W, STRIP_H, theme.surface)
        rl.draw_rectangle(0, STRIP_Y, W, 1, theme.border)  # top border

        sm  = self.fonts['sm']
        xs  = self.fonts['xs']
        mid_y = STRIP_Y + STRIP_H // 2

        # Left — speed + gear
        spd_unit = 'mph' if state.units_mph else 'kph'
        spd_str  = f"{int(state.speed_mph)} {spd_unit}"
        rl.draw_text_ex(sm, spd_str, rl.Vector2(80, mid_y - 9), 16, 1, theme.fg)
        sv = rl.measure_text_ex(sm, spd_str, 16, 1)

        gear_names = ["P", "R", "N", "D"]
        gear_label = " · " + gear_names[state.gear]
        if state.gear == 3:
            g_color = theme.accent
        elif state.gear == 1:
            g_color = theme.warn
        else:
            g_color = theme.fg2
        rl.draw_text_ex(sm, gear_label,
                        rl.Vector2(80 + sv.x, mid_y - 9), 16, 1, g_color)

        # Center — nav instruction
        nav_txt = state.nav_instruction[:45]
        nv = rl.measure_text_ex(sm, nav_txt, 16, 1)
        rl.draw_text_ex(sm, nav_txt,
                        rl.Vector2(W / 2 - nv.x / 2, mid_y - 9), 16, 1, theme.fg)

        # Right — clock
        clock_str = _time.strftime("%I:%M %p")
        _draw_text_right(xs, clock_str, 1250, mid_y - 8, 13, theme.fg2)

    # ──────────────────────────────────────────────────────────────────────────
    # Content dispatcher
    # ──────────────────────────────────────────────────────────────────────────

    def _render_content(self, state, theme) -> None:
        app = state.infotainment_app
        if   app == 0: self._render_home(state, theme)
        elif app == 1: self._render_nav(state, theme)
        elif app == 2: self._render_music(state, theme)
        elif app == 3: self._render_climate(state, theme)
        elif app == 4: self._render_phone(state, theme)
        elif app == 5: self._render_settings(state, theme)

    # ──────────────────────────────────────────────────────────────────────────
    # App 0 — Home
    # ──────────────────────────────────────────────────────────────────────────

    def _render_home(self, state, theme) -> None:
        t = rl.get_time()

        # ── Left media card ───────────────────────────────────────────────────
        lx, ly, lw, lh = 76, 16, 440, 412
        card(lx, ly, lw, lh, theme, radius=0.08)

        cx = lx + lw // 2
        cy = ly + 160

        a_color = _artist_color(state.music_artist)
        rl.draw_circle(cx, cy, 70, a_color)

        # Animated progress ring
        pulse = math.sin(t * 2) * 2 if state.music_playing else 0
        outer = 80 + pulse
        end_angle = -90 + 360 * state.music_progress
        if state.music_progress > 0:
            rl.draw_ring(rl.Vector2(cx, cy), 74, outer, -90, end_angle, 60, theme.accent)

        # Artist initial
        initial = state.music_artist[0].upper() if state.music_artist else "?"
        blg = self.fonts['blg']
        _draw_text_centered(blg, initial, cx, cy, 36, rl.WHITE)

        # Artist label
        sm = self.fonts['sm']
        xs = self.fonts['xs']
        md = self.fonts['md']
        _draw_text_centered(sm, state.music_artist, cx, cy + 88, 16, theme.fg2)
        _draw_text_centered(md, state.music_title,  cx, cy + 112, 22, theme.fg)

        # Playing/paused indicator
        state_str = "\u25b6 Playing" if state.music_playing else "\u23f8 Paused"
        _draw_text_centered(xs, state_str, cx, cy + 140, 13, theme.fg2)

        # Progress bar
        bar_x = lx + 20
        bar_y = ly + lh - 60
        bar_w = lw - 40
        rl.draw_rectangle_rounded(rl.Rectangle(bar_x, bar_y, bar_w, 4), 1.0, 4, theme.surface2)
        fill_w = max(4, int(bar_w * state.music_progress))
        rl.draw_rectangle_rounded(rl.Rectangle(bar_x, bar_y, fill_w, 4), 1.0, 4, theme.accent)

        # ── Right 2×2 tiles ───────────────────────────────────────────────────
        tile_ox = 532
        tile_oy = 16
        tile_w  = 580
        tile_h  = 194
        gap     = 12

        tiles = [
            ("Navigation",  state.nav_instruction[:32],   _eta_string(state.eta_seconds)),
            ("Climate",     f"{state.driver_temp_f:.0f}\u00b0F", "Driver zone"),
            ("Phone",       self._CONTACTS[0][0],          self._CONTACTS[0][2]),
            ("Settings",    state.car_profile.capitalize(), "OpenCar v1.0"),
        ]

        for i, (header, main_txt, sub_txt) in enumerate(tiles):
            col   = i % 2
            row   = i // 2
            tx    = CONTENT_X + tile_ox - CONTENT_X + col * (tile_w // 2 + gap) + 8
            ty    = tile_oy + row * (tile_h + gap)
            tw    = tile_w // 2 - gap // 2
            th    = tile_h

            # Clamp to content area
            tx = CONTENT_X + 8 + col * (tw + gap)
            tx = 532 + col * (tw + gap // 2)

            card(tx, ty, tw, th, theme, radius=0.10)

            if self._home_tile == i:
                rl.draw_rectangle_rounded_lines_ex(
                    rl.Rectangle(tx, ty, tw, th), 0.10, 8, 2.0, theme.accent)

            xs = self.fonts['xs']
            sm = self.fonts['sm']
            md = self.fonts['md']
            rl.draw_text_ex(xs, header,   rl.Vector2(tx + 16, ty + 14), 13, 1, theme.fg2)
            rl.draw_text_ex(md, main_txt, rl.Vector2(tx + 16, ty + 38), 20, 1, theme.fg)
            rl.draw_text_ex(xs, sub_txt,  rl.Vector2(tx + 16, ty + 68), 13, 1, theme.fg2)

    # ──────────────────────────────────────────────────────────────────────────
    # App 1 — Navigation
    # ──────────────────────────────────────────────────────────────────────────

    def _render_nav(self, state, theme) -> None:
        t    = rl.get_time()
        mx   = CONTENT_X          # 64
        mw   = 750
        mh   = CONTENT_H          # 444

        bg   = theme.bg
        map_bg = rl.Color(
            max(0, bg.r - 8),
            max(0, bg.g - 8),
            max(0, bg.b - 10),
            255,
        )
        rl.draw_rectangle(mx, 0, mw, mh, map_bg)

        # Road grid — horizontal lines
        h_spacings = [20, 35, 28, 50, 18, 40, 60, 25, 32, 45, 55, 22, 38, 42, 27,
                      30, 48, 17, 52, 36]
        y = 0
        for sp in h_spacings:
            y += sp
            if y > mh:
                break
            rl.draw_line_ex(rl.Vector2(mx, y), rl.Vector2(mx + mw, y),
                            1.5, theme.border)

        # Road grid — vertical lines
        v_spacings = [40, 55, 30, 70, 45, 80, 35, 60, 50, 90, 25, 65, 42, 38, 75]
        x = mx
        for sp in v_spacings:
            x += sp
            if x > mx + mw:
                break
            rl.draw_line_ex(rl.Vector2(x, 0), rl.Vector2(x, mh),
                            1.5, theme.border)

        # Route line — simulated curved path from bottom-center upward
        car_x = mx + mw // 2
        car_y = mh - 60

        route_pts = [
            rl.Vector2(car_x,       car_y),
            rl.Vector2(car_x,       car_y - 80),
            rl.Vector2(car_x - 30,  car_y - 160),
            rl.Vector2(car_x - 30,  car_y - 260),
            rl.Vector2(car_x + 40,  car_y - 330),
            rl.Vector2(car_x + 40,  40),
        ]
        for i in range(len(route_pts) - 1):
            rl.draw_line_ex(route_pts[i], route_pts[i + 1], 4.0, theme.accent)

        # Car dot — pulsing donut
        r = 8 + math.sin(t * 3) * 2
        rl.draw_circle(car_x, car_y, r,     theme.accent)
        rl.draw_circle(car_x, car_y, r - 3, theme.bg)
        rl.draw_circle(car_x, car_y, r - 5, theme.accent)

        # Compass — top-right of map area
        comp_cx = mx + mw - 30
        comp_cy = 30
        xs = self.fonts['xs']
        rl.draw_circle_lines(comp_cx, comp_cy, 18, theme.border)
        rl.draw_text_ex(xs, "N", rl.Vector2(comp_cx - 4, comp_cy - 16), 12, 1, theme.fg)
        rl.draw_text_ex(xs, "S", rl.Vector2(comp_cx - 4, comp_cy + 6),  12, 1, theme.fg2)
        rl.draw_text_ex(xs, "E", rl.Vector2(comp_cx + 7, comp_cy - 5),  12, 1, theme.fg2)
        rl.draw_text_ex(xs, "W", rl.Vector2(comp_cx - 17, comp_cy - 5), 12, 1, theme.fg2)

        # ── Instruction panel
        px = mx + mw + 6    # ~820
        py = 16
        pw = CONTENT_X + CONTENT_W - px - 8  # fills to right edge
        ph = 412
        card(px, py, pw, ph, theme)

        sm = self.fonts['sm']
        md = self.fonts['md']

        # Direction arrow (pointing up as default)
        arrow_cx = px + pw // 2
        arrow_top = py + 20
        arrow_w, arrow_h = 30, 44
        # Shaft
        rl.draw_rectangle(arrow_cx - 8, arrow_top + 18, 16, arrow_h - 18, theme.accent)
        # Arrowhead triangle
        rl.draw_triangle(
            rl.Vector2(arrow_cx,          arrow_top),
            rl.Vector2(arrow_cx - arrow_w // 2, arrow_top + 22),
            rl.Vector2(arrow_cx + arrow_w // 2, arrow_top + 22),
            theme.accent,
        )

        # Street name
        street = state.nav_instruction
        _draw_text_centered(md, street[:22], px + pw // 2, py + 82, 20, theme.fg)
        if len(street) > 22:
            _draw_text_centered(md, street[22:44], px + pw // 2, py + 106, 20, theme.fg)

        # Distance
        _draw_text_centered(sm, "In 0.4 mi", px + pw // 2, py + 136, 16, theme.accent)

        # ETA
        xs = self.fonts['xs']
        _draw_text_centered(xs, _eta_string(state.eta_seconds),
                            px + pw // 2, py + 158, 13, theme.fg2)

        # Separator
        rl.draw_rectangle(px + 16, py + 178, pw - 32, 1, theme.border)

        # Destination pill
        dest_y = py + ph - 56
        pill_rect = rl.Rectangle(px + 16, dest_y, pw - 32, 36)
        rl.draw_rectangle_rounded(pill_rect, 1.0, 8, theme.surface2)
        dest_str = f"\u25ce  {state.destination}"
        _draw_text_centered(sm, dest_str, px + pw // 2, dest_y + 18, 14, theme.fg)

    # ──────────────────────────────────────────────────────────────────────────
    # App 2 — Music
    # ──────────────────────────────────────────────────────────────────────────

    def _render_music(self, state, theme) -> None:
        t = rl.get_time()

        # ── Album art zone
        ax, ay, aw, ah = 80, 20, 310, 404
        a_color  = _artist_color(state.music_artist)
        cx, cy   = ax + aw // 2, ay + 170

        # Background track ring (full 360°)
        rl.draw_ring(rl.Vector2(cx, cy), 114, 122, 0, 360, 64, theme.border)

        # Progress ring
        prog_color = theme.accent if state.music_playing else theme.fg2
        if state.music_progress > 0:
            end_a = -90 + 360 * state.music_progress
            rl.draw_ring(rl.Vector2(cx, cy), 114, 122, -90, end_a, 64, prog_color)

        # Main circle
        rl.draw_circle(cx, cy, 110, a_color)

        # Artist initial
        blg = self.fonts['blg']
        _draw_text_centered(blg, state.music_artist[0].upper(), cx, cy, 80, rl.WHITE)

        # ── Track info
        tx, ty = 410, 40
        sm  = self.fonts['sm']
        xs  = self.fonts['xs']
        md  = self.fonts['md']
        blg = self.fonts['blg']

        rl.draw_text_ex(sm,  state.music_artist, rl.Vector2(tx, ty),      16, 1, theme.fg2)
        rl.draw_text_ex(blg, state.music_title,  rl.Vector2(tx, ty + 28), 32, 1, theme.fg)
        rl.draw_text_ex(xs,  "Album (Simulated)", rl.Vector2(tx, ty + 72), 13, 1, theme.fg2)

        # Separator
        sep_y = ty + 96
        rl.draw_rectangle(tx, sep_y, 520, 1, theme.border)

        # Progress bar
        pb_y = sep_y + 14
        rl.draw_rectangle_rounded(rl.Rectangle(tx, pb_y, 500, 4), 1.0, 4, theme.surface2)
        fill_w = max(4, int(500 * state.music_progress))
        rl.draw_rectangle_rounded(rl.Rectangle(tx, pb_y, fill_w, 4), 1.0, 4, theme.accent)

        # Elapsed / total
        total_sec = 210
        elapsed   = int(state.music_progress * total_sec)
        e_str = f"{elapsed // 60}:{elapsed % 60:02d} / {total_sec // 60}:{total_sec % 60:02d}"
        rl.draw_text_ex(xs, e_str, rl.Vector2(tx, pb_y + 12), 13, 1, theme.fg2)

        # ── Controls + Waveform
        ctrl_x, ctrl_y = 950, 60
        ctrl_labels = ["\u23ee", "\u23ef", "\u23ed"]

        for i, label in enumerate(ctrl_labels):
            bx = ctrl_x + 40
            by = ctrl_y + i * 76
            bw, bh = 60, 60
            rl.draw_rectangle_rounded(rl.Rectangle(bx, by, bw, bh), 0.3, 8, theme.surface2)
            _draw_text_centered(md, label, bx + bw // 2, by + bh // 2, 22, theme.fg)

        # Waveform
        wave_x  = ctrl_x - 30
        wave_cy = ctrl_y + 3 * 76 + 50
        bar_w   = 7
        gap     = 4
        for i in range(24):
            bh = (30 + 25 * math.sin(t * 4 + i * 0.4)) if state.music_playing else 8
            bh = max(4, bh)
            color = theme.accent if state.music_playing else theme.fg2
            bx2   = wave_x + i * (bar_w + gap)
            rl.draw_rectangle_rounded(
                rl.Rectangle(bx2, wave_cy - bh / 2, bar_w, bh),
                0.5, 4, color,
            )

    # ──────────────────────────────────────────────────────────────────────────
    # App 3 — Climate
    # ──────────────────────────────────────────────────────────────────────────

    def _render_climate(self, state, theme) -> None:
        focus = self._climate_focus

        card_w, card_h = 560, 260
        c1x, c2x, cy = 80, 680, 30
        xs  = self.fonts['xs']
        xl  = self.fonts['xl']
        md  = self.fonts['md']

        for zone_idx, (cx2, label, temp) in enumerate([
            (c1x, "DRIVER",    state.driver_temp_f),
            (c2x, "PASSENGER", state.pass_temp_f),
        ]):
            # Card
            card(cx2, cy, card_w, card_h, theme, radius=0.08)
            active_zone = (focus == zone_idx)
            if active_zone:
                rl.draw_rectangle_rounded_lines_ex(
                    rl.Rectangle(cx2, cy, card_w, card_h), 0.08, 8, 2.0, theme.accent)

            # Label
            _draw_text_centered(xs, label, cx2 + card_w // 2, cy + 20, 13, theme.fg2)

            # Big temp number
            temp_str = f"{temp:.0f}"
            _draw_text_centered(xl, temp_str, cx2 + card_w // 2 - 20, cy + card_h // 2, 72, theme.fg)

            # Degree + F superscript
            tv = rl.measure_text_ex(xl, temp_str, 72, 1)
            deg_x = cx2 + card_w // 2 - 20 + tv.x // 2 + 6
            rl.draw_text_ex(md, "\u00b0F", rl.Vector2(deg_x, cy + 50), 22, 1, theme.fg2)

            # ▲ button
            up_rect   = rl.Rectangle(cx2 + card_w - 70, cy + 60,  40, 40)
            down_rect = rl.Rectangle(cx2 + card_w - 70, cy + 110, 40, 40)
            rl.draw_rectangle_rounded(up_rect,   0.3, 6, theme.surface2)
            rl.draw_rectangle_rounded(down_rect, 0.3, 6, theme.surface2)
            _draw_text_centered(xs, "\u25b2", cx2 + card_w - 50, cy + 80,  12, theme.accent)
            _draw_text_centered(xs, "\u25bc", cx2 + card_w - 50, cy + 130, 12, theme.accent)

        # ── Fan dot row
        fan_y = cy + card_h + 28
        dots_x_start = CONTENT_X + CONTENT_W // 2 - (5 * 24) // 2
        for i in range(5):
            dx = dots_x_start + i * 24
            color = theme.accent if (i + 1) <= state.fan_level else theme.surface2
            rl.draw_circle(dx, fan_y, 8, color)
            if focus == 6:
                rl.draw_circle_lines(dx, fan_y, 10, theme.accent)

        _draw_text_centered(xs, "FAN", CONTENT_X + CONTENT_W // 2, fan_y + 22, 13, theme.fg2)

        # ── Toggle pill strip
        toggles = [
            ("A/C",          state.ac_on),
            ("HEATED SEATS", state.heated_seats),
            ("DEFROST",      state.rear_defrost),
            ("SYNC",         False),
        ]
        pill_w    = 140
        pill_h    = 36
        pill_gap  = 12
        total_pw  = len(toggles) * pill_w + (len(toggles) - 1) * pill_gap
        pill_sx   = CONTENT_X + CONTENT_W // 2 - total_pw // 2
        pill_y    = fan_y + 44

        for i, (label, active) in enumerate(toggles):
            px2 = pill_sx + i * (pill_w + pill_gap)
            focus_toggle = (focus == (i + 2))
            bg_col = theme.accent if active else theme.surface2
            rl.draw_rectangle_rounded(rl.Rectangle(px2, pill_y, pill_w, pill_h), 1.0, 8, bg_col)
            if focus_toggle:
                rl.draw_rectangle_rounded_lines_ex(
                    rl.Rectangle(px2, pill_y, pill_w, pill_h), 1.0, 8, 2.0, theme.accent)
            txt_col = rl.Color(20, 20, 20, 255) if active else theme.fg2
            sm = self.fonts['sm']
            pill_button(px2, pill_y, pill_w, pill_h, label, sm, theme, active=active)

    # ──────────────────────────────────────────────────────────────────────────
    # App 4 — Phone
    # ──────────────────────────────────────────────────────────────────────────

    def _render_phone(self, state, theme) -> None:
        sm  = self.fonts['sm']
        xs  = self.fonts['xs']
        md  = self.fonts['md']
        blg = self.fonts['blg']

        # ── Contact list
        lx, ly = 80, 20
        row_h  = 72
        lw     = 600

        for i, (name, number, t_ago, call_type) in enumerate(self._CONTACTS):
            ry = ly + i * row_h
            if i == self._phone_row:
                rl.draw_rectangle(lx, ry, lw, row_h, theme.surface2)
                rl.draw_rectangle(lx, ry, 3, row_h, theme.accent)
            else:
                rl.draw_rectangle(lx, ry, lw, row_h, theme.surface)

            # Bottom border (not on last)
            if i < len(self._CONTACTS) - 1:
                rl.draw_rectangle(lx, ry + row_h - 1, lw, 1, theme.border)

            # Call type dot
            dot_color = (theme.good  if call_type == "incoming" else
                         theme.warn  if call_type == "missed"   else
                         theme.accent)
            rl.draw_circle(lx + 20, ry + row_h // 2, 5, dot_color)

            # Name + number
            rl.draw_text_ex(sm, name,   rl.Vector2(lx + 38, ry + 14), 16, 1, theme.fg)
            rl.draw_text_ex(xs, number, rl.Vector2(lx + 38, ry + 38), 13, 1, theme.fg2)

            # Time right-aligned
            tw_v = rl.measure_text_ex(xs, t_ago, 13, 1)
            rl.draw_text_ex(xs, t_ago,
                            rl.Vector2(lx + lw - tw_v.x - 12, ry + 14), 13, 1, theme.fg2)

        # ── Dial button
        dial_y  = 20
        dial_x  = 720
        dial_bw = 520
        dial_bh = 60
        rl.draw_rectangle_rounded(rl.Rectangle(dial_x, dial_y, dial_bw, dial_bh), 1.0, 8, theme.accent)
        _draw_text_centered(md, "\u260e DIAL", dial_x + dial_bw // 2, dial_y + dial_bh // 2, 20,
                            rl.Color(15, 15, 20, 255))

        # Dial buffer display
        buf_str = self._dial_buf if self._dial_buf else " "
        _draw_text_right(blg, buf_str, dial_x + dial_bw - 12, dial_y + dial_bh + 8, 28, theme.fg)

        # ── Keypad 4×3 grid
        kp_x    = dial_x
        kp_y    = dial_y + dial_bh + 48
        key_w   = 120
        key_h   = 64
        kp_gap  = 8
        labels  = [
            ("1", ""),      ("2", "ABC"),  ("3", "DEF"),
            ("4", "GHI"),   ("5", "JKL"),  ("6", "MNO"),
            ("7", "PQRS"),  ("8", "TUV"),  ("9", "WXYZ"),
            ("*", ""),      ("0", "+"),    ("#", ""),
        ]
        for i, (digit, sub) in enumerate(labels):
            col = i % 3
            row = i // 3
            kx  = kp_x + col * (key_w + kp_gap)
            ky  = kp_y + row * (key_h + kp_gap)
            focused = self._phone_keypad and (self._keypad_focus == i)
            rl.draw_rectangle_rounded(rl.Rectangle(kx, ky, key_w, key_h), 0.12, 8, theme.surface2)
            if focused:
                rl.draw_rectangle_rounded_lines_ex(
                    rl.Rectangle(kx, ky, key_w, key_h), 0.12, 8, 2.0, theme.accent)
            _draw_text_centered(md, digit, kx + key_w // 2, ky + key_h // 2 - 6, 20, theme.fg)
            if sub:
                _draw_text_centered(xs, sub, kx + key_w // 2, ky + key_h // 2 + 14, 11, theme.fg2)

    # ──────────────────────────────────────────────────────────────────────────
    # App 5 — Settings
    # ──────────────────────────────────────────────────────────────────────────

    def _render_settings(self, state, theme) -> None:
        sm  = self.fonts['sm']
        xs  = self.fonts['xs']
        md  = self.fonts['md']

        row_h   = 70
        sx      = 80
        sw      = CONTENT_W - 80
        rows_y  = 10

        profiles = ["toyota", "honda", "gm", "ford"]

        for i, label in enumerate(self._SETTINGS_LABELS):
            ry      = rows_y + i * row_h
            focused = (self._settings_row == i)

            # Row background
            bg_col = theme.surface2 if focused else theme.surface
            rl.draw_rectangle(sx, ry, sw, row_h, bg_col)

            # Left accent bar if focused
            if focused:
                rl.draw_rectangle(sx, ry, 3, row_h, theme.accent)

            # Bottom border
            rl.draw_rectangle(sx, ry + row_h - 1, sw, 1, theme.border)

            # Row label
            rl.draw_text_ex(sm, label, rl.Vector2(sx + 20, ry + row_h // 2 - 8), 16, 1, theme.fg)

            right_x = sx + sw - 16

            # Row 0 — Vehicle Profile pills
            if i == 0:
                pw, ph = 90, 32
                pg     = 10
                total  = len(profiles) * pw + (len(profiles) - 1) * pg
                pill_start = right_x - total
                for pi, prof in enumerate(profiles):
                    pix = pill_start + pi * (pw + pg)
                    piy = ry + row_h // 2 - ph // 2
                    pill_button(pix, piy, pw, ph, prof.capitalize(), sm, theme,
                                active=(state.car_profile == prof))

            # Row 1 — Theme toggle switch
            elif i == 1:
                sw_w, sw_h = 64, 30
                sw_x = right_x - sw_w
                sw_y = ry + row_h // 2 - sw_h // 2
                sw_color = theme.accent if not state.theme_dark else theme.surface2
                rl.draw_rectangle_rounded(rl.Rectangle(sw_x, sw_y, sw_w, sw_h), 1.0, 8, sw_color)
                thumb_x = sw_x + (40 if not state.theme_dark else 4)
                rl.draw_circle(int(thumb_x + 12), int(sw_y + 15), 11, rl.WHITE)
                mode_lbl = "Dark" if state.theme_dark else "Light"
                rl.draw_text_ex(xs, mode_lbl, rl.Vector2(sw_x - 50, ry + row_h // 2 - 7),
                                13, 1, theme.fg2)

            # Row 2 — Units MPH/KPH
            elif i == 2:
                for pi, unit_lbl in enumerate(["MPH", "KPH"]):
                    pu_w, pu_h = 80, 32
                    pu_x = right_x - 2 * pu_w - 8 + pi * (pu_w + 8)
                    pu_y = ry + row_h // 2 - pu_h // 2
                    active = (unit_lbl == "MPH") == state.units_mph
                    pill_button(pu_x, pu_y, pu_w, pu_h, unit_lbl, sm, theme, active=active)

            # Row 3 — Brightness slider
            elif i == 3:
                sl_w, sl_h = 180, 8
                sl_x = right_x - sl_w
                sl_y = ry + row_h // 2 - sl_h // 2
                rl.draw_rectangle_rounded(rl.Rectangle(sl_x, sl_y, sl_w, sl_h),
                                          1.0, 4, theme.surface2)
                fill = int(sl_w * state.brightness / 100)
                rl.draw_rectangle_rounded(rl.Rectangle(sl_x, sl_y, fill, sl_h),
                                          1.0, 4, theme.accent)
                thumb_cx = sl_x + fill
                rl.draw_circle(thumb_cx, sl_y + sl_h // 2, 7, theme.accent)
                bri_lbl = f"{state.brightness}%"
                rl.draw_text_ex(xs, bri_lbl,
                                rl.Vector2(sl_x - 42, ry + row_h // 2 - 7), 13, 1, theme.fg2)

            # Row 4 — About
            elif i == 4:
                rl.draw_text_ex(xs, "OpenCar v1.0",
                                rl.Vector2(right_x - 300, ry + 14), 13, 1, theme.fg2)
                rl.draw_text_ex(xs, "4 OEM profiles \u00b7 Real opendbc CAN",
                                rl.Vector2(right_x - 300, ry + 36), 13, 1, theme.fg2)


# ──────────────────────────────────────────────────────────────────────────────
# Utility — cannot close over theme inside icon drawing methods
# ──────────────────────────────────────────────────────────────────────────────

def theme_bg_approx(base_color: rl.Color) -> rl.Color:
    """Dark near-black to punch out icon details."""
    return rl.Color(15, 15, 15, 255)


def _keycode_to_digit(key: int) -> str:
    """Map KEY_ZERO..KEY_NINE to '0'..'9'."""
    mapping = {
        rl.KeyboardKey.KEY_ZERO:  "0",
        rl.KeyboardKey.KEY_ONE:   "1",
        rl.KeyboardKey.KEY_TWO:   "2",
        rl.KeyboardKey.KEY_THREE: "3",
        rl.KeyboardKey.KEY_FOUR:  "4",
        rl.KeyboardKey.KEY_FIVE:  "5",
        rl.KeyboardKey.KEY_SIX:   "6",
        rl.KeyboardKey.KEY_SEVEN: "7",
        rl.KeyboardKey.KEY_EIGHT: "8",
        rl.KeyboardKey.KEY_NINE:  "9",
    }
    return mapping.get(key, "")

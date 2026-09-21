import pyray as rl
import os
import math
import time

_TRACKS = [
    ("The Midnight", "Los Angeles"),
    ("Tycho", "Awake"),
    ("Bonobo", "Kong"),
    ("Polo & Pan", "Canopee"),
    ("Washed Out", "Feel It All Around")
]
_CONTACTS = [
    ("Sarah Connor", "555-0101"),
    ("John Connor", "555-0102"),
    ("Kyle Reese", "555-0103"),
    ("Miles Dyson", "555-0104")
]
_SETTINGS_LABELS = [
    "Vehicle Profile", "Theme", "Units", "Brightness", "ADAS Sensitivity", "About OpenCar"
]

class InfoSurface:
    def __init__(self, fonts: dict):
        self.fonts = fonts
        self.focused_setting = 0
        
        # State tracking for airflow and seat heaters
        self.driver_airflow = [True, True, False]  # [Windshield, Face, Feet]
        self.pass_airflow   = [False, True, True]  # [Windshield, Face, Feet]
        self.driver_seat_heat = 2  # 0=off, 1=low, 2=med, 3=high
        self.pass_seat_heat   = 1
        self.driver_seat_cool = 0  # 0=off, 1=low, 2=med, 3=high
        self.pass_seat_cool   = 0
        self.recirc_mode = True
        self.air_purify  = True
        self.auto_mode = True
        self.sync_mode = True
        self.master_volume = 75
        
        self.icons = {}
        icon_names = [
            "play_white.png", "pause_white.png", "skip-back_white.png", "skip-forward_white.png",
            "play_dark.png", "pause_dark.png",
            "home_white.png", "map-pin_white.png", "music_white.png", "snowflake_white.png",
            "phone_white.png", "settings_white.png", "navigation_white.png", "fan_white.png",
            "thermometer_white.png", "arrow-up_white.png", "arrow-down_white.png",
            "check-circle_white.png", "zap_white.png", "fuel_white.png", "gauge_white.png",
            "battery-full_white.png", "bluetooth_white.png", "wifi_white.png", "signal_white.png",
            "volume-2_white.png", "wind_white.png", "sun_white.png", "car_white.png"
        ]
        for name in icon_names:
            path = f"assets/icons/{name}"
            self.icons[name] = self._safe_load(path)
            
        self.album_arts = {}
        for name in ["the_midnight.jpg", "tycho.jpg", "bonobo.jpg"]:
            path = f"assets/music/{name}"
            self.album_arts[name] = self._safe_load(path)
            
        self.card_bg = rl.Color(41, 41, 41, 255)
        self.card_inner = rl.Color(32, 32, 32, 255)
        self.pure_black = rl.Color(0, 0, 0, 255)
        self.gray_text = rl.Color(170, 170, 170, 255)
        self.gray_label = rl.Color(135, 135, 135, 255)
        self.white = rl.Color(255, 255, 255, 255)
        self.green = rl.Color(51, 171, 76, 255)
        self.sky_blue = rl.Color(130, 177, 255, 255)
        self.cyan = rl.Color(0, 210, 255, 255)
        self.dark_gray = rl.Color(57, 57, 57, 255)
        self.amber = rl.Color(245, 166, 35, 255)

    def _safe_load(self, path):
        if os.path.exists(path):
            return rl.load_texture(path)
        return None

    def _draw_icon(self, name, x, y, size, tint=None):
        tex = self.icons.get(name)
        if tex and tex.id > 0:
            scale = float(size) / max(tex.width, 1)
            rl.draw_texture_ex(tex, rl.Vector2(x, y), 0.0, scale, tint or self.white)

    def _draw_icon_centered(self, name, cx, cy, size, tint=None):
        tex = self.icons.get(name)
        if tex and tex.id > 0:
            scale = float(size) / max(tex.width, 1)
            w = tex.width * scale
            h = tex.height * scale
            rl.draw_texture_ex(tex, rl.Vector2(cx - w / 2, cy - h / 2), 0.0, scale, tint or self.white)

    def _draw_card(self, x, y, w, h):
        rl.draw_rectangle_rounded(rl.Rectangle(x, y, w, h), 0.25, 32, self.card_bg)

    def render(self, state, theme) -> None:
        W = rl.get_screen_width()
        H = rl.get_screen_height()
        
        rl.clear_background(self.pure_black)
        
        # ── Sidebar Dock (Inset Pill — Zero Left-Border Bleed) ────────────────
        dock_w = 80
        rl.draw_rectangle(0, 0, dock_w, H - 54, self.pure_black)
        
        sidebar_icons = [
            "home_white.png", "map-pin_white.png", "music_white.png", 
            "snowflake_white.png", "phone_white.png", "settings_white.png"
        ]
        
        tab_h = (H - 54) / 6
        for i, icon_name in enumerate(sidebar_icons):
            y = int(i * tab_h)
            is_active = (state.infotainment_app == i)
            
            if is_active:
                dock_pill = rl.Rectangle(12, y + tab_h / 2 - 26, dock_w - 24, 52)
                rl.draw_rectangle_rounded(dock_pill, 0.35, 12, rl.Color(51, 171, 76, 45))
                rl.draw_rectangle_rounded_lines_ex(dock_pill, 0.35, 12, 1.5, self.green)
                tint = self.white
            else:
                tint = self.gray_label
                
            self._draw_icon_centered(icon_name, dock_w // 2, y + int(tab_h // 2), 30, tint)
                
        # Touch / Click input handling
        clicked = rl.is_mouse_button_pressed(rl.MouseButton.MOUSE_BUTTON_LEFT)
        mouse = rl.get_mouse_position()

        # Sidebar touch
        if clicked and mouse.x < dock_w and mouse.y < H - 54:
            app_idx = int(mouse.y / tab_h)
            if 0 <= app_idx < 6:
                state.infotainment_app = app_idx

        # Content Area
        cx = dock_w
        cy = 0
        cw = W - dock_w
        ch = H - 54  # leaving 54 for bottom bar
        
        if state.infotainment_app == 0:
            self._render_home(state, cx, cy, cw, ch, mouse, clicked)
        elif state.infotainment_app == 1:
            self._render_nav(state, cx, cy, cw, ch, mouse, clicked)
        elif state.infotainment_app == 2:
            self._render_music(state, cx, cy, cw, ch, mouse, clicked)
        elif state.infotainment_app == 3:
            self._render_climate(state, cx, cy, cw, ch, mouse, clicked)
        elif state.infotainment_app == 4:
            self._render_phone(state, cx, cy, cw, ch, mouse, clicked)
        elif state.infotainment_app == 5:
            self._render_settings(state, cx, cy, cw, ch, mouse, clicked)
            
        # Bottom status bar
        self._render_bottom_bar(state, W, H)

    # ════════════════════════════════════════════════════════════════════════════
    # 1. HOME SCREEN - Rich Cards (No Empty Voids, Spatial Chassis Tire Display)
    # ════════════════════════════════════════════════════════════════════════════
    def _render_home(self, state, cx, cy, cw, ch, mouse, clicked):
        gap = 16
        card_w1 = int((cw - gap * 3) * 0.52)
        card_w2 = cw - gap * 3 - card_w1
        card_h = (ch - gap * 3) // 2
        
        # ── 1. NOW PLAYING Card ───────────────────────────────────────────────
        rect_music = rl.Rectangle(cx + gap, cy + gap, card_w1, card_h)
        self._draw_card(rect_music.x, rect_music.y, rect_music.width, rect_music.height)
        
        self._draw_icon("music_white.png", rect_music.x + 24, rect_music.y + 20, 16, self.gray_label)
        rl.draw_text_ex(self.fonts['xs'], 'NOW PLAYING', rl.Vector2(rect_music.x + 48, rect_music.y + 20), self.fonts['xs'].baseSize, 0, self.gray_label)
        
        # Spotify Pill Badge
        badge_w = 90
        rl.draw_rectangle_rounded(rl.Rectangle(rect_music.x + card_w1 - badge_w - 24, rect_music.y + 16, badge_w, 24), 0.5, 16, self.dark_gray)
        rl.draw_circle(int(rect_music.x + card_w1 - badge_w - 14), int(rect_music.y + 28), 4, self.green)
        rl.draw_text_ex(self.fonts['xs'], 'SPOTIFY', rl.Vector2(rect_music.x + card_w1 - badge_w + 2, rect_music.y + 20), self.fonts['xs'].baseSize, 0, self.white)

        # Album Art
        art_size = 120
        art_keys = ["the_midnight.jpg", "tycho.jpg", "bonobo.jpg"]
        art_idx = state.music_track % len(art_keys)
        art_tex = self.album_arts.get(art_keys[art_idx])
        art_x = rect_music.x + 24
        art_y = rect_music.y + 54
        if art_tex and art_tex.id > 0:
            scale = art_size / max(art_tex.width, 1)
            rl.draw_texture_ex(art_tex, rl.Vector2(art_x, art_y), 0.0, scale, rl.WHITE)
            rl.draw_rectangle_lines_ex(rl.Rectangle(art_x, art_y, art_size, art_size), 1.0, rl.Color(80, 80, 80, 200))
        
        info_x = art_x + art_size + 20
        rl.draw_text_ex(self.fonts['blg'], state.music_title or "Los Angeles", rl.Vector2(info_x, art_y + 8), self.fonts['blg'].baseSize, 0, self.white)
        rl.draw_text_ex(self.fonts['md'], state.music_artist or "The Midnight", rl.Vector2(info_x, art_y + 54), self.fonts['md'].baseSize, 0, self.gray_text)
        rl.draw_text_ex(self.fonts['xs'], "FLAC 96kHz · Lossless Master Audio", rl.Vector2(info_x, art_y + 92), self.fonts['xs'].baseSize, 0, self.sky_blue)

        # Mini Progress Scrubber
        prog_y = rect_music.y + card_h - 60
        prog_w = card_w1 - 48
        prog_rx = rect_music.x + 24
        
        rl.draw_rectangle_rounded(rl.Rectangle(prog_rx, prog_y, prog_w, 6), 1.0, 16, self.dark_gray)
        fill_w = int(prog_w * max(0.0, min(1.0, state.music_progress)))
        if fill_w > 0:
            rl.draw_rectangle_rounded(rl.Rectangle(prog_rx, prog_y, fill_w, 6), 1.0, 16, self.green)
            rl.draw_circle(int(prog_rx + fill_w), int(prog_y + 3), 6, self.white)
            
        total_sec = 225
        curr_sec = int(state.music_progress * total_sec)
        t_curr = f"{curr_sec // 60}:{curr_sec % 60:02d}"
        t_rem = f"-{(total_sec - curr_sec) // 60}:{(total_sec - curr_sec) % 60:02d}"
        rl.draw_text_ex(self.fonts['xs'], t_curr, rl.Vector2(prog_rx, prog_y + 12), self.fonts['xs'].baseSize, 0, self.gray_text)
        rl.draw_text_ex(self.fonts['xs'], t_rem, rl.Vector2(prog_rx + prog_w - 40, prog_y + 12), self.fonts['xs'].baseSize, 0, self.gray_text)
        
        # High-Contrast Mini Media Buttons
        ctrl_cx = prog_rx + prog_w / 2
        ctrl_cy = prog_y + 20
        
        btn_prev = rl.Rectangle(ctrl_cx - 64, ctrl_cy - 16, 36, 36)
        btn_play = rl.Rectangle(ctrl_cx - 18, ctrl_cy - 18, 40, 40)
        btn_next = rl.Rectangle(ctrl_cx + 28, ctrl_cy - 16, 36, 36)
        
        rl.draw_rectangle_rounded(btn_prev, 0.5, 16, rl.Color(70, 70, 70, 255))
        rl.draw_rectangle_rounded(btn_play, 0.5, 16, self.green)
        rl.draw_rectangle_rounded(btn_next, 0.5, 16, rl.Color(70, 70, 70, 255))
        
        self._draw_icon_centered("skip-back_white.png", ctrl_cx - 46, ctrl_cy + 2, 20, self.white)
        self._draw_icon_centered("pause_dark.png" if state.music_playing else "play_dark.png", ctrl_cx + 2, ctrl_cy + 2, 20, self.pure_black)
        self._draw_icon_centered("skip-forward_white.png", ctrl_cx + 46, ctrl_cy + 2, 20, self.white)
        
        if clicked:
            if rl.check_collision_point_rec(mouse, btn_prev):
                state.music_track = (state.music_track - 1) % len(_TRACKS)
                state.music_artist, state.music_title = _TRACKS[state.music_track]
                state.music_progress = 0.0
            elif rl.check_collision_point_rec(mouse, btn_play):
                state.music_playing = not state.music_playing
            elif rl.check_collision_point_rec(mouse, btn_next):
                state.music_track = (state.music_track + 1) % len(_TRACKS)
                state.music_artist, state.music_title = _TRACKS[state.music_track]
                state.music_progress = 0.0
            elif rl.check_collision_point_rec(mouse, rect_music) and mouse.y < prog_y:
                state.infotainment_app = 2

        # ── 2. NAVIGATION Card (With Lane Guidance to Fill Void) ──────────────
        rect_nav = rl.Rectangle(cx + gap * 2 + card_w1, cy + gap, card_w2, card_h)
        self._draw_card(rect_nav.x, rect_nav.y, rect_nav.width, rect_nav.height)
        
        self._draw_icon("navigation_white.png", rect_nav.x + 24, rect_nav.y + 20, 16, self.gray_label)
        rl.draw_text_ex(self.fonts['xs'], "NAVIGATION", rl.Vector2(rect_nav.x + 48, rect_nav.y + 20), self.fonts['xs'].baseSize, 0, self.gray_label)
        
        dest_str = getattr(state, 'destination', "Downtown SF")
        rl.draw_text_ex(self.fonts['blg'], dest_str, rl.Vector2(rect_nav.x + 24, rect_nav.y + 50), self.fonts['blg'].baseSize, 0, self.white)
        
        # Maneuver Banner
        maneuver_y = rect_nav.y + 104
        badge_rect = rl.Rectangle(rect_nav.x + 24, maneuver_y, 48, 48)
        rl.draw_rectangle_rounded(badge_rect, 0.35, 16, self.green)
        self._draw_icon_centered("arrow-up_white.png", rect_nav.x + 48, maneuver_y + 24, 28, self.pure_black)
        
        rl.draw_text_ex(self.fonts['bmd'], "In 800 ft, Exit 432B", rl.Vector2(rect_nav.x + 84, maneuver_y + 2), self.fonts['bmd'].baseSize, 0, self.white)
        rl.draw_text_ex(self.fonts['sm'], "Merge onto US-101 North", rl.Vector2(rect_nav.x + 84, maneuver_y + 26), self.fonts['sm'].baseSize, 0, self.gray_text)
        
        # Upcoming Lane Guidance (Fills the right-side void)
        lg_x = rect_nav.x + card_w2 - 180
        rl.draw_text_ex(self.fonts['xs'], "LANE ASSIST", rl.Vector2(lg_x, maneuver_y - 14), self.fonts['xs'].baseSize, 0, self.gray_label)
        lanes = ["LEFT", "THRU", "EXIT"]
        for l_idx, lname in enumerate(lanes):
            lx = lg_x + l_idx * 56
            is_exit = (l_idx == 2)
            rl.draw_rectangle_rounded(rl.Rectangle(lx, maneuver_y + 8, 48, 30), 0.25, 4, self.green if is_exit else self.dark_gray)
            self._draw_text_centered(self.fonts['xs'], lname, lx + 24, maneuver_y + 23, self.pure_black if is_exit else self.white)
        
        # ETA & Distance Pills
        eta_y = rect_nav.y + card_h - 52
        pills = [
            ("14 MIN", self.green, self.pure_black),
            ("12.4 MI", self.dark_gray, self.white),
            ("ETA 5:42 PM", self.dark_gray, self.white)
        ]
        px = rect_nav.x + 24
        for text, bg_col, fg_col in pills:
            ts = rl.measure_text_ex(self.fonts['xs'], text, self.fonts['xs'].baseSize, 0)
            pw = ts.x + 24
            rl.draw_rectangle_rounded(rl.Rectangle(px, eta_y, pw, 32), 0.5, 16, bg_col)
            rl.draw_text_ex(self.fonts['xs'], text, rl.Vector2(px + 12, eta_y + 8), self.fonts['xs'].baseSize, 0, fg_col)
            px += pw + 10
            
        if clicked and rl.check_collision_point_rec(mouse, rect_nav):
            state.infotainment_app = 1

        # ── 3. CLIMATE CONTROL Card ───────────────────────────────────────────
        rect_clim = rl.Rectangle(cx + gap, cy + gap * 2 + card_h, card_w1, card_h)
        self._draw_card(rect_clim.x, rect_clim.y, rect_clim.width, rect_clim.height)
        
        self._draw_icon("fan_white.png", rect_clim.x + 24, rect_clim.y + 20, 16, self.gray_label)
        rl.draw_text_ex(self.fonts['xs'], "CLIMATE CONTROL", rl.Vector2(rect_clim.x + 48, rect_clim.y + 20), self.fonts['xs'].baseSize, 0, self.gray_label)
        
        ac_text = "AUTO  ·  A/C ON" if state.ac_on else "CLIMATE OFF"
        ac_bg = self.green if state.ac_on else self.dark_gray
        ac_fg = self.pure_black if state.ac_on else self.gray_text
        rl.draw_rectangle_rounded(rl.Rectangle(rect_clim.x + card_w1 - 130, rect_clim.y + 16, 110, 24), 0.5, 16, ac_bg)
        rl.draw_text_ex(self.fonts['xs'], ac_text, rl.Vector2(rect_clim.x + card_w1 - 122, rect_clim.y + 20), self.fonts['xs'].baseSize, 0, ac_fg)

        col_w = (card_w1 - 64) // 3
        d_col_x = rect_clim.x + 24
        mid_y = rect_clim.y + 54
        
        # Driver Column
        rl.draw_text_ex(self.fonts['xs'], "DRIVER", rl.Vector2(d_col_x, mid_y), self.fonts['xs'].baseSize, 0, self.gray_label)
        rl.draw_text_ex(self.fonts['xl'], f"{int(state.driver_temp_f)}°", rl.Vector2(d_col_x, mid_y + 22), self.fonts['xl'].baseSize, 0, self.white)
        
        btn_d_minus = rl.Rectangle(d_col_x, mid_y + 104, 42, 42)
        btn_d_plus  = rl.Rectangle(d_col_x + 50, mid_y + 104, 42, 42)
        rl.draw_rectangle_rounded(btn_d_minus, 0.5, 16, self.dark_gray)
        rl.draw_rectangle_rounded(btn_d_plus,  0.5, 16, self.dark_gray)
        rl.draw_text_ex(self.fonts['blg'], "-", rl.Vector2(btn_d_minus.x + 14, btn_d_minus.y + 5), self.fonts['blg'].baseSize, 0, self.white)
        rl.draw_text_ex(self.fonts['blg'], "+", rl.Vector2(btn_d_plus.x + 12,  btn_d_plus.y + 5), self.fonts['blg'].baseSize, 0, self.white)

        # Center Column: Fan & Airflow
        c_col_x = d_col_x + col_w + 16
        rl.draw_text_ex(self.fonts['xs'], "VENTILATION", rl.Vector2(c_col_x, mid_y), self.fonts['xs'].baseSize, 0, self.gray_label)
        self._draw_icon("fan_white.png", c_col_x, mid_y + 30, 24, self.green if state.ac_on else self.gray_text)
        rl.draw_text_ex(self.fonts['md'], f"FAN {getattr(state, 'fan_level', 3)}", rl.Vector2(c_col_x + 32, mid_y + 28), self.fonts['md'].baseSize, 0, self.white)
        
        fan_lvl = getattr(state, 'fan_level', 3)
        for b in range(5):
            bar_rect = rl.Rectangle(c_col_x + b * 18, mid_y + 68, 12, 18)
            rl.draw_rectangle_rounded(bar_rect, 0.2, 4, self.green if b < fan_lvl else self.dark_gray)
            
        rl.draw_text_ex(self.fonts['xs'], "Airflow: Dash & Floor", rl.Vector2(c_col_x, mid_y + 112), self.fonts['xs'].baseSize, 0, self.gray_text)

        # Passenger Column
        p_col_x = c_col_x + col_w + 16
        p_temp = int(getattr(state, 'pass_temp_f', 70))
        rl.draw_text_ex(self.fonts['xs'], "PASSENGER", rl.Vector2(p_col_x, mid_y), self.fonts['xs'].baseSize, 0, self.gray_label)
        rl.draw_text_ex(self.fonts['xl'], f"{p_temp}°", rl.Vector2(p_col_x, mid_y + 22), self.fonts['xl'].baseSize, 0, self.white)
        
        btn_p_minus = rl.Rectangle(p_col_x, mid_y + 104, 42, 42)
        btn_p_plus  = rl.Rectangle(p_col_x + 50, mid_y + 104, 42, 42)
        rl.draw_rectangle_rounded(btn_p_minus, 0.5, 16, self.dark_gray)
        rl.draw_rectangle_rounded(btn_p_plus,  0.5, 16, self.dark_gray)
        rl.draw_text_ex(self.fonts['blg'], "-", rl.Vector2(btn_p_minus.x + 14, btn_p_minus.y + 5), self.fonts['blg'].baseSize, 0, self.white)
        rl.draw_text_ex(self.fonts['blg'], "+", rl.Vector2(btn_p_plus.x + 12,  btn_p_plus.y + 5), self.fonts['blg'].baseSize, 0, self.white)
        
        if clicked:
            if rl.check_collision_point_rec(mouse, btn_d_minus): state.driver_temp_f = max(60, state.driver_temp_f - 1)
            elif rl.check_collision_point_rec(mouse, btn_d_plus): state.driver_temp_f = min(85, state.driver_temp_f + 1)
            elif rl.check_collision_point_rec(mouse, btn_p_minus): state.pass_temp_f = max(60, p_temp - 1)
            elif rl.check_collision_point_rec(mouse, btn_p_plus): state.pass_temp_f = min(85, p_temp + 1)
            elif rl.check_collision_point_rec(mouse, rect_clim) and mouse.y < mid_y + 100:
                state.infotainment_app = 3

        # ── 4. VEHICLE STATUS Card (Spatial Top-Down Chassis Layout) ───────────
        rect_veh = rl.Rectangle(cx + gap * 2 + card_w1, cy + gap * 2 + card_h, card_w2, card_h)
        self._draw_card(rect_veh.x, rect_veh.y, rect_veh.width, rect_veh.height)
        
        self._draw_icon("car_white.png", rect_veh.x + 24, rect_veh.y + 20, 16, self.gray_label)
        rl.draw_text_ex(self.fonts['xs'], "VEHICLE SYSTEM", rl.Vector2(rect_veh.x + 48, rect_veh.y + 20), self.fonts['xs'].baseSize, 0, self.gray_label)
        
        rl.draw_circle(int(rect_veh.x + card_w2 - 110), int(rect_veh.y + 28), 4, self.green)
        rl.draw_text_ex(self.fonts['xs'], "All Systems OK", rl.Vector2(rect_veh.x + card_w2 - 100, rect_veh.y + 20), self.fonts['xs'].baseSize, 0, self.green)
        
        # Left side: Car & Openpilot telemetry info
        vx = rect_veh.x + 24
        car_name = str(getattr(state, 'car_profile', "toyota")).capitalize()
        rl.draw_text_ex(self.fonts['blg'], f"{car_name} Camry", rl.Vector2(vx, rect_veh.y + 48), self.fonts['blg'].baseSize, 0, self.white)
        rl.draw_text_ex(self.fonts['sm'], "openpilot 0.9.7 · Comma 3X Engaged", rl.Vector2(vx, rect_veh.y + 94), self.fonts['sm'].baseSize, 0, self.green)
        rl.draw_text_ex(self.fonts['xs'], "CAN Bus: ISO 15765-4 (500 kbps) · 60 PIDs", rl.Vector2(vx, rect_veh.y + 124), self.fonts['xs'].baseSize, 0, self.gray_text)
        rl.draw_text_ex(self.fonts['xs'], "TPMS: All Sensors Calibrated & Nominal", rl.Vector2(vx, rect_veh.y + 146), self.fonts['xs'].baseSize, 0, self.sky_blue)

        # Right side: Spatial 2x2 Chassis Schematic
        car_cx = rect_veh.x + card_w2 - 146
        car_cy = rect_veh.y + 114
        # Draw central chassis capsule
        rl.draw_rectangle_rounded(rl.Rectangle(car_cx - 20, car_cy - 34, 40, 68), 0.4, 8, rl.Color(50, 50, 50, 255))
        rl.draw_rectangle_rounded_lines_ex(rl.Rectangle(car_cx - 20, car_cy - 34, 40, 68), 0.4, 8, 1.5, rl.Color(80, 80, 80, 255))
        
        # 4 Tires with high-contrast green labels
        tire_w, tire_h = 88, 28
        # FL / FR
        fl_rect = rl.Rectangle(car_cx - 20 - 8 - tire_w, car_cy - 32, tire_w, tire_h)
        fr_rect = rl.Rectangle(car_cx + 20 + 8, car_cy - 32, tire_w, tire_h)
        rl.draw_rectangle_rounded(fl_rect, 0.35, 8, self.dark_gray)
        rl.draw_rectangle_rounded(fr_rect, 0.35, 8, self.dark_gray)
        rl.draw_text_ex(self.fonts['xs'], "FL", rl.Vector2(fl_rect.x + 6, fl_rect.y + 6), self.fonts['xs'].baseSize, 0, self.gray_text)
        rl.draw_text_ex(self.fonts['bmd'], "35 PSI", rl.Vector2(fl_rect.x + 28, fl_rect.y + 2), self.fonts['bmd'].baseSize, 0, self.green)
        rl.draw_text_ex(self.fonts['xs'], "FR", rl.Vector2(fr_rect.x + 6, fr_rect.y + 6), self.fonts['xs'].baseSize, 0, self.gray_text)
        rl.draw_text_ex(self.fonts['bmd'], "35 PSI", rl.Vector2(fr_rect.x + 28, fr_rect.y + 2), self.fonts['bmd'].baseSize, 0, self.green)
        
        # RL / RR
        rl_rect = rl.Rectangle(car_cx - 20 - 8 - tire_w, car_cy + 6, tire_w, tire_h)
        rr_rect = rl.Rectangle(car_cx + 20 + 8, car_cy + 6, tire_w, tire_h)
        rl.draw_rectangle_rounded(rl_rect, 0.35, 8, self.dark_gray)
        rl.draw_rectangle_rounded(rr_rect, 0.35, 8, self.dark_gray)
        rl.draw_text_ex(self.fonts['xs'], "RL", rl.Vector2(rl_rect.x + 6, rl_rect.y + 6), self.fonts['xs'].baseSize, 0, self.gray_text)
        rl.draw_text_ex(self.fonts['bmd'], "34 PSI", rl.Vector2(rl_rect.x + 28, rl_rect.y + 2), self.fonts['bmd'].baseSize, 0, self.green)
        rl.draw_text_ex(self.fonts['xs'], "RR", rl.Vector2(rr_rect.x + 6, rr_rect.y + 6), self.fonts['xs'].baseSize, 0, self.gray_text)
        rl.draw_text_ex(self.fonts['bmd'], "35 PSI", rl.Vector2(rr_rect.x + 28, rr_rect.y + 2), self.fonts['bmd'].baseSize, 0, self.green)

        # Vehicle Vitals: Battery & Fuel
        v_bot_y = rect_veh.y + card_h - 40
        self._draw_icon("zap_white.png", rect_veh.x + 24, v_bot_y + 2, 16, self.amber)
        rl.draw_text_ex(self.fonts['sm'], "14.2V", rl.Vector2(rect_veh.x + 46, v_bot_y), self.fonts['sm'].baseSize, 0, self.white)
        
        fuel_pct = int(getattr(state, 'fuel_level', 0.8) * 100)
        self._draw_icon("fuel_white.png", rect_veh.x + 130, v_bot_y + 2, 16, self.white)
        rl.draw_text_ex(self.fonts['sm'], f"{fuel_pct}% (340 MI)", rl.Vector2(rect_veh.x + 152, v_bot_y), self.fonts['sm'].baseSize, 0, self.white)

        rl.draw_text_ex(self.fonts['xs'], "ODO: 18,420 MI", rl.Vector2(rect_veh.x + card_w2 - 130, v_bot_y + 2), self.fonts['xs'].baseSize, 0, self.gray_label)

        if clicked and rl.check_collision_point_rec(mouse, rect_veh):
            state.infotainment_app = 5

    # ════════════════════════════════════════════════════════════════════════════
    # 2. MUSIC APP SCREEN - 220px Artwork, Volume Steppers & Queue
    # ════════════════════════════════════════════════════════════════════════════
    def _render_music(self, state, cx, cy, cw, ch, mouse, clicked):
        col_gap = 24
        left_w = int((cw - 48 - col_gap) * 0.58)
        right_w = cw - 48 - col_gap - left_w
        
        player_x = cx + 24
        player_y = cy + 20
        player_h = ch - 40
        self._draw_card(player_x, player_y, left_w, player_h)
        
        px = player_x + 24
        py = player_y + 24
        
        art_size = 200
        art_keys = ["the_midnight.jpg", "tycho.jpg", "bonobo.jpg"]
        art_idx = state.music_track % len(art_keys)
        art_tex = self.album_arts.get(art_keys[art_idx])
        if art_tex and art_tex.id > 0:
            scale = art_size / max(art_tex.width, 1)
            rl.draw_texture_ex(art_tex, rl.Vector2(px, py), 0.0, scale, rl.WHITE)
            rl.draw_rectangle_lines_ex(rl.Rectangle(px, py, art_size, art_size), 1.0, rl.Color(80, 80, 80, 200))
            
        meta_x = px + art_size + 24
        rl.draw_text_ex(self.fonts['xs'], "NOW PLAYING FROM SPOTIFY", rl.Vector2(meta_x, py + 8), self.fonts['xs'].baseSize, 0, self.green)
        rl.draw_text_ex(self.fonts['blg'], state.music_title or "Los Angeles", rl.Vector2(meta_x, py + 34), self.fonts['blg'].baseSize, 0, self.white)
        rl.draw_text_ex(self.fonts['bmd'], state.music_artist or "The Midnight", rl.Vector2(meta_x, py + 90), self.fonts['bmd'].baseSize, 0, self.gray_text)
        rl.draw_text_ex(self.fonts['xs'], "Master Quality · 96kHz 24-bit Lossless", rl.Vector2(meta_x, py + 134), self.fonts['xs'].baseSize, 0, self.sky_blue)
        
        # Audio tech badges
        badge_row_y = py + 162
        b1_w, b2_w = 110, 118
        rl.draw_rectangle_rounded(rl.Rectangle(meta_x, badge_row_y, b1_w, 24), 0.5, 8, self.dark_gray)
        rl.draw_text_ex(self.fonts['xs'], "DOLBY ATMOS", rl.Vector2(meta_x + 12, badge_row_y + 4), self.fonts['xs'].baseSize, 0, self.white)
        rl.draw_rectangle_rounded(rl.Rectangle(meta_x + b1_w + 12, badge_row_y, b2_w, 24), 0.5, 8, self.dark_gray)
        rl.draw_text_ex(self.fonts['xs'], "IMMERSIVE 3D", rl.Vector2(meta_x + b1_w + 22, badge_row_y + 4), self.fonts['xs'].baseSize, 0, self.green)
        
        # Scrubber
        bar_y = py + art_size + 36
        bar_w = left_w - 48
        bar_rect = rl.Rectangle(px, bar_y - 12, bar_w, 32)
        if clicked and rl.check_collision_point_rec(mouse, bar_rect):
            state.music_progress = max(0.0, min(1.0, (mouse.x - px) / bar_w))
            
        rl.draw_rectangle_rounded(rl.Rectangle(px, bar_y, bar_w, 8), 1.0, 16, self.dark_gray)
        prog_w = int(bar_w * state.music_progress)
        rl.draw_rectangle_rounded(rl.Rectangle(px, bar_y, prog_w, 8), 1.0, 16, self.green)
        rl.draw_circle(int(px + prog_w), int(bar_y + 4), 10, self.white)
        
        total_sec = 225
        curr_sec = int(state.music_progress * total_sec)
        t_curr = f"{curr_sec // 60}:{curr_sec % 60:02d}"
        t_rem = f"-{(total_sec - curr_sec) // 60}:{(total_sec - curr_sec) % 60:02d}"
        rl.draw_text_ex(self.fonts['sm'], t_curr, rl.Vector2(px, bar_y + 16), self.fonts['sm'].baseSize, 0, self.gray_text)
        ts_rem = rl.measure_text_ex(self.fonts['sm'], t_rem, self.fonts['sm'].baseSize, 0)
        rl.draw_text_ex(self.fonts['sm'], t_rem, rl.Vector2(px + bar_w - ts_rem.x, bar_y + 16), self.fonts['sm'].baseSize, 0, self.gray_text)
        
        # Transport controls
        btn_y = bar_y + 54
        btn_cx = px + bar_w / 2
        
        btn_prev = rl.Rectangle(btn_cx - 130, btn_y, 64, 64)
        rl.draw_rectangle_rounded(btn_prev, 0.5, 32, rl.Color(65, 65, 65, 255))
        self._draw_icon_centered("skip-back_white.png", btn_cx - 98, btn_y + 32, 28, self.white)
        
        btn_play = rl.Rectangle(btn_cx - 40, btn_y - 8, 80, 80)
        rl.draw_rectangle_rounded(btn_play, 0.5, 32, self.white)
        hero_icon = "pause_dark.png" if state.music_playing else "play_dark.png"
        self._draw_icon_centered(hero_icon, btn_cx, btn_y + 32, 36, self.pure_black)
        
        btn_next = rl.Rectangle(btn_cx + 66, btn_y, 64, 64)
        rl.draw_rectangle_rounded(btn_next, 0.5, 32, rl.Color(65, 65, 65, 255))
        self._draw_icon_centered("skip-forward_white.png", btn_cx + 98, btn_y + 32, 28, self.white)
        
        # Volume Control Strip with Discrete Step Buttons
        vol_y = btn_y + 88
        self._draw_icon("volume-2_white.png", px + 20, vol_y - 4, 24, self.white)
        rl.draw_text_ex(self.fonts['xs'], f"VOLUME {self.master_volume}%", rl.Vector2(px + 52, vol_y + 2), self.fonts['xs'].baseSize, 0, self.gray_text)
        
        btn_vol_m = rl.Rectangle(px + 170, vol_y - 8, 36, 36)
        btn_vol_p = rl.Rectangle(px + bar_w - 56, vol_y - 8, 36, 36)
        rl.draw_rectangle_rounded(btn_vol_m, 0.5, 16, self.dark_gray)
        rl.draw_rectangle_rounded(btn_vol_p, 0.5, 16, self.dark_gray)
        rl.draw_text_ex(self.fonts['bmd'], "-", rl.Vector2(btn_vol_m.x + 12, btn_vol_m.y + 4), self.fonts['bmd'].baseSize, 0, self.white)
        rl.draw_text_ex(self.fonts['bmd'], "+", rl.Vector2(btn_vol_p.x + 10, btn_vol_p.y + 4), self.fonts['bmd'].baseSize, 0, self.white)
        
        vol_bar_x = px + 220
        vol_bar_w = bar_w - 290
        rl.draw_rectangle_rounded(rl.Rectangle(vol_bar_x, vol_y + 6, vol_bar_w, 8), 1.0, 16, self.dark_gray)
        v_fill = int(vol_bar_w * (self.master_volume / 100.0))
        rl.draw_rectangle_rounded(rl.Rectangle(vol_bar_x, vol_y + 6, v_fill, 8), 1.0, 16, self.white)
        rl.draw_circle(int(vol_bar_x + v_fill), int(vol_y + 10), 10, self.white)

        # Mode buttons & Audio Spectrum
        mode_y = vol_y + 50
        btn_shuf = rl.Rectangle(px, mode_y, 110, 36)
        btn_rep = rl.Rectangle(px + 122, mode_y, 110, 36)
        btn_bass = rl.Rectangle(px + 244, mode_y, 120, 36)
        
        rl.draw_rectangle_rounded(btn_shuf, 0.35, 8, self.green)
        rl.draw_text_ex(self.fonts['xs'], "SHUFFLE ON", rl.Vector2(px + 16, mode_y + 10), self.fonts['xs'].baseSize, 0, self.pure_black)
        
        rl.draw_rectangle_rounded(btn_rep, 0.35, 8, self.dark_gray)
        rl.draw_text_ex(self.fonts['xs'], "REPEAT ALL", rl.Vector2(px + 138, mode_y + 10), self.fonts['xs'].baseSize, 0, self.white)
        
        rl.draw_rectangle_rounded(btn_bass, 0.35, 8, self.dark_gray)
        rl.draw_text_ex(self.fonts['xs'], "BASS BOOST", rl.Vector2(px + 260, mode_y + 10), self.fonts['xs'].baseSize, 0, self.white)
        
        # 12-bar animated graphic audio spectrum
        spec_x = px + bar_w - 180
        spec_base_y = mode_y + 36
        now_time = time.time() * 9
        spec_heights = [12, 22, 34, 18, 28, 38, 24, 30, 16, 26, 32, 14]
        for s_i, s_h in enumerate(spec_heights):
            h_live = int(s_h * (0.4 + 0.6 * abs(((now_time + s_i * 0.9) % 2) - 1)))
            bar_rx = spec_x + s_i * 14
            bar_ry = spec_base_y - h_live
            rl.draw_rectangle_rounded(rl.Rectangle(bar_rx, bar_ry, 8, h_live), 0.5, 4, self.green)

        # ── Right Column: Up Next Queue ───────────────────────────────────────
        q_x = player_x + left_w + col_gap
        q_y = cy + 20
        q_h = ch - 40
        self._draw_card(q_x, q_y, right_w, q_h)
        
        rl.draw_text_ex(self.fonts['xs'], "UP NEXT IN QUEUE", rl.Vector2(q_x + 24, q_y + 20), self.fonts['xs'].baseSize, 0, self.gray_label)
        
        for idx, (artist, title) in enumerate(_TRACKS):
            item_y = q_y + 56 + idx * 80
            item_rect = rl.Rectangle(q_x + 16, item_y, right_w - 32, 68)
            is_cur = (idx == state.music_track)
            
            if is_cur:
                rl.draw_rectangle_rounded(item_rect, 0.2, 8, rl.Color(55, 55, 55, 255))
                rl.draw_rectangle(int(item_rect.x), int(item_rect.y), 4, int(item_rect.height), self.green)
            else:
                if rl.check_collision_point_rec(mouse, item_rect):
                    rl.draw_rectangle_rounded(item_rect, 0.2, 8, rl.Color(48, 48, 48, 255))
                    
            if clicked and rl.check_collision_point_rec(mouse, item_rect):
                state.music_track = idx
                state.music_artist, state.music_title = _TRACKS[idx]
                state.music_progress = 0.0
                
            track_num = f"{idx + 1}"
            rl.draw_text_ex(self.fonts['bmd'], track_num, rl.Vector2(item_rect.x + 18, item_rect.y + 22), self.fonts['bmd'].baseSize, 0, self.green if is_cur else self.gray_label)
            rl.draw_text_ex(self.fonts['bmd'], title, rl.Vector2(item_rect.x + 48, item_rect.y + 12), self.fonts['bmd'].baseSize, 0, self.white)
            rl.draw_text_ex(self.fonts['xs'], artist, rl.Vector2(item_rect.x + 48, item_rect.y + 42), self.fonts['xs'].baseSize, 0, self.gray_text)
            
            dur = ["3:45", "4:12", "3:58", "4:30", "3:15"][idx]
            rl.draw_text_ex(self.fonts['xs'], dur, rl.Vector2(item_rect.x + item_rect.width - 50, item_rect.y + 26), self.fonts['xs'].baseSize, 0, self.gray_label)
        
        if clicked:
            if rl.check_collision_point_rec(mouse, btn_prev):
                state.music_track = (state.music_track - 1) % len(_TRACKS)
                state.music_artist, state.music_title = _TRACKS[state.music_track]
                state.music_progress = 0.0
            elif rl.check_collision_point_rec(mouse, btn_play):
                state.music_playing = not state.music_playing
            elif rl.check_collision_point_rec(mouse, btn_next):
                state.music_track = (state.music_track + 1) % len(_TRACKS)
                state.music_artist, state.music_title = _TRACKS[state.music_track]
                state.music_progress = 0.0
            elif rl.check_collision_point_rec(mouse, btn_vol_m):
                self.master_volume = max(0, self.master_volume - 5)
            elif rl.check_collision_point_rec(mouse, btn_vol_p):
                self.master_volume = min(100, self.master_volume + 5)

    # ════════════════════════════════════════════════════════════════════════════
    # 3. CLIMATE APP SCREEN - Airflow Selectors, 3-Stage Heaters & Full Density
    # ════════════════════════════════════════════════════════════════════════════
    def _render_climate(self, state, cx, cy, cw, ch, mouse, clicked):
        gap = 20
        top_card_h = ch - 160
        card_w = (cw - gap * 3) // 2
        
        # ── Driver Card ───────────────────────────────────────────────────────
        self._draw_card(cx + gap, cy + gap, card_w, top_card_h)
        self._draw_icon("thermometer_white.png", cx + gap + 24, cy + gap + 20, 18, self.gray_label)
        rl.draw_text_ex(self.fonts['sm'], "DRIVER CLIMATE ZONE", rl.Vector2(cx + gap + 50, cy + gap + 20), self.fonts['sm'].baseSize, 0, self.gray_label)
        
        # Temp Hero & Flanked Touch Steppers (Tight Proximity)
        center_x = cx + gap + card_w / 2
        temp_y = cy + gap + 80
        temp_txt = f"{int(state.driver_temp_f)}°"
        t_size = rl.measure_text_ex(self.fonts['bxl'], temp_txt, self.fonts['bxl'].baseSize, 0)
        
        btn_minus_d = rl.Rectangle(center_x - t_size.x / 2 - 80, temp_y - 8, 64, 64)
        btn_plus_d  = rl.Rectangle(center_x + t_size.x / 2 + 16, temp_y - 8, 64, 64)
        rl.draw_rectangle_rounded(btn_minus_d, 0.5, 32, self.dark_gray)
        rl.draw_rectangle_rounded(btn_plus_d,  0.5, 32, self.dark_gray)
        rl.draw_text_ex(self.fonts['blg'], "-", rl.Vector2(btn_minus_d.x + 24, btn_minus_d.y + 10), self.fonts['blg'].baseSize, 0, self.white)
        rl.draw_text_ex(self.fonts['blg'], "+", rl.Vector2(btn_plus_d.x + 20,  btn_plus_d.y + 10), self.fonts['blg'].baseSize, 0, self.white)
        
        rl.draw_text_ex(self.fonts['bxl'], temp_txt, rl.Vector2(center_x - t_size.x / 2, temp_y - 12), self.fonts['bxl'].baseSize, 0, self.white)
        
        # 1. Airflow Direction Routing (Defog, Vent, Floor)
        af_y = temp_y + 90
        rl.draw_text_ex(self.fonts['xs'], "AIRFLOW DISTRIBUTION", rl.Vector2(cx + gap + 24, af_y), self.fonts['xs'].baseSize, 0, self.gray_label)
        
        af_labels = ["WINDSHIELD", "DASH VENTS", "FOOTWELL"]
        af_btn_w = (card_w - 48 - 16 * 2) // 3
        for af_i, af_lbl in enumerate(af_labels):
            af_x = cx + gap + 24 + af_i * (af_btn_w + 16)
            af_rect = rl.Rectangle(af_x, af_y + 24, af_btn_w, 48)
            is_af_on = self.driver_airflow[af_i]
            
            if clicked and rl.check_collision_point_rec(mouse, af_rect):
                self.driver_airflow[af_i] = not self.driver_airflow[af_i]
                
            rl.draw_rectangle_rounded(af_rect, 0.3, 12, self.green if is_af_on else self.dark_gray)
            self._draw_text_centered(self.fonts['xs'], af_lbl, af_x + af_btn_w / 2, af_y + 48, self.pure_black if is_af_on else self.white)

        # 2. 3-Stage Heated Seat Control
        heat_y = af_y + 82
        heat_box_w = card_w - 48
        heat_rect = rl.Rectangle(cx + gap + 24, heat_y, heat_box_w, 52)
        rl.draw_rectangle_rounded(heat_rect, 0.25, 12, rl.Color(32, 32, 32, 255))
        
        self._draw_icon("thermometer_white.png", cx + gap + 40, heat_y + 15, 22, self.amber if self.driver_seat_heat > 0 else self.gray_text)
        rl.draw_text_ex(self.fonts['sm'], "SEAT HEATER", rl.Vector2(cx + gap + 72, heat_y + 15), self.fonts['sm'].baseSize, 0, self.white)
        
        # 3 LED Indicator Bars (High / Med / Low)
        for led_i in range(3):
            lx = cx + gap + heat_box_w - 70 + led_i * 20
            l_rect = rl.Rectangle(lx, heat_y + 17, 14, 18)
            is_lit = (led_i < self.driver_seat_heat)
            rl.draw_rectangle_rounded(l_rect, 0.3, 4, self.amber if is_lit else self.dark_gray)
            
        if clicked and rl.check_collision_point_rec(mouse, heat_rect):
            self.driver_seat_heat = (self.driver_seat_heat + 1) % 4
            state.heated_seats = (self.driver_seat_heat > 0)

        # 3. 3-Stage Seat Ventilation / Cooling Control
        cool_y = heat_y + 58
        cool_rect = rl.Rectangle(cx + gap + 24, cool_y, heat_box_w, 52)
        rl.draw_rectangle_rounded(cool_rect, 0.25, 12, rl.Color(32, 32, 32, 255))
        self._draw_icon("fan_white.png", cx + gap + 40, cool_y + 15, 22, self.cyan if self.driver_seat_cool > 0 else self.gray_text)
        rl.draw_text_ex(self.fonts['sm'], "SEAT VENTILATION", rl.Vector2(cx + gap + 72, cool_y + 15), self.fonts['sm'].baseSize, 0, self.white)
        for led_i in range(3):
            lx = cx + gap + heat_box_w - 70 + led_i * 20
            l_rect = rl.Rectangle(lx, cool_y + 17, 14, 18)
            is_lit = (led_i < self.driver_seat_cool)
            rl.draw_rectangle_rounded(l_rect, 0.3, 4, self.cyan if is_lit else self.dark_gray)
            
        if clicked and rl.check_collision_point_rec(mouse, cool_rect):
            self.driver_seat_cool = (self.driver_seat_cool + 1) % 4

        # 4. Cabin Air Recirculation & Purify Toggles
        pur_y = cool_y + 58
        half_btn_w = (heat_box_w - 16) // 2
        btn_recirc = rl.Rectangle(cx + gap + 24, pur_y, half_btn_w, 44)
        btn_purify = rl.Rectangle(cx + gap + 24 + half_btn_w + 16, pur_y, half_btn_w, 44)
        
        rl.draw_rectangle_rounded(btn_recirc, 0.3, 10, self.green if self.recirc_mode else self.dark_gray)
        self._draw_text_centered(self.fonts['xs'], "AIR RECIRC: ON" if self.recirc_mode else "FRESH AIR: ON", btn_recirc.x + half_btn_w/2, pur_y + 22, self.pure_black if self.recirc_mode else self.white)
        
        rl.draw_rectangle_rounded(btn_purify, 0.3, 10, self.green if self.air_purify else self.dark_gray)
        self._draw_text_centered(self.fonts['xs'], "HEPA PURIFY: ACTIVE" if self.air_purify else "HEPA PURIFY: OFF", btn_purify.x + half_btn_w/2, pur_y + 22, self.pure_black if self.air_purify else self.white)
        
        if clicked:
            if rl.check_collision_point_rec(mouse, btn_recirc): self.recirc_mode = not self.recirc_mode
            elif rl.check_collision_point_rec(mouse, btn_purify): self.air_purify = not self.air_purify

        # ── Passenger Card ────────────────────────────────────────────────────
        pass_card_x = cx + gap * 2 + card_w
        self._draw_card(pass_card_x, cy + gap, card_w, top_card_h)
        self._draw_icon("thermometer_white.png", pass_card_x + 24, cy + gap + 20, 18, self.gray_label)
        rl.draw_text_ex(self.fonts['sm'], "PASSENGER CLIMATE ZONE", rl.Vector2(pass_card_x + 50, cy + gap + 20), self.fonts['sm'].baseSize, 0, self.gray_label)
        
        p_center_x = pass_card_x + card_w / 2
        p_temp = int(getattr(state, 'pass_temp_f', 70))
        temp_txt_p = f"{p_temp}°"
        t_size_p = rl.measure_text_ex(self.fonts['bxl'], temp_txt_p, self.fonts['bxl'].baseSize, 0)
        
        btn_minus_p = rl.Rectangle(p_center_x - t_size_p.x / 2 - 80, temp_y - 8, 64, 64)
        btn_plus_p  = rl.Rectangle(p_center_x + t_size_p.x / 2 + 16, temp_y - 8, 64, 64)
        rl.draw_rectangle_rounded(btn_minus_p, 0.5, 32, self.dark_gray)
        rl.draw_rectangle_rounded(btn_plus_p,  0.5, 32, self.dark_gray)
        rl.draw_text_ex(self.fonts['blg'], "-", rl.Vector2(btn_minus_p.x + 24, btn_minus_p.y + 10), self.fonts['blg'].baseSize, 0, self.white)
        rl.draw_text_ex(self.fonts['blg'], "+", rl.Vector2(btn_plus_p.x + 20,  btn_plus_p.y + 10), self.fonts['blg'].baseSize, 0, self.white)
        
        rl.draw_text_ex(self.fonts['bxl'], temp_txt_p, rl.Vector2(p_center_x - t_size_p.x / 2, temp_y - 12), self.fonts['bxl'].baseSize, 0, self.white)
        
        # Airflow Distribution
        rl.draw_text_ex(self.fonts['xs'], "AIRFLOW DISTRIBUTION", rl.Vector2(pass_card_x + 24, af_y), self.fonts['xs'].baseSize, 0, self.gray_label)
        for af_i, af_lbl in enumerate(af_labels):
            af_x = pass_card_x + 24 + af_i * (af_btn_w + 16)
            af_rect = rl.Rectangle(af_x, af_y + 24, af_btn_w, 48)
            is_af_on = self.pass_airflow[af_i]
            
            if clicked and rl.check_collision_point_rec(mouse, af_rect):
                self.pass_airflow[af_i] = not self.pass_airflow[af_i]
                
            rl.draw_rectangle_rounded(af_rect, 0.3, 12, self.green if is_af_on else self.dark_gray)
            self._draw_text_centered(self.fonts['xs'], af_lbl, af_x + af_btn_w / 2, af_y + 48, self.pure_black if is_af_on else self.white)

        # 3-Stage Passenger Heated Seat
        heat_rect_p = rl.Rectangle(pass_card_x + 24, heat_y, heat_box_w, 52)
        rl.draw_rectangle_rounded(heat_rect_p, 0.25, 12, rl.Color(32, 32, 32, 255))
        self._draw_icon("thermometer_white.png", pass_card_x + 40, heat_y + 15, 22, self.amber if self.pass_seat_heat > 0 else self.gray_text)
        rl.draw_text_ex(self.fonts['sm'], "SEAT HEATER", rl.Vector2(pass_card_x + 72, heat_y + 15), self.fonts['sm'].baseSize, 0, self.white)
        for led_i in range(3):
            lx = pass_card_x + heat_box_w - 70 + led_i * 20
            l_rect = rl.Rectangle(lx, heat_y + 17, 14, 18)
            is_lit = (led_i < self.pass_seat_heat)
            rl.draw_rectangle_rounded(l_rect, 0.3, 4, self.amber if is_lit else self.dark_gray)
            
        if clicked and rl.check_collision_point_rec(mouse, heat_rect_p):
            self.pass_seat_heat = (self.pass_seat_heat + 1) % 4

        # 3-Stage Passenger Seat Cooling
        cool_rect_p = rl.Rectangle(pass_card_x + 24, cool_y, heat_box_w, 52)
        rl.draw_rectangle_rounded(cool_rect_p, 0.25, 12, rl.Color(32, 32, 32, 255))
        self._draw_icon("fan_white.png", pass_card_x + 40, cool_y + 15, 22, self.cyan if self.pass_seat_cool > 0 else self.gray_text)
        rl.draw_text_ex(self.fonts['sm'], "SEAT VENTILATION", rl.Vector2(pass_card_x + 72, cool_y + 15), self.fonts['sm'].baseSize, 0, self.white)
        for led_i in range(3):
            lx = pass_card_x + heat_box_w - 70 + led_i * 20
            l_rect = rl.Rectangle(lx, cool_y + 17, 14, 18)
            is_lit = (led_i < self.pass_seat_cool)
            rl.draw_rectangle_rounded(l_rect, 0.3, 4, self.cyan if is_lit else self.dark_gray)
            
        if clicked and rl.check_collision_point_rec(mouse, cool_rect_p):
            self.pass_seat_cool = (self.pass_seat_cool + 1) % 4

        # Passenger Sync & Rear Zone Toggles
        btn_sync = rl.Rectangle(pass_card_x + 24, pur_y, half_btn_w, 44)
        btn_rear = rl.Rectangle(pass_card_x + 24 + half_btn_w + 16, pur_y, half_btn_w, 44)
        
        rl.draw_rectangle_rounded(btn_sync, 0.3, 10, self.green if self.sync_mode else self.dark_gray)
        self._draw_text_centered(self.fonts['xs'], "SYNC DUAL: ON" if self.sync_mode else "SYNC DUAL: OFF", btn_sync.x + half_btn_w/2, pur_y + 22, self.pure_black if self.sync_mode else self.white)
        
        rl.draw_rectangle_rounded(btn_rear, 0.3, 10, self.green)
        self._draw_text_centered(self.fonts['xs'], "REAR CABIN: AUTO", btn_rear.x + half_btn_w/2, pur_y + 22, self.pure_black)
        
        if clicked and rl.check_collision_point_rec(mouse, btn_sync):
            self.sync_mode = not self.sync_mode
            if self.sync_mode:
                state.pass_temp_f = state.driver_temp_f

        if clicked:
            if rl.check_collision_point_rec(mouse, btn_minus_d): state.driver_temp_f = max(60, state.driver_temp_f - 1)
            elif rl.check_collision_point_rec(mouse, btn_plus_d): state.driver_temp_f = min(85, state.driver_temp_f + 1)
            elif rl.check_collision_point_rec(mouse, btn_minus_p): state.pass_temp_f = max(60, p_temp - 1)
            elif rl.check_collision_point_rec(mouse, btn_plus_p): state.pass_temp_f = min(85, p_temp + 1)

        # ── Fan Speed Strip ───────────────────────────────────────────────────
        fan_strip_y = cy + gap + top_card_h + 10
        fan_strip_w = cw - gap * 2
        rl.draw_rectangle_rounded(rl.Rectangle(cx + gap, fan_strip_y, fan_strip_w, 44), 0.35, 16, self.card_bg)
        
        self._draw_icon("fan_white.png", cx + gap + 20, fan_strip_y + 12, 20, self.white)
        rl.draw_text_ex(self.fonts['xs'], "BLOWER SPEED", rl.Vector2(cx + gap + 48, fan_strip_y + 14), self.fonts['xs'].baseSize, 0, self.gray_label)
        
        btn_fan_minus = rl.Rectangle(cx + gap + 160, fan_strip_y + 6, 32, 32)
        btn_fan_plus  = rl.Rectangle(cx + gap + fan_strip_w - 56, fan_strip_y + 6, 32, 32)
        rl.draw_rectangle_rounded(btn_fan_minus, 0.5, 16, self.dark_gray)
        rl.draw_rectangle_rounded(btn_fan_plus,  0.5, 16, self.dark_gray)
        rl.draw_text_ex(self.fonts['md'], "-", rl.Vector2(btn_fan_minus.x + 11, btn_fan_minus.y + 4), self.fonts['md'].baseSize, 0, self.white)
        rl.draw_text_ex(self.fonts['md'], "+", rl.Vector2(btn_fan_plus.x + 9,   btn_fan_plus.y + 4), self.fonts['md'].baseSize, 0, self.white)
        
        fan_cur = getattr(state, 'fan_level', 3)
        seg_start_x = cx + gap + 206
        seg_w = (fan_strip_w - 280) / 7
        for s in range(7):
            sx = seg_start_x + s * seg_w
            s_rect = rl.Rectangle(sx + 3, fan_strip_y + 12, seg_w - 6, 20)
            rl.draw_rectangle_rounded(s_rect, 0.25, 4, self.green if s < fan_cur else self.dark_gray)
            if clicked and rl.check_collision_point_rec(mouse, s_rect):
                state.fan_level = s + 1
                
        if clicked:
            if rl.check_collision_point_rec(mouse, btn_fan_minus): state.fan_level = max(1, fan_cur - 1)
            elif rl.check_collision_point_rec(mouse, btn_fan_plus): state.fan_level = min(7, fan_cur + 1)

        # ── Mode Toggle Bar (With Prominent AUTO and SYNC) ─────────────────────
        py = fan_strip_y + 52
        mode_labels = ["AUTO", "A/C", "HEAT", "DEFROST", "REAR DEF", "SYNC"]
        pill_w = (cw - gap * 2 - (len(mode_labels) - 1) * 14) // len(mode_labels)
        
        for i, lbl in enumerate(mode_labels):
            px = cx + gap + i * (pill_w + 14)
            pill_rect = rl.Rectangle(px, py, pill_w, 46)
            
            is_on = False
            if lbl == "AUTO": is_on = self.auto_mode
            elif lbl == "A/C": is_on = state.ac_on
            elif lbl == "HEAT": is_on = getattr(state, 'heat_on', False)
            elif lbl == "DEFROST": is_on = getattr(state, 'def_on', False)
            elif lbl == "REAR DEF": is_on = getattr(state, 'rear_defrost', False)
            elif lbl == "SYNC": is_on = self.sync_mode
            
            if clicked and rl.check_collision_point_rec(mouse, pill_rect):
                if lbl == "AUTO": self.auto_mode = not self.auto_mode
                elif lbl == "A/C": state.ac_on = not state.ac_on
                elif lbl == "HEAT": state.heat_on = not getattr(state, 'heat_on', False)
                elif lbl == "DEFROST": state.def_on = not getattr(state, 'def_on', False)
                elif lbl == "REAR DEF": state.rear_defrost = not getattr(state, 'rear_defrost', False)
                elif lbl == "SYNC":
                    self.sync_mode = not self.sync_mode
                    if self.sync_mode: state.pass_temp_f = state.driver_temp_f
                is_on = not is_on
                
            bg = self.green if is_on else self.card_bg
            fg = self.pure_black if is_on else self.white
            rl.draw_rectangle_rounded(pill_rect, 0.35, 16, bg)
            l_size = rl.measure_text_ex(self.fonts['bmd'], lbl, self.fonts['bmd'].baseSize, 0)
            rl.draw_text_ex(self.fonts['bmd'], lbl, rl.Vector2(px + pill_w / 2 - l_size.x / 2, py + 23 - l_size.y / 2), self.fonts['bmd'].baseSize, 0, fg)

    # ════════════════════════════════════════════════════════════════════════════
    # 4. NAVIGATION APP SCREEN
    # ════════════════════════════════════════════════════════════════════════════
    def _render_nav(self, state, cx, cy, cw, ch, mouse, clicked):
        map_w = int(cw * 0.68)
        rl.draw_rectangle(int(cx), int(cy), map_w, int(ch), rl.Color(28, 28, 30, 255))
        
        rl.draw_line_ex(rl.Vector2(cx, cy + ch * 0.5), rl.Vector2(cx + map_w, cy + ch * 0.5), 18, rl.Color(50, 50, 54, 255))
        rl.draw_line_ex(rl.Vector2(cx + map_w * 0.45, cy), rl.Vector2(cx + map_w * 0.45, cy + ch), 24, self.green)
        rl.draw_line_ex(rl.Vector2(cx + map_w * 0.45, cy + ch * 0.4), rl.Vector2(cx + map_w * 0.8, cy + ch * 0.1), 14, self.green)
        
        veh_pos = rl.Vector2(cx + map_w * 0.45, cy + ch * 0.6)
        rl.draw_circle(int(veh_pos.x), int(veh_pos.y), 14, self.green)
        rl.draw_circle(int(veh_pos.x), int(veh_pos.y), 6, self.white)
        
        hud_nav = rl.Rectangle(cx + 24, cy + 24, 340, 110)
        rl.draw_rectangle_rounded(hud_nav, 0.25, 16, rl.Color(0, 0, 0, 220))
        self._draw_icon_centered("arrow-up_white.png", hud_nav.x + 40, hud_nav.y + 40, 32, self.green)
        rl.draw_text_ex(self.fonts['blg'], "In 800 ft", rl.Vector2(hud_nav.x + 75, hud_nav.y + 16), self.fonts['blg'].baseSize, 0, self.white)
        rl.draw_text_ex(self.fonts['sm'], "Exit 432B · Downtown SF", rl.Vector2(hud_nav.x + 75, hud_nav.y + 60), self.fonts['sm'].baseSize, 0, self.gray_text)

        rp_x = cx + map_w + 16
        rp_w = cw - map_w - 32
        self._draw_card(rp_x, cy + 16, rp_w, ch - 32)
        
        rl.draw_text_ex(self.fonts['xs'], "DESTINATION", rl.Vector2(rp_x + 24, cy + 36), self.fonts['xs'].baseSize, 0, self.gray_label)
        dest = getattr(state, 'destination', "San Francisco, CA")
        rl.draw_text_ex(self.fonts['blg'], dest, rl.Vector2(rp_x + 24, cy + 60), self.fonts['blg'].baseSize, 0, self.white)
        
        stats = [
            ("Distance Remaining", f"{getattr(state, 'trip_distance_mi', 12.4):.1f} MI"),
            ("Estimated Time", "14 MIN"),
            ("Arrival Time", "5:42 PM"),
            ("Via Route", "US-101 Northbound")
        ]
        for idx, (lbl, val) in enumerate(stats):
            sy = cy + 130 + idx * 56
            rl.draw_text_ex(self.fonts['sm'], lbl, rl.Vector2(rp_x + 24, sy), self.fonts['sm'].baseSize, 0, self.gray_text)
            rl.draw_text_ex(self.fonts['bmd'], val, rl.Vector2(rp_x + rp_w - 140, sy), self.fonts['bmd'].baseSize, 0, self.white)

        btn_end = rl.Rectangle(rp_x + 24, cy + ch - 80, rp_w - 48, 48)
        rl.draw_rectangle_rounded(btn_end, 0.35, 16, rl.Color(226, 44, 44, 255))
        self._draw_text_centered(self.fonts['bmd'], "CANCEL ROUTE", btn_end.x + (rp_w - 48) / 2, btn_end.y + 24, self.white)

    # ════════════════════════════════════════════════════════════════════════════
    # 5. PHONE APP SCREEN
    # ════════════════════════════════════════════════════════════════════════════
    def _render_phone(self, state, cx, cy, cw, ch, mouse, clicked):
        gap = 16
        for i, (name, number) in enumerate(_CONTACTS):
            ry = cy + gap + i * (84 + gap)
            rect = rl.Rectangle(cx + gap, ry, cw - gap * 2, 84)
            self._draw_card(rect.x, rect.y, rect.width, rect.height)
            
            rl.draw_circle(int(cx + gap + 50), int(ry + 42), 24, self.dark_gray)
            self._draw_icon_centered("phone_white.png", cx + gap + 50, ry + 42, 20, self.green)
            
            rl.draw_text_ex(self.fonts['blg'], name, rl.Vector2(cx + gap + 90, ry + 18), self.fonts['blg'].baseSize, 0, self.white)
            rl.draw_text_ex(self.fonts['md'], number, rl.Vector2(cx + gap + 90, ry + 52), self.fonts['md'].baseSize, 0, self.gray_text)
            
            call_btn = rl.Rectangle(cx + cw - gap - 120, ry + 22, 90, 40)
            rl.draw_rectangle_rounded(call_btn, 0.5, 16, self.green)
            self._draw_text_centered(self.fonts['bmd'], "CALL", call_btn.x + 45, call_btn.y + 20, self.pure_black)

    # ════════════════════════════════════════════════════════════════════════════
    # 6. SETTINGS SCREEN
    # ════════════════════════════════════════════════════════════════════════════
    def _render_settings(self, state, cx, cy, cw, ch, mouse, clicked):
        gap = 16
        for i, lbl in enumerate(_SETTINGS_LABELS):
            ry = cy + gap + i * (74 + gap)
            rect = rl.Rectangle(cx + gap, ry, cw - gap * 2, 74)
            self._draw_card(rect.x, rect.y, rect.width, rect.height)
            
            if clicked and rl.check_collision_point_rec(mouse, rect):
                self.focused_setting = i
                
            if i == self.focused_setting:
                rl.draw_rectangle_rounded_lines_ex(rect, 0.25, 32, 2.0, self.green)
            
            rl.draw_text_ex(self.fonts['blg'], lbl, rl.Vector2(cx + gap + 32, ry + 18), self.fonts['blg'].baseSize, 0, self.white)
            
            val_text = "Standard"
            if lbl == "Vehicle Profile": val_text = str(getattr(state, 'car_profile', 'toyota')).upper()
            elif lbl == "Units": val_text = "Imperial (MPH, °F)"
            elif lbl == "Brightness": val_text = "80%"
            elif lbl == "About OpenCar": val_text = "v2.0-opendbc"
                
            rl.draw_text_ex(self.fonts['md'], val_text, rl.Vector2(cx + cw - gap - 220, ry + 22), self.fonts['md'].baseSize, 0, self.gray_text)

    # ════════════════════════════════════════════════════════════════════════════
    # BOTTOM STATUS BAR - High-Luminance Automotive Grammar
    # ════════════════════════════════════════════════════════════════════════════
    def _render_bottom_bar(self, state, W, H):
        bh = 54
        by = H - bh
        rl.draw_rectangle(0, by, W, bh, rl.Color(32, 32, 32, 255))
        rl.draw_line_ex(rl.Vector2(0, by), rl.Vector2(W, by), 1.0, rl.Color(50, 50, 50, 255))
        
        # Left: Speed + Glare-Resistant PRNDL Badge
        speed_int = int(getattr(state, 'speed_mph', 0))
        rl.draw_text_ex(self.fonts['bmd'], f"{speed_int} MPH", rl.Vector2(100, by + 14), self.fonts['bmd'].baseSize, 0, self.white)
        
        raw_gear = getattr(state, 'gear', 0)
        gears = ['P', 'R', 'N', 'D']
        gear_str = gears[raw_gear] if isinstance(raw_gear, int) and 0 <= raw_gear < 4 else str(raw_gear).upper()
            
        gear_bg = self.green if gear_str == 'D' else (rl.Color(226, 44, 44, 255) if gear_str == 'R' else self.dark_gray)
        gear_rect = rl.Rectangle(205, by + 12, 34, 30)
        rl.draw_rectangle_rounded(gear_rect, 0.35, 8, gear_bg)
        self._draw_text_centered(self.fonts['bmd'], gear_str, gear_rect.x + 17, gear_rect.y + 15, self.pure_black if gear_str in ['D', 'P'] else self.white)
        
        # Comma 3X Active Indicator
        rl.draw_circle(260, by + 27, 4, self.green)
        rl.draw_text_ex(self.fonts['xs'], "comma active", rl.Vector2(272, by + 19), self.fonts['xs'].baseSize, 0, self.white)

        # Center: Current Nav maneuver snippet
        nav_info = "Continue on US-101 North · 12.4 MI"
        self._draw_icon("navigation_white.png", W // 2 - 160, by + 18, 16, self.green)
        rl.draw_text_ex(self.fonts['sm'], nav_info, rl.Vector2(W // 2 - 136, by + 16), self.fonts['sm'].baseSize, 0, self.gray_text)
        
        # Right: Connectivity Icons + System Clock
        self._draw_icon("bluetooth_white.png", W - 230, by + 18, 18, self.white)
        self._draw_icon("signal_white.png", W - 195, by + 18, 18, self.white)
        self._draw_icon("wifi_white.png", W - 160, by + 18, 18, self.white)
        
        clock = time.strftime("%I:%M %p")
        rl.draw_text_ex(self.fonts['bmd'], clock, rl.Vector2(W - 120, by + 14), self.fonts['bmd'].baseSize, 0, self.white)

    def _draw_text_centered(self, font, text, cx, cy, color):
        ts = rl.measure_text_ex(font, text, font.baseSize, 0)
        rl.draw_text_ex(font, text, rl.Vector2(cx - ts.x / 2, cy - ts.y / 2), font.baseSize, 0, color)

    def handle_key(self, key, state, theme):
        if key == rl.KeyboardKey.KEY_H: state.infotainment_app = 0; return
        if key == rl.KeyboardKey.KEY_N and state.infotainment_app != 2: state.infotainment_app = 1; return
        if key == rl.KeyboardKey.KEY_M: state.infotainment_app = 2; return
        if key == rl.KeyboardKey.KEY_C: state.infotainment_app = 3; return
        if key == rl.KeyboardKey.KEY_P and state.infotainment_app != 2: state.infotainment_app = 4; return
        if key == rl.KeyboardKey.KEY_S and state.infotainment_app != 3: state.infotainment_app = 5; return
        if key == rl.KeyboardKey.KEY_LEFT: state.infotainment_app = max(0, state.infotainment_app - 1)
        elif key == rl.KeyboardKey.KEY_RIGHT: state.infotainment_app = min(5, state.infotainment_app + 1)
        
        if state.infotainment_app == 2:
            if key == rl.KeyboardKey.KEY_SPACE: state.music_playing = not state.music_playing
            elif key == rl.KeyboardKey.KEY_N:
                state.music_track = (state.music_track + 1) % len(_TRACKS)
                state.music_artist, state.music_title = _TRACKS[state.music_track]
                state.music_progress = 0.0
        elif state.infotainment_app == 3:
            if key == rl.KeyboardKey.KEY_UP: state.driver_temp_f = min(85, state.driver_temp_f + 1)
            elif key == rl.KeyboardKey.KEY_DOWN: state.driver_temp_f = max(60, state.driver_temp_f - 1)
            elif key == rl.KeyboardKey.KEY_A: state.ac_on = not state.ac_on
        elif state.infotainment_app == 5:
            if key == rl.KeyboardKey.KEY_UP: self.focused_setting = max(0, self.focused_setting - 1)
            elif key == rl.KeyboardKey.KEY_DOWN: self.focused_setting = min(len(_SETTINGS_LABELS)-1, self.focused_setting + 1)

# surfaces/infotainment.py — Comma 4 Glassmorphic Infotainment Surface
import pyray as rl
import os
import math
import time
import glass

_TRACKS = [
    ("The Midnight", "Los Angeles"),
    ("Tycho", "Awake"),
    ("Bonobo", "Kong"),
    ("Polo & Pan", "Canopee"),
    ("Washed Out", "Feel It All Around"),
    ("Kavinsky", "Nightcall"),
    ("Daft Punk", "Veridis Quo")
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

    def _safe_load(self, path):
        if os.path.exists(path):
            return rl.load_texture(path)
        return None

    def _draw_icon(self, name, x, y, size, tint=None):
        tex = self.icons.get(name)
        if tex and tex.id > 0:
            scale = float(size) / max(tex.width, 1)
            rl.draw_texture_ex(tex, rl.Vector2(x, y), 0.0, scale, tint or glass.TEXT_PRIMARY)

    def _draw_icon_centered(self, name, cx, cy, size, tint=None):
        tex = self.icons.get(name)
        if tex and tex.id > 0:
            scale = float(size) / max(tex.width, 1)
            w = tex.width * scale
            h = tex.height * scale
            rl.draw_texture_ex(tex, rl.Vector2(cx - w / 2, cy - h / 2), 0.0, scale, tint or glass.TEXT_PRIMARY)

    def _draw_card(self, x, y, w, h, roundness=0.36, glow=None):
        glass.draw_glass_card(rl.Rectangle(x, y, w, h), roundness=roundness, glow_color=glow)

    def _draw_text_centered(self, font, text, cx, cy, color):
        ts = rl.measure_text_ex(font, text, font.baseSize, 0)
        rl.draw_text_ex(font, text, rl.Vector2(cx - ts.x / 2, cy - ts.y / 2), font.baseSize, 0, color)

    def render(self, state, theme) -> None:
        W = rl.get_screen_width()
        H = rl.get_screen_height()
        
        glass.draw_ambient_backdrop(W, H)
        
        # ── Sidebar Dock (Floating Frosted Glass Rail) ────────────────
        dock_x = 12
        dock_y = 12
        dock_w = 70
        dock_h = H - 74
        dock_rect = rl.Rectangle(dock_x, dock_y, dock_w, dock_h)
        glass.draw_glass_card(dock_rect, roundness=0.35, bg=rl.Color(16, 18, 26, 230))
        
        sidebar_icons = [
            ("home_white.png", 0),
            ("map-pin_white.png", 1),
            ("music_white.png", 2),
            ("snowflake_white.png", 3),
            ("phone_white.png", 4),
            ("settings_white.png", 5)
        ]
        
        clicked = rl.is_mouse_button_pressed(rl.MouseButton.MOUSE_BUTTON_LEFT)
        mouse = rl.get_mouse_position()
        
        tab_h = dock_h / 6.0
        for icon_name, app_idx in sidebar_icons:
            iy = dock_y + app_idx * tab_h
            is_active = (state.infotainment_app == app_idx)
            hit_r = rl.Rectangle(dock_x, iy, dock_w, tab_h)
            
            if clicked and rl.check_collision_point_rec(mouse, hit_r):
                state.infotainment_app = app_idx
                
            center_x = dock_x + dock_w / 2
            center_y = iy + tab_h / 2
            
            if is_active:
                pill_r = rl.Rectangle(dock_x + 8, center_y - 24, dock_w - 16, 48)
                glass.draw_glass_pill(pill_r, roundness=0.45, active=True, solid=True)
                self._draw_icon_centered(icon_name, center_x, center_y, 24, glass.OBSIDIAN_BG)
            else:
                self._draw_icon_centered(icon_name, center_x, center_y, 24, rl.Color(210, 215, 230, 230))

        # Content Area
        cx = dock_x + dock_w + 14
        cy = 12
        cw = W - cx - 14
        ch = H - 76
        
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
            
        # Bottom dock bar
        self._render_bottom_bar(state, W, H)

    # ════════════════════════════════════════════════════════════════════════════
    # 1. HOME SCREEN - Comma 4 Card Glassmorphic Architecture
    # ════════════════════════════════════════════════════════════════════════════
    def _render_home(self, state, cx, cy, cw, ch, mouse, clicked):
        gap = 14
        card_w1 = int((cw - gap) * 0.51)
        card_w2 = cw - gap - card_w1
        card_h = (ch - gap) // 2
        
        # ── 1. NOW PLAYING Card ───────────────────────────────────────────────
        rect_music = rl.Rectangle(cx, cy, card_w1, card_h)
        self._draw_card(rect_music.x, rect_music.y, rect_music.width, rect_music.height)
        
        self._draw_icon("music_white.png", rect_music.x + 22, rect_music.y + 18, 16, glass.TEXT_MUTED)
        rl.draw_text_ex(self.fonts['xs'], 'NOW PLAYING', rl.Vector2(rect_music.x + 44, rect_music.y + 18), self.fonts['xs'].baseSize, 0, glass.TEXT_MUTED)
        
        # Spotify Glass Pill Badge
        badge_w = 90
        badge_rect = rl.Rectangle(rect_music.x + card_w1 - badge_w - 20, rect_music.y + 14, badge_w, 24)
        glass.draw_glass_pill(badge_rect, roundness=0.5)
        rl.draw_circle(int(badge_rect.x + 12), int(badge_rect.y + 12), 4, glass.COMMA_GREEN)
        rl.draw_text_ex(self.fonts['xs'], 'SPOTIFY', rl.Vector2(badge_rect.x + 24, badge_rect.y + 5), self.fonts['xs'].baseSize, 0, glass.TEXT_PRIMARY)

        # Album Art with drop shadow
        art_size = 112
        art_keys = ["the_midnight.jpg", "tycho.jpg", "bonobo.jpg"]
        art_idx = getattr(state, 'music_track', 0) % len(art_keys)
        art_tex = self.album_arts.get(art_keys[art_idx])
        art_x = rect_music.x + 22
        art_y = rect_music.y + 50
        rl.draw_rectangle_rounded(rl.Rectangle(art_x - 3, art_y - 1, art_size + 6, art_size + 8), 0.18, 16, glass.SHADOW_CORE)
        if art_tex and art_tex.id > 0:
            scale = art_size / max(art_tex.width, 1)
            rl.draw_texture_ex(art_tex, rl.Vector2(art_x, art_y), 0.0, scale, rl.WHITE)
            rl.draw_rectangle_rounded_lines_ex(rl.Rectangle(art_x, art_y, art_size, art_size), 0.18, 16, 1.2, glass.GLASS_BORDER)
        
        info_x = art_x + art_size + 18
        rl.draw_text_ex(self.fonts['blg'], getattr(state, 'music_title', "Los Angeles"), rl.Vector2(info_x, art_y + 4), self.fonts['blg'].baseSize, 0, glass.TEXT_PRIMARY)
        rl.draw_text_ex(self.fonts['md'], getattr(state, 'music_artist', "The Midnight"), rl.Vector2(info_x, art_y + 46), self.fonts['md'].baseSize, 0, glass.TEXT_SECONDARY)
        rl.draw_text_ex(self.fonts['xs'], "FLAC 96kHz · Lossless Master Audio", rl.Vector2(info_x, art_y + 82), self.fonts['xs'].baseSize, 0, glass.SKY_BLUE)

        # Equalizer bars
        eq_rx = rect_music.x + card_w1 - 92
        eq_ry = art_y + 82
        now_t = time.time() * 8
        for b_i in range(6):
            h_anim = int(22 * (0.35 + 0.65 * abs(((now_t + b_i * 1.2) % 2) - 1)))
            glass.draw_glass_pill(rl.Rectangle(eq_rx + b_i * 11, eq_ry - h_anim, 6, h_anim), roundness=0.5, bg=glass.COMMA_GREEN, border=glass.COMMA_GREEN)

        # Scrubber
        prog_y = rect_music.y + card_h - 60
        prog_w = card_w1 - 44
        prog_rx = rect_music.x + 22
        
        rl.draw_rectangle_rounded(rl.Rectangle(prog_rx, prog_y, prog_w, 6), 1.0, 16, rl.Color(32, 35, 45, 255))
        fill_w = int(prog_w * max(0.0, min(1.0, getattr(state, 'music_progress', 0.38))))
        if fill_w > 0:
            rl.draw_rectangle_rounded(rl.Rectangle(prog_rx, prog_y, fill_w, 6), 1.0, 16, glass.COMMA_GREEN)
            rl.draw_circle(int(prog_rx + fill_w), int(prog_y + 3), 6, glass.TEXT_PRIMARY)
            rl.draw_circle(int(prog_rx + fill_w), int(prog_y + 3), 10, glass.COMMA_GREEN_GLOW)
            
        total_sec = 225
        curr_sec = int(getattr(state, 'music_progress', 0.38) * total_sec)
        t_curr = f"{curr_sec // 60}:{curr_sec % 60:02d}"
        t_rem = f"-{(total_sec - curr_sec) // 60}:{(total_sec - curr_sec) % 60:02d}"
        rl.draw_text_ex(self.fonts['xs'], t_curr, rl.Vector2(prog_rx, prog_y + 12), self.fonts['xs'].baseSize, 0, glass.TEXT_MUTED)
        rl.draw_text_ex(self.fonts['xs'], t_rem, rl.Vector2(prog_rx + prog_w - 38, prog_y + 12), self.fonts['xs'].baseSize, 0, glass.TEXT_MUTED)
        
        # Floating Circular Mini Media Buttons
        ctrl_cx = prog_rx + prog_w / 2
        ctrl_cy = prog_y + 18
        
        glass.draw_circular_button(ctrl_cx - 52, ctrl_cy, 18, bg=rl.Color(28, 30, 40, 230))
        self._draw_icon_centered("skip-back_white.png", ctrl_cx - 52, ctrl_cy, 18, glass.TEXT_PRIMARY)
        
        is_playing = getattr(state, 'music_playing', True)
        play_col = glass.COMMA_GREEN if not is_playing else rl.Color(245, 245, 245, 255)
        glass.draw_circular_button(ctrl_cx, ctrl_cy, 22, bg=play_col, glow=glass.COMMA_GREEN_GLOW)
        self._draw_icon_centered("pause_dark.png" if is_playing else "play_dark.png", ctrl_cx, ctrl_cy, 20, glass.OBSIDIAN_BG)
        
        glass.draw_circular_button(ctrl_cx + 52, ctrl_cy, 18, bg=rl.Color(28, 30, 40, 230))
        self._draw_icon_centered("skip-forward_white.png", ctrl_cx + 52, ctrl_cy, 18, glass.TEXT_PRIMARY)
        
        if clicked:
            btn_prev_r = rl.Rectangle(ctrl_cx - 70, ctrl_cy - 18, 36, 36)
            btn_play_r = rl.Rectangle(ctrl_cx - 22, ctrl_cy - 22, 44, 44)
            btn_next_r = rl.Rectangle(ctrl_cx + 34, ctrl_cy - 18, 36, 36)
            if rl.check_collision_point_rec(mouse, btn_prev_r):
                state.music_track = (state.music_track - 1) % len(_TRACKS)
                state.music_artist, state.music_title = _TRACKS[state.music_track]
                state.music_progress = 0.0
            elif rl.check_collision_point_rec(mouse, btn_play_r):
                state.music_playing = not state.music_playing
            elif rl.check_collision_point_rec(mouse, btn_next_r):
                state.music_track = (state.music_track + 1) % len(_TRACKS)
                state.music_artist, state.music_title = _TRACKS[state.music_track]
                state.music_progress = 0.0
            elif rl.check_collision_point_rec(mouse, rect_music) and mouse.y < prog_y - 10:
                state.infotainment_app = 2

        # ── 2. NAVIGATION Card ────────────────────────────────────────────────
        rect_nav = rl.Rectangle(cx + card_w1 + gap, cy, card_w2, card_h)
        self._draw_card(rect_nav.x, rect_nav.y, rect_nav.width, rect_nav.height)
        
        self._draw_icon("navigation_white.png", rect_nav.x + 22, rect_nav.y + 18, 16, glass.TEXT_MUTED)
        rl.draw_text_ex(self.fonts['xs'], "NAVIGATION", rl.Vector2(rect_nav.x + 44, rect_nav.y + 18), self.fonts['xs'].baseSize, 0, glass.TEXT_MUTED)
        
        dest_str = getattr(state, 'destination', "Downtown SF")
        rl.draw_text_ex(self.fonts['blg'], dest_str, rl.Vector2(rect_nav.x + 22, rect_nav.y + 46), self.fonts['blg'].baseSize, 0, glass.TEXT_PRIMARY)
        
        # Maneuver Banner with Circular Glowing Badge
        maneuver_y = rect_nav.y + 98
        glass.draw_circular_button(rect_nav.x + 44, maneuver_y + 22, 22, bg=glass.COMMA_GREEN, glow=glass.COMMA_GREEN_GLOW)
        self._draw_icon_centered("arrow-up_white.png", rect_nav.x + 44, maneuver_y + 22, 24, glass.OBSIDIAN_BG)
        
        rl.draw_text_ex(self.fonts['bmd'], "In 800 ft, Exit 432B", rl.Vector2(rect_nav.x + 78, maneuver_y + 2), self.fonts['bmd'].baseSize, 0, glass.TEXT_PRIMARY)
        rl.draw_text_ex(self.fonts['sm'], "Merge onto US-101 North", rl.Vector2(rect_nav.x + 78, maneuver_y + 26), self.fonts['sm'].baseSize, 0, glass.TEXT_SECONDARY)
        
        # Upcoming Lane Guidance
        lg_x = rect_nav.x + card_w2 - 170
        rl.draw_text_ex(self.fonts['xs'], "LANE ASSIST", rl.Vector2(lg_x, maneuver_y - 12), self.fonts['xs'].baseSize, 0, glass.TEXT_MUTED)
        lanes = ["LEFT", "THRU", "EXIT"]
        for l_idx, lname in enumerate(lanes):
            lx = lg_x + l_idx * 54
            is_exit = (l_idx == 2)
            l_box = rl.Rectangle(lx, maneuver_y + 8, 48, 28)
            glass.draw_glass_pill(l_box, roundness=0.35, active=is_exit)
            self._draw_text_centered(self.fonts['xs'], lname, lx + 24, maneuver_y + 22, glass.OBSIDIAN_BG if is_exit else glass.TEXT_PRIMARY)
        
        # ETA & Distance Frosted Pills
        eta_y = rect_nav.y + card_h - 48
        pills = [
            ("14 MIN", glass.COMMA_GREEN, glass.OBSIDIAN_BG),
            ("12.4 MI", glass.PILL_BG, glass.TEXT_PRIMARY),
            ("ETA 5:42 PM", glass.PILL_BG, glass.TEXT_PRIMARY)
        ]
        px = rect_nav.x + 22
        for text, bg_col, fg_col in pills:
            ts = rl.measure_text_ex(self.fonts['xs'], text, self.fonts['xs'].baseSize, 0)
            pw = ts.x + 22
            pill_r = rl.Rectangle(px, eta_y, pw, 30)
            is_act = (bg_col == glass.COMMA_GREEN)
            glass.draw_glass_pill(pill_r, roundness=0.5, bg=bg_col if is_act else None, active=is_act)
            rl.draw_text_ex(self.fonts['xs'], text, rl.Vector2(px + 11, eta_y + 7), self.fonts['xs'].baseSize, 0, fg_col)
            px += pw + 8
            
        if clicked and rl.check_collision_point_rec(mouse, rect_nav):
            state.infotainment_app = 1

        # ── 3. CLIMATE CONTROL Card ───────────────────────────────────────────
        rect_clim = rl.Rectangle(cx, cy + card_h + gap, card_w1, card_h)
        self._draw_card(rect_clim.x, rect_clim.y, rect_clim.width, rect_clim.height)
        
        self._draw_icon("fan_white.png", rect_clim.x + 22, rect_clim.y + 18, 16, glass.TEXT_MUTED)
        rl.draw_text_ex(self.fonts['xs'], "CLIMATE CONTROL", rl.Vector2(rect_clim.x + 44, rect_clim.y + 18), self.fonts['xs'].baseSize, 0, glass.TEXT_MUTED)
        
        ac_text = "AUTO · A/C ON" if state.ac_on else "CLIMATE OFF"
        ac_rect = rl.Rectangle(rect_clim.x + card_w1 - 124, rect_clim.y + 14, 104, 24)
        glass.draw_glass_pill(ac_rect, roundness=0.5, active=state.ac_on)
        self._draw_text_centered(self.fonts['xs'], ac_text, ac_rect.x + 52, ac_rect.y + 12, glass.OBSIDIAN_BG if state.ac_on else glass.TEXT_MUTED)

        col_w = (card_w1 - 64) // 3
        d_col_x = rect_clim.x + 22
        mid_y = rect_clim.y + 50
        
        # Driver Column
        rl.draw_text_ex(self.fonts['xs'], "DRIVER", rl.Vector2(d_col_x, mid_y), self.fonts['xs'].baseSize, 0, glass.TEXT_MUTED)
        rl.draw_text_ex(self.fonts['xl'], f"{int(state.driver_temp_f)}°", rl.Vector2(d_col_x, mid_y + 20), self.fonts['xl'].baseSize, 0, glass.TEXT_PRIMARY)
        
        btn_d_minus = rl.Rectangle(d_col_x, mid_y + 102, 38, 38)
        btn_d_plus  = rl.Rectangle(d_col_x + 46, mid_y + 102, 38, 38)
        glass.draw_circular_button(d_col_x + 19, mid_y + 121, 19)
        glass.draw_circular_button(d_col_x + 65, mid_y + 121, 19)
        self._draw_text_centered(self.fonts['blg'], "-", d_col_x + 19, mid_y + 119, glass.TEXT_PRIMARY)
        self._draw_text_centered(self.fonts['blg'], "+", d_col_x + 65, mid_y + 119, glass.TEXT_PRIMARY)

        # Center Column: Fan & Airflow
        c_col_x = d_col_x + col_w + 14
        rl.draw_text_ex(self.fonts['xs'], "VENTILATION", rl.Vector2(c_col_x, mid_y), self.fonts['xs'].baseSize, 0, glass.TEXT_MUTED)
        self._draw_icon("fan_white.png", c_col_x, mid_y + 26, 22, glass.COMMA_GREEN if state.ac_on else glass.TEXT_MUTED)
        rl.draw_text_ex(self.fonts['md'], f"FAN {getattr(state, 'fan_level', 3)}", rl.Vector2(c_col_x + 30, mid_y + 24), self.fonts['md'].baseSize, 0, glass.TEXT_PRIMARY)
        
        fan_lvl = getattr(state, 'fan_level', 3)
        for b in range(5):
            bar_rect = rl.Rectangle(c_col_x + b * 18, mid_y + 64, 12, 16)
            glass.draw_glass_pill(bar_rect, roundness=0.3, active=(b < fan_lvl), solid=(b < fan_lvl))
            
        rl.draw_text_ex(self.fonts['xs'], "Airflow: Dash & Floor", rl.Vector2(c_col_x, mid_y + 108), self.fonts['xs'].baseSize, 0, glass.TEXT_SECONDARY)

        # Passenger Column
        p_col_x = c_col_x + col_w + 14
        p_temp = int(getattr(state, 'pass_temp_f', 70))
        rl.draw_text_ex(self.fonts['xs'], "PASSENGER", rl.Vector2(p_col_x, mid_y), self.fonts['xs'].baseSize, 0, glass.TEXT_MUTED)
        rl.draw_text_ex(self.fonts['xl'], f"{p_temp}°", rl.Vector2(p_col_x, mid_y + 20), self.fonts['xl'].baseSize, 0, glass.TEXT_PRIMARY)
        
        btn_p_minus = rl.Rectangle(p_col_x, mid_y + 102, 38, 38)
        btn_p_plus  = rl.Rectangle(p_col_x + 46, mid_y + 102, 38, 38)
        glass.draw_circular_button(p_col_x + 19, mid_y + 121, 19)
        glass.draw_circular_button(p_col_x + 65, mid_y + 121, 19)
        self._draw_text_centered(self.fonts['blg'], "-", p_col_x + 19, mid_y + 119, glass.TEXT_PRIMARY)
        self._draw_text_centered(self.fonts['blg'], "+", p_col_x + 65, mid_y + 119, glass.TEXT_PRIMARY)
        
        if clicked:
            if rl.check_collision_point_rec(mouse, btn_d_minus): state.driver_temp_f = max(60, state.driver_temp_f - 1)
            elif rl.check_collision_point_rec(mouse, btn_d_plus): state.driver_temp_f = min(85, state.driver_temp_f + 1)
            elif rl.check_collision_point_rec(mouse, btn_p_minus): state.pass_temp_f = max(60, p_temp - 1)
            elif rl.check_collision_point_rec(mouse, btn_p_plus): state.pass_temp_f = min(85, p_temp + 1)
            elif rl.check_collision_point_rec(mouse, rect_clim) and mouse.y < mid_y + 90:
                state.infotainment_app = 3

        # ── 4. VEHICLE SYSTEM Card (Sleek EV Silhouette & TPMS) ───────────────
        rect_veh = rl.Rectangle(cx + card_w1 + gap, cy + card_h + gap, card_w2, card_h)
        self._draw_card(rect_veh.x, rect_veh.y, rect_veh.width, rect_veh.height)
        
        self._draw_icon("car_white.png", rect_veh.x + 22, rect_veh.y + 18, 16, glass.TEXT_MUTED)
        rl.draw_text_ex(self.fonts['xs'], "VEHICLE SYSTEM", rl.Vector2(rect_veh.x + 44, rect_veh.y + 18), self.fonts['xs'].baseSize, 0, glass.TEXT_MUTED)
        
        rl.draw_circle(int(rect_veh.x + card_w2 - 106), int(rect_veh.y + 26), 4, glass.COMMA_GREEN)
        rl.draw_text_ex(self.fonts['xs'], "All Systems OK", rl.Vector2(rect_veh.x + card_w2 - 96, rect_veh.y + 18), self.fonts['xs'].baseSize, 0, glass.COMMA_GREEN)
        
        # Telemetry info
        vx = rect_veh.x + 22
        car_name = str(getattr(state, 'car_profile', "toyota")).capitalize()
        rl.draw_text_ex(self.fonts['blg'], f"{car_name} Camry", rl.Vector2(vx, rect_veh.y + 44), self.fonts['blg'].baseSize, 0, glass.TEXT_PRIMARY)
        rl.draw_text_ex(self.fonts['sm'], "openpilot 0.9.7 · Comma 3X Engaged", rl.Vector2(vx, rect_veh.y + 90), self.fonts['sm'].baseSize, 0, glass.COMMA_GREEN)
        rl.draw_text_ex(self.fonts['xs'], "CAN Bus: ISO 15765-4 (500 kbps) · 60 PIDs", rl.Vector2(vx, rect_veh.y + 118), self.fonts['xs'].baseSize, 0, glass.TEXT_SECONDARY)
        rl.draw_text_ex(self.fonts['xs'], "TPMS: All Sensors Calibrated & Nominal", rl.Vector2(vx, rect_veh.y + 138), self.fonts['xs'].baseSize, 0, glass.SKY_BLUE)

        # Vector Car Silhouette & 4 TPMS capsules (No overlap, generous margins)
        car_cx = rect_veh.x + card_w2 - 124
        car_cy = rect_veh.y + 104
        glass.draw_car_silhouette_topdown(car_cx, car_cy, length=94, width=44)
        
        tire_w, tire_h = 82, 26
        fl_rect = rl.Rectangle(car_cx - 22 - 10 - tire_w, car_cy - 36, tire_w, tire_h)
        fr_rect = rl.Rectangle(car_cx + 22 + 10, car_cy - 36, tire_w, tire_h)
        rl_rect = rl.Rectangle(car_cx - 22 - 10 - tire_w, car_cy + 12, tire_w, tire_h)
        rr_rect = rl.Rectangle(car_cx + 22 + 10, car_cy + 12, tire_w, tire_h)
        for r, tag, psi in [(fl_rect, "FL", "35"), (fr_rect, "FR", "35"), (rl_rect, "RL", "34"), (rr_rect, "RR", "35")]:
            glass.draw_glass_pill(r, roundness=0.35, bg=rl.Color(16, 28, 22, 220), border=rl.Color(46, 213, 115, 140))
            rl.draw_text_ex(self.fonts['xs'], tag, rl.Vector2(r.x + 8, r.y + 6), self.fonts['xs'].baseSize, 0, glass.TEXT_MUTED)
            rl.draw_text_ex(self.fonts['sm'], f"{psi} PSI", rl.Vector2(r.x + 30, r.y + 2), self.fonts['sm'].baseSize, 0, glass.COMMA_GREEN)

        # Vehicle Vitals: Battery & Fuel
        v_bot_y = rect_veh.y + card_h - 38
        self._draw_icon("zap_white.png", rect_veh.x + 22, v_bot_y + 2, 16, glass.AMBER_WARM)
        rl.draw_text_ex(self.fonts['sm'], "14.2V", rl.Vector2(rect_veh.x + 44, v_bot_y), self.fonts['sm'].baseSize, 0, glass.TEXT_PRIMARY)
        
        fuel_pct = int(getattr(state, 'fuel_level', 0.82) * 100)
        self._draw_icon("fuel_white.png", rect_veh.x + 120, v_bot_y + 2, 16, glass.TEXT_PRIMARY)
        rl.draw_text_ex(self.fonts['sm'], f"{fuel_pct}% (340 MI)", rl.Vector2(rect_veh.x + 142, v_bot_y), self.fonts['sm'].baseSize, 0, glass.TEXT_PRIMARY)

        rl.draw_text_ex(self.fonts['xs'], "ODO: 18,420 MI", rl.Vector2(rect_veh.x + card_w2 - 120, v_bot_y + 2), self.fonts['xs'].baseSize, 0, glass.TEXT_MUTED)

        if clicked and rl.check_collision_point_rec(mouse, rect_veh):
            state.infotainment_app = 5

    # ════════════════════════════════════════════════════════════════════════════
    # 2. MUSIC APP SCREEN - Glass Player & Frosted Queue
    # ════════════════════════════════════════════════════════════════════════════
    def _render_music(self, state, cx, cy, cw, ch, mouse, clicked):
        col_gap = 20
        left_w = int((cw - col_gap) * 0.58)
        right_w = cw - col_gap - left_w
        
        # Player Glass Card
        self._draw_card(cx, cy, left_w, ch)
        
        px = cx + 24
        py = cy + 24
        
        art_size = 190
        art_keys = ["the_midnight.jpg", "tycho.jpg", "bonobo.jpg"]
        art_idx = getattr(state, 'music_track', 0) % len(art_keys)
        art_tex = self.album_arts.get(art_keys[art_idx])
        
        rl.draw_rectangle_rounded(rl.Rectangle(px - 4, py - 2, art_size + 8, art_size + 10), 0.18, 16, glass.SHADOW_CORE)
        if art_tex and art_tex.id > 0:
            scale = art_size / max(art_tex.width, 1)
            rl.draw_texture_ex(art_tex, rl.Vector2(px, py), 0.0, scale, rl.WHITE)
            rl.draw_rectangle_rounded_lines_ex(rl.Rectangle(px, py, art_size, art_size), 0.18, 16, 1.2, glass.GLASS_BORDER)
            
        meta_x = px + art_size + 24
        badge_sp = rl.Rectangle(meta_x, py + 4, 170, 24)
        glass.draw_glass_pill(badge_sp, roundness=0.5, active=True)
        rl.draw_text_ex(self.fonts['xs'], "NOW PLAYING · SPOTIFY", rl.Vector2(meta_x + 12, py + 8), self.fonts['xs'].baseSize, 0, glass.OBSIDIAN_BG)
        
        rl.draw_text_ex(self.fonts['blg'], getattr(state, 'music_title', "Los Angeles"), rl.Vector2(meta_x, py + 38), self.fonts['blg'].baseSize, 0, glass.TEXT_PRIMARY)
        rl.draw_text_ex(self.fonts['bmd'], getattr(state, 'music_artist', "The Midnight"), rl.Vector2(meta_x, py + 92), self.fonts['bmd'].baseSize, 0, glass.TEXT_SECONDARY)
        rl.draw_text_ex(self.fonts['xs'], "Master Quality · 96kHz 24-bit Lossless", rl.Vector2(meta_x, py + 132), self.fonts['xs'].baseSize, 0, glass.SKY_BLUE)
        
        # Audio badges
        badge_row_y = py + 158
        b1_r = rl.Rectangle(meta_x, badge_row_y, 106, 24)
        b2_r = rl.Rectangle(meta_x + 114, badge_row_y, 116, 24)
        glass.draw_glass_pill(b1_r, roundness=0.5)
        rl.draw_text_ex(self.fonts['xs'], "DOLBY ATMOS", rl.Vector2(b1_r.x + 12, badge_row_y + 4), self.fonts['xs'].baseSize, 0, glass.TEXT_PRIMARY)
        glass.draw_glass_pill(b2_r, roundness=0.5, active=True)
        rl.draw_text_ex(self.fonts['xs'], "IMMERSIVE 3D", rl.Vector2(b2_r.x + 16, badge_row_y + 4), self.fonts['xs'].baseSize, 0, glass.OBSIDIAN_BG)
        
        # Scrubber
        bar_y = py + art_size + 34
        bar_w = left_w - 48
        bar_rect = rl.Rectangle(px, bar_y - 10, bar_w, 28)
        if clicked and rl.check_collision_point_rec(mouse, bar_rect):
            state.music_progress = max(0.0, min(1.0, (mouse.x - px) / bar_w))
            
        rl.draw_rectangle_rounded(rl.Rectangle(px, bar_y, bar_w, 8), 1.0, 16, rl.Color(32, 36, 48, 255))
        prog_w = int(bar_w * getattr(state, 'music_progress', 0.38))
        rl.draw_rectangle_rounded(rl.Rectangle(px, bar_y, prog_w, 8), 1.0, 16, glass.COMMA_GREEN)
        rl.draw_circle(int(px + prog_w), int(bar_y + 4), 9, glass.TEXT_PRIMARY)
        rl.draw_circle(int(px + prog_w), int(bar_y + 4), 14, glass.COMMA_GREEN_GLOW)
        
        total_sec = 225
        curr_sec = int(getattr(state, 'music_progress', 0.38) * total_sec)
        t_curr = f"{curr_sec // 60}:{curr_sec % 60:02d}"
        t_rem = f"-{(total_sec - curr_sec) // 60}:{(total_sec - curr_sec) % 60:02d}"
        rl.draw_text_ex(self.fonts['sm'], t_curr, rl.Vector2(px, bar_y + 14), self.fonts['sm'].baseSize, 0, glass.TEXT_MUTED)
        ts_rem = rl.measure_text_ex(self.fonts['sm'], t_rem, self.fonts['sm'].baseSize, 0)
        rl.draw_text_ex(self.fonts['sm'], t_rem, rl.Vector2(px + bar_w - ts_rem.x, bar_y + 14), self.fonts['sm'].baseSize, 0, glass.TEXT_MUTED)
        
        # Floating Circular Transport Controls
        btn_y = bar_y + 54
        btn_cx = px + bar_w / 2
        
        glass.draw_circular_button(btn_cx - 100, btn_y + 32, 28, bg=rl.Color(26, 30, 42, 240))
        self._draw_icon_centered("skip-back_white.png", btn_cx - 100, btn_y + 32, 26, glass.TEXT_PRIMARY)
        
        is_playing = getattr(state, 'music_playing', True)
        play_hero_col = glass.COMMA_GREEN if not is_playing else rl.Color(250, 250, 250, 255)
        glass.draw_circular_button(btn_cx, btn_y + 32, 36, bg=play_hero_col, glow=glass.COMMA_GREEN_GLOW)
        hero_icon = "pause_dark.png" if is_playing else "play_dark.png"
        self._draw_icon_centered(hero_icon, btn_cx, btn_y + 32, 32, glass.OBSIDIAN_BG)
        
        glass.draw_circular_button(btn_cx + 100, btn_y + 32, 28, bg=rl.Color(26, 30, 42, 240))
        self._draw_icon_centered("skip-forward_white.png", btn_cx + 100, btn_y + 32, 26, glass.TEXT_PRIMARY)
        
        # Volume Control Strip
        vol_y = btn_y + 88
        self._draw_icon("volume-2_white.png", px + 14, vol_y - 2, 22, glass.TEXT_PRIMARY)
        rl.draw_text_ex(self.fonts['xs'], f"VOLUME {self.master_volume}%", rl.Vector2(px + 44, vol_y + 2), self.fonts['xs'].baseSize, 0, glass.TEXT_MUTED)
        
        btn_vol_m_cx = px + 176
        btn_vol_p_cx = px + bar_w - 40
        glass.draw_circular_button(btn_vol_m_cx, vol_y + 10, 18)
        glass.draw_circular_button(btn_vol_p_cx, vol_y + 10, 18)
        self._draw_text_centered(self.fonts['blg'], "-", btn_vol_m_cx, vol_y + 8, glass.TEXT_PRIMARY)
        self._draw_text_centered(self.fonts['blg'], "+", btn_vol_p_cx, vol_y + 8, glass.TEXT_PRIMARY)
        
        vol_bar_x = px + 208
        vol_bar_w = bar_w - 270
        rl.draw_rectangle_rounded(rl.Rectangle(vol_bar_x, vol_y + 6, vol_bar_w, 8), 1.0, 16, rl.Color(32, 36, 48, 255))
        v_fill = int(vol_bar_w * (self.master_volume / 100.0))
        rl.draw_rectangle_rounded(rl.Rectangle(vol_bar_x, vol_y + 6, v_fill, 8), 1.0, 16, glass.TEXT_PRIMARY)
        rl.draw_circle(int(vol_bar_x + v_fill), int(vol_y + 10), 9, glass.TEXT_PRIMARY)

        # Mode Buttons & Animated Spectrum
        mode_y = vol_y + 48
        shuf_r = rl.Rectangle(px, mode_y, 114, 34)
        rep_r  = rl.Rectangle(px + 126, mode_y, 114, 34)
        bass_r = rl.Rectangle(px + 252, mode_y, 114, 34)
        
        glass.draw_glass_pill(shuf_r, roundness=0.4, active=True)
        self._draw_text_centered(self.fonts['xs'], "SHUFFLE ON", shuf_r.x + shuf_r.width / 2, mode_y + 17, glass.OBSIDIAN_BG)
        glass.draw_glass_pill(rep_r, roundness=0.4)
        self._draw_text_centered(self.fonts['xs'], "REPEAT ALL", rep_r.x + rep_r.width / 2, mode_y + 17, glass.TEXT_PRIMARY)
        glass.draw_glass_pill(bass_r, roundness=0.4)
        self._draw_text_centered(self.fonts['xs'], "BASS BOOST", bass_r.x + bass_r.width / 2, mode_y + 17, glass.TEXT_PRIMARY)
        
        # 12-bar animated graphic equalizer
        spec_x = px + bar_w - 170
        spec_base_y = mode_y + 34
        now_time = time.time() * 9
        spec_heights = [12, 22, 34, 18, 28, 38, 24, 30, 16, 26, 32, 14]
        for s_i, s_h in enumerate(spec_heights):
            h_live = int(s_h * (0.4 + 0.6 * abs(((now_time + s_i * 0.9) % 2) - 1)))
            glass.draw_glass_pill(rl.Rectangle(spec_x + s_i * 14, spec_base_y - h_live, 7, h_live), roundness=0.5, bg=glass.COMMA_GREEN, border=glass.COMMA_GREEN)

        # ── Up Next Queue Card ────────────────────────────────────────────────
        q_x = cx + left_w + col_gap
        self._draw_card(q_x, cy, right_w, ch)
        
        rl.draw_text_ex(self.fonts['xs'], "UP NEXT IN QUEUE", rl.Vector2(q_x + 22, cy + 20), self.fonts['xs'].baseSize, 0, glass.TEXT_MUTED)
        
        for idx, (artist, title) in enumerate(_TRACKS):
            item_y = cy + 54 + idx * 76
            item_rect = rl.Rectangle(q_x + 14, item_y, right_w - 28, 64)
            is_cur = (idx == getattr(state, 'music_track', 0))
            
            if is_cur:
                glass.draw_glass_pill(item_rect, roundness=0.28, bg=rl.Color(26, 38, 32, 230), border=glass.COMMA_GREEN, active=True)
            else:
                glass.draw_glass_pill(item_rect, roundness=0.28, bg=rl.Color(22, 25, 34, 180), border=glass.GLASS_BORDER)
                    
            if clicked and rl.check_collision_point_rec(mouse, item_rect):
                state.music_track = idx
                state.music_artist, state.music_title = _TRACKS[idx]
                state.music_progress = 0.0
                
            track_num = f"{idx + 1}"
            rl.draw_text_ex(self.fonts['bmd'], track_num, rl.Vector2(item_rect.x + 16, item_rect.y + 20), self.fonts['bmd'].baseSize, 0, glass.COMMA_GREEN if is_cur else glass.TEXT_MUTED)
            rl.draw_text_ex(self.fonts['bmd'], title, rl.Vector2(item_rect.x + 44, item_rect.y + 10), self.fonts['bmd'].baseSize, 0, glass.TEXT_PRIMARY)
            rl.draw_text_ex(self.fonts['xs'], artist, rl.Vector2(item_rect.x + 44, item_rect.y + 38), self.fonts['xs'].baseSize, 0, glass.TEXT_SECONDARY)
            
            dur = ["3:45", "4:12", "3:58", "4:30", "3:15", "4:18", "5:27"][idx % 7]
            rl.draw_text_ex(self.fonts['xs'], dur, rl.Vector2(item_rect.x + item_rect.width - 48, item_rect.y + 24), self.fonts['xs'].baseSize, 0, glass.TEXT_MUTED)
        
        if clicked:
            btn_prev_r = rl.Rectangle(btn_cx - 128, btn_y + 4, 56, 56)
            btn_play_r = rl.Rectangle(btn_cx - 36, btn_y - 4, 72, 72)
            btn_next_r = rl.Rectangle(btn_cx + 72, btn_y + 4, 56, 56)
            btn_vm_r   = rl.Rectangle(btn_vol_m_cx - 18, vol_y - 8, 36, 36)
            btn_vp_r   = rl.Rectangle(btn_vol_p_cx - 18, vol_y - 8, 36, 36)
            if rl.check_collision_point_rec(mouse, btn_prev_r):
                state.music_track = (state.music_track - 1) % len(_TRACKS)
                state.music_artist, state.music_title = _TRACKS[state.music_track]
                state.music_progress = 0.0
            elif rl.check_collision_point_rec(mouse, btn_play_r):
                state.music_playing = not state.music_playing
            elif rl.check_collision_point_rec(mouse, btn_next_r):
                state.music_track = (state.music_track + 1) % len(_TRACKS)
                state.music_artist, state.music_title = _TRACKS[state.music_track]
                state.music_progress = 0.0
            elif rl.check_collision_point_rec(mouse, btn_vm_r):
                self.master_volume = max(0, self.master_volume - 5)
            elif rl.check_collision_point_rec(mouse, btn_vp_r):
                self.master_volume = min(100, self.master_volume + 5)

    # ════════════════════════════════════════════════════════════════════════════
    # 3. CLIMATE APP SCREEN - Glass Dual Pods, Airflow & Steppers
    # ════════════════════════════════════════════════════════════════════════════
    def _render_climate(self, state, cx, cy, cw, ch, mouse, clicked):
        gap = 16
        top_card_h = ch - 150
        card_w = (cw - gap) // 2
        
        # ── Driver Glass Pod ──────────────────────────────────────────────────
        self._draw_card(cx, cy, card_w, top_card_h)
        self._draw_icon("thermometer_white.png", cx + 22, cy + 18, 18, glass.TEXT_MUTED)
        rl.draw_text_ex(self.fonts['sm'], "DRIVER CLIMATE ZONE", rl.Vector2(cx + 46, cy + 18), self.fonts['sm'].baseSize, 0, glass.TEXT_MUTED)
        
        # Temp Hero & Circular Steppers
        center_x = cx + card_w / 2
        temp_y = cy + 76
        temp_txt = f"{int(state.driver_temp_f)}°"
        t_size = rl.measure_text_ex(self.fonts['bxl'], temp_txt, self.fonts['bxl'].baseSize, 0)
        
        minus_d_cx = center_x - t_size.x / 2 - 50
        plus_d_cx  = center_x + t_size.x / 2 + 50
        glass.draw_circular_button(minus_d_cx, temp_y + 24, 26)
        glass.draw_circular_button(plus_d_cx, temp_y + 24, 26)
        self._draw_text_centered(self.fonts['blg'], "-", minus_d_cx, temp_y + 22, glass.TEXT_PRIMARY)
        self._draw_text_centered(self.fonts['blg'], "+", plus_d_cx, temp_y + 22, glass.TEXT_PRIMARY)
        
        rl.draw_text_ex(self.fonts['bxl'], temp_txt, rl.Vector2(center_x - t_size.x / 2, temp_y - 16), self.fonts['bxl'].baseSize, 0, glass.TEXT_PRIMARY)
        
        # Airflow Direction Routing
        af_y = temp_y + 86
        rl.draw_text_ex(self.fonts['xs'], "AIRFLOW DISTRIBUTION", rl.Vector2(cx + 22, af_y), self.fonts['xs'].baseSize, 0, glass.TEXT_MUTED)
        
        af_labels = ["WINDSHIELD", "DASH VENTS", "FOOTWELL"]
        af_btn_w = (card_w - 44 - 12 * 2) // 3
        for af_i, af_lbl in enumerate(af_labels):
            af_x = cx + 22 + af_i * (af_btn_w + 12)
            af_rect = rl.Rectangle(af_x, af_y + 22, af_btn_w, 44)
            is_af_on = self.driver_airflow[af_i]
            
            if clicked and rl.check_collision_point_rec(mouse, af_rect):
                self.driver_airflow[af_i] = not self.driver_airflow[af_i]
                
            glass.draw_glass_pill(af_rect, roundness=0.35, active=is_af_on, solid=is_af_on)
            self._draw_text_centered(self.fonts['xs'], af_lbl, af_x + af_btn_w / 2, af_y + 44, glass.OBSIDIAN_BG if is_af_on else glass.TEXT_PRIMARY)

        # 3-Stage Heated Seat Control
        heat_y = af_y + 78
        heat_box_w = card_w - 44
        heat_rect = rl.Rectangle(cx + 22, heat_y, heat_box_w, 48)
        glass.draw_glass_pill(heat_rect, roundness=0.32, bg=rl.Color(24, 28, 38, 220))
        
        self._draw_icon("thermometer_white.png", cx + 38, heat_y + 14, 20, glass.AMBER_WARM if self.driver_seat_heat > 0 else glass.TEXT_MUTED)
        rl.draw_text_ex(self.fonts['sm'], "SEAT HEATER", rl.Vector2(cx + 68, heat_y + 14), self.fonts['sm'].baseSize, 0, glass.TEXT_PRIMARY)
        
        for led_i in range(3):
            lx = cx + heat_box_w - 60 + led_i * 20
            l_rect = rl.Rectangle(lx, heat_y + 15, 14, 18)
            is_lit = (led_i < self.driver_seat_heat)
            glass.draw_glass_pill(l_rect, roundness=0.3, bg=glass.AMBER_WARM if is_lit else rl.Color(40, 44, 56, 255), active=is_lit, solid=is_lit)
            
        if clicked and rl.check_collision_point_rec(mouse, heat_rect):
            self.driver_seat_heat = (self.driver_seat_heat + 1) % 4
            state.heated_seats = (self.driver_seat_heat > 0)

        # 3-Stage Seat Cooling
        cool_y = heat_y + 56
        cool_rect = rl.Rectangle(cx + 22, cool_y, heat_box_w, 48)
        glass.draw_glass_pill(cool_rect, roundness=0.32, bg=rl.Color(24, 28, 38, 220))
        self._draw_icon("fan_white.png", cx + 38, cool_y + 14, 20, glass.CYAN_COOL if self.driver_seat_cool > 0 else glass.TEXT_MUTED)
        rl.draw_text_ex(self.fonts['sm'], "SEAT VENTILATION", rl.Vector2(cx + 68, cool_y + 14), self.fonts['sm'].baseSize, 0, glass.TEXT_PRIMARY)
        for led_i in range(3):
            lx = cx + heat_box_w - 60 + led_i * 20
            l_rect = rl.Rectangle(lx, cool_y + 15, 14, 18)
            is_lit = (led_i < self.driver_seat_cool)
            glass.draw_glass_pill(l_rect, roundness=0.3, bg=glass.CYAN_COOL if is_lit else rl.Color(40, 44, 56, 255), active=is_lit, solid=is_lit)
            
        if clicked and rl.check_collision_point_rec(mouse, cool_rect):
            self.driver_seat_cool = (self.driver_seat_cool + 1) % 4

        # Air Recirc & Purify
        pur_y = cool_y + 56
        half_btn_w = (heat_box_w - 12) // 2
        btn_recirc = rl.Rectangle(cx + 22, pur_y, half_btn_w, 42)
        btn_purify = rl.Rectangle(cx + 22 + half_btn_w + 12, pur_y, half_btn_w, 42)
        
        glass.draw_glass_pill(btn_recirc, roundness=0.35, active=self.recirc_mode, solid=self.recirc_mode)
        self._draw_text_centered(self.fonts['xs'], "AIR RECIRC: ON" if self.recirc_mode else "FRESH AIR", btn_recirc.x + half_btn_w/2, pur_y + 21, glass.OBSIDIAN_BG if self.recirc_mode else glass.TEXT_PRIMARY)
        
        glass.draw_glass_pill(btn_purify, roundness=0.35, active=self.air_purify, solid=self.air_purify)
        self._draw_text_centered(self.fonts['xs'], "HEPA PURIFY: ON" if self.air_purify else "HEPA PURIFY: OFF", btn_purify.x + half_btn_w/2, pur_y + 21, glass.OBSIDIAN_BG if self.air_purify else glass.TEXT_PRIMARY)
        
        if clicked:
            if rl.check_collision_point_rec(mouse, btn_recirc): self.recirc_mode = not self.recirc_mode
            elif rl.check_collision_point_rec(mouse, btn_purify): self.air_purify = not self.air_purify

        # ── Passenger Glass Pod ───────────────────────────────────────────────
        pass_card_x = cx + card_w + gap
        self._draw_card(pass_card_x, cy, card_w, top_card_h)
        self._draw_icon("thermometer_white.png", pass_card_x + 22, cy + 18, 18, glass.TEXT_MUTED)
        rl.draw_text_ex(self.fonts['sm'], "PASSENGER CLIMATE ZONE", rl.Vector2(pass_card_x + 46, cy + 18), self.fonts['sm'].baseSize, 0, glass.TEXT_MUTED)
        
        p_center_x = pass_card_x + card_w / 2
        p_temp = int(getattr(state, 'pass_temp_f', 70))
        temp_txt_p = f"{p_temp}°"
        t_size_p = rl.measure_text_ex(self.fonts['bxl'], temp_txt_p, self.fonts['bxl'].baseSize, 0)
        
        minus_p_cx = p_center_x - t_size_p.x / 2 - 50
        plus_p_cx  = p_center_x + t_size_p.x / 2 + 50
        glass.draw_circular_button(minus_p_cx, temp_y + 24, 26)
        glass.draw_circular_button(plus_p_cx, temp_y + 24, 26)
        self._draw_text_centered(self.fonts['blg'], "-", minus_p_cx, temp_y + 22, glass.TEXT_PRIMARY)
        self._draw_text_centered(self.fonts['blg'], "+", plus_p_cx, temp_y + 22, glass.TEXT_PRIMARY)
        
        rl.draw_text_ex(self.fonts['bxl'], temp_txt_p, rl.Vector2(p_center_x - t_size_p.x / 2, temp_y - 16), self.fonts['bxl'].baseSize, 0, glass.TEXT_PRIMARY)
        
        # Airflow
        rl.draw_text_ex(self.fonts['xs'], "AIRFLOW DISTRIBUTION", rl.Vector2(pass_card_x + 22, af_y), self.fonts['xs'].baseSize, 0, glass.TEXT_MUTED)
        for af_i, af_lbl in enumerate(af_labels):
            af_x = pass_card_x + 22 + af_i * (af_btn_w + 12)
            af_rect = rl.Rectangle(af_x, af_y + 22, af_btn_w, 44)
            is_af_on = self.pass_airflow[af_i]
            
            if clicked and rl.check_collision_point_rec(mouse, af_rect):
                self.pass_airflow[af_i] = not self.pass_airflow[af_i]
                
            glass.draw_glass_pill(af_rect, roundness=0.35, active=is_af_on, solid=is_af_on)
            self._draw_text_centered(self.fonts['xs'], af_lbl, af_x + af_btn_w / 2, af_y + 44, glass.OBSIDIAN_BG if is_af_on else glass.TEXT_PRIMARY)

        # Passenger Heated Seat
        heat_rect_p = rl.Rectangle(pass_card_x + 22, heat_y, heat_box_w, 48)
        glass.draw_glass_pill(heat_rect_p, roundness=0.32, bg=rl.Color(24, 28, 38, 220))
        self._draw_icon("thermometer_white.png", pass_card_x + 38, heat_y + 14, 20, glass.AMBER_WARM if self.pass_seat_heat > 0 else glass.TEXT_MUTED)
        rl.draw_text_ex(self.fonts['sm'], "SEAT HEATER", rl.Vector2(pass_card_x + 68, heat_y + 14), self.fonts['sm'].baseSize, 0, glass.TEXT_PRIMARY)
        for led_i in range(3):
            lx = pass_card_x + heat_box_w - 60 + led_i * 20
            l_rect = rl.Rectangle(lx, heat_y + 15, 14, 18)
            is_lit = (led_i < self.pass_seat_heat)
            glass.draw_glass_pill(l_rect, roundness=0.3, bg=glass.AMBER_WARM if is_lit else rl.Color(40, 44, 56, 255), active=is_lit, solid=is_lit)
            
        if clicked and rl.check_collision_point_rec(mouse, heat_rect_p):
            self.pass_seat_heat = (self.pass_seat_heat + 1) % 4

        # Passenger Cooled Seat
        cool_rect_p = rl.Rectangle(pass_card_x + 22, cool_y, heat_box_w, 48)
        glass.draw_glass_pill(cool_rect_p, roundness=0.32, bg=rl.Color(24, 28, 38, 220))
        self._draw_icon("fan_white.png", pass_card_x + 38, cool_y + 14, 20, glass.CYAN_COOL if self.pass_seat_cool > 0 else glass.TEXT_MUTED)
        rl.draw_text_ex(self.fonts['sm'], "SEAT VENTILATION", rl.Vector2(pass_card_x + 68, cool_y + 14), self.fonts['sm'].baseSize, 0, glass.TEXT_PRIMARY)
        for led_i in range(3):
            lx = pass_card_x + heat_box_w - 60 + led_i * 20
            l_rect = rl.Rectangle(lx, cool_y + 15, 14, 18)
            is_lit = (led_i < self.pass_seat_cool)
            glass.draw_glass_pill(l_rect, roundness=0.3, bg=glass.CYAN_COOL if is_lit else rl.Color(40, 44, 56, 255), active=is_lit, solid=is_lit)
            
        if clicked and rl.check_collision_point_rec(mouse, cool_rect_p):
            self.pass_seat_cool = (self.pass_seat_cool + 1) % 4

        # Sync & Rear
        btn_sync = rl.Rectangle(pass_card_x + 22, pur_y, half_btn_w, 42)
        btn_rear = rl.Rectangle(pass_card_x + 22 + half_btn_w + 12, pur_y, half_btn_w, 42)
        
        glass.draw_glass_pill(btn_sync, roundness=0.35, active=self.sync_mode, solid=self.sync_mode)
        self._draw_text_centered(self.fonts['xs'], "SYNC DUAL: ON" if self.sync_mode else "SYNC DUAL: OFF", btn_sync.x + half_btn_w/2, pur_y + 21, glass.OBSIDIAN_BG if self.sync_mode else glass.TEXT_PRIMARY)
        
        glass.draw_glass_pill(btn_rear, roundness=0.35, active=True, solid=True)
        self._draw_text_centered(self.fonts['xs'], "REAR CABIN: AUTO", btn_rear.x + half_btn_w/2, pur_y + 21, glass.OBSIDIAN_BG)
        
        if clicked and rl.check_collision_point_rec(mouse, btn_sync):
            self.sync_mode = not self.sync_mode
            if self.sync_mode:
                state.pass_temp_f = state.driver_temp_f

        if clicked:
            btn_md_r = rl.Rectangle(minus_d_cx - 26, temp_y - 2, 52, 52)
            btn_pd_r = rl.Rectangle(plus_d_cx - 26, temp_y - 2, 52, 52)
            btn_mp_r = rl.Rectangle(minus_p_cx - 26, temp_y - 2, 52, 52)
            btn_pp_r = rl.Rectangle(plus_p_cx - 26, temp_y - 2, 52, 52)
            if rl.check_collision_point_rec(mouse, btn_md_r): state.driver_temp_f = max(60, state.driver_temp_f - 1)
            elif rl.check_collision_point_rec(mouse, btn_pd_r): state.driver_temp_f = min(85, state.driver_temp_f + 1)
            elif rl.check_collision_point_rec(mouse, btn_mp_r): state.pass_temp_f = max(60, p_temp - 1)
            elif rl.check_collision_point_rec(mouse, btn_pp_r): state.pass_temp_f = min(85, p_temp + 1)

        # ── Fan Speed Strip ───────────────────────────────────────────────────
        fan_strip_y = cy + top_card_h + 10
        fan_strip_w = cw
        glass.draw_glass_card(rl.Rectangle(cx, fan_strip_y, fan_strip_w, 42), roundness=0.35)
        
        self._draw_icon("fan_white.png", cx + 20, fan_strip_y + 11, 20, glass.TEXT_PRIMARY)
        rl.draw_text_ex(self.fonts['xs'], "BLOWER SPEED", rl.Vector2(cx + 48, fan_strip_y + 13), self.fonts['xs'].baseSize, 0, glass.TEXT_MUTED)
        
        btn_fan_m_cx = cx + 160
        btn_fan_p_cx = cx + fan_strip_w - 40
        glass.draw_circular_button(btn_fan_m_cx, fan_strip_y + 21, 15)
        glass.draw_circular_button(btn_fan_p_cx, fan_strip_y + 21, 15)
        self._draw_text_centered(self.fonts['md'], "-", btn_fan_m_cx, fan_strip_y + 19, glass.TEXT_PRIMARY)
        self._draw_text_centered(self.fonts['md'], "+", btn_fan_p_cx, fan_strip_y + 19, glass.TEXT_PRIMARY)
        
        fan_cur = getattr(state, 'fan_level', 3)
        seg_start_x = cx + 190
        seg_w = (fan_strip_w - 250) / 7
        for s in range(7):
            sx = seg_start_x + s * seg_w
            s_rect = rl.Rectangle(sx + 3, fan_strip_y + 12, seg_w - 6, 18)
            glass.draw_glass_pill(s_rect, roundness=0.25, active=(s < fan_cur), solid=(s < fan_cur))
            if clicked and rl.check_collision_point_rec(mouse, s_rect):
                state.fan_level = s + 1
                
        if clicked:
            if rl.check_collision_point_rec(mouse, rl.Rectangle(btn_fan_m_cx - 15, fan_strip_y + 6, 30, 30)): state.fan_level = max(1, fan_cur - 1)
            elif rl.check_collision_point_rec(mouse, rl.Rectangle(btn_fan_p_cx - 15, fan_strip_y + 6, 30, 30)): state.fan_level = min(7, fan_cur + 1)

        # ── Mode Bar ──────────────────────────────────────────────────────────
        mode_y = fan_strip_y + 48
        mode_labels = ["AUTO", "A/C", "HEAT", "DEFROST", "REAR DEF", "SYNC"]
        pill_w = (cw - (len(mode_labels) - 1) * 12) // len(mode_labels)
        
        for i, lbl in enumerate(mode_labels):
            m_px = cx + i * (pill_w + 12)
            pill_rect = rl.Rectangle(m_px, mode_y, pill_w, 42)
            
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
                
            glass.draw_glass_pill(pill_rect, roundness=0.35, active=is_on, solid=is_on)
            self._draw_text_centered(self.fonts['bmd'], lbl, m_px + pill_w / 2, mode_y + 21, glass.OBSIDIAN_BG if is_on else glass.TEXT_PRIMARY)

    # ════════════════════════════════════════════════════════════════════════════
    # 4. NAVIGATION APP SCREEN - Glass HUD Overlay & Trip Card
    # ════════════════════════════════════════════════════════════════════════════
    def _render_nav(self, state, cx, cy, cw, ch, mouse, clicked):
        map_w = int(cw * 0.66)
        
        # Dark Map Surface
        map_rect = rl.Rectangle(cx, cy, map_w, ch)
        glass.draw_glass_card(map_rect, roundness=0.35, bg=rl.Color(16, 18, 25, 255))
        
        # Stylized Highway Grid
        rl.draw_line_ex(rl.Vector2(cx + 40, cy + ch * 0.5), rl.Vector2(cx + map_w - 40, cy + ch * 0.5), 16, rl.Color(34, 38, 52, 255))
        rl.draw_line_ex(rl.Vector2(cx + map_w * 0.45, cy + 30), rl.Vector2(cx + map_w * 0.45, cy + ch - 30), 22, glass.COMMA_GREEN)
        rl.draw_line_ex(rl.Vector2(cx + map_w * 0.45, cy + ch * 0.42), rl.Vector2(cx + map_w * 0.8, cy + ch * 0.15), 14, glass.COMMA_GREEN)
        
        veh_pos = rl.Vector2(cx + map_w * 0.45, cy + ch * 0.6)
        rl.draw_circle(int(veh_pos.x), int(veh_pos.y), 16, glass.COMMA_GREEN_GLOW)
        rl.draw_circle(int(veh_pos.x), int(veh_pos.y), 10, glass.COMMA_GREEN)
        rl.draw_circle(int(veh_pos.x), int(veh_pos.y), 4, glass.TEXT_PRIMARY)
        
        # Turn HUD Floating Glass Card
        hud_nav = rl.Rectangle(cx + 20, cy + 20, 320, 100)
        glass.draw_glass_card(hud_nav, roundness=0.35)
        glass.draw_circular_button(hud_nav.x + 38, hud_nav.y + 40, 22, bg=glass.COMMA_GREEN, glow=glass.COMMA_GREEN_GLOW)
        self._draw_icon_centered("arrow-up_white.png", hud_nav.x + 38, hud_nav.y + 40, 24, glass.OBSIDIAN_BG)
        rl.draw_text_ex(self.fonts['blg'], "In 800 ft", rl.Vector2(hud_nav.x + 72, hud_nav.y + 16), self.fonts['blg'].baseSize, 0, glass.TEXT_PRIMARY)
        rl.draw_text_ex(self.fonts['sm'], "Exit 432B · Downtown SF", rl.Vector2(hud_nav.x + 72, hud_nav.y + 58), self.fonts['sm'].baseSize, 0, glass.TEXT_SECONDARY)

        # Right Route Stats Glass Card
        rp_x = cx + map_w + 16
        rp_w = cw - map_w - 16
        self._draw_card(rp_x, cy, rp_w, ch)
        
        rl.draw_text_ex(self.fonts['xs'], "DESTINATION", rl.Vector2(rp_x + 22, cy + 24), self.fonts['xs'].baseSize, 0, glass.TEXT_MUTED)
        dest = getattr(state, 'destination', "San Francisco, CA")
        rl.draw_text_ex(self.fonts['blg'], dest, rl.Vector2(rp_x + 22, cy + 48), self.fonts['blg'].baseSize, 0, glass.TEXT_PRIMARY)
        
        stats = [
            ("Distance Remaining", f"{getattr(state, 'trip_distance_mi', 12.4):.1f} MI"),
            ("Estimated Time", "14 MIN"),
            ("Arrival Time", "5:42 PM"),
            ("Via Route", "US-101 Northbound")
        ]
        for idx, (lbl, val) in enumerate(stats):
            sy = cy + 120 + idx * 56
            s_rect = rl.Rectangle(rp_x + 16, sy, rp_w - 32, 46)
            glass.draw_glass_pill(s_rect, roundness=0.25)
            rl.draw_text_ex(self.fonts['sm'], lbl, rl.Vector2(rp_x + 28, sy + 13), self.fonts['sm'].baseSize, 0, glass.TEXT_SECONDARY)
            rl.draw_text_ex(self.fonts['bmd'], val, rl.Vector2(rp_x + rp_w - 160, sy + 10), self.fonts['bmd'].baseSize, 0, glass.TEXT_PRIMARY)

        btn_end = rl.Rectangle(rp_x + 22, cy + ch - 72, rp_w - 44, 48)
        glass.draw_glass_pill(btn_end, roundness=0.35, bg=glass.CRIMSON_RED, border=glass.CRIMSON_RED)
        self._draw_text_centered(self.fonts['bmd'], "CANCEL ROUTE", btn_end.x + (rp_w - 44) / 2, btn_end.y + 24, glass.TEXT_PRIMARY)

    # ════════════════════════════════════════════════════════════════════════════
    # 5. PHONE APP SCREEN - Frosted Contact Cards & Circular Call Badges
    # ════════════════════════════════════════════════════════════════════════════
    def _render_phone(self, state, cx, cy, cw, ch, mouse, clicked):
        gap = 14
        for i, (name, number) in enumerate(_CONTACTS):
            ry = cy + i * (80 + gap)
            rect = rl.Rectangle(cx, ry, cw, 80)
            self._draw_card(rect.x, rect.y, rect.width, rect.height)
            
            glass.draw_circular_button(cx + 48, ry + 40, 22, bg=rl.Color(26, 32, 45, 255))
            self._draw_icon_centered("phone_white.png", cx + 48, ry + 40, 18, glass.COMMA_GREEN)
            
            rl.draw_text_ex(self.fonts['blg'], name, rl.Vector2(cx + 86, ry + 14), self.fonts['blg'].baseSize, 0, glass.TEXT_PRIMARY)
            rl.draw_text_ex(self.fonts['md'], number, rl.Vector2(cx + 86, ry + 48), self.fonts['md'].baseSize, 0, glass.TEXT_SECONDARY)
            
            call_btn = rl.Rectangle(cx + cw - 120, ry + 20, 96, 40)
            glass.draw_glass_pill(call_btn, roundness=0.5, active=True)
            self._draw_text_centered(self.fonts['bmd'], "CALL", call_btn.x + 48, call_btn.y + 20, glass.OBSIDIAN_BG)

    # ════════════════════════════════════════════════════════════════════════════
    # 6. SETTINGS SCREEN - Frosted System Preference Cards
    # ════════════════════════════════════════════════════════════════════════════
    def _render_settings(self, state, cx, cy, cw, ch, mouse, clicked):
        gap = 12
        for i, lbl in enumerate(_SETTINGS_LABELS):
            ry = cy + i * (68 + gap)
            rect = rl.Rectangle(cx, ry, cw, 68)
            
            if clicked and rl.check_collision_point_rec(mouse, rect):
                self.focused_setting = i
                
            is_foc = (i == self.focused_setting)
            glow = glass.COMMA_GREEN_GLOW if is_foc else None
            brd = glass.COMMA_GREEN if is_foc else glass.GLASS_BORDER
            glass.draw_glass_card(rect, roundness=0.32, border=brd, glow_color=glow)
            
            rl.draw_text_ex(self.fonts['blg'], lbl, rl.Vector2(cx + 28, ry + 16), self.fonts['blg'].baseSize, 0, glass.TEXT_PRIMARY)
            
            val_text = "Standard"
            if lbl == "Vehicle Profile": val_text = str(getattr(state, 'car_profile', 'toyota')).upper()
            elif lbl == "Units": val_text = "Imperial (MPH, °F)"
            elif lbl == "Brightness": val_text = "80%"
            elif lbl == "About OpenCar": val_text = "v2.0-opendbc"
                
            rl.draw_text_ex(self.fonts['md'], val_text, rl.Vector2(cx + cw - 240, ry + 20), self.fonts['md'].baseSize, 0, glass.TEXT_SECONDARY)

    # ════════════════════════════════════════════════════════════════════════════
    # BOTTOM DOCK BAR - Frosted Floating Rail with 1.5px Specular Line
    # ════════════════════════════════════════════════════════════════════════════
    def _render_bottom_bar(self, state, W, H):
        bh = 50
        by = H - bh
        rl.draw_rectangle(0, by, W, bh, rl.Color(12, 14, 18, 240))
        rl.draw_line_ex(rl.Vector2(0, by), rl.Vector2(W, by), 1.5, glass.GLASS_BORDER)
        
        # Left: Speed + Glare-Resistant PRNDL Badge
        speed_int = int(getattr(state, 'speed_mph', 0))
        rl.draw_text_ex(self.fonts['bmd'], f"{speed_int} MPH", rl.Vector2(92, by + 12), self.fonts['bmd'].baseSize, 0, glass.TEXT_PRIMARY)
        
        raw_gear = getattr(state, 'gear', 3)
        gears = ['P', 'R', 'N', 'D']
        gear_str = gears[raw_gear] if isinstance(raw_gear, int) and 0 <= raw_gear < 4 else str(raw_gear).upper()
            
        gear_rect = rl.Rectangle(194, by + 10, 34, 30)
        is_drive = (gear_str == 'D')
        gear_bg = glass.COMMA_GREEN if is_drive else (glass.CRIMSON_RED if gear_str == 'R' else rl.Color(34, 38, 50, 255))
        glass.draw_glass_pill(gear_rect, roundness=0.35, bg=gear_bg)
        self._draw_text_centered(self.fonts['bmd'], gear_str, gear_rect.x + 17, gear_rect.y + 15, glass.OBSIDIAN_BG if is_drive else glass.TEXT_PRIMARY)
        
        # Comma active indicator
        rl.draw_circle(248, by + 25, 4, glass.COMMA_GREEN)
        rl.draw_circle(248, by + 25, 8, glass.COMMA_GREEN_GLOW)
        rl.draw_text_ex(self.fonts['xs'], "comma active", rl.Vector2(260, by + 17), self.fonts['xs'].baseSize, 0, glass.TEXT_PRIMARY)

        # Center: Current Nav maneuver snippet
        nav_info = "Continue on US-101 North · 12.4 MI"
        self._draw_icon("navigation_white.png", W // 2 - 150, by + 16, 16, glass.COMMA_GREEN)
        rl.draw_text_ex(self.fonts['sm'], nav_info, rl.Vector2(W // 2 - 126, by + 15), self.fonts['sm'].baseSize, 0, glass.TEXT_SECONDARY)
        
        # Right: Connectivity Icons + System Clock
        self._draw_icon("bluetooth_white.png", W - 220, by + 16, 18, glass.TEXT_PRIMARY)
        self._draw_icon("signal_white.png", W - 186, by + 16, 18, glass.TEXT_PRIMARY)
        self._draw_icon("wifi_white.png", W - 152, by + 16, 18, glass.TEXT_PRIMARY)
        
        clock = time.strftime("%I:%M %p")
        rl.draw_text_ex(self.fonts['bmd'], clock, rl.Vector2(W - 114, by + 12), self.fonts['bmd'].baseSize, 0, glass.TEXT_PRIMARY)

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

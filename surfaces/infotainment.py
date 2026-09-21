import pyray as rl
import os
import math

_TRACKS = [("The Midnight","Los Angeles"),("Tycho","Awake"),("Bonobo","Kong"),("Polo & Pan","Canop\u00e9e"),("Washed Out","Feel It All Around")]
_CONTACTS = [("Sarah Connor","555-0101"),("John Connor","555-0102"),("Kyle Reese","555-0103"),("Miles Dyson","555-0104")]
_SETTINGS_LABELS = ["Vehicle Profile","Theme","Units","Brightness","About"]

class InfoSurface:
    def __init__(self, fonts: dict):
        self.fonts = fonts
        self.focused_setting = 0
        
        self.icons = {}
        icon_names = [
            "play_white.png", "pause_white.png", "skip-back_white.png", "skip-forward_white.png",
            "home_white.png", "map-pin_white.png", "music_white.png", "snowflake_white.png",
            "phone_white.png", "settings_white.png", "navigation_white.png", "fan_white.png", "thermometer_white.png",
            "shield-check_white.png" # Assuming this might exist
        ]
        for name in icon_names:
            path = f"assets/icons/{name}"
            self.icons[name] = self._safe_load(path)
            
        self.album_arts = {}
        for name in ["the_midnight.jpg", "tycho.jpg", "bonobo.jpg"]:
            path = f"assets/music/{name}"
            self.album_arts[name] = self._safe_load(path)
            
        self.card_bg = rl.Color(41, 41, 41, 255)
        self.pure_black = rl.Color(0, 0, 0, 255)
        self.gray_text = rl.Color(170, 170, 170, 255)
        self.gray_label = rl.Color(128, 128, 128, 255)
        self.white = rl.Color(255, 255, 255, 255)
        self.green = rl.Color(51, 171, 76, 255)
        self.blue = rl.Color(70, 91, 234, 255)
        self.dark_gray = rl.Color(57, 57, 57, 255)

    def _safe_load(self, path):
        if os.path.exists(path):
            return rl.load_texture(path)
        return None

    def render(self, state, theme) -> None:
        W = rl.get_screen_width()
        H = rl.get_screen_height()
        
        rl.clear_background(self.pure_black)
        
        # Sidebar
        rl.draw_rectangle(0, 0, 80, H, self.pure_black)
        
        sidebar_icons = [
            "home_white.png", "map-pin_white.png", "music_white.png", 
            "snowflake_white.png", "phone_white.png", "settings_white.png"
        ]
        
        tab_h = H / 6
        for i, icon_name in enumerate(sidebar_icons):
            y = int(i * tab_h)
            is_active = (state.infotainment_app == i)
            
            if is_active:
                rl.draw_rectangle(0, y, 4, int(tab_h), self.green)
                tint = self.white
            else:
                tint = self.gray_text
                
            tex = self.icons.get(icon_name)
            if tex and tex.id > 0:
                scale = 32.0 / max(tex.width, 1)
                ix = 40 - (tex.width * scale) / 2
                iy = y + tab_h/2 - (tex.height * scale) / 2
                rl.draw_texture_ex(tex, rl.Vector2(ix, iy), 0.0, scale, tint)
                
        # Content Area
        cx = 80
        cy = 0
        cw = W - 80
        ch = H - 60 # leaving 60 for bottom bar
        
        if state.infotainment_app == 0:
            self._render_home(state, cx, cy, cw, ch)
        elif state.infotainment_app == 1:
            self._render_nav(state, cx, cy, cw, ch)
        elif state.infotainment_app == 2:
            self._render_music(state, cx, cy, cw, ch)
        elif state.infotainment_app == 3:
            self._render_climate(state, cx, cy, cw, ch)
        elif state.infotainment_app == 4:
            self._render_phone(state, cx, cy, cw, ch)
        elif state.infotainment_app == 5:
            self._render_settings(state, cx, cy, cw, ch)
            
        # Bottom status bar
        self._render_bottom_bar(state, W, H)

    def _render_home(self, state, cx, cy, cw, ch):
        gap = 16
        card_w1 = int((cw - gap * 3) * 0.55)
        card_w2 = cw - gap * 3 - card_w1
        card_h = (ch - gap * 3) // 2
        
        # NOW PLAYING
        self._draw_card(cx + gap, cy + gap, card_w1, card_h)
        rl.draw_text_ex(self.fonts['xs'], "NOW PLAYING", rl.Vector2(cx + gap + 32, cy + gap + 32), self.fonts['xs'].baseSize, 0, self.gray_label)
        
        art_size = card_h - 64 - 16
        if art_size > 200: art_size = 200
        # Draw album art
        art_keys = ["the_midnight.jpg", "tycho.jpg", "bonobo.jpg"]
        art_idx = state.music_track % len(art_keys)
        art_tex = self.album_arts.get(art_keys[art_idx])
        art_x = cx + gap + 32
        art_y = cy + gap + 60
        if art_tex and art_tex.id > 0:
            scale = art_size / max(art_tex.width, 1)
            rl.draw_texture_ex(art_tex, rl.Vector2(art_x, art_y), 0.0, scale, rl.WHITE)
        
        title_x = cx + gap + 32 + art_size + 32
        title_y = cy + gap + 32 + 32
        rl.draw_text_ex(self.fonts['blg'], state.music_title, rl.Vector2(title_x, title_y), self.fonts['blg'].baseSize, 0, self.white)
        rl.draw_text_ex(self.fonts['md'], state.music_artist, rl.Vector2(title_x, title_y + 60), self.fonts['md'].baseSize, 0, self.gray_text)
        
        # NAV
        self._draw_card(cx + gap*2 + card_w1, cy + gap, card_w2, card_h)
        rl.draw_text_ex(self.fonts['xs'], "NAVIGATION", rl.Vector2(cx + gap*2 + card_w1 + 32, cy + gap + 32), self.fonts['xs'].baseSize, 0, self.gray_label)
        rl.draw_text_ex(self.fonts['blg'], getattr(state, 'destination', "Downtown"), rl.Vector2(cx + gap*2 + card_w1 + 32, cy + gap + 80), self.fonts['blg'].baseSize, 0, self.white)
        rl.draw_text_ex(self.fonts['md'], "Continue on US-101", rl.Vector2(cx + gap*2 + card_w1 + 32, cy + gap + 140), self.fonts['md'].baseSize, 0, self.gray_text)
        rl.draw_text_ex(self.fonts['sm'], "ETA: 14 min", rl.Vector2(cx + gap*2 + card_w1 + 32, cy + gap + 190), self.fonts['sm'].baseSize, 0, self.green)
        
        # CLIMATE
        self._draw_card(cx + gap, cy + gap*2 + card_h, card_w1, card_h)
        rl.draw_text_ex(self.fonts['xs'], "CLIMATE", rl.Vector2(cx + gap + 32, cy + gap*2 + card_h + 32), self.fonts['xs'].baseSize, 0, self.gray_label)
        rl.draw_text_ex(self.fonts['xl'], f"{int(state.driver_temp_f)}°", rl.Vector2(cx + gap + 32, cy + gap*2 + card_h + 80), self.fonts['xl'].baseSize, 0, self.white)
        
        # VEHICLE
        self._draw_card(cx + gap*2 + card_w1, cy + gap*2 + card_h, card_w2, card_h)
        rl.draw_text_ex(self.fonts['xs'], "VEHICLE", rl.Vector2(cx + gap*2 + card_w1 + 32, cy + gap*2 + card_h + 32), self.fonts['xs'].baseSize, 0, self.gray_label)
        rl.draw_text_ex(self.fonts['blg'], str(state.car_profile).capitalize(), rl.Vector2(cx + gap*2 + card_w1 + 32, cy + gap*2 + card_h + 80), self.fonts['blg'].baseSize, 0, self.white)
        rl.draw_text_ex(self.fonts['md'], "All Systems OK", rl.Vector2(cx + gap*2 + card_w1 + 32, cy + gap*2 + card_h + 140), self.fonts['md'].baseSize, 0, self.green)

    def _render_music(self, state, cx, cy, cw, ch):
        art_size = int(cw * 0.4)
        if art_size > ch - 64: art_size = ch - 64
        
        art_x = cx + 64
        art_y = cy + (ch - art_size) // 2
        
        rl.draw_rectangle_rounded(rl.Rectangle(art_x, art_y, art_size, art_size), 0.1, 32, self.card_bg)
        # Draw album art texture
        art_keys = ["the_midnight.jpg", "tycho.jpg", "bonobo.jpg"]
        art_idx = state.music_track % len(art_keys)
        art_tex = self.album_arts.get(art_keys[art_idx])
        if art_tex and art_tex.id > 0:
            scale = art_size / max(art_tex.width, 1)
            rl.draw_texture_ex(art_tex, rl.Vector2(art_x, art_y), 0.0, scale, rl.WHITE)
        
        info_x = art_x + art_size + 64
        info_y = art_y + 32
        
        rl.draw_text_ex(self.fonts['xl'], state.music_title, rl.Vector2(info_x, info_y), self.fonts['xl'].baseSize, 0, self.white)
        rl.draw_text_ex(self.fonts['lg'], state.music_artist, rl.Vector2(info_x, info_y + 110), self.fonts['lg'].baseSize, 0, self.gray_text)
        
        # Progress bar
        bar_w = cw - (info_x - cx) - 64
        bar_y = info_y + 200
        rl.draw_rectangle_rounded(rl.Rectangle(info_x, bar_y, bar_w, 12), 1.0, 32, self.card_bg)
        prog_w = int(bar_w * state.music_progress)
        rl.draw_rectangle_rounded(rl.Rectangle(info_x, bar_y, prog_w, 12), 1.0, 32, self.blue)
        rl.draw_circle(int(info_x + prog_w), int(bar_y + 6), 16, self.white)
        
        # Transport
        bx = info_x + bar_w/2 - 120 - 24
        by = bar_y + 60
        for i, icon in enumerate(["skip-back_white.png", "pause_white.png" if state.music_playing else "play_white.png", "skip-forward_white.png"]):
            rl.draw_rectangle_rounded(rl.Rectangle(bx + i*(80+24), by, 80, 80), 0.35, 32, self.card_bg)
            tex = self.icons.get(icon)
            if tex and tex.id > 0:
                scale = 32.0 / max(tex.width, 1)
                ix = bx + i*(80+24) + 40 - (tex.width * scale) / 2
                iy = by + 40 - (tex.height * scale) / 2
                rl.draw_texture_ex(tex, rl.Vector2(ix, iy), 0.0, scale, self.white)

    def _render_climate(self, state, cx, cy, cw, ch):
        gap = 32
        card_w = (cw - gap*3) // 2
        card_h = ch - 160
        
        # Driver
        self._draw_card(cx + gap, cy + gap, card_w, card_h)
        lbl_size = rl.measure_text_ex(self.fonts['sm'], "DRIVER", self.fonts['sm'].baseSize, 0)
        rl.draw_text_ex(self.fonts['sm'], "DRIVER", rl.Vector2(cx + gap + card_w/2 - lbl_size.x/2, cy + gap + 32), self.fonts['sm'].baseSize, 0, self.gray_text)
        
        temp_txt = f"{int(state.driver_temp_f)}°"
        t_size = rl.measure_text_ex(self.fonts['bxl'], temp_txt, self.fonts['bxl'].baseSize, 0)
        rl.draw_text_ex(self.fonts['bxl'], temp_txt, rl.Vector2(cx + gap + card_w/2 - t_size.x/2, cy + gap + card_h/2 - t_size.y/2), self.fonts['bxl'].baseSize, 0, self.white)
        
        # Pass
        self._draw_card(cx + gap*2 + card_w, cy + gap, card_w, card_h)
        lbl_size = rl.measure_text_ex(self.fonts['sm'], "PASSENGER", self.fonts['sm'].baseSize, 0)
        rl.draw_text_ex(self.fonts['sm'], "PASSENGER", rl.Vector2(cx + gap*2 + card_w + card_w/2 - lbl_size.x/2, cy + gap + 32), self.fonts['sm'].baseSize, 0, self.gray_text)
        
        temp_txt = f"{int(getattr(state, 'pass_temp_f', 70))}°"
        t_size = rl.measure_text_ex(self.fonts['bxl'], temp_txt, self.fonts['bxl'].baseSize, 0)
        rl.draw_text_ex(self.fonts['bxl'], temp_txt, rl.Vector2(cx + gap*2 + card_w + card_w/2 - t_size.x/2, cy + gap + card_h/2 - t_size.y/2), self.fonts['bxl'].baseSize, 0, self.white)

        # Bottom pills
        py = cy + gap + card_h + 32
        for i, lbl in enumerate(["A/C", "HEAT", "DEF", "SYNC"]):
            px = cx + gap + i*(140 + 24)
            is_on = getattr(state, lbl.lower().replace("/","")+"_on", False)
            if lbl == "A/C": is_on = state.ac_on
            
            bg = self.green if is_on else self.dark_gray
            fg = self.pure_black if is_on else self.gray_text
            
            rl.draw_rectangle_rounded(rl.Rectangle(px, py, 140, 64), 0.5, 32, bg)
            l_size = rl.measure_text_ex(self.fonts['bmd'], lbl, self.fonts['bmd'].baseSize, 0)
            rl.draw_text_ex(self.fonts['bmd'], lbl, rl.Vector2(px + 70 - l_size.x/2, py + 32 - l_size.y/2), self.fonts['bmd'].baseSize, 0, fg)

    def _render_phone(self, state, cx, cy, cw, ch):
        gap = 16
        for i, (name, number) in enumerate(_CONTACTS):
            ry = cy + gap + i*(80 + gap)
            self._draw_card(cx + gap, ry, cw - gap*2, 80)
            rl.draw_text_ex(self.fonts['blg'], name, rl.Vector2(cx + gap + 32, ry + 16), self.fonts['blg'].baseSize, 0, self.white)
            rl.draw_text_ex(self.fonts['md'], number, rl.Vector2(cx + gap + cw/2, ry + 24), self.fonts['md'].baseSize, 0, self.gray_text)

    def _render_settings(self, state, cx, cy, cw, ch):
        gap = 16
        for i, lbl in enumerate(_SETTINGS_LABELS):
            ry = cy + gap + i*(80 + gap)
            self._draw_card(cx + gap, ry, cw - gap*2, 80)
            if i == self.focused_setting:
                rl.draw_rectangle_rounded_lines_ex(rl.Rectangle(cx + gap, ry, cw - gap*2, 80), 0.35, 32, 2.0, self.green)
            
            rl.draw_text_ex(self.fonts['blg'], lbl, rl.Vector2(cx + gap + 32, ry + 16), self.fonts['blg'].baseSize, 0, self.white)

    def _render_nav(self, state, cx, cy, cw, ch):
        map_w = int(cw * 0.7)
        rl.draw_rectangle(int(cx), int(cy), map_w, int(ch), self.dark_gray)
        
        self._draw_card(cx + map_w + 16, cy + 16, cw - map_w - 32, ch - 32)
        rl.draw_text_ex(self.fonts['blg'], getattr(state, 'destination', "Home"), rl.Vector2(cx + map_w + 48, cy + 48), self.fonts['blg'].baseSize, 0, self.white)

    def _render_bottom_bar(self, state, W, H):
        import time
        bh = 48
        by = H - bh
        rl.draw_rectangle_rounded(rl.Rectangle(0, by, W, bh), 0.0, 1, rl.Color(41, 41, 41, 255))
        # Left: speed + gear
        rl.draw_text_ex(self.fonts['sm'], f"{int(state.speed_mph)} MPH  |  {state.gear}", rl.Vector2(100, by + 14), self.fonts['sm'].baseSize, 0, self.white)
        # Center: nav
        nav = "Continue on US-101"
        nav_size = rl.measure_text_ex(self.fonts['sm'], nav, self.fonts['sm'].baseSize, 0)
        rl.draw_text_ex(self.fonts['sm'], nav, rl.Vector2(W/2 - nav_size.x/2, by + 14), self.fonts['sm'].baseSize, 0, self.gray_text)
        # Right: clock
        clock = time.strftime("%I:%M %p")
        clk_size = rl.measure_text_ex(self.fonts['sm'], clock, self.fonts['sm'].baseSize, 0)
        rl.draw_text_ex(self.fonts['sm'], clock, rl.Vector2(W - clk_size.x - 32, by + 14), self.fonts['sm'].baseSize, 0, self.white)

    def _draw_card(self, x, y, w, h):
        rl.draw_rectangle_rounded(rl.Rectangle(x, y, w, h), 0.35, 32, self.card_bg)

    def handle_key(self, key, state, theme):
        if key == rl.KeyboardKey.KEY_H: state.infotainment_app = 0; return
        if key == rl.KeyboardKey.KEY_N and state.infotainment_app != 2: state.infotainment_app = 1; return
        if key == rl.KeyboardKey.KEY_M: state.infotainment_app = 2; return
        if key == rl.KeyboardKey.KEY_C: state.infotainment_app = 3; return
        if key == rl.KeyboardKey.KEY_P and state.infotainment_app != 2: state.infotainment_app = 4; return
        if key == rl.KeyboardKey.KEY_S and state.infotainment_app != 3: state.infotainment_app = 5; return
        if key == rl.KeyboardKey.KEY_LEFT: state.infotainment_app = max(0, state.infotainment_app - 1)
        elif key == rl.KeyboardKey.KEY_RIGHT: state.infotainment_app = min(5, state.infotainment_app + 1)
        # App-specific keys...
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

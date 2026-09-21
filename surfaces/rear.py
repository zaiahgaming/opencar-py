import pyray as rl
import math
import os

_TRACKS = [
    ("The Midnight", "Los Angeles"),
    ("Tycho", "Awake"),
    ("Bonobo", "Kong"),
    ("Polo & Pan", "Canopee"),
    ("Washed Out", "Feel It All Around")
]

class PongGame:
    BALL_SPEED = 320.0
    PAD_SPEED  = 300.0
    PAD_W, PAD_H = 16, 110
    BALL_R = 12

    def __init__(self):
        self.reset()
        
    def reset(self):
        self.ball_pos = [640, 360]
        self.ball_vel = [self.BALL_SPEED, self.BALL_SPEED]
        self.p1_y = 360
        self.p2_y = 360
        self.p1_score = 0
        self.p2_score = 0

    def update(self, dt, h, w):
        self.ball_pos[0] += self.ball_vel[0] * dt
        self.ball_pos[1] += self.ball_vel[1] * dt

        if self.ball_pos[1] - self.BALL_R <= 80 or self.ball_pos[1] + self.BALL_R >= h - 40:
            self.ball_vel[1] *= -1
            self.ball_pos[1] = max(80 + self.BALL_R, min(h - 40 - self.BALL_R, self.ball_pos[1]))
            
        # P1 paddle collision
        p1_rect = rl.Rectangle(60, self.p1_y - self.PAD_H/2, self.PAD_W, self.PAD_H)
        if rl.check_collision_circle_rec(rl.Vector2(self.ball_pos[0], self.ball_pos[1]), self.BALL_R, p1_rect):
            self.ball_vel[0] = abs(self.ball_vel[0]) * 1.05
            self.ball_pos[0] = 60 + self.PAD_W + self.BALL_R
            
        # P2 paddle collision
        p2_rect = rl.Rectangle(w - 60 - self.PAD_W, self.p2_y - self.PAD_H/2, self.PAD_W, self.PAD_H)
        if rl.check_collision_circle_rec(rl.Vector2(self.ball_pos[0], self.ball_pos[1]), self.BALL_R, p2_rect):
            self.ball_vel[0] = -abs(self.ball_vel[0]) * 1.05
            self.ball_pos[0] = w - 60 - self.PAD_W - self.BALL_R

        # Score check
        if self.ball_pos[0] < 0:
            self.p2_score += 1
            self.ball_pos = [w/2, h/2]
            self.ball_vel = [self.BALL_SPEED, self.BALL_SPEED * (1 if self.p2_score % 2 == 0 else -1)]
        elif self.ball_pos[0] > w:
            self.p1_score += 1
            self.ball_pos = [w/2, h/2]
            self.ball_vel = [-self.BALL_SPEED, self.BALL_SPEED * (1 if self.p1_score % 2 == 0 else -1)]

class RearSurface:
    def __init__(self, fonts: dict):
        self.fonts = fonts
        self.pong = PongGame()
        self.tabs = ["Home", "Media", "Games", "Trip", "Climate"]
        self.active_tab = 0
        
        # Textures & Icons
        self.icons = {}
        for name in [
            "home_white.png", "music_white.png", "play_white.png", "pause_white.png",
            "skip-back_white.png", "skip-forward_white.png", "play_dark.png", "pause_dark.png",
            "fan_white.png", "navigation_white.png", "activity_white.png", "thermometer_white.png",
            "volume-2_white.png"
        ]:
            path = f"assets/icons/{name}"
            if os.path.exists(path):
                self.icons[name] = rl.load_texture(path)
                
        self.album_arts = {}
        for name in ["the_midnight.jpg", "tycho.jpg", "bonobo.jpg"]:
            path = f"assets/music/{name}"
            if os.path.exists(path):
                self.album_arts[name] = rl.load_texture(path)
                
        self.card_bg = rl.Color(41, 41, 41, 255)
        self.pure_black = rl.Color(0, 0, 0, 255)
        self.gray_text = rl.Color(170, 170, 170, 255)
        self.gray_label = rl.Color(128, 128, 128, 255)
        self.white = rl.Color(255, 255, 255, 255)
        self.green = rl.Color(51, 171, 76, 255)
        self.blue = rl.Color(70, 91, 234, 255)
        self.dark_gray = rl.Color(57, 57, 57, 255)

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
    
    def render(self, state, theme):
        w = rl.get_screen_width()
        h = rl.get_screen_height()
        dt = rl.get_frame_time()
        
        rl.clear_background(self.pure_black)
        state.rear_app = self.active_tab
        
        # Tabs bar
        tab_y = 16
        tab_w = 170
        tab_height = 52
        gap = 16
        total_w = len(self.tabs) * tab_w + (len(self.tabs) - 1) * gap
        start_x = (w - total_w) / 2
        
        clicked = rl.is_mouse_button_pressed(rl.MouseButton.MOUSE_BUTTON_LEFT)
        mouse = rl.get_mouse_position()
        
        for i, tab in enumerate(self.tabs):
            x = start_x + i * (tab_w + gap)
            rect = rl.Rectangle(x, tab_y, tab_w, tab_height)
            if clicked and rl.check_collision_point_rec(mouse, rect):
                self.active_tab = i
                
            if i == self.active_tab:
                bg = self.green
                text_col = self.pure_black
                font = self.fonts.get('bmd', self.fonts.get('md', rl.get_font_default()))
            else:
                bg = self.card_bg
                text_col = self.gray_text
                font = self.fonts.get('sm', rl.get_font_default())
                
            rl.draw_rectangle_rounded(rect, 0.4, 16, bg)
            
            ts = rl.measure_text_ex(font, tab, font.baseSize, 0)
            tx = x + (tab_w - ts.x) / 2
            ty = tab_y + (tab_height - ts.y) / 2
            rl.draw_text_ex(font, tab, rl.Vector2(tx, ty), font.baseSize, 0, text_col)

        app_area_y = tab_y + tab_height + 24
        app_area_h = h - app_area_y - 24

        # Touch paddle control in Pong
        if self.active_tab == 2 and rl.is_mouse_button_down(rl.MouseButton.MOUSE_BUTTON_LEFT):
            if mouse.x < w * 0.4:
                self.pong.p1_y = max(80 + self.pong.PAD_H/2, min(h - 40 - self.pong.PAD_H/2, mouse.y))
        
        if self.active_tab == 0:
            self._render_home(w, h, app_area_y, app_area_h, state, theme, mouse, clicked)
        elif self.active_tab == 1:
            self._render_music(w, h, app_area_y, app_area_h, state, theme, mouse, clicked)
        elif self.active_tab == 2:
            self._render_pong(w, h, app_area_y, app_area_h, state, theme, dt)
        elif self.active_tab == 3:
            self._render_trip(w, h, app_area_y, app_area_h, state, theme)
        elif self.active_tab == 4:
            self._render_climate(w, h, app_area_y, app_area_h, state, theme, mouse, clicked)

    def _render_home(self, w, h, sy, sh, state, theme, mouse, clicked):
        gap = 16
        card_w = (w - 64 - gap) / 2
        card_h = (sh - gap) / 2
        
        # ── 1. NOW PLAYING Card ───────────────────────────────────────────────
        c0_x = 32
        c0_y = sy
        rect_m = rl.Rectangle(c0_x, c0_y, card_w, card_h)
        rl.draw_rectangle_rounded(rect_m, 0.25, 16, self.card_bg)
        
        self._draw_icon("music_white.png", c0_x + 24, c0_y + 20, 16, self.gray_label)
        rl.draw_text_ex(self.fonts['xs'], "NOW PLAYING", rl.Vector2(c0_x + 48, c0_y + 20), self.fonts['xs'].baseSize, 0, self.gray_label)
        
        art_keys = ["the_midnight.jpg", "tycho.jpg", "bonobo.jpg"]
        art_idx = state.music_track % len(art_keys)
        art_tex = self.album_arts.get(art_keys[art_idx])
        art_size = int(card_h - 96)
        if art_size > 130: art_size = 130
        if art_tex and art_tex.id > 0:
            scale = art_size / max(art_tex.width, 1)
            rl.draw_texture_ex(art_tex, rl.Vector2(c0_x + 24, c0_y + 50), 0.0, scale, rl.WHITE)
            rl.draw_rectangle_lines_ex(rl.Rectangle(c0_x + 24, c0_y + 50, art_size, art_size), 1.0, rl.Color(80, 80, 80, 200))
            
        tx = c0_x + 24 + art_size + 20
        rl.draw_text_ex(self.fonts['blg'], state.music_title or "Los Angeles", rl.Vector2(tx, c0_y + 50), self.fonts['blg'].baseSize, 0, self.white)
        rl.draw_text_ex(self.fonts['md'], state.music_artist or "The Midnight", rl.Vector2(tx, c0_y + 92), self.fonts['md'].baseSize, 0, self.gray_text)
        
        # Mini transport buttons on card
        ctrl_y = c0_y + 120
        btn_sz = 44
        btn_prev = rl.Rectangle(tx, ctrl_y, btn_sz, btn_sz)
        btn_play = rl.Rectangle(tx + btn_sz + 10, ctrl_y, btn_sz, btn_sz)
        btn_next = rl.Rectangle(tx + (btn_sz + 10)*2, ctrl_y, btn_sz, btn_sz)
        rl.draw_rectangle_rounded(btn_prev, 0.5, 16, self.dark_gray)
        rl.draw_rectangle_rounded(btn_play, 0.5, 16, self.green)
        rl.draw_rectangle_rounded(btn_next, 0.5, 16, self.dark_gray)
        self._draw_icon_centered("skip-back_white.png", btn_prev.x + btn_sz/2, ctrl_y + btn_sz/2, 20, self.white)
        self._draw_icon_centered("pause_dark.png" if state.music_playing else "play_dark.png", btn_play.x + btn_sz/2, ctrl_y + btn_sz/2, 20, self.pure_black)
        self._draw_icon_centered("skip-forward_white.png", btn_next.x + btn_sz/2, ctrl_y + btn_sz/2, 20, self.white)
        
        # Mini progress
        pb_w = card_w - 48
        pb_y = c0_y + card_h - 24
        rl.draw_rectangle_rounded(rl.Rectangle(c0_x + 24, pb_y, pb_w, 6), 1.0, 8, self.dark_gray)
        prog_val = max(0.0, min(1.0, getattr(state, 'music_progress', 0.4)))
        rl.draw_rectangle_rounded(rl.Rectangle(c0_x + 24, pb_y, int(pb_w * prog_val), 6), 1.0, 8, self.green)
        
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
            elif rl.check_collision_point_rec(mouse, rect_m):
                self.active_tab = 1

        # ── 2. TRIP METRICS Card ──────────────────────────────────────────────
        c1_x = 32 + card_w + gap
        c1_y = sy
        rect_t = rl.Rectangle(c1_x, c1_y, card_w, card_h)
        rl.draw_rectangle_rounded(rect_t, 0.25, 16, self.card_bg)
        
        self._draw_icon("navigation_white.png", c1_x + 24, c1_y + 20, 16, self.gray_label)
        rl.draw_text_ex(self.fonts['xs'], "PASSENGER TRIP MONITOR", rl.Vector2(c1_x + 48, c1_y + 20), self.fonts['xs'].baseSize, 0, self.gray_label)
        
        dest = getattr(state, 'destination', "Downtown SF")
        rl.draw_text_ex(self.fonts['blg'], dest, rl.Vector2(c1_x + 24, c1_y + 50), self.fonts['blg'].baseSize, 0, self.white)
        
        dist_str = f"{getattr(state, 'nav_remaining_mi', 12.4):.1f} mi remaining · US-101 N"
        rl.draw_text_ex(self.fonts['bmd'], dist_str, rl.Vector2(c1_x + 24, c1_y + 96), self.fonts['bmd'].baseSize, 0, self.green)
        
        # Route progress bar
        r_bar_y = c1_y + 138
        rl.draw_rectangle_rounded(rl.Rectangle(c1_x + 24, r_bar_y, card_w - 48, 6), 1.0, 8, self.dark_gray)
        rl.draw_rectangle_rounded(rl.Rectangle(c1_x + 24, r_bar_y, int((card_w - 48) * 0.65), 6), 1.0, 8, self.blue)
        
        # ETA Pills
        pills_y = c1_y + card_h - 48
        pills = [("14 MIN", self.green, self.pure_black), ("12.4 MI", self.dark_gray, self.white), ("ETA 5:42 PM", self.dark_gray, self.white)]
        p_x = c1_x + 24
        for text, p_bg, p_fg in pills:
            pts = rl.measure_text_ex(self.fonts['xs'], text, self.fonts['xs'].baseSize, 0)
            pw = pts.x + 20
            rl.draw_rectangle_rounded(rl.Rectangle(p_x, pills_y, pw, 28), 0.5, 16, p_bg)
            rl.draw_text_ex(self.fonts['xs'], text, rl.Vector2(p_x + 10, pills_y + 6), self.fonts['xs'].baseSize, 0, p_fg)
            p_x += pw + 10

        # ── 3. REAR CLIMATE Card ──────────────────────────────────────────────
        c2_x = 32
        c2_y = sy + card_h + gap
        rect_c = rl.Rectangle(c2_x, c2_y, card_w, card_h)
        rl.draw_rectangle_rounded(rect_c, 0.25, 16, self.card_bg)
        
        self._draw_icon("fan_white.png", c2_x + 24, c2_y + 20, 16, self.gray_label)
        rl.draw_text_ex(self.fonts['xs'], "REAR CLIMATE ZONE", rl.Vector2(c2_x + 48, c2_y + 20), self.fonts['xs'].baseSize, 0, self.gray_label)
        
        rear_t = int(getattr(state, 'rear_driver_temp', 71.0))
        rl.draw_text_ex(self.fonts['xl'], f"{rear_t}°", rl.Vector2(c2_x + 32, c2_y + 54), self.fonts['xl'].baseSize, 0, self.white)
        rl.draw_text_ex(self.fonts['sm'], "Rear Comfort Auto Mode · Low Airflow", rl.Vector2(c2_x + 32, c2_y + 144), self.fonts['sm'].baseSize, 0, self.gray_text)
        
        btn_rminus = rl.Rectangle(c2_x + card_w - 170, c2_y + 68, 64, 64)
        btn_rplus  = rl.Rectangle(c2_x + card_w - 88,  c2_y + 68, 64, 64)
        rl.draw_rectangle_rounded(btn_rminus, 0.5, 16, self.dark_gray)
        rl.draw_rectangle_rounded(btn_rplus,  0.5, 16, self.dark_gray)
        rl.draw_text_ex(self.fonts['blg'], "-", rl.Vector2(btn_rminus.x + 24, btn_rminus.y + 10), self.fonts['blg'].baseSize, 0, self.white)
        rl.draw_text_ex(self.fonts['blg'], "+", rl.Vector2(btn_rplus.x + 20,  btn_rplus.y + 10), self.fonts['blg'].baseSize, 0, self.white)
        
        if clicked:
            if rl.check_collision_point_rec(mouse, btn_rminus):
                state.rear_driver_temp = max(60, rear_t - 1)
            elif rl.check_collision_point_rec(mouse, btn_rplus):
                state.rear_driver_temp = min(85, rear_t + 1)

        # ── 4. QUICK LAUNCH Card ──────────────────────────────────────────────
        c3_x = 32 + card_w + gap
        c3_y = sy + card_h + gap
        rect_q = rl.Rectangle(c3_x, c3_y, card_w, card_h)
        rl.draw_rectangle_rounded(rect_q, 0.25, 16, self.card_bg)
        
        self._draw_icon("activity_white.png", c3_x + 24, c3_y + 20, 16, self.gray_label)
        rl.draw_text_ex(self.fonts['xs'], "ENTERTAINMENT LAUNCHER", rl.Vector2(c3_x + 48, c3_y + 20), self.fonts['xs'].baseSize, 0, self.gray_label)
        
        btn_pong = rl.Rectangle(c3_x + 24, c3_y + 54, card_w - 48, 52)
        rl.draw_rectangle_rounded(btn_pong, 0.35, 16, self.green)
        rl.draw_text_ex(self.fonts['bmd'], "PLAY RETRO PONG", rl.Vector2(btn_pong.x + 24, btn_pong.y + 12), self.fonts['bmd'].baseSize, 0, self.pure_black)
        
        btn_media = rl.Rectangle(c3_x + 24, c3_y + 120, card_w - 48, 52)
        rl.draw_rectangle_rounded(btn_media, 0.35, 16, self.dark_gray)
        rl.draw_text_ex(self.fonts['bmd'], "OPEN AUDIO PLAYER", rl.Vector2(btn_media.x + 24, btn_media.y + 12), self.fonts['bmd'].baseSize, 0, self.white)
        
        if clicked:
            if rl.check_collision_point_rec(mouse, btn_pong):
                self.active_tab = 2
            elif rl.check_collision_point_rec(mouse, btn_media):
                self.active_tab = 1

    def _render_music(self, w, h, sy, sh, state, theme, mouse, clicked):
        col_gap = 32
        left_w = int((w - 64 - col_gap) * 0.58)
        right_w = w - 64 - col_gap - left_w
        
        # ── Left Column: Player Card ──────────────────────────────────────────
        player_x = 32
        player_y = sy
        player_h = sh
        rl.draw_rectangle_rounded(rl.Rectangle(player_x, player_y, left_w, player_h), 0.25, 16, self.card_bg)
        
        px = player_x + 28
        py = player_y + 24
        
        art_size = 180
        art_keys = ["the_midnight.jpg", "tycho.jpg", "bonobo.jpg"]
        art_idx = state.music_track % len(art_keys)
        art_tex = self.album_arts.get(art_keys[art_idx])
        if art_tex and art_tex.id > 0:
            scale = art_size / max(art_tex.width, 1)
            rl.draw_texture_ex(art_tex, rl.Vector2(px, py), 0.0, scale, rl.WHITE)
        meta_x = px + art_size + 28
        rl.draw_text_ex(self.fonts['xs'], "PASSENGER AUDIO STREAM", rl.Vector2(meta_x, py + 8), self.fonts['xs'].baseSize, 0, self.green)
        rl.draw_text_ex(self.fonts['blg'], state.music_title or "Los Angeles", rl.Vector2(meta_x, py + 34), self.fonts['blg'].baseSize, 0, self.white)
        rl.draw_text_ex(self.fonts['bmd'], state.music_artist or "The Midnight", rl.Vector2(meta_x, py + 90), self.fonts['bmd'].baseSize, 0, self.gray_text)
        rl.draw_text_ex(self.fonts['xs'], "Master Quality · 96kHz 24-bit Lossless", rl.Vector2(meta_x, py + 134), self.fonts['xs'].baseSize, 0, self.blue)
        
        # Progress Bar & Timestamps
        bar_y = py + art_size + 36
        bar_w = left_w - 56
        bar_rect = rl.Rectangle(px, bar_y - 12, bar_w, 32)
        if clicked and rl.check_collision_point_rec(mouse, bar_rect):
            state.music_progress = max(0.0, min(1.0, (mouse.x - px) / bar_w))
            
        rl.draw_rectangle_rounded(rl.Rectangle(px, bar_y, bar_w, 8), 1.0, 16, self.dark_gray)
        prog_val = max(0.0, min(1.0, getattr(state, 'music_progress', 0.4)))
        prog_w = int(bar_w * prog_val)
        rl.draw_rectangle_rounded(rl.Rectangle(px, bar_y, prog_w, 8), 1.0, 16, self.green)
        rl.draw_circle(int(px + prog_w), int(bar_y + 4), 10, self.white)
        
        total_sec = 225
        curr_sec = int(prog_val * total_sec)
        t_curr = f"{curr_sec // 60}:{curr_sec % 60:02d}"
        t_rem = f"-{(total_sec - curr_sec) // 60}:{(total_sec - curr_sec) % 60:02d}"
        rl.draw_text_ex(self.fonts['sm'], t_curr, rl.Vector2(px, bar_y + 16), self.fonts['sm'].baseSize, 0, self.gray_text)
        ts_rem = rl.measure_text_ex(self.fonts['sm'], t_rem, self.fonts['sm'].baseSize, 0)
        rl.draw_text_ex(self.fonts['sm'], t_rem, rl.Vector2(px + bar_w - ts_rem.x, bar_y + 16), self.fonts['sm'].baseSize, 0, self.gray_text)
        
        # Transport controls
        btn_y = bar_y + 54
        btn_cx = px + bar_w / 2
        
        btn_prev = rl.Rectangle(btn_cx - 130, btn_y, 64, 64)
        is_prev_hover = rl.check_collision_point_rec(mouse, btn_prev)
        rl.draw_rectangle_rounded(btn_prev, 0.5, 32, rl.Color(80, 80, 80, 255) if is_prev_hover else rl.Color(60, 60, 60, 255))
        self._draw_icon_centered("skip-back_white.png", btn_cx - 98, btn_y + 32, 28, self.white)
        
        btn_play = rl.Rectangle(btn_cx - 40, btn_y - 8, 80, 80)
        is_play_hover = rl.check_collision_point_rec(mouse, btn_play)
        rl.draw_rectangle_rounded(btn_play, 0.5, 32, rl.Color(230, 230, 230, 255) if is_play_hover else self.white)
        hero_icon = "pause_dark.png" if state.music_playing else "play_dark.png"
        self._draw_icon_centered(hero_icon, btn_cx, btn_y + 32, 36, self.pure_black)
        
        btn_next = rl.Rectangle(btn_cx + 66, btn_y, 64, 64)
        is_next_hover = rl.check_collision_point_rec(mouse, btn_next)
        rl.draw_rectangle_rounded(btn_next, 0.5, 32, rl.Color(80, 80, 80, 255) if is_next_hover else rl.Color(60, 60, 60, 255))
        self._draw_icon_centered("skip-forward_white.png", btn_cx + 98, btn_y + 32, 28, self.white)
        
        # Volume Bar
        vol_y = btn_y + 88
        self._draw_icon("volume-2_white.png", px + 40, vol_y - 4, 22, self.gray_text)
        vol_bar_x = px + 80
        vol_bar_w = bar_w - 160
        rl.draw_rectangle_rounded(rl.Rectangle(vol_bar_x, vol_y + 4, vol_bar_w, 6), 1.0, 16, self.dark_gray)
        rl.draw_rectangle_rounded(rl.Rectangle(vol_bar_x, vol_y + 4, int(vol_bar_w * 0.75), 6), 1.0, 16, self.white)
        rl.draw_circle(int(vol_bar_x + vol_bar_w * 0.75), int(vol_y + 7), 8, self.white)
        
        # ── Right Column: Up Next Queue ───────────────────────────────────────
        q_x = player_x + left_w + col_gap
        q_y = sy
        q_h = sh
        rl.draw_rectangle_rounded(rl.Rectangle(q_x, q_y, right_w, q_h), 0.25, 16, self.card_bg)
        
        rl.draw_text_ex(self.fonts['xs'], "UP NEXT IN QUEUE", rl.Vector2(q_x + 24, q_y + 20), self.fonts['xs'].baseSize, 0, self.gray_label)
        
        for idx, (artist, title) in enumerate(_TRACKS):
            item_y = q_y + 56 + idx * 78
            item_rect = rl.Rectangle(q_x + 16, item_y, right_w - 32, 66)
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
            rl.draw_text_ex(self.fonts['bmd'], track_num, rl.Vector2(item_rect.x + 18, item_rect.y + 20), self.fonts['bmd'].baseSize, 0, self.green if is_cur else self.gray_label)
            rl.draw_text_ex(self.fonts['bmd'], title, rl.Vector2(item_rect.x + 48, item_rect.y + 12), self.fonts['bmd'].baseSize, 0, self.white)
            rl.draw_text_ex(self.fonts['xs'], artist, rl.Vector2(item_rect.x + 48, item_rect.y + 40), self.fonts['xs'].baseSize, 0, self.gray_text)
            
            dur = ["3:45", "4:12", "3:58", "4:30", "3:15"][idx]
            rl.draw_text_ex(self.fonts['xs'], dur, rl.Vector2(item_rect.x + item_rect.width - 50, item_rect.y + 24), self.fonts['xs'].baseSize, 0, self.gray_label)
            
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

    def _render_pong(self, w, h, sy, sh, state, theme, dt):
        self.pong.update(dt, h, w)
        
        # Court background & lines
        rl.draw_rectangle_lines_ex(rl.Rectangle(32, sy, w - 64, sh), 2.0, self.dark_gray)
        for y in range(int(sy), int(sy + sh), 36):
            rl.draw_rectangle(w//2 - 2, y, 4, 18, self.dark_gray)
            
        # Score Board
        font_score = self.fonts.get('xl', rl.get_font_default())
        score = f"{self.pong.p1_score}   {self.pong.p2_score}"
        ts = rl.measure_text_ex(font_score, score, font_score.baseSize, 0)
        rl.draw_text_ex(font_score, score, rl.Vector2((w - ts.x)/2, sy + 16), font_score.baseSize, 0, self.white)
        rl.draw_text_ex(self.fonts['xs'], "TOUCH OR DRAG LEFT PADDLE TO PLAY", rl.Vector2(w/2 - 140, sy + sh - 30), self.fonts['xs'].baseSize, 0, self.gray_text)
        
        # Paddles
        p1_r = rl.Rectangle(60, self.pong.p1_y - self.pong.PAD_H/2, self.pong.PAD_W, self.pong.PAD_H)
        p2_r = rl.Rectangle(w - 60 - self.pong.PAD_W, self.pong.p2_y - self.pong.PAD_H/2, self.pong.PAD_W, self.pong.PAD_H)
        rl.draw_rectangle_rounded(p1_r, 0.3, 8, self.green)
        rl.draw_rectangle_rounded(p2_r, 0.3, 8, self.white)
        
        # Ball
        rl.draw_circle(int(self.pong.ball_pos[0]), int(self.pong.ball_pos[1]), float(self.pong.BALL_R), self.white)
        
        # AI for P2
        if self.pong.ball_pos[1] > self.pong.p2_y:
            self.pong.p2_y += self.pong.PAD_SPEED * dt
        elif self.pong.ball_pos[1] < self.pong.p2_y:
            self.pong.p2_y -= self.pong.PAD_SPEED * dt
            
        self.pong.p2_y = max(sy + self.pong.PAD_H/2, min(sy + sh - self.pong.PAD_H/2, self.pong.p2_y))

    def _render_trip(self, w, h, sy, sh, state, theme):
        font_lbl = self.fonts.get('blg', rl.get_font_default())
        font_val = self.fonts.get('bmd', rl.get_font_default())
        
        stats = [
            ("Trip Remaining", f"{getattr(state, 'nav_remaining_mi', 12.4):.1f} mi"),
            ("Trip Odometer", f"{getattr(state, 'trip_distance_mi', 127.4):.1f} mi"),
            ("Time to Destination", f"{getattr(state, 'eta_seconds', 840) // 60} min"),
            ("Estimated Arrival", "5:42 PM"),
            ("Average Cruising Speed", f"{int(getattr(state, 'speed_mph', 65))} mph"),
        ]
        
        for i, (lbl, val) in enumerate(stats):
            ry = sy + i * 86
            rl.draw_rectangle_rounded(rl.Rectangle(64, ry, w - 128, 72), 0.25, 16, self.card_bg)
            rl.draw_text_ex(font_lbl, lbl, rl.Vector2(96, ry + 16), font_lbl.baseSize, 0, self.white)
            ts = rl.measure_text_ex(font_val, val, font_val.baseSize, 0)
            rl.draw_text_ex(font_val, val, rl.Vector2(w - 96 - ts.x, ry + 20), font_val.baseSize, 0, self.green)

    def _render_climate(self, w, h, sy, sh, state, theme, mouse, clicked):
        card_w = (w - 128 - 32) / 2
        card_h = sh * 0.72
        cy = sy + (sh - card_h) / 2
        
        font_temp = self.fonts.get('bxl', rl.get_font_default())
        
        # Rear Left / Rear Right Zones
        for i, zone in enumerate(["REAR LEFT", "REAR RIGHT"]):
            cx = 64 + i * (card_w + 32)
            rl.draw_rectangle_rounded(rl.Rectangle(cx, cy, card_w, card_h), 0.25, 16, self.card_bg)
            rl.draw_text_ex(self.fonts['sm'], zone, rl.Vector2(cx + 32, cy + 24), self.fonts['sm'].baseSize, 0, self.gray_label)
            
            temp_val = int(getattr(state, 'rear_driver_temp' if i == 0 else 'rear_pass_temp', 71))
            temp_str = f"{temp_val}°"
            ts = rl.measure_text_ex(font_temp, temp_str, font_temp.baseSize, 0)
            rl.draw_text_ex(font_temp, temp_str, rl.Vector2(cx + (card_w - ts.x)/2, cy + (card_h - ts.y)/2 - 30), font_temp.baseSize, 0, self.white)
            
            # +/- Buttons
            btn_m = rl.Rectangle(cx + card_w/2 - 90, cy + card_h - 90, 72, 72)
            btn_p = rl.Rectangle(cx + card_w/2 + 18, cy + card_h - 90, 72, 72)
            rl.draw_rectangle_rounded(btn_m, 0.5, 32, self.dark_gray)
            rl.draw_rectangle_rounded(btn_p, 0.5, 32, self.dark_gray)
            rl.draw_text_ex(self.fonts['blg'], "-", rl.Vector2(btn_m.x + 28, btn_m.y + 12), self.fonts['blg'].baseSize, 0, self.white)
            rl.draw_text_ex(self.fonts['blg'], "+", rl.Vector2(btn_p.x + 24, btn_p.y + 12), self.fonts['blg'].baseSize, 0, self.white)
            
            if clicked:
                if rl.check_collision_point_rec(mouse, btn_m):
                    if i == 0: state.rear_driver_temp = max(60, temp_val - 1)
                    else: state.rear_pass_temp = max(60, temp_val - 1)
                elif rl.check_collision_point_rec(mouse, btn_p):
                    if i == 0: state.rear_driver_temp = min(85, temp_val + 1)
                    else: state.rear_pass_temp = min(85, temp_val + 1)

    def handle_key(self, key: int, state, theme):
        if key == rl.KeyboardKey.KEY_TAB or key == rl.KeyboardKey.KEY_RIGHT:
            self.active_tab = (self.active_tab + 1) % len(self.tabs)
        elif key == rl.KeyboardKey.KEY_LEFT:
            self.active_tab = (self.active_tab - 1) % len(self.tabs)
            
        if self.active_tab == 2:
            if key == rl.KeyboardKey.KEY_UP:
                self.pong.p1_y -= 40
            elif key == rl.KeyboardKey.KEY_DOWN:
                self.pong.p1_y += 40

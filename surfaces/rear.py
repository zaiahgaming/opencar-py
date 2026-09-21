# surfaces/rear.py — Comma 4 Glassmorphic Rear Surface
import pyray as rl
import math
import os
import time
import glass

_TRACKS = [
    ("The Midnight", "Los Angeles"),
    ("Tycho", "Awake"),
    ("Bonobo", "Kong"),
    ("Polo & Pan", "Canopee"),
    ("Washed Out", "Feel It All Around")
]

class PongGame:
    BALL_SPEED = 340.0
    PAD_SPEED  = 320.0
    PAD_W, PAD_H = 16, 110
    BALL_R = 12

    def __init__(self):
        self.reset()
        
    def reset(self):
        self.ball_pos = [640, 360]
        self.ball_vel = [self.BALL_SPEED, self.BALL_SPEED]
        self.p1_y = 360
        self.p2_y = 360
        self.p1_score = 3
        self.p2_score = 2

    def update(self, dt, h, w, top_bound, bot_bound):
        self.ball_pos[0] += self.ball_vel[0] * dt
        self.ball_pos[1] += self.ball_vel[1] * dt

        if self.ball_pos[1] - self.BALL_R <= top_bound:
            self.ball_vel[1] = abs(self.ball_vel[1])
            self.ball_pos[1] = top_bound + self.BALL_R
        elif self.ball_pos[1] + self.BALL_R >= bot_bound:
            self.ball_vel[1] = -abs(self.ball_vel[1])
            self.ball_pos[1] = bot_bound - self.BALL_R
            
        # P1 paddle collision
        p1_rect = rl.Rectangle(64, self.p1_y - self.PAD_H/2, self.PAD_W, self.PAD_H)
        if rl.check_collision_circle_rec(rl.Vector2(self.ball_pos[0], self.ball_pos[1]), self.BALL_R, p1_rect):
            self.ball_vel[0] = abs(self.ball_vel[0]) * 1.04
            self.ball_pos[0] = 64 + self.PAD_W + self.BALL_R
            
        # P2 paddle collision
        p2_rect = rl.Rectangle(w - 64 - self.PAD_W, self.p2_y - self.PAD_H/2, self.PAD_W, self.PAD_H)
        if rl.check_collision_circle_rec(rl.Vector2(self.ball_pos[0], self.ball_pos[1]), self.BALL_R, p2_rect):
            self.ball_vel[0] = -abs(self.ball_vel[0]) * 1.04
            self.ball_pos[0] = w - 64 - self.PAD_W - self.BALL_R

        # Score check
        if self.ball_pos[0] < 0:
            self.p2_score += 1
            self.ball_pos = [w/2, (top_bound + bot_bound)/2]
            self.ball_vel = [self.BALL_SPEED, self.BALL_SPEED * (1 if self.p2_score % 2 == 0 else -1)]
        elif self.ball_pos[0] > w:
            self.p1_score += 1
            self.ball_pos = [w/2, (top_bound + bot_bound)/2]
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

    def _draw_card(self, x, y, w, h, roundness=0.35, glow=None):
        glass.draw_glass_card(rl.Rectangle(x, y, w, h), roundness=roundness, glow_color=glow)

    def _draw_text_centered(self, font, text, cx, cy, color):
        ts = rl.measure_text_ex(font, text, font.baseSize, 0)
        rl.draw_text_ex(font, text, rl.Vector2(cx - ts.x / 2, cy - ts.y / 2), font.baseSize, 0, color)
    
    def render(self, state, theme):
        w = rl.get_screen_width()
        h = rl.get_screen_height()
        dt = rl.get_frame_time()
        
        glass.draw_ambient_backdrop(w, h)
        state.rear_app = self.active_tab
        
        # ── Top Navigation Dock (Floating Frosted Glass Capsule Rail) ───
        tab_y = 14
        tab_w = 160
        tab_height = 46
        gap = 12
        total_w = len(self.tabs) * tab_w + (len(self.tabs) - 1) * gap
        start_x = (w - total_w) / 2
        
        # Surrounding dock pill
        dock_outer = rl.Rectangle(start_x - 8, tab_y - 4, total_w + 16, tab_height + 8)
        glass.draw_glass_card(dock_outer, roundness=0.5, bg=rl.Color(16, 18, 26, 220))
        
        clicked = rl.is_mouse_button_pressed(rl.MouseButton.MOUSE_BUTTON_LEFT)
        mouse = rl.get_mouse_position()
        
        for i, tab in enumerate(self.tabs):
            x = start_x + i * (tab_w + gap)
            rect = rl.Rectangle(x, tab_y, tab_w, tab_height)
            if clicked and rl.check_collision_point_rec(mouse, rect):
                self.active_tab = i
                
            is_act = (i == self.active_tab)
            glass.draw_glass_pill(rect, roundness=0.45, active=is_act, solid=is_act)
            
            font = self.fonts.get('bmd', self.fonts['md']) if is_act else self.fonts['sm']
            text_col = glass.OBSIDIAN_BG if is_act else glass.TEXT_PRIMARY
            self._draw_text_centered(font, tab, x + tab_w / 2, tab_y + tab_height / 2, text_col)

        app_area_y = tab_y + tab_height + 18
        app_area_h = h - app_area_y - 16

        # Touch paddle control in Pong
        if self.active_tab == 2 and rl.is_mouse_button_down(rl.MouseButton.MOUSE_BUTTON_LEFT):
            if mouse.x < w * 0.4:
                self.pong.p1_y = max(app_area_y + self.pong.PAD_H/2, min(app_area_y + app_area_h - self.pong.PAD_H/2, mouse.y))
        
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

    # ════════════════════════════════════════════════════════════════════════════
    # 1. HOME SCREEN - 4 Glass Cards Grid
    # ════════════════════════════════════════════════════════════════════════════
    def _render_home(self, w, h, sy, sh, state, theme, mouse, clicked):
        gap = 14
        margin_x = 24
        card_w = (w - margin_x * 2 - gap) / 2
        card_h = (sh - gap) / 2
        
        # ── 1. NOW PLAYING Glass Card ─────────────────────────────────────────
        c0_x = margin_x
        c0_y = sy
        self._draw_card(c0_x, c0_y, card_w, card_h)
        
        self._draw_icon("music_white.png", c0_x + 22, c0_y + 18, 16, glass.TEXT_MUTED)
        rl.draw_text_ex(self.fonts['xs'], "NOW PLAYING", rl.Vector2(c0_x + 44, c0_y + 18), self.fonts['xs'].baseSize, 0, glass.TEXT_MUTED)
        
        badge_sp = rl.Rectangle(c0_x + card_w - 96, c0_y + 14, 76, 22)
        glass.draw_glass_pill(badge_sp, roundness=0.5, active=True)
        self._draw_text_centered(self.fonts['xs'], "SPOTIFY", badge_sp.x + 38, c0_y + 25, glass.OBSIDIAN_BG)
        
        art_keys = ["the_midnight.jpg", "tycho.jpg", "bonobo.jpg"]
        art_idx = getattr(state, 'music_track', 0) % len(art_keys)
        art_tex = self.album_arts.get(art_keys[art_idx])
        art_size = int(card_h - 96)
        if art_size > 120: art_size = 120
        
        rl.draw_rectangle_rounded(rl.Rectangle(c0_x + 20, c0_y + 48, art_size + 4, art_size + 6), 0.18, 16, glass.SHADOW_CORE)
        if art_tex and art_tex.id > 0:
            scale = art_size / max(art_tex.width, 1)
            rl.draw_texture_ex(art_tex, rl.Vector2(c0_x + 22, c0_y + 50), 0.0, scale, rl.WHITE)
            rl.draw_rectangle_rounded_lines_ex(rl.Rectangle(c0_x + 22, c0_y + 50, art_size, art_size), 0.18, 16, 1.2, glass.GLASS_BORDER)
            
        tx = c0_x + 22 + art_size + 18
        rl.draw_text_ex(self.fonts['blg'], getattr(state, 'music_title', "Los Angeles"), rl.Vector2(tx, c0_y + 46), self.fonts['blg'].baseSize, 0, glass.TEXT_PRIMARY)
        rl.draw_text_ex(self.fonts['md'], getattr(state, 'music_artist', "The Midnight"), rl.Vector2(tx, c0_y + 88), self.fonts['md'].baseSize, 0, glass.TEXT_SECONDARY)
        
        # Circular Mini Transport Buttons
        ctrl_y = c0_y + 130
        glass.draw_circular_button(tx + 20, ctrl_y + 20, 20)
        self._draw_icon_centered("skip-back_white.png", tx + 20, ctrl_y + 20, 18, glass.TEXT_PRIMARY)
        
        is_playing = getattr(state, 'music_playing', True)
        play_bg = glass.COMMA_GREEN if not is_playing else rl.Color(250, 250, 250, 255)
        glass.draw_circular_button(tx + 72, ctrl_y + 20, 24, bg=play_bg, glow=glass.COMMA_GREEN_GLOW)
        self._draw_icon_centered("pause_dark.png" if is_playing else "play_dark.png", tx + 72, ctrl_y + 20, 22, glass.OBSIDIAN_BG)
        
        glass.draw_circular_button(tx + 124, ctrl_y + 20, 20)
        self._draw_icon_centered("skip-forward_white.png", tx + 124, ctrl_y + 20, 18, glass.TEXT_PRIMARY)
        
        # Mini Progress
        pb_w = card_w - 44
        pb_y = c0_y + card_h - 24
        rl.draw_rectangle_rounded(rl.Rectangle(c0_x + 22, pb_y, pb_w, 6), 1.0, 8, rl.Color(32, 36, 48, 255))
        prog_val = max(0.0, min(1.0, getattr(state, 'music_progress', 0.4)))
        rl.draw_rectangle_rounded(rl.Rectangle(c0_x + 22, pb_y, int(pb_w * prog_val), 6), 1.0, 8, glass.COMMA_GREEN)
        
        if clicked:
            if rl.check_collision_point_rec(mouse, rl.Rectangle(tx, ctrl_y, 40, 40)):
                state.music_track = (state.music_track - 1) % len(_TRACKS)
                state.music_artist, state.music_title = _TRACKS[state.music_track]
                state.music_progress = 0.0
            elif rl.check_collision_point_rec(mouse, rl.Rectangle(tx + 50, ctrl_y - 4, 48, 48)):
                state.music_playing = not state.music_playing
            elif rl.check_collision_point_rec(mouse, rl.Rectangle(tx + 104, ctrl_y, 40, 40)):
                state.music_track = (state.music_track + 1) % len(_TRACKS)
                state.music_artist, state.music_title = _TRACKS[state.music_track]
                state.music_progress = 0.0
            elif rl.check_collision_point_rec(mouse, rl.Rectangle(c0_x, c0_y, card_w, card_h)):
                self.active_tab = 1

        # ── 2. TRIP METRICS Glass Card ────────────────────────────────────────
        c1_x = margin_x + card_w + gap
        c1_y = sy
        self._draw_card(c1_x, c1_y, card_w, card_h)
        
        self._draw_icon("navigation_white.png", c1_x + 22, c1_y + 18, 16, glass.TEXT_MUTED)
        rl.draw_text_ex(self.fonts['xs'], "PASSENGER TRIP MONITOR", rl.Vector2(c1_x + 44, c1_y + 18), self.fonts['xs'].baseSize, 0, glass.TEXT_MUTED)
        
        dest = getattr(state, 'destination', "Downtown SF")
        rl.draw_text_ex(self.fonts['blg'], dest, rl.Vector2(c1_x + 22, c1_y + 46), self.fonts['blg'].baseSize, 0, glass.TEXT_PRIMARY)
        
        dist_str = f"{getattr(state, 'nav_remaining_mi', 12.4):.1f} mi remaining · US-101 N"
        rl.draw_text_ex(self.fonts['bmd'], dist_str, rl.Vector2(c1_x + 22, c1_y + 92), self.fonts['bmd'].baseSize, 0, glass.COMMA_GREEN)
        
        # Route progress bar
        r_bar_y = c1_y + 130
        rl.draw_rectangle_rounded(rl.Rectangle(c1_x + 22, r_bar_y, card_w - 44, 6), 1.0, 8, rl.Color(32, 36, 48, 255))
        rl.draw_rectangle_rounded(rl.Rectangle(c1_x + 22, r_bar_y, int((card_w - 44) * 0.65), 6), 1.0, 8, glass.SKY_BLUE)
        
        # ETA Pills
        pills_y = c1_y + card_h - 44
        pills = [("14 MIN", glass.COMMA_GREEN, glass.OBSIDIAN_BG), ("12.4 MI", glass.PILL_BG, glass.TEXT_PRIMARY), ("ETA 5:42 PM", glass.PILL_BG, glass.TEXT_PRIMARY)]
        p_x = c1_x + 22
        for text, p_bg, p_fg in pills:
            pts = rl.measure_text_ex(self.fonts['xs'], text, self.fonts['xs'].baseSize, 0)
            pw = pts.x + 22
            pill_r = rl.Rectangle(p_x, pills_y, pw, 28)
            is_act = (p_bg == glass.COMMA_GREEN)
            glass.draw_glass_pill(pill_r, roundness=0.5, bg=p_bg if is_act else None, active=is_act)
            rl.draw_text_ex(self.fonts['xs'], text, rl.Vector2(p_x + 11, pills_y + 6), self.fonts['xs'].baseSize, 0, p_fg)
            p_x += pw + 10

        # ── 3. REAR CLIMATE Glass Card ────────────────────────────────────────
        c2_x = margin_x
        c2_y = sy + card_h + gap
        self._draw_card(c2_x, c2_y, card_w, card_h)
        
        self._draw_icon("fan_white.png", c2_x + 22, c2_y + 18, 16, glass.TEXT_MUTED)
        rl.draw_text_ex(self.fonts['xs'], "REAR CLIMATE ZONE", rl.Vector2(c2_x + 44, c2_y + 18), self.fonts['xs'].baseSize, 0, glass.TEXT_MUTED)
        
        rear_t = int(getattr(state, 'rear_driver_temp', 71.0))
        rl.draw_text_ex(self.fonts['xl'], f"{rear_t}°", rl.Vector2(c2_x + 28, c2_y + 50), self.fonts['xl'].baseSize, 0, glass.TEXT_PRIMARY)
        rl.draw_text_ex(self.fonts['sm'], "Rear Comfort Auto Mode · Low Airflow", rl.Vector2(c2_x + 28, c2_y + 138), self.fonts['sm'].baseSize, 0, glass.TEXT_SECONDARY)
        
        # Circular Steppers
        rm_cx = c2_x + card_w - 130
        rp_cx = c2_x + card_w - 54
        glass.draw_circular_button(rm_cx, c2_y + 96, 26)
        glass.draw_circular_button(rp_cx, c2_y + 96, 26)
        self._draw_text_centered(self.fonts['blg'], "-", rm_cx, c2_y + 94, glass.TEXT_PRIMARY)
        self._draw_text_centered(self.fonts['blg'], "+", rp_cx, c2_y + 94, glass.TEXT_PRIMARY)
        
        if clicked:
            if rl.check_collision_point_rec(mouse, rl.Rectangle(rm_cx - 26, c2_y + 70, 52, 52)):
                state.rear_driver_temp = max(60, rear_t - 1)
            elif rl.check_collision_point_rec(mouse, rl.Rectangle(rp_cx - 26, c2_y + 70, 52, 52)):
                state.rear_driver_temp = min(85, rear_t + 1)

        # ── 4. ENTERTAINMENT LAUNCHER Glass Card ──────────────────────────────
        c3_x = margin_x + card_w + gap
        c3_y = sy + card_h + gap
        self._draw_card(c3_x, c3_y, card_w, card_h)
        
        self._draw_icon("activity_white.png", c3_x + 22, c3_y + 18, 16, glass.TEXT_MUTED)
        rl.draw_text_ex(self.fonts['xs'], "ENTERTAINMENT LAUNCHER", rl.Vector2(c3_x + 44, c3_y + 18), self.fonts['xs'].baseSize, 0, glass.TEXT_MUTED)
        
        btn_pong = rl.Rectangle(c3_x + 22, c3_y + 50, card_w - 44, 48)
        glass.draw_glass_pill(btn_pong, roundness=0.35, active=True, solid=True)
        self._draw_text_centered(self.fonts['bmd'], "PLAY RETRO PONG", btn_pong.x + btn_pong.width / 2, c3_y + 74, glass.OBSIDIAN_BG)
        
        btn_media = rl.Rectangle(c3_x + 22, c3_y + 112, card_w - 44, 48)
        glass.draw_glass_pill(btn_media, roundness=0.35)
        self._draw_text_centered(self.fonts['bmd'], "OPEN AUDIO PLAYER", btn_media.x + btn_media.width / 2, c3_y + 136, glass.TEXT_PRIMARY)
        
        if clicked:
            if rl.check_collision_point_rec(mouse, btn_pong):
                self.active_tab = 2
            elif rl.check_collision_point_rec(mouse, btn_media):
                self.active_tab = 1

    # ════════════════════════════════════════════════════════════════════════════
    # 2. MEDIA SCREEN - Glass Player & Frosted Queue
    # ════════════════════════════════════════════════════════════════════════════
    def _render_music(self, w, h, sy, sh, state, theme, mouse, clicked):
        col_gap = 20
        margin_x = 24
        left_w = int((w - margin_x * 2 - col_gap) * 0.58)
        right_w = w - margin_x * 2 - col_gap - left_w
        
        # Player Glass Card
        self._draw_card(margin_x, sy, left_w, sh)
        
        px = margin_x + 24
        py = sy + 24
        
        art_size = 180
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
        rl.draw_text_ex(self.fonts['xs'], "PASSENGER AUDIO STREAM", rl.Vector2(meta_x + 12, py + 8), self.fonts['xs'].baseSize, 0, glass.OBSIDIAN_BG)
        
        rl.draw_text_ex(self.fonts['blg'], getattr(state, 'music_title', "Los Angeles"), rl.Vector2(meta_x, py + 38), self.fonts['blg'].baseSize, 0, glass.TEXT_PRIMARY)
        rl.draw_text_ex(self.fonts['bmd'], getattr(state, 'music_artist', "The Midnight"), rl.Vector2(meta_x, py + 92), self.fonts['bmd'].baseSize, 0, glass.TEXT_SECONDARY)
        rl.draw_text_ex(self.fonts['xs'], "Master Quality · 96kHz 24-bit Lossless", rl.Vector2(meta_x, py + 132), self.fonts['xs'].baseSize, 0, glass.SKY_BLUE)
        
        # Scrubber
        bar_y = py + art_size + 34
        bar_w = left_w - 48
        bar_rect = rl.Rectangle(px, bar_y - 10, bar_w, 28)
        if clicked and rl.check_collision_point_rec(mouse, bar_rect):
            state.music_progress = max(0.0, min(1.0, (mouse.x - px) / bar_w))
            
        rl.draw_rectangle_rounded(rl.Rectangle(px, bar_y, bar_w, 8), 1.0, 16, rl.Color(32, 36, 48, 255))
        prog_val = max(0.0, min(1.0, getattr(state, 'music_progress', 0.4)))
        prog_w = int(bar_w * prog_val)
        rl.draw_rectangle_rounded(rl.Rectangle(px, bar_y, prog_w, 8), 1.0, 16, glass.COMMA_GREEN)
        rl.draw_circle(int(px + prog_w), int(bar_y + 4), 9, glass.TEXT_PRIMARY)
        
        total_sec = 225
        curr_sec = int(prog_val * total_sec)
        t_curr = f"{curr_sec // 60}:{curr_sec % 60:02d}"
        t_rem = f"-{(total_sec - curr_sec) // 60}:{(total_sec - curr_sec) % 60:02d}"
        rl.draw_text_ex(self.fonts['sm'], t_curr, rl.Vector2(px, bar_y + 14), self.fonts['sm'].baseSize, 0, glass.TEXT_MUTED)
        ts_rem = rl.measure_text_ex(self.fonts['sm'], t_rem, self.fonts['sm'].baseSize, 0)
        rl.draw_text_ex(self.fonts['sm'], t_rem, rl.Vector2(px + bar_w - ts_rem.x, bar_y + 14), self.fonts['sm'].baseSize, 0, glass.TEXT_MUTED)
        
        # Circular Transport controls
        btn_y = bar_y + 54
        btn_cx = px + bar_w / 2
        
        glass.draw_circular_button(btn_cx - 96, btn_y + 32, 26)
        self._draw_icon_centered("skip-back_white.png", btn_cx - 96, btn_y + 32, 24, glass.TEXT_PRIMARY)
        
        is_playing = getattr(state, 'music_playing', True)
        play_hero_col = glass.COMMA_GREEN if not is_playing else rl.Color(250, 250, 250, 255)
        glass.draw_circular_button(btn_cx, btn_y + 32, 34, bg=play_hero_col, glow=glass.COMMA_GREEN_GLOW)
        self._draw_icon_centered("pause_dark.png" if is_playing else "play_dark.png", btn_cx, btn_y + 32, 30, glass.OBSIDIAN_BG)
        
        glass.draw_circular_button(btn_cx + 96, btn_y + 32, 26)
        self._draw_icon_centered("skip-forward_white.png", btn_cx + 96, btn_y + 32, 24, glass.TEXT_PRIMARY)
        
        # Volume Bar
        vol_y = btn_y + 88
        self._draw_icon("volume-2_white.png", px + 20, vol_y - 2, 20, glass.TEXT_PRIMARY)
        vol_bar_x = px + 54
        vol_bar_w = bar_w - 80
        rl.draw_rectangle_rounded(rl.Rectangle(vol_bar_x, vol_y + 4, vol_bar_w, 6), 1.0, 16, rl.Color(32, 36, 48, 255))
        rl.draw_rectangle_rounded(rl.Rectangle(vol_bar_x, vol_y + 4, int(vol_bar_w * 0.75), 6), 1.0, 16, glass.TEXT_PRIMARY)
        rl.draw_circle(int(vol_bar_x + vol_bar_w * 0.75), int(vol_y + 7), 8, glass.TEXT_PRIMARY)
        
        # ── Up Next Queue Glass Card ──────────────────────────────────────────
        q_x = margin_x + left_w + col_gap
        self._draw_card(q_x, sy, right_w, sh)
        
        rl.draw_text_ex(self.fonts['xs'], "UP NEXT IN QUEUE", rl.Vector2(q_x + 22, sy + 20), self.fonts['xs'].baseSize, 0, glass.TEXT_MUTED)
        
        for idx, (artist, title) in enumerate(_TRACKS):
            item_y = sy + 54 + idx * 76
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
            
            dur = ["3:45", "4:12", "3:58", "4:30", "3:15"][idx]
            rl.draw_text_ex(self.fonts['xs'], dur, rl.Vector2(item_rect.x + item_rect.width - 48, item_rect.y + 24), self.fonts['xs'].baseSize, 0, glass.TEXT_MUTED)
            
        if clicked:
            if rl.check_collision_point_rec(mouse, rl.Rectangle(btn_cx - 122, btn_y + 6, 52, 52)):
                state.music_track = (state.music_track - 1) % len(_TRACKS)
                state.music_artist, state.music_title = _TRACKS[state.music_track]
                state.music_progress = 0.0
            elif rl.check_collision_point_rec(mouse, rl.Rectangle(btn_cx - 34, btn_y - 2, 68, 68)):
                state.music_playing = not state.music_playing
            elif rl.check_collision_point_rec(mouse, rl.Rectangle(btn_cx + 70, btn_y + 6, 52, 52)):
                state.music_track = (state.music_track + 1) % len(_TRACKS)
                state.music_artist, state.music_title = _TRACKS[state.music_track]
                state.music_progress = 0.0

    # ════════════════════════════════════════════════════════════════════════════
    # 3. GAMES SCREEN - Cyberpunk Neon Glass Pong Court
    # ════════════════════════════════════════════════════════════════════════════
    def _render_pong(self, w, h, sy, sh, state, theme, dt):
        margin_x = 24
        court_w = w - margin_x * 2
        court_rect = rl.Rectangle(margin_x, sy, court_w, sh)
        
        # Frosted glass court
        glass.draw_glass_card(court_rect, roundness=0.35, bg=rl.Color(14, 16, 22, 240))
        
        self.pong.update(dt, h, w, sy + 16, sy + sh - 16)
        
        # Center Court Luminous Net
        for ny in range(int(sy + 20), int(sy + sh - 20), 32):
            glass.draw_glass_pill(rl.Rectangle(w//2 - 2, ny, 4, 16), roundness=0.5, bg=rl.Color(60, 70, 90, 200))
            
        # Floating Score Board Pill
        score_w = 260
        score_h = 44
        score_r = rl.Rectangle(w / 2 - score_w / 2, sy + 18, score_w, score_h)
        glass.draw_glass_pill(score_r, roundness=0.5, bg=rl.Color(20, 24, 34, 220))
        
        font_score = self.fonts.get('blg', self.fonts['md'])
        s_p1 = f"P1: {self.pong.p1_score}"
        s_p2 = f"P2: {self.pong.p2_score}"
        rl.draw_text_ex(font_score, s_p1, rl.Vector2(score_r.x + 30, sy + 26), font_score.baseSize, 0, glass.COMMA_GREEN)
        rl.draw_text_ex(self.fonts['md'], "·", rl.Vector2(w / 2 - 4, sy + 24), self.fonts['md'].baseSize, 0, glass.TEXT_MUTED)
        rl.draw_text_ex(font_score, s_p2, rl.Vector2(score_r.x + score_w - 100, sy + 26), font_score.baseSize, 0, glass.SKY_BLUE)
        
        # Instruction Pill
        inst_r = rl.Rectangle(w / 2 - 180, sy + sh - 40, 360, 26)
        glass.draw_glass_pill(inst_r, roundness=0.5)
        self._draw_text_centered(self.fonts['xs'], "TOUCH OR DRAG LEFT PADDLE TO PLAY", w / 2, sy + sh - 27, glass.TEXT_MUTED)
        
        # Paddles with glowing aura
        p1_r = rl.Rectangle(margin_x + 36, self.pong.p1_y - self.pong.PAD_H/2, self.pong.PAD_W, self.pong.PAD_H)
        p2_r = rl.Rectangle(w - margin_x - 36 - self.pong.PAD_W, self.pong.p2_y - self.pong.PAD_H/2, self.pong.PAD_W, self.pong.PAD_H)
        
        rl.draw_rectangle_rounded(rl.Rectangle(p1_r.x - 3, p1_r.y - 3, p1_r.width + 6, p1_r.height + 6), 0.5, 8, glass.COMMA_GREEN_GLOW)
        rl.draw_rectangle_rounded(p1_r, 0.5, 8, glass.COMMA_GREEN)
        
        rl.draw_rectangle_rounded(rl.Rectangle(p2_r.x - 3, p2_r.y - 3, p2_r.width + 6, p2_r.height + 6), 0.5, 8, glass.SKY_BLUE_GLOW)
        rl.draw_rectangle_rounded(p2_r, 0.5, 8, glass.SKY_BLUE)
        
        # Ball with glowing halo
        bx = int(self.pong.ball_pos[0])
        by = int(self.pong.ball_pos[1])
        rl.draw_circle(bx, by, float(self.pong.BALL_R) + 6, glass.COMMA_GREEN_GLOW)
        rl.draw_circle(bx, by, float(self.pong.BALL_R), glass.TEXT_PRIMARY)
        
        # AI for P2
        if self.pong.ball_pos[1] > self.pong.p2_y:
            self.pong.p2_y += self.pong.PAD_SPEED * dt
        elif self.pong.ball_pos[1] < self.pong.p2_y:
            self.pong.p2_y -= self.pong.PAD_SPEED * dt
            
        self.pong.p2_y = max(sy + 16 + self.pong.PAD_H/2, min(sy + sh - 16 - self.pong.PAD_H/2, self.pong.p2_y))

    # ════════════════════════════════════════════════════════════════════════════
    # 4. TRIP MONITOR SCREEN - Frosted Cards
    # ════════════════════════════════════════════════════════════════════════════
    def _render_trip(self, w, h, sy, sh, state, theme):
        font_lbl = self.fonts.get('blg', self.fonts['md'])
        font_val = self.fonts.get('bmd', self.fonts['md'])
        margin_x = 36
        
        stats = [
            ("Trip Remaining", f"{getattr(state, 'nav_remaining_mi', 12.4):.1f} mi"),
            ("Trip Odometer", f"{getattr(state, 'trip_distance_mi', 127.4):.1f} mi"),
            ("Time to Destination", f"{getattr(state, 'eta_seconds', 840) // 60} min"),
            ("Estimated Arrival", "5:42 PM"),
            ("Average Cruising Speed", f"{int(getattr(state, 'speed_mph', 65))} mph"),
        ]
        
        for i, (lbl, val) in enumerate(stats):
            ry = sy + i * 82
            rect = rl.Rectangle(margin_x, ry, w - margin_x * 2, 70)
            self._draw_card(rect.x, rect.y, rect.width, rect.height)
            rl.draw_text_ex(font_lbl, lbl, rl.Vector2(margin_x + 32, ry + 16), font_lbl.baseSize, 0, glass.TEXT_PRIMARY)
            ts = rl.measure_text_ex(font_val, val, font_val.baseSize, 0)
            rl.draw_text_ex(font_val, val, rl.Vector2(w - margin_x - 32 - ts.x, ry + 18), font_val.baseSize, 0, glass.COMMA_GREEN)

    # ════════════════════════════════════════════════════════════════════════════
    # 5. CLIMATE SCREEN - Rear Dual Zones with Steppers
    # ════════════════════════════════════════════════════════════════════════════
    def _render_climate(self, w, h, sy, sh, state, theme, mouse, clicked):
        margin_x = 36
        gap = 24
        card_w = (w - margin_x * 2 - gap) / 2
        card_h = sh * 0.76
        cy = sy + (sh - card_h) / 2
        
        font_temp = self.fonts.get('bxl', self.fonts['xl'])
        
        for i, zone in enumerate(["REAR LEFT ZONE", "REAR RIGHT ZONE"]):
            cx = margin_x + i * (card_w + gap)
            self._draw_card(cx, cy, card_w, card_h)
            
            self._draw_icon("fan_white.png", cx + 24, cy + 22, 18, glass.TEXT_MUTED)
            rl.draw_text_ex(self.fonts['sm'], zone, rl.Vector2(cx + 48, cy + 22), self.fonts['sm'].baseSize, 0, glass.TEXT_MUTED)
            
            temp_val = int(getattr(state, 'rear_driver_temp' if i == 0 else 'rear_pass_temp', 71))
            temp_str = f"{temp_val}°"
            ts = rl.measure_text_ex(font_temp, temp_str, font_temp.baseSize, 0)
            rl.draw_text_ex(font_temp, temp_str, rl.Vector2(cx + (card_w - ts.x)/2, cy + (card_h - ts.y)/2 - 36), font_temp.baseSize, 0, glass.TEXT_PRIMARY)
            
            # Steppers
            btn_m_cx = cx + card_w/2 - 64
            btn_p_cx = cx + card_w/2 + 64
            btn_y = cy + card_h - 70
            glass.draw_circular_button(btn_m_cx, btn_y, 28)
            glass.draw_circular_button(btn_p_cx, btn_y, 28)
            self._draw_text_centered(self.fonts['blg'], "-", btn_m_cx, btn_y - 2, glass.TEXT_PRIMARY)
            self._draw_text_centered(self.fonts['blg'], "+", btn_p_cx, btn_y - 2, glass.TEXT_PRIMARY)
            
            if clicked:
                if rl.check_collision_point_rec(mouse, rl.Rectangle(btn_m_cx - 28, btn_y - 28, 56, 56)):
                    if i == 0: state.rear_driver_temp = max(60, temp_val - 1)
                    else: state.rear_pass_temp = max(60, temp_val - 1)
                elif rl.check_collision_point_rec(mouse, rl.Rectangle(btn_p_cx - 28, btn_y - 28, 56, 56)):
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

import pyray as rl
import math
import os

_TRACKS = [
    ("The Midnight", "Los Angeles"),
    ("Tycho", "Awake"),
    ("Bonobo", "Kong"),
    ("Polo & Pan", "Canop\u00e9e"),
    ("Washed Out", "Feel It All Around")
]

class PongGame:
    BALL_SPEED = 300.0
    PAD_SPEED  = 280.0
    PAD_W, PAD_H = 16, 100
    BALL_R = 12

    def __init__(self):
        self.reset()
        
    def reset(self):
        self.bx, self.by = 0.5, 0.5 # Relative to screen width/height for simplicity, but wait, usually physics uses pixels. Let's use proportional to window.
        self.vx = self.BALL_SPEED
        self.vy = self.BALL_SPEED
        # Instead, let's just keep physics in pixels and update bounds on render.
        self.ball_pos = [640, 360]
        self.ball_vel = [self.BALL_SPEED, self.BALL_SPEED]
        self.p1_y = 360
        self.p2_y = 360
        self.p1_score = 0
        self.p2_score = 0

    def update(self, dt, h, w):
        # basic update
        self.ball_pos[0] += self.ball_vel[0] * dt
        self.ball_pos[1] += self.ball_vel[1] * dt

        if self.ball_pos[1] - self.BALL_R <= 0 or self.ball_pos[1] + self.BALL_R >= h:
            self.ball_vel[1] *= -1
            
        # P1 paddle collision
        p1_rect = rl.Rectangle(50, self.p1_y - self.PAD_H/2, self.PAD_W, self.PAD_H)
        if rl.check_collision_circle_rec(rl.Vector2(self.ball_pos[0], self.ball_pos[1]), self.BALL_R, p1_rect):
            self.ball_vel[0] *= -1
            self.ball_pos[0] = 50 + self.PAD_W + self.BALL_R
            
        # P2 paddle collision
        p2_rect = rl.Rectangle(w - 50 - self.PAD_W, self.p2_y - self.PAD_H/2, self.PAD_W, self.PAD_H)
        if rl.check_collision_circle_rec(rl.Vector2(self.ball_pos[0], self.ball_pos[1]), self.BALL_R, p2_rect):
            self.ball_vel[0] *= -1
            self.ball_pos[0] = w - 50 - self.PAD_W - self.BALL_R

        # Score
        if self.ball_pos[0] < 0:
            self.p2_score += 1
            self.ball_pos = [w/2, h/2]
        elif self.ball_pos[0] > w:
            self.p1_score += 1
            self.ball_pos = [w/2, h/2]

class RearSurface:
    def __init__(self, fonts: dict):
        self.fonts = fonts
        self.pong = PongGame()
        self.tabs = ["Home", "Video", "Music", "Pong", "Trip", "Climate"]
        self.active_tab = 0
        self.textures = {}
        # Try loading textures if paths exist, else None
        # In a real app we'd load them properly
    
    def render(self, state, theme):
        w = rl.get_screen_width()
        h = rl.get_screen_height()
        dt = rl.get_frame_time()
        
        # Ensure we sync app with tab
        state.rear_app = self.active_tab
        
        # Tabs
        tab_h = h * 0.08
        tab_y = 16
        tab_w = 160
        tab_height = 56
        gap = 16
        total_w = len(self.tabs) * tab_w + (len(self.tabs) - 1) * gap
        start_x = (w - total_w) / 2
        
        # Touch / Click tab selection
        clicked = rl.is_mouse_button_pressed(rl.MouseButton.MOUSE_BUTTON_LEFT)
        mouse = rl.get_mouse_position()
        
        for i, tab in enumerate(self.tabs):
            x = start_x + i * (tab_w + gap)
            rect = rl.Rectangle(x, tab_y, tab_w, tab_height)
            if clicked and rl.check_collision_point_rec(mouse, rect):
                self.active_tab = i
                
            if i == self.active_tab:
                bg = rl.Color(51, 171, 76, 255) # #33ab4c
                font = self.fonts.get('bmd', self.fonts.get('md', rl.get_font_default()))
                text_col = rl.BLACK
            else:
                bg = rl.Color(41, 41, 41, 255) # #292929
                font = self.fonts.get('sm', rl.get_font_default())
                text_col = rl.Color(170, 170, 170, 255) # #AAAAAA
                
            rl.draw_rectangle_rounded(rect, 0.5, 32, bg)
            
            ts = rl.measure_text_ex(font, tab, font.baseSize, 1)
            tx = x + (tab_w - ts.x) / 2
            ty = tab_y + (tab_height - ts.y) / 2
            rl.draw_text_ex(font, tab, rl.Vector2(tx, ty), font.baseSize, 1, text_col)

        app_area_y = tab_y + tab_height + 32
        app_area_h = h - app_area_y - 32

        # Touch paddle control in Pong
        if self.active_tab == 3 and rl.is_mouse_button_down(rl.MouseButton.MOUSE_BUTTON_LEFT):
            if mouse.x < w * 0.35:
                self.pong.p1_pos = max(0.0, min(float(h - self.pong.PAD_H), float(mouse.y - self.pong.PAD_H / 2)))
        
        if self.active_tab == 0:
            self._render_home(w, h, app_area_y, app_area_h, state, theme)
        elif self.active_tab == 2:
            self._render_music(w, h, app_area_y, app_area_h, state, theme)
        elif self.active_tab == 3:
            self._render_pong(w, h, app_area_y, app_area_h, state, theme, dt)
        elif self.active_tab == 4:
            self._render_trip(w, h, app_area_y, app_area_h, state, theme)
        elif self.active_tab == 5:
            self._render_climate(w, h, app_area_y, app_area_h, state, theme)

    def _render_home(self, w, h, sy, sh, state, theme):
        gap = 16
        card_w = (w - 64 - gap) / 2
        card_h = (sh - gap) / 2
        bg = rl.Color(41, 41, 41, 255)
        
        # 4 Cards
        for i in range(4):
            cx = 32 + (i % 2) * (card_w + gap)
            cy = sy + (i // 2) * (card_h + gap)
            rl.draw_rectangle_rounded(rl.Rectangle(cx, cy, card_w, card_h), 0.35, 32, bg)
            
            if i == 0:
                # NOW PLAYING
                font_title = self.fonts.get('blg', rl.get_font_default())
                font_artist = self.fonts.get('md', rl.get_font_default())
                rl.draw_text_ex(font_title, state.music_title or "Track Title", rl.Vector2(cx + 192, cy + 32), font_title.baseSize, 1, rl.WHITE)
                rl.draw_text_ex(font_artist, state.music_artist or "Artist", rl.Vector2(cx + 192, cy + 80), font_artist.baseSize, 1, rl.Color(170, 170, 170, 255))
            elif i == 1:
                # TRIP INFO
                font_val = self.fonts.get('blg', rl.get_font_default())
                font_lbl = self.fonts.get('md', rl.get_font_default())
                dist = f"{getattr(state, 'trip_distance_mi', 0.0):.1f} mi"
                eta = f"ETA {getattr(state, 'eta_seconds', 0) // 60} min"
                rl.draw_text_ex(font_val, dist, rl.Vector2(cx + 32, cy + 32), font_val.baseSize, 1, rl.WHITE)
                rl.draw_text_ex(font_lbl, eta, rl.Vector2(cx + 32, cy + 96), font_lbl.baseSize, 1, rl.Color(170, 170, 170, 255))
            elif i == 2:
                # REAR CLIMATE
                font_temp = self.fonts.get('xl', rl.get_font_default())
                temp = f"{int(getattr(state, 'rear_temp_f', 72))}\u00b0"
                rl.draw_text_ex(font_temp, temp, rl.Vector2(cx + 32, cy + 32), font_temp.baseSize, 1, rl.WHITE)
                # Buttons
                rl.draw_circle(int(cx + card_w - 64 - 80), int(cy + card_h/2), 32, rl.Color(80, 80, 80, 255))
                rl.draw_circle(int(cx + card_w - 64), int(cy + card_h/2), 32, rl.Color(80, 80, 80, 255))
            elif i == 3:
                # QUICK LAUNCH
                rl.draw_rectangle_rounded(rl.Rectangle(cx + 32, cy + 32, card_w - 64, 80), 0.5, 32, rl.Color(51, 171, 76, 255))
                rl.draw_rectangle_rounded(rl.Rectangle(cx + 32, cy + 128, card_w - 64, 80), 0.5, 32, rl.Color(80, 80, 80, 255))

    def _render_music(self, w, h, sy, sh, state, theme):
        font_trk = self.fonts.get('xl', rl.get_font_default())
        font_art = self.fonts.get('lg', rl.get_font_default())
        
        art_w = w * 0.4
        rl.draw_rectangle(32, int(sy + (sh - art_w)/2), int(art_w), int(art_w), rl.Color(41, 41, 41, 255))
        
        tx = 32 + art_w + 64
        rl.draw_text_ex(font_trk, state.music_title or "Track", rl.Vector2(tx, sy + 100), font_trk.baseSize, 1, rl.WHITE)
        rl.draw_text_ex(font_art, state.music_artist or "Artist", rl.Vector2(tx, sy + 200), font_art.baseSize, 1, rl.Color(170, 170, 170, 255))
        
        # Progress
        py = sy + sh - 100
        rl.draw_rectangle(int(tx), int(py), int(w - tx - 64), 12, rl.Color(80, 80, 80, 255))
        rl.draw_rectangle(int(tx), int(py), int((w - tx - 64) * 0.4), 12, rl.Color(70, 91, 234, 255)) # #465bea
        
        # Transport
        for i in range(3):
            rl.draw_rectangle_rounded(rl.Rectangle(tx + i * 100, py - 120, 80, 80), 0.5, 32, rl.Color(41, 41, 41, 255))

    def _render_pong(self, w, h, sy, sh, state, theme, dt):
        self.pong.update(dt, h, w)
        
        # Center line
        for y in range(0, h, 40):
            rl.draw_rectangle(w//2 - 2, y, 4, 20, rl.Color(80, 80, 80, 255))
            
        # Score
        font_score = self.fonts.get('xl', rl.get_font_default())
        score = f"{self.pong.p1_score}   {self.pong.p2_score}"
        ts = rl.measure_text_ex(font_score, score, font_score.baseSize, 1)
        rl.draw_text_ex(font_score, score, rl.Vector2((w - ts.x)/2, 64), font_score.baseSize, 1, rl.WHITE)
        
        # Paddles
        p1_r = rl.Rectangle(50, self.pong.p1_y - self.pong.PAD_H/2, self.pong.PAD_W, self.pong.PAD_H)
        p2_r = rl.Rectangle(w - 50 - self.pong.PAD_W, self.pong.p2_y - self.pong.PAD_H/2, self.pong.PAD_W, self.pong.PAD_H)
        rl.draw_rectangle_rounded(p1_r, 0.3, 32, rl.WHITE)
        rl.draw_rectangle_rounded(p2_r, 0.3, 32, rl.WHITE)
        
        # Ball
        rl.draw_circle(int(self.pong.ball_pos[0]), int(self.pong.ball_pos[1]), float(self.pong.BALL_R), rl.WHITE)
        
        # Auto-play for P2 (simple AI)
        if self.pong.ball_pos[1] > self.pong.p2_y:
            self.pong.p2_y += self.pong.PAD_SPEED * dt
        elif self.pong.ball_pos[1] < self.pong.p2_y:
            self.pong.p2_y -= self.pong.PAD_SPEED * dt

    def _render_trip(self, w, h, sy, sh, state, theme):
        font_lbl = self.fonts.get('blg', rl.get_font_default())
        font_val = self.fonts.get('md', rl.get_font_default())
        
        stats = [
            ("Distance", f"{getattr(state, 'trip_distance_mi', 0.0):.1f} mi"),
            ("Time", f"{getattr(state, 'eta_seconds', 0) // 60} min"),
            ("Avg Speed", "45 mph")
        ]
        
        for i, (lbl, val) in enumerate(stats):
            ry = sy + i * 96
            rl.draw_rectangle_rounded(rl.Rectangle(64, ry, w - 128, 80), 0.3, 32, rl.Color(41, 41, 41, 255))
            rl.draw_text_ex(font_lbl, lbl, rl.Vector2(96, ry + 16), font_lbl.baseSize, 1, rl.WHITE)
            ts = rl.measure_text_ex(font_val, val, font_val.baseSize, 1)
            rl.draw_text_ex(font_val, val, rl.Vector2(w - 64 - 32 - ts.x, ry + 24), font_val.baseSize, 1, rl.Color(170, 170, 170, 255))

    def _render_climate(self, w, h, sy, sh, state, theme):
        card_w = (w - 128 - 32) / 2
        card_h = sh * 0.6
        cy = sy + (sh - card_h) / 2
        
        font_temp = self.fonts.get('bxl', rl.get_font_default())
        
        for i in range(2):
            cx = 64 + i * (card_w + 32)
            rl.draw_rectangle_rounded(rl.Rectangle(cx, cy, card_w, card_h), 0.35, 32, rl.Color(41, 41, 41, 255))
            
            temp = f"72\u00b0"
            ts = rl.measure_text_ex(font_temp, temp, font_temp.baseSize, 1)
            rl.draw_text_ex(font_temp, temp, rl.Vector2(cx + (card_w - ts.x)/2, cy + (card_h - ts.y)/2), font_temp.baseSize, 1, rl.WHITE)
            
            # +/- Buttons
            rl.draw_circle(int(cx + card_w/2 - 80), int(cy + card_h - 60), 40, rl.Color(80, 80, 80, 255))
            rl.draw_circle(int(cx + card_w/2 + 80), int(cy + card_h - 60), 40, rl.Color(80, 80, 80, 255))

    def handle_key(self, key: int, state, theme):
        if key == rl.KEY_TAB:
            self.active_tab = (self.active_tab + 1) % len(self.tabs)
        elif key == rl.KEY_RIGHT:
            self.active_tab = (self.active_tab + 1) % len(self.tabs)
        elif key == rl.KEY_LEFT:
            self.active_tab = (self.active_tab - 1) % len(self.tabs)
            
        if self.active_tab == 3:
            if key == rl.KEY_UP:
                self.pong.p1_y -= 40
            elif key == rl.KEY_DOWN:
                self.pong.p1_y += 40

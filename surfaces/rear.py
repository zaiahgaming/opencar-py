# surfaces/rear.py — Rear Entertainment Surface for OpenCar
# Window: 1280×480  |  Python 3 + pyray (raylib 6.0)

import math
import random
import time

import pyray as rl


# ---------------------------------------------------------------------------
# Helper: draw a simple "DVD" logotype using basic shapes
# ---------------------------------------------------------------------------

def _measure(fonts, key, text, size, spacing=2):
    """Return measured Vector2 for text."""
    return rl.measure_text_ex(fonts[key], text, size, spacing)


def _draw_text(fonts, key, text, x, y, size, color, spacing=2):
    rl.draw_text_ex(fonts[key], text, rl.Vector2(x, y), size, spacing, color)


def _draw_text_centered(fonts, key, text, cx, y, size, color, spacing=2):
    v = rl.measure_text_ex(fonts[key], text, size, spacing)
    rl.draw_text_ex(fonts[key], text, rl.Vector2(cx - v.x / 2, y), size, spacing, color)


def _fmt_eta(seconds):
    """Format seconds as '1h 22m' or '45m'."""
    h = int(seconds) // 3600
    m = (int(seconds) % 3600) // 60
    if h > 0:
        return f"{h}h {m:02d}m"
    return f"{m}m"


def _fmt_duration(seconds):
    """Format elapsed seconds as 'H:MM:SS'."""
    h = int(seconds) // 3600
    m = (int(seconds) % 3600) // 60
    s = int(seconds) % 60
    return f"{h}:{m:02d}:{s:02d}"


# ---------------------------------------------------------------------------
# PongGame — fully playable Pong with physics
# ---------------------------------------------------------------------------

class PongGame:
    BALL_SPEED = 300.0
    PAD_SPEED  = 280.0
    PAD_W, PAD_H = 12, 80
    BALL_R = 8

    def __init__(self):
        self.score_p  = 0
        self.score_ai = 0
        self.player_y = 240 - 40
        self.ai_y     = 240 - 40
        self.reset_ball()

    def reset_ball(self):
        angle = random.uniform(-0.5, 0.5)
        dir_x = random.choice([-1, 1])
        self.bx  = 640.0
        self.by  = 240.0
        self.bvx = dir_x * self.BALL_SPEED * math.cos(angle)
        self.bvy = self.BALL_SPEED * math.sin(angle)

    def update(self, dt, up_held, down_held):
        # Player paddle
        if up_held:   self.player_y -= self.PAD_SPEED * dt
        if down_held: self.player_y += self.PAD_SPEED * dt
        self.player_y = max(0, min(480 - self.PAD_H, self.player_y))

        # AI paddle tracks ball with speed lag
        ai_center = self.ai_y + self.PAD_H / 2
        diff = self.by - ai_center
        move = min(abs(diff), self.PAD_SPEED * 0.7 * dt) * (1 if diff > 0 else -1)
        self.ai_y += move
        self.ai_y = max(0, min(480 - self.PAD_H, self.ai_y))

        # Ball movement
        self.bx += self.bvx * dt
        self.by += self.bvy * dt

        # Wall bounce top / bottom
        if self.by - self.BALL_R < 0:
            self.by = float(self.BALL_R)
            self.bvy = abs(self.bvy)
        if self.by + self.BALL_R > 480:
            self.by = 480.0 - self.BALL_R
            self.bvy = -abs(self.bvy)

        # Player paddle collision (left side)
        px = 30 + self.PAD_W
        if (self.bx - self.BALL_R < px and
                self.by > self.player_y and
                self.by < self.player_y + self.PAD_H and
                self.bvx < 0):
            self.bvx = abs(self.bvx) * 1.05
            rel = (self.by - (self.player_y + self.PAD_H / 2)) / (self.PAD_H / 2)
            self.bvy = rel * self.BALL_SPEED * 1.2

        # AI paddle collision (right side)
        ax = 1280 - 30 - self.PAD_W
        if (self.bx + self.BALL_R > ax and
                self.by > self.ai_y and
                self.by < self.ai_y + self.PAD_H and
                self.bvx > 0):
            self.bvx = -abs(self.bvx) * 1.05
            rel = (self.by - (self.ai_y + self.PAD_H / 2)) / (self.PAD_H / 2)
            self.bvy = rel * self.BALL_SPEED * 1.2

        # Scoring
        if self.bx < 0:
            self.score_ai += 1
            self.reset_ball()
            return 'ai'
        if self.bx > 1280:
            self.score_p += 1
            self.reset_ball()
            return 'player'
        return None

    def draw(self, fonts, theme):
        # Dark court background
        rl.clear_background(rl.Color(5, 5, 10, 255))

        # Center dashed line
        for y in range(0, 480, 20):
            rl.draw_rectangle(638, y, 4, 10, rl.Color(60, 60, 60, 255))

        # Score display
        score_txt = f"{self.score_p}  {self.score_ai}"
        v = rl.measure_text_ex(fonts['lg'], score_txt, 48, 4)
        rl.draw_text_ex(fonts['lg'], score_txt,
                        rl.Vector2(640 - v.x / 2, 20), 48, 4,
                        rl.Color(80, 80, 80, 255))

        # Player / CPU labels
        rl.draw_text_ex(fonts['xs'], "YOU",
                        rl.Vector2(10, 10), 13, 1, theme.fg2)
        rl.draw_text_ex(fonts['xs'], "CPU",
                        rl.Vector2(1250, 10), 13, 1, theme.fg2)

        # Player paddle (accent)
        rl.draw_rectangle_rounded(
            rl.Rectangle(30, self.player_y, self.PAD_W, self.PAD_H),
            0.3, 4, theme.accent)

        # AI paddle (warn orange)
        rl.draw_rectangle_rounded(
            rl.Rectangle(1280 - 30 - self.PAD_W, self.ai_y,
                         self.PAD_W, self.PAD_H),
            0.3, 4, theme.warn)

        # Ball
        rl.draw_circle(int(self.bx), int(self.by), self.BALL_R, rl.WHITE)

        # Controls hint at bottom
        rl.draw_text_ex(fonts['xs'],
                        "\u2191\u2193 Move   R=Reset   Backspace=Back",
                        rl.Vector2(10, 458), 13, 1,
                        rl.Color(50, 50, 50, 255))


# ---------------------------------------------------------------------------
# RearSurface
# ---------------------------------------------------------------------------

class RearSurface:
    # Chapter data for video screen
    CHAPTERS = [
        ("The Journey Begins",  "18:42"),
        ("Desert Highway",       "22:15"),
        ("Night Drive",          "19:55"),
        ("City of Lights",       "25:10"),
        ("Homecoming",           "21:33"),
    ]

    def __init__(self, fonts):
        self.fonts = fonts
        self.screen = 0          # 0=home 1=video 2=music 3=pong 4=trip 5=climate

        # ---- Home state ----
        self.playing = True

        # ---- Video state ----
        self.video_playing   = True
        self.video_progress  = 0.0    # 0.0–1.0
        self.video_chapter   = 0      # current chapter index
        self.video_focused   = 2      # focused transport button 0..4
        # Transport labels: rewind | prev | stop | play | ffwd
        self._transport_labels = ["\u23ee", "\u25c0", "\u25a0", "\u25b6", "\u23ed"]

        # ---- DVD bounce state ----
        self.dvd_mode  = False
        self.dvd_x     = 100.0
        self.dvd_y     = 100.0
        self.dvd_vx    = 1.0
        self.dvd_vy    = 0.7
        self.dvd_color = rl.Color(99, 179, 237, 255)  # start accent

        # ---- Music screen ----
        self._waveform_offsets = [random.uniform(0, math.pi * 2) for _ in range(32)]

        # ---- Pong ----
        self.pong = PongGame()

        # ---- Trip ----
        self._trip_start = time.time()

        # ---- Climate ----
        self._climate_sel = 0   # 0=left zone, 1=right zone

    # -----------------------------------------------------------------------
    # handle_key
    # -----------------------------------------------------------------------

    def handle_key(self, key, state, theme):
        K = rl.KeyboardKey

        # Global: Backspace always returns home and exits DVD mode
        if key == K.KEY_BACKSPACE:
            self.screen   = 0
            self.dvd_mode = False
            return

        if self.screen == 0:
            # Navigate to sub-screens
            if key == K.KEY_V: self.screen = 1
            if key == K.KEY_M: self.screen = 2
            if key == K.KEY_G: self.screen = 3
            if key == K.KEY_I: self.screen = 4
            if key == K.KEY_C: self.screen = 5
            if key == K.KEY_SPACE:
                self.playing = not self.playing

        elif self.screen == 1:  # video
            if key == K.KEY_D:
                self.dvd_mode = not self.dvd_mode
            if key == K.KEY_SPACE:
                self.video_playing = not self.video_playing
            if not self.dvd_mode:
                if key == K.KEY_LEFT:
                    self.video_focused = max(0, self.video_focused - 1)
                if key == K.KEY_RIGHT:
                    self.video_focused = min(4, self.video_focused + 1)
                if key == K.KEY_ENTER:
                    self._activate_transport(state)
                if key == K.KEY_UP:
                    self.video_chapter = max(0, self.video_chapter - 1)
                if key == K.KEY_DOWN:
                    self.video_chapter = min(len(self.CHAPTERS) - 1,
                                             self.video_chapter + 1)

        elif self.screen == 2:  # music
            if key == K.KEY_SPACE:
                state.set('music_playing', not state.music_playing)

        elif self.screen == 3:  # pong
            if key == K.KEY_R:
                self.pong.score_p  = 0
                self.pong.score_ai = 0
                self.pong.reset_ball()

        elif self.screen == 5:  # climate
            if key == K.KEY_TAB:
                self._climate_sel = 1 - self._climate_sel
            attr = 'rear_driver_temp' if self._climate_sel == 0 else 'rear_pass_temp'
            if key == K.KEY_UP:
                state.set(attr, state.get(attr) + 1.0)
            if key == K.KEY_DOWN:
                state.set(attr, state.get(attr) - 1.0)
            if key == K.KEY_F:
                cur = state.get('rear_fan')
                state.set('rear_fan', min(5, cur + 1))
            if key == K.KEY_G:
                cur = state.get('rear_fan')
                state.set('rear_fan', max(0, cur - 1))

    def _activate_transport(self, state):
        """Handle ENTER on transport button."""
        if self.video_focused == 0:   # rewind
            self.video_progress = max(0.0, self.video_progress - 0.05)
        elif self.video_focused == 1: # prev chapter
            self.video_chapter = max(0, self.video_chapter - 1)
            self.video_progress = 0.0
        elif self.video_focused == 2: # stop
            self.video_playing  = False
            self.video_progress = 0.0
        elif self.video_focused == 3: # play/pause
            self.video_playing = not self.video_playing
        elif self.video_focused == 4: # next chapter
            self.video_chapter = min(len(self.CHAPTERS) - 1,
                                     self.video_chapter + 1)
            self.video_progress = 0.0

    # -----------------------------------------------------------------------
    # render (dispatch)
    # -----------------------------------------------------------------------

    def render(self, state, theme):
        if self.screen == 0:
            self._render_home(state, theme)
        elif self.screen == 1:
            self._render_video(state, theme)
        elif self.screen == 2:
            self._render_music(state, theme)
        elif self.screen == 3:
            self._render_pong(state, theme)
        elif self.screen == 4:
            self._render_trip(state, theme)
        elif self.screen == 5:
            self._render_climate(state, theme)

    # -----------------------------------------------------------------------
    # Screen 0 — Home
    # -----------------------------------------------------------------------

    def _render_home(self, state, theme):
        rl.clear_background(theme.bg)

        # ---- LEFT ZONE — Now Playing (0..750) ----
        artist  = state.music_artist
        title   = state.music_title
        prog    = state.music_progress   # 0.0–1.0

        # Advance progress if playing
        if state.music_playing:
            dt = rl.get_frame_time()
            new_prog = min(1.0, prog + dt / 210.0)
            state.set('music_progress', new_prog)
            prog = new_prog

        cx, cy = 200, 200   # circle center

        # Artist color circle
        artist_color = rl.Color(60, 130, 200, 255)
        rl.draw_circle(cx, cy, 90, artist_color)

        # Progress ring
        end_angle = -90 + 360 * prog
        rl.draw_ring(rl.Vector2(cx, cy), 93, 101,
                     -90, end_angle, 60, theme.accent)

        # Artist initial — centered in circle
        initial = artist[0].upper() if artist else "?"
        v = rl.measure_text_ex(self.fonts['blg'], initial, 48, 2)
        rl.draw_text_ex(self.fonts['blg'], initial,
                        rl.Vector2(cx - v.x / 2, cy - v.y / 2),
                        48, 2, rl.WHITE)

        # Artist + title below circle
        _draw_text_centered(self.fonts, 'md', artist, cx, cy + 105, 28, theme.fg)
        _draw_text_centered(self.fonts, 'sm', title,  cx, cy + 140, 18, theme.fg2)

        # Play/pause indicator
        pp_label = "\u25b6 Playing" if state.music_playing else "\u23f8 Paused"
        _draw_text_centered(self.fonts, 'xs', pp_label, cx, cy + 165, 13, theme.accent)

        # Progress bar
        bar_x, bar_y, bar_w = 30, cy + 188, 340
        rl.draw_rectangle(bar_x, bar_y, bar_w, 4, theme.border)
        rl.draw_rectangle(bar_x, bar_y, int(bar_w * prog), 4, theme.accent)

        # Time labels
        elapsed = int(prog * 210)
        remain  = 210 - elapsed
        _draw_text(self.fonts, 'xs', f"{elapsed//60}:{elapsed%60:02d}",
                   bar_x, bar_y + 8, 13, theme.fg2)
        rt = f"{remain//60}:{remain%60:02d}"
        v2 = rl.measure_text_ex(self.fonts['xs'], rt, 13, 1)
        _draw_text(self.fonts, 'xs', rt,
                   bar_x + bar_w - int(v2.x), bar_y + 8, 13, theme.fg2)

        # SPACE hint
        _draw_text(self.fonts, 'xs', "SPACE = play/pause",
                   30, 420, 13, theme.fg2)

        # Vertical divider
        rl.draw_rectangle(750, 0, 1, 480, theme.border)

        # ---- RIGHT ZONE — App row + trip info (760..1280) ----
        rz_x = 760

        # App pill buttons row
        apps  = ["VIDEO", "MUSIC", "PONG", "TRIP", "CLIMATE"]
        keys  = ["V",     "M",     "G",    "I",    "C"]
        pill_w, pill_h = 96, 40
        pill_gap = 8
        row_total = len(apps) * pill_w + (len(apps) - 1) * pill_gap
        pill_start_x = rz_x + (520 - row_total) // 2
        pill_y = 20

        for i, (label, kchar) in enumerate(zip(apps, keys)):
            px = pill_start_x + i * (pill_w + pill_gap)
            rl.draw_rectangle_rounded(
                rl.Rectangle(px, pill_y, pill_w, pill_h),
                0.5, 8, theme.surface2)
            lv = rl.measure_text_ex(self.fonts['xs'], label, 13, 1)
            rl.draw_text_ex(self.fonts['xs'], label,
                            rl.Vector2(px + (pill_w - lv.x) / 2,
                                       pill_y + (pill_h - lv.y) / 2),
                            13, 1, theme.accent)
            # Key shortcut tiny label
            kv = rl.measure_text_ex(self.fonts['xs'], kchar, 11, 1)
            rl.draw_text_ex(self.fonts['xs'], kchar,
                            rl.Vector2(px + (pill_w - kv.x) / 2,
                                       pill_y + pill_h + 2),
                            11, 1, theme.fg2)

        # Trip info card
        card_x, card_y = rz_x + 10, 90
        card_w, card_h = 500, 360
        rl.draw_rectangle_rounded(
            rl.Rectangle(card_x, card_y, card_w, card_h),
            0.05, 8, theme.surface)

        ty = card_y + 20
        # Destination
        dest = state.destination
        _draw_text(self.fonts, 'xs', "DESTINATION", card_x + 20, ty, 13, theme.fg2)
        ty += 18
        _draw_text(self.fonts, 'md', dest, card_x + 20, ty, 22, theme.fg)
        ty += 36

        # ETA
        eta_str = _fmt_eta(state.eta_seconds)
        _draw_text(self.fonts, 'xs', "ETA", card_x + 20, ty, 13, theme.fg2)
        _draw_text(self.fonts, 'sm', eta_str,
                   card_x + card_w - 120, ty, 18, theme.accent)
        ty += 24

        # Trip progress bar
        tp = state.trip_progress
        rl.draw_rectangle(card_x + 20, ty, card_w - 40, 4, theme.border)
        rl.draw_rectangle(card_x + 20, ty, int((card_w - 40) * tp), 4, theme.accent)
        ty += 18

        # Trip distance
        dist_done = state.trip_distance_mi * tp
        dist_rem  = state.trip_distance_mi * (1.0 - tp)
        _draw_text(self.fonts, 'xs',
                   f"{dist_done:.1f} mi traveled  /  {dist_rem:.1f} mi remaining",
                   card_x + 20, ty, 13, theme.fg2)
        ty += 28

        # Separator
        rl.draw_rectangle(card_x + 20, ty, card_w - 40, 1, theme.border)
        ty += 12

        # Speed row
        spd = state.speed_mph
        _draw_text(self.fonts, 'xs', "CURRENT SPEED", card_x + 20, ty, 13, theme.fg2)
        ty += 16
        _draw_text(self.fonts, 'md',
                   f"{spd:.0f} mph", card_x + 20, ty, 28, theme.fg)
        ty += 40

        # Avg speed
        _draw_text(self.fonts, 'xs', "AVG SPEED", card_x + 20, ty, 13, theme.fg2)
        ty += 16
        avg = state.avg_speed_mph
        _draw_text(self.fonts, 'sm', f"{avg:.0f} mph", card_x + 20, ty, 18, theme.fg)
        ty += 30

        # Fuel bar
        fuel = state.fuel_level
        _draw_text(self.fonts, 'xs', "FUEL", card_x + 20, ty, 13, theme.fg2)
        ty += 16
        fuel_color = theme.good if fuel > 0.3 else theme.warn
        rl.draw_rectangle(card_x + 20, ty, card_w - 40, 8, theme.border)
        rl.draw_rectangle(card_x + 20, ty,
                          int((card_w - 40) * fuel), 8, fuel_color)

    # -----------------------------------------------------------------------
    # Screen 1 — Video / DVD Player
    # -----------------------------------------------------------------------

    def _render_video(self, state, theme):
        # Advance video progress each frame
        dt = rl.get_frame_time()
        if self.video_playing:
            self.video_progress = min(1.0, self.video_progress + dt / 3600.0)
            # Also update shared state
            state.set('video_progress', self.video_progress)

        if self.dvd_mode:
            self._render_dvd_bounce(dt, theme)
            return

        # ---------- VIDEO AREA (left 65%) ----------
        vw = 832
        t = rl.get_time()

        # Animated dark gradient background (fake video)
        r = int(20 + 15 * math.sin(t * 0.3))
        g = int(10 + 8  * math.sin(t * 0.2 + 1))
        b = int(30 + 20 * math.sin(t * 0.1 + 2))
        rl.draw_rectangle(0, 0, vw, 480, rl.Color(r, g, b, 255))

        # Scanline effect — thin semi-transparent lines every 4px
        for scan_y in range(0, 480, 4):
            rl.draw_line(0, scan_y, vw, scan_y, rl.Color(0, 0, 0, 40))

        # Title overlay at top
        _draw_text(self.fonts, 'blg',
                   "Chapter 1: The Road",
                   12, 12, 24, theme.fg)

        # Timecode (bottom-left, before transport bar)
        total_secs  = int(self.video_progress * 3600)
        tc_h  = total_secs // 3600
        tc_m  = (total_secs % 3600) // 60
        tc_s  = total_secs % 60
        tc_str = f"{tc_h:02d}:{tc_m:02d}:{tc_s:02d}"
        _draw_text(self.fonts, 'xs', tc_str, 8, 400, 13, theme.fg2)

        # Progress bar at y=410
        rl.draw_rectangle(0, 410, vw, 4, theme.border)
        rl.draw_rectangle(0, 410, int(vw * self.video_progress), 4, theme.accent)

        # Transport controls bar y=420, h=50
        bar_bg = rl.Color(0, 0, 0, 140)
        rl.draw_rectangle(0, 420, vw, 50, bar_bg)

        btn_labels = self._transport_labels
        btn_w, btn_h = 50, 40
        btn_count = len(btn_labels)
        total_btn_w = btn_count * btn_w + (btn_count - 1) * 8
        bx_start = vw // 2 - total_btn_w // 2
        by = 425

        for i, lbl in enumerate(btn_labels):
            bx = bx_start + i * (btn_w + 8)
            bg = theme.surface2 if i != self.video_focused else rl.Color(0, 0, 0, 180)
            rl.draw_rectangle_rounded(rl.Rectangle(bx, by, btn_w, btn_h),
                                      0.2, 4, bg)
            if i == self.video_focused:
                rl.draw_rectangle_rounded_lines(
                    rl.Rectangle(bx, by, btn_w, btn_h),
                    0.2, 4, theme.accent, 2)
            lv = rl.measure_text_ex(self.fonts['sm'], lbl, 18, 1)
            rl.draw_text_ex(self.fonts['sm'], lbl,
                            rl.Vector2(bx + (btn_w - lv.x) / 2,
                                       by  + (btn_h - lv.y) / 2),
                            18, 1, theme.fg)

        # D key hint
        _draw_text(self.fonts, 'xs', "D=DVD Bounce  \u2190\u2192=Select  SPACE=Play/Pause",
                   4, 466, 13, rl.Color(50, 50, 50, 255))

        # Vertical divider
        rl.draw_rectangle(vw, 0, 1, 480, theme.border)

        # ---------- CHAPTER LIST (right 35%) ----------
        cx0 = 840
        rl.draw_rectangle(cx0, 0, 440, 480, theme.surface)

        _draw_text(self.fonts, 'xs', "CHAPTERS", cx0 + 16, 12, 13, theme.fg2)
        rl.draw_rectangle(cx0, 32, 440, 1, theme.border)

        row_h = 72
        for i, (ch_title, ch_dur) in enumerate(self.CHAPTERS):
            ry = 36 + i * row_h
            is_current = (i == self.video_chapter)

            if is_current:
                rl.draw_rectangle(cx0, ry, 440, row_h, theme.surface2)
                rl.draw_rectangle(cx0, ry, 3, row_h, theme.accent)

            ch_num = f"CH {i + 1:02d}"
            _draw_text(self.fonts, 'xs', ch_num, cx0 + 16, ry + 8, 13, theme.accent)
            txt_col = theme.accent if is_current else theme.fg
            _draw_text(self.fonts, 'sm', ch_title, cx0 + 16, ry + 28, 18, txt_col)

            # Duration right-aligned
            dv = rl.measure_text_ex(self.fonts['xs'], ch_dur, 13, 1)
            rl.draw_text_ex(self.fonts['xs'], ch_dur,
                            rl.Vector2(cx0 + 440 - dv.x - 12, ry + 10),
                            13, 1, theme.fg2)

            rl.draw_rectangle(cx0, ry + row_h - 1, 440, 1, theme.border)

        # Nav hint
        _draw_text(self.fonts, 'xs', "\u2191\u2193=Select Chapter  ENTER=Confirm",
                   cx0 + 8, 462, 13, rl.Color(50, 50, 50, 255))

    def _render_dvd_bounce(self, dt, theme):
        """DVD bounce screensaver."""
        # Update position
        self.dvd_x += self.dvd_vx * dt * 80
        self.dvd_y += self.dvd_vy * dt * 80

        # Bounce off walls (1280 wide, 480 tall; logo ~120×60)
        bounced = False
        if self.dvd_x < 0 or self.dvd_x > 1280 - 120:
            self.dvd_vx *= -1
            self.dvd_x   = max(0.0, min(float(1280 - 120), self.dvd_x))
            bounced = True
        if self.dvd_y < 0 or self.dvd_y > 480 - 60:
            self.dvd_vy *= -1
            self.dvd_y   = max(0.0, min(float(480 - 60), self.dvd_y))
            bounced = True
        if bounced:
            self.dvd_color = rl.Color(
                random.randint(80, 255),
                random.randint(80, 255),
                random.randint(80, 255),
                255)

        rl.clear_background(rl.Color(0, 0, 0, 255))
        rl.draw_text_ex(self.fonts['blg'], "DVD",
                        rl.Vector2(self.dvd_x, self.dvd_y),
                        48, 2, self.dvd_color)

        # Hint to exit
        rl.draw_text_ex(self.fonts['xs'],
                        "D=Exit DVD Mode  Backspace=Back",
                        rl.Vector2(10, 460), 13, 1,
                        rl.Color(40, 40, 40, 255))

    # -----------------------------------------------------------------------
    # Screen 2 — Music (Rear)
    # -----------------------------------------------------------------------

    def _render_music(self, state, theme):
        rl.clear_background(theme.bg)

        # Rear audio label top
        _draw_text_centered(self.fonts, 'xs',
                            "\U0001F3B5 Rear Audio",
                            640, 8, 13, theme.fg2)

        artist  = state.music_artist
        title   = state.music_title
        prog    = state.music_progress

        # Advance progress if playing
        if state.music_playing:
            dt  = rl.get_frame_time()
            prog = min(1.0, prog + dt / 210.0)
            state.set('music_progress', prog)

        cx, cy = 420, 230  # centered-ish

        # Artist color circle
        rl.draw_circle(cx, cy, 110, rl.Color(50, 110, 180, 255))

        # Animated ring
        end_angle = -90 + 360 * prog
        rl.draw_ring(rl.Vector2(cx, cy), 113, 123,
                     -90, end_angle if end_angle != -90 else -89.9,
                     60, theme.accent)

        # Artist initial
        initial = artist[0].upper() if artist else "?"
        v = rl.measure_text_ex(self.fonts['blg'], initial, 48, 2)
        rl.draw_text_ex(self.fonts['blg'], initial,
                        rl.Vector2(cx - v.x / 2, cy - v.y / 2),
                        48, 2, rl.WHITE)

        # Artist / title
        _draw_text_centered(self.fonts, 'md', artist, cx, cy + 125, 28, theme.fg)
        _draw_text_centered(self.fonts, 'sm', title,  cx, cy + 162, 18, theme.fg2)

        # Play state
        pp = "\u25b6 Playing" if state.music_playing else "\u23f8 Paused"
        _draw_text_centered(self.fonts, 'xs', pp, cx, cy + 188, 13, theme.accent)

        # Progress bar
        bar_x, bar_y, bar_w = cx - 200, cy + 210, 400
        rl.draw_rectangle(bar_x, bar_y, bar_w, 4, theme.border)
        rl.draw_rectangle(bar_x, bar_y, int(bar_w * prog), 4, theme.accent)

        elapsed = int(prog * 210)
        remain  = 210 - elapsed
        _draw_text(self.fonts, 'xs', f"{elapsed//60}:{elapsed%60:02d}",
                   bar_x, bar_y + 8, 13, theme.fg2)
        rt = f"{remain//60}:{remain%60:02d}"
        rv = rl.measure_text_ex(self.fonts['xs'], rt, 13, 1)
        _draw_text(self.fonts, 'xs', rt,
                   bar_x + bar_w - int(rv.x), bar_y + 8, 13, theme.fg2)

        # --- Waveform bars (right side) ---
        t  = rl.get_time()
        wx = 870
        wy = 240
        bar_count = 32
        bar_max_h = 120
        bw = 8
        gap = 4

        for i in range(bar_count):
            if state.music_playing:
                h = int(abs(math.sin(t * 3.5 + self._waveform_offsets[i] * 2.5))
                        * bar_max_h * (0.4 + 0.6 * (i % 5 + 1) / 5))
                h = max(6, h)
            else:
                h = 6
            bx = wx + i * (bw + gap)
            alpha = int(180 * (i / bar_count))
            col = rl.Color(theme.accent.r, theme.accent.g, theme.accent.b, 120 + alpha)
            rl.draw_rectangle_rounded(
                rl.Rectangle(bx, wy - h // 2, bw, h),
                0.3, 4, col)

        # SPACE hint
        _draw_text(self.fonts, 'xs', "SPACE=Play/Pause  Backspace=Back",
                   870, 460, 13, theme.fg2)

    # -----------------------------------------------------------------------
    # Screen 3 — Pong
    # -----------------------------------------------------------------------

    def _render_pong(self, state, theme):
        dt   = rl.get_frame_time()
        up   = rl.is_key_down(rl.KeyboardKey.KEY_UP)
        down = rl.is_key_down(rl.KeyboardKey.KEY_DOWN)
        self.pong.update(dt, up, down)
        self.pong.draw(self.fonts, theme)
        state.set('pong_score_player', self.pong.score_p)
        state.set('pong_score_ai',     self.pong.score_ai)

    # -----------------------------------------------------------------------
    # Screen 4 — Trip Info
    # -----------------------------------------------------------------------

    def _render_trip(self, state, theme):
        rl.clear_background(theme.bg)

        # Header
        _draw_text_centered(self.fonts, 'xs', "TRIP OVERVIEW", 640, 12, 13, theme.fg2)
        rl.draw_rectangle(40, 34, 1200, 1, theme.border)

        # Cards grid: 4 rows × 2 columns
        card_w, card_h = 570, 88
        col_gap, row_gap = 20, 12
        col1_x = 50
        col2_x = col1_x + card_w + col_gap
        start_y = 46

        # Elapsed trip duration
        trip_elapsed = time.time() - self._trip_start

        # Build card data
        spd   = state.speed_mph
        avg   = state.avg_speed_mph
        tp    = state.trip_progress
        dist  = state.trip_distance_mi
        done  = dist * tp
        rem   = dist * (1 - tp)
        eta_s = state.eta_seconds
        fuel  = state.fuel_level
        car   = state.car_profile.upper()

        cards = [
            # row 0
            ("CURRENT SPEED",    f"{spd:.0f} mph",           theme.fg,     False),
            ("AVG SPEED",        f"{avg:.0f} mph",           theme.fg,     False),
            # row 1
            ("DISTANCE TOTAL",   f"{dist:.1f} mi",           theme.fg,     False),
            ("DISTANCE REM.",    f"{rem:.1f} mi",            theme.accent, False),
            # row 2
            ("ETA COUNTDOWN",    _fmt_eta(eta_s),            theme.accent, False),
            ("FUEL LEVEL",       f"{int(fuel*100)}%",        theme.good if fuel > 0.3 else theme.warn, True),
            # row 3
            ("TRIP DURATION",    _fmt_duration(trip_elapsed), theme.fg,    False),
            ("CAR PROFILE",      car,                         theme.fg2,   False),
        ]

        for i, (label, val, val_col, is_fuel) in enumerate(cards):
            row = i // 2
            col = i %  2
            cx  = col1_x if col == 0 else col2_x
            cy  = start_y + row * (card_h + row_gap)

            rl.draw_rectangle_rounded(
                rl.Rectangle(cx, cy, card_w, card_h),
                0.1, 8, theme.surface)

            _draw_text(self.fonts, 'xs', label, cx + 16, cy + 12, 13, theme.fg2)
            _draw_text(self.fonts, 'md', val,   cx + 16, cy + 36, 28, val_col)

            # Fuel bar below value
            if is_fuel:
                fb_x = cx + 16
                fb_y = cy + 70
                fb_w = card_w - 32
                rl.draw_rectangle(fb_x, fb_y, fb_w, 6, theme.border)
                fc = theme.good if fuel > 0.3 else theme.warn
                rl.draw_rectangle(fb_x, fb_y, int(fb_w * fuel), 6, fc)

        # Trip progress bottom bar
        rl.draw_rectangle(40, 458, 1200, 1, theme.border)
        tp_label = f"Trip Progress: {int(tp * 100)}%   Destination: {state.destination}"
        _draw_text_centered(self.fonts, 'xs', tp_label, 640, 463, 13, theme.fg2)

    # -----------------------------------------------------------------------
    # Screen 5 — Rear Climate
    # -----------------------------------------------------------------------

    def _render_climate(self, state, theme):
        rl.clear_background(theme.bg)

        _draw_text_centered(self.fonts, 'xs', "REAR CLIMATE", 640, 12, 13, theme.fg2)
        rl.draw_rectangle(40, 32, 1200, 1, theme.border)

        # Two zone cards side by side
        zone_labels  = ["REAR LEFT",   "REAR RIGHT"]
        temp_attrs   = ["rear_driver_temp", "rear_pass_temp"]
        zone_x_start = [60,  680]
        zone_w       = 580
        zone_h       = 340
        zone_y       = 50

        fan_level = state.rear_fan

        for z in range(2):
            zx  = zone_x_start[z]
            sel = (z == self._climate_sel)

            # Card background
            bg_col = theme.surface2 if sel else theme.surface
            rl.draw_rectangle_rounded(
                rl.Rectangle(zx, zone_y, zone_w, zone_h),
                0.08, 8, bg_col)

            # Selected indicator border
            if sel:
                rl.draw_rectangle_rounded_lines(
                    rl.Rectangle(zx, zone_y, zone_w, zone_h),
                    0.08, 8, theme.accent, 2)

            temp = state.get(temp_attrs[z])

            # Zone label
            _draw_text_centered(self.fonts, 'xs',
                                zone_labels[z],
                                zx + zone_w // 2, zone_y + 16, 13, theme.fg2)

            # Temperature large display
            temp_str = f"{temp:.0f}\u00b0F"
            _draw_text_centered(self.fonts, 'xl',
                                temp_str,
                                zx + zone_w // 2, zone_y + 50, 96, theme.accent)

            # ▲ / ▼ buttons
            btn_up_rect   = rl.Rectangle(zx + zone_w // 2 - 60, zone_y + 165, 55, 44)
            btn_down_rect = rl.Rectangle(zx + zone_w // 2 + 5,  zone_y + 165, 55, 44)

            rl.draw_rectangle_rounded(btn_up_rect,   0.3, 4, theme.surface3)
            rl.draw_rectangle_rounded(btn_down_rect, 0.3, 4, theme.surface3)

            _draw_text_centered(self.fonts, 'md', "\u25b2",
                                zx + zone_w // 2 - 33, zone_y + 170, 24, theme.fg)
            _draw_text_centered(self.fonts, 'md', "\u25bc",
                                zx + zone_w // 2 + 32, zone_y + 170, 24, theme.fg)

            if sel:
                _draw_text_centered(self.fonts, 'xs',
                                    "\u2191\u2193=Adjust  TAB=Switch Zone",
                                    zx + zone_w // 2, zone_y + 218, 13, theme.fg2)

            # Fan level dots
            _draw_text(self.fonts, 'xs', "FAN",
                       zx + 24, zone_y + 252, 13, theme.fg2)
            dot_r = 7
            dot_gap = 20
            dots_x0 = zx + 80
            for d in range(5):
                dcx = dots_x0 + d * (dot_r * 2 + dot_gap)
                dcy = zone_y + 260
                col = theme.accent if d < fan_level else theme.border
                rl.draw_circle(dcx, dcy, dot_r, col)

            # Heated seats toggle pill
            _draw_text(self.fonts, 'xs', "HEATED SEATS",
                       zx + 24, zone_y + 290, 13, theme.fg2)
            hs = state.heated_seats
            pill_r = rl.Rectangle(zx + 160, zone_y + 286, 54, 24)
            rl.draw_rectangle_rounded(pill_r, 1.0, 8,
                                      theme.accent if hs else theme.border)
            dot_cx = (zx + 160 + 39) if hs else (zx + 160 + 15)
            rl.draw_circle(dot_cx, zone_y + 298, 9, rl.WHITE)
            _draw_text(self.fonts, 'xs',
                       "ON" if hs else "OFF",
                       zx + 222, zone_y + 291, 13,
                       theme.accent if hs else theme.fg2)

        # Vent mode icons row (bottom)
        rl.draw_rectangle(40, 408, 1200, 1, theme.border)
        _draw_text_centered(self.fonts, 'xs', "VENT MODE", 640, 416, 13, theme.fg2)

        vent_labels = ["FACE", "FEET", "DEFROST", "COMBO"]
        vent_x0 = 640 - (len(vent_labels) * 120) // 2 + 60
        for vi, vlabel in enumerate(vent_labels):
            vx = vent_x0 + vi * 120
            vy = 438
            # Simple icon drawn as shapes
            if vlabel == "FACE":
                rl.draw_circle(vx, vy, 16, theme.surface2)
                rl.draw_circle(vx, vy, 14, theme.fg2)
                rl.draw_circle(vx - 5, vy - 3, 3, theme.bg)
                rl.draw_circle(vx + 5, vy - 3, 3, theme.bg)
                rl.draw_circle(vx, vy + 5, 3, theme.bg)
            elif vlabel == "FEET":
                rl.draw_rectangle(vx - 10, vy - 10, 20, 20, theme.fg2)
                rl.draw_rectangle(vx - 8,  vy + 5,  7,  8,  theme.surface)
                rl.draw_rectangle(vx + 1,  vy + 5,  7,  8,  theme.surface)
            elif vlabel == "DEFROST":
                for li in range(3):
                    rl.draw_line(vx - 12 + li * 10, vy - 12,
                                 vx - 12 + li * 10, vy + 12,
                                 theme.accent)
                    rl.draw_line(vx - 12 + li * 10, vy,
                                 vx - 6  + li * 10, vy - 6,
                                 theme.accent)
                    rl.draw_line(vx - 12 + li * 10, vy,
                                 vx - 6  + li * 10, vy + 6,
                                 theme.accent)
            else:
                rl.draw_circle(vx, vy, 12, theme.surface2)
                rl.draw_ring(rl.Vector2(vx, vy), 6, 12,
                             0, 180, 12, theme.accent)

            _draw_text_centered(self.fonts, 'xs', vlabel,
                                vx, vy + 20, 11, theme.fg2)

        # F/G hint for fan
        _draw_text(self.fonts, 'xs',
                   "F=Fan+  G=Fan-  TAB=Zone  \u2191\u2193=Temp  Backspace=Back",
                   40, 466, 13, theme.fg2)

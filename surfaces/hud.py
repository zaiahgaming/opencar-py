import pyray as rl
import os
import math
import time

class HUDSurface:
    def __init__(self, fonts: dict):
        self.fonts = fonts
        
        self._smooth_speed = 0.0
        self._smooth_rpm = 0.0
        self._smooth_temp = 195.0
        self._smooth_lead_dist = 42.0
        self._smooth_torque = 0.35
        
        self.turn_left = False
        self.turn_right = False
        self.hazard = False
        self.headlights = True
        self.target_speed = 65
        self.drive_mode_idx = 1  # NORMAL
        
        self.textures = {}
        for name, path in [
            ('nav', 'assets/icons/navigation_white.png'),
            ('music', 'assets/icons/music_white.png'),
            ('gauge', 'assets/icons/gauge_white.png'),
            ('fuel', 'assets/icons/fuel_white.png'),
            ('shield', 'assets/icons/shield-check_white.png'),
            ('car', 'assets/icons/car_white.png'),
            ('sun', 'assets/icons/sun_white.png'),
            ('zap', 'assets/icons/zap_white.png'),
            ('art1', 'assets/music/the_midnight.jpg'),
            ('art2', 'assets/music/tycho.jpg'),
            ('art3', 'assets/music/bonobo.jpg'),
        ]:
            self._load_texture(name, path)

    def _load_texture(self, name, path):
        if os.path.exists(path):
            self.textures[name] = rl.load_texture(path)
        else:
            self.textures[name] = None
            
    def _draw_text_centered(self, font, text, x, y, color):
        size = rl.measure_text_ex(font, text, font.baseSize, 0)
        rl.draw_text_ex(font, text, rl.Vector2(x - size.x / 2, y - size.y / 2), font.baseSize, 0, color)
        
    def render(self, state, theme):
        w = rl.get_screen_width()
        h = rl.get_screen_height()
        
        rl.draw_rectangle(0, 0, w, h, rl.Color(0, 0, 0, 255))
        
        speed = getattr(state, 'speed_mph', 65.0)
        rpm = getattr(state, 'rpm', 2400.0)
        temp = getattr(state, 'engine_temp_f', 195.0)

        self._smooth_speed += (speed - self._smooth_speed) * 0.1
        self._smooth_rpm += (rpm - self._smooth_rpm) * 0.1
        self._smooth_temp += (temp - self._smooth_temp) * 0.1
        
        top_h = h * 0.06
        bottom_h = h * 0.08
        left_w = w * 0.28
        center_w = w * 0.44
        right_w = w * 0.28
        
        clicked = rl.is_mouse_button_pressed(rl.MouseButton.MOUSE_BUTTON_LEFT)
        mouse = rl.get_mouse_position()

        # Center section - Speed and Dynamic Openpilot Road Path
        self._draw_center_panel(state, left_w, top_h, center_w, h - top_h - bottom_h, theme)
        
        # Left section - Comma 3X ADAS Hub + High-Luminance PRNDL + Powertrain
        self._draw_left_panel(state, 0, top_h, left_w, h - top_h - bottom_h, theme)
        
        # Right section - Navigation with Lane Guidance + Media Card
        self._draw_right_panel(state, left_w + center_w, top_h, right_w, h - top_h - bottom_h, theme)
        
        # Top strip - ISO 2575 Telltale Glyphs & Directional Turn Arrows
        self._draw_top_strip(state, w, top_h, theme, mouse=mouse, clicked=clicked)
        
        # Bottom strip - Rounded Capsule Dock (Fuel, Calibrated Trip, Cluster Status)
        self._draw_bottom_strip(state, 0, h - bottom_h, w, bottom_h, theme, mouse=mouse, clicked=clicked)

    # ════════════════════════════════════════════════════════════════════════════
    # 1. LEFT PANEL - Comma 3X ADAS Telemetry Hub & High-Luminance PRNDL
    # ════════════════════════════════════════════════════════════════════════════
    def _draw_left_panel(self, state, x, y, w, h, theme):
        pad = 20
        rect = rl.Rectangle(x + pad, y + pad, w - pad * 2, h - pad * 2)
        rl.draw_rectangle_rounded(rect, 0.25, 32, rl.Color(41, 41, 41, 255))
        
        # Card Header: Comma 3X ADAS Active
        rl.draw_circle(int(rect.x + 24), int(rect.y + 26), 5, rl.Color(51, 171, 76, 255))
        rl.draw_text_ex(self.fonts['xs'], "comma 3X · openpilot active", rl.Vector2(rect.x + 38, rect.y + 18), self.fonts['xs'].baseSize, 0, rl.Color(51, 171, 76, 255))
        
        # ── 1. Lead Vehicle Radar Card Section ────────────────────────────────
        lead_y = rect.y + 48
        lead_w = rect.width - 40
        rl.draw_rectangle_rounded(rl.Rectangle(rect.x + 20, lead_y, lead_w, 82), 0.2, 16, rl.Color(32, 32, 32, 255))
        
        rl.draw_text_ex(self.fonts['xs'], "RADAR TRACKING", rl.Vector2(rect.x + 34, lead_y + 12), self.fonts['xs'].baseSize, 0, rl.Color(128, 128, 128, 255))
        rl.draw_text_ex(self.fonts['bmd'], "LEAD CAR: 42 m", rl.Vector2(rect.x + 34, lead_y + 36), self.fonts['bmd'].baseSize, 0, rl.Color(255, 255, 255, 255))
        
        # Following Gap Bars (1-3 bars)
        rl.draw_text_ex(self.fonts['xs'], "GAP 3", rl.Vector2(rect.x + lead_w - 30, lead_y + 12), self.fonts['xs'].baseSize, 0, rl.Color(51, 171, 76, 255))
        for g in range(3):
            g_rect = rl.Rectangle(rect.x + lead_w - 40 + g * 16, lead_y + 42, 10, 18)
            rl.draw_rectangle_rounded(g_rect, 0.3, 4, rl.Color(51, 171, 76, 255))
            
        # ── 2. Steering Torque / Actuator Readiness ───────────────────────────
        torq_y = lead_y + 96
        rl.draw_text_ex(self.fonts['xs'], "STEERING TORQUE (LATERAL ACTUATOR)", rl.Vector2(rect.x + 20, torq_y), self.fonts['xs'].baseSize, 0, rl.Color(128, 128, 128, 255))
        
        # Dual-direction torque meter bar
        bar_w = rect.width - 40
        rl.draw_rectangle_rounded(rl.Rectangle(rect.x + 20, torq_y + 20, bar_w, 10), 1.0, 8, rl.Color(55, 55, 55, 255))
        # Center line
        rl.draw_rectangle(int(rect.x + 20 + bar_w / 2 - 1), int(torq_y + 16), 2, 18, rl.Color(200, 200, 200, 255))
        # Fill
        t_fill_w = int((bar_w / 2) * self._smooth_torque)
        rl.draw_rectangle_rounded(rl.Rectangle(rect.x + 20 + bar_w / 2, torq_y + 20, t_fill_w, 10), 1.0, 8, rl.Color(51, 171, 76, 255))
        
        # ── 3. High-Luminance PRNDL Strip (ISO 15008 Compliant) ───────────────
        prndl_y = torq_y + 54
        gears = ['P', 'R', 'N', 'D']
        raw_gear = getattr(state, 'gear', 3)
        gear_idx = raw_gear if isinstance(raw_gear, int) and 0 <= raw_gear < 4 else 3
        
        prndl_box_w = rect.width - 40
        rl.draw_rectangle_rounded(rl.Rectangle(rect.x + 20, prndl_y, prndl_box_w, 64), 0.25, 16, rl.Color(32, 32, 32, 255))
        
        slot_w = prndl_box_w / 4
        for i, g in enumerate(gears):
            gx = rect.x + 20 + i * slot_w + slot_w / 2
            gy = prndl_y + 32
            is_active = (i == gear_idx)
            
            if is_active:
                pill_w, pill_h = 56, 44
                active_bg = rl.Color(51, 171, 76, 255) if g != 'R' else rl.Color(226, 44, 44, 255)
                rl.draw_rectangle_rounded(rl.Rectangle(gx - pill_w/2, gy - pill_h/2, pill_w, pill_h), 0.35, 16, active_bg)
                self._draw_text_centered(self.fonts['blg'], g, gx, gy, rl.Color(0, 0, 0, 255))
            else:
                self._draw_text_centered(self.fonts['blg'], g, gx, gy, rl.Color(110, 110, 110, 255))

        # ── 4. Powertrain: Calibrated Coolant Temp & RPM ───────────────────────
        pt_y = prndl_y + 84
        rl.draw_text_ex(self.fonts['xs'], "ENGINE COOLANT", rl.Vector2(rect.x + 20, pt_y), self.fonts['xs'].baseSize, 0, rl.Color(128, 128, 128, 255))
        temp_int = int(self._smooth_temp)
        rl.draw_text_ex(self.fonts['bmd'], f"{temp_int}°F", rl.Vector2(rect.x + rect.width - 90, pt_y - 2), self.fonts['bmd'].baseSize, 0, rl.Color(255, 255, 255, 255))
        
        # Calibrated bar with min/max indices
        t_bar_y = pt_y + 24
        t_bar_w = rect.width - 40
        rl.draw_rectangle_rounded(rl.Rectangle(rect.x + 20, t_bar_y, t_bar_w, 8), 1.0, 8, rl.Color(55, 55, 55, 255))
        pct = max(0.0, min(1.0, (self._smooth_temp - 100) / 140.0))
        t_col = rl.Color(51, 171, 76, 255) if pct < 0.8 else rl.Color(226, 44, 44, 255)
        rl.draw_rectangle_rounded(rl.Rectangle(rect.x + 20, t_bar_y, int(t_bar_w * pct), 8), 1.0, 8, t_col)
        
        # Calibration ticks
        rl.draw_text_ex(self.fonts['xs'], "140°F", rl.Vector2(rect.x + 20, t_bar_y + 12), self.fonts['xs'].baseSize, 0, rl.Color(110, 110, 110, 255))
        rl.draw_text_ex(self.fonts['xs'], "NOMINAL", rl.Vector2(rect.x + t_bar_w / 2 - 10, t_bar_y + 12), self.fonts['xs'].baseSize, 0, rl.Color(51, 171, 76, 255))
        rl.draw_text_ex(self.fonts['xs'], "240°F", rl.Vector2(rect.x + rect.width - 60, t_bar_y + 12), self.fonts['xs'].baseSize, 0, rl.Color(110, 110, 110, 255))
        
        # RPM compact indicator
        rpm_val = int(self._smooth_rpm)
        rl.draw_text_ex(self.fonts['xs'], f"TACH: {rpm_val:,} RPM", rl.Vector2(rect.x + 20, rect.y + rect.height - 28), self.fonts['xs'].baseSize, 0, rl.Color(140, 140, 140, 255))

    # ════════════════════════════════════════════════════════════════════════════
    # 2. CENTER PANEL - Openpilot Vision Spline, Speedometer & Clear Margin Limit
    # ════════════════════════════════════════════════════════════════════════════
    def _draw_center_panel(self, state, x, y, w, h, theme):
        cx = x + w / 2
        cy = y + h * 0.38
        
        # Dynamic Openpilot Driving Path (Green Polygon Corridor)
        path_p1 = rl.Vector2(cx - 180, y + h)
        path_p2 = rl.Vector2(cx + 180, y + h)
        path_p3 = rl.Vector2(cx + 40, cy + 110)
        path_p4 = rl.Vector2(cx - 40, cy + 110)
        
        # Corridor polygon glow
        rl.draw_triangle(path_p1, path_p2, path_p3, rl.Color(51, 171, 76, 35))
        rl.draw_triangle(path_p1, path_p3, path_p4, rl.Color(51, 171, 76, 35))
        
        # Lane Boundaries
        rl.draw_line_ex(path_p1, path_p4, 4, rl.Color(51, 171, 76, 180))
        rl.draw_line_ex(path_p2, path_p3, 4, rl.Color(51, 171, 76, 180))
        
        # Lead Vehicle 3D Bounding Box on path
        box_w, box_h = 58, 34
        box_x = cx - box_w / 2
        box_y = cy + 115
        rl.draw_rectangle_rounded(rl.Rectangle(box_x, box_y, box_w, box_h), 0.25, 8, rl.Color(51, 171, 76, 220))
        rl.draw_rectangle_rounded_lines_ex(rl.Rectangle(box_x, box_y, box_w, box_h), 0.25, 8, 2.0, rl.Color(255, 255, 255, 240))
        self._draw_text_centered(self.fonts['xs'], "42m", cx, box_y + box_h / 2, rl.Color(0, 0, 0, 255))
        
        # Speedometer Arc
        inner_r = w * 0.28
        outer_r = w * 0.33
        center = rl.Vector2(cx, cy)
        
        # Track
        rl.draw_ring(center, inner_r, outer_r, 135, 405, 64, rl.Color(50, 50, 50, 255))
        
        # Speed fill
        fill_angle = 135 + (self._smooth_speed / 120) * 270
        fill_angle = min(max(fill_angle, 135), 405)
        rl.draw_ring(center, inner_r, outer_r, 135, fill_angle, 64, rl.Color(70, 91, 234, 255))
        
        # Digital Speed Number
        speed_str = str(int(self._smooth_speed))
        speed_font = self.fonts.get('xxl', self.fonts['xl'])
        self._draw_text_centered(speed_font, speed_str, cx, cy - 20, rl.Color(255, 255, 255, 255))
        self._draw_text_centered(self.fonts['md'], "MPH", cx, cy + 70, rl.Color(170, 170, 170, 255))
        
        # Speed Limit Sign with 48px explicit clearance margin (No Collision)
        sign_w = 68
        sign_h = 82
        sign_x = cx + outer_r + 36
        sign_y = cy - 41
        rl.draw_rectangle_rounded(rl.Rectangle(sign_x, sign_y, sign_w, sign_h), 0.15, 8, rl.Color(255, 255, 255, 255))
        rl.draw_rectangle_rounded_lines_ex(rl.Rectangle(sign_x + 3, sign_y + 3, sign_w - 6, sign_h - 6), 0.12, 8, 2.0, rl.Color(0, 0, 0, 255))
        self._draw_text_centered(self.fonts['xs'], "SPEED", sign_x + sign_w / 2, sign_y + 16, rl.Color(0, 0, 0, 255))
        self._draw_text_centered(self.fonts['xs'], "LIMIT", sign_x + sign_w / 2, sign_y + 28, rl.Color(0, 0, 0, 255))
        self._draw_text_centered(self.fonts['bmd'], str(self.target_speed), sign_x + sign_w / 2, sign_y + 54, rl.Color(0, 0, 0, 255))

    # ════════════════════════════════════════════════════════════════════════════
    # 3. RIGHT PANEL - Navigation with Lane Guidance & Media
    # ════════════════════════════════════════════════════════════════════════════
    def _draw_right_panel(self, state, x, y, w, h, theme):
        pad = 20
        
        # ── Navigation Card ───────────────────────────────────────────────────
        nav_h = h * 0.50
        nav_rect = rl.Rectangle(x + pad, y + pad, w - pad * 2, nav_h - pad)
        rl.draw_rectangle_rounded(nav_rect, 0.25, 32, rl.Color(41, 41, 41, 255))
        
        nx = nav_rect.x + 20
        ny = nav_rect.y + 16
        rl.draw_text_ex(self.fonts['xs'], "NAVIGATION", rl.Vector2(nx, ny), self.fonts['xs'].baseSize, 0, rl.Color(128, 128, 128, 255))
        rl.draw_text_ex(self.fonts['blg'], getattr(state, 'destination', 'Downtown SF'), rl.Vector2(nx, ny + 20), self.fonts['blg'].baseSize, 0, rl.Color(255, 255, 255, 255))
        
        # Maneuver Badge & Next Step
        maneuver_y = ny + 68
        rl.draw_rectangle_rounded(rl.Rectangle(nx, maneuver_y, 44, 44), 0.35, 16, rl.Color(51, 171, 76, 255))
        nav_tex = self.textures.get('nav')
        if nav_tex and nav_tex.id > 0:
            scale = 26.0 / max(nav_tex.width, 1)
            rl.draw_texture_ex(nav_tex, rl.Vector2(nx + 9, maneuver_y + 9), 0.0, scale, rl.Color(0, 0, 0, 255))
            
        rl.draw_text_ex(self.fonts['bmd'], "In 800 ft, Exit 432B", rl.Vector2(nx + 54, maneuver_y + 2), self.fonts['bmd'].baseSize, 0, rl.Color(255, 255, 255, 255))
        rl.draw_text_ex(self.fonts['sm'], "Merge onto US-101 North", rl.Vector2(nx + 54, maneuver_y + 24), self.fonts['sm'].baseSize, 0, rl.Color(170, 170, 170, 255))
        
        # Lane Guidance Diagram (Fills the previous void)
        lane_y = maneuver_y + 54
        rl.draw_text_ex(self.fonts['xs'], "LANE GUIDANCE", rl.Vector2(nx, lane_y), self.fonts['xs'].baseSize, 0, rl.Color(128, 128, 128, 255))
        
        lanes = ["LEFT", "THRU", "THRU", "EXIT"]
        active_lane = 3  # Exit lane
        for idx, lname in enumerate(lanes):
            lx = nx + idx * 56
            is_active_lane = (idx == active_lane)
            l_box = rl.Rectangle(lx, lane_y + 18, 48, 26)
            rl.draw_rectangle_rounded(l_box, 0.25, 4, rl.Color(51, 171, 76, 255) if is_active_lane else rl.Color(55, 55, 55, 255))
            txt_col = rl.Color(0, 0, 0, 255) if is_active_lane else rl.Color(180, 180, 180, 255)
            self._draw_text_centered(self.fonts['xs'], lname, lx + 24, lane_y + 31, txt_col)
            
        # ETA Capsule Badge
        eta_y = nav_rect.y + nav_rect.height - 36
        rl.draw_rectangle_rounded(rl.Rectangle(nx, eta_y, 180, 26), 0.5, 16, rl.Color(55, 55, 55, 255))
        rl.draw_text_ex(self.fonts['xs'], "14 MIN  ·  12.4 MI  ·  5:42 PM", rl.Vector2(nx + 12, eta_y + 5), self.fonts['xs'].baseSize, 0, rl.Color(51, 171, 76, 255))

        # ── Media Card ────────────────────────────────────────────────────────
        media_y = y + nav_h + 12
        media_h = h - nav_h - 12 - pad
        media_rect = rl.Rectangle(x + pad, media_y, w - pad * 2, media_h)
        rl.draw_rectangle_rounded(media_rect, 0.25, 32, rl.Color(41, 41, 41, 255))
        
        mx = media_rect.x + 20
        my = media_rect.y + 16
        rl.draw_text_ex(self.fonts['xs'], "NOW PLAYING", rl.Vector2(mx, my), self.fonts['xs'].baseSize, 0, rl.Color(128, 128, 128, 255))
        
        # Audio source badge
        src_w = 70
        src_x = media_rect.x + media_rect.width - src_w - 20
        rl.draw_rectangle_rounded(rl.Rectangle(src_x, my - 2, src_w, 22), 0.5, 8, rl.Color(50, 50, 50, 255))
        rl.draw_text_ex(self.fonts['xs'], "SPOTIFY", rl.Vector2(src_x + 10, my + 1), self.fonts['xs'].baseSize, 0, rl.Color(51, 171, 76, 255))
        
        art_keys = ['art1', 'art2', 'art3']
        track_idx = getattr(state, 'music_track', 0) % len(art_keys)
        art_tex = self.textures.get(art_keys[track_idx])
        art_size = 68
        if art_tex and art_tex.id > 0:
            scale = art_size / max(art_tex.width, 1)
            rl.draw_texture_ex(art_tex, rl.Vector2(mx, my + 24), 0.0, scale, rl.WHITE)
            rl.draw_rectangle_lines_ex(rl.Rectangle(mx, my + 24, art_size, art_size), 1.0, rl.Color(80, 80, 80, 200))
            
        text_x = mx + art_size + 16
        rl.draw_text_ex(self.fonts['bmd'], state.music_title or 'Los Angeles', rl.Vector2(text_x, my + 24), self.fonts['bmd'].baseSize, 0, rl.Color(255, 255, 255, 255))
        rl.draw_text_ex(self.fonts['sm'], state.music_artist or 'The Midnight', rl.Vector2(text_x, my + 58), self.fonts['sm'].baseSize, 0, rl.Color(170, 170, 170, 255))
        
        # 5-bar animated audio equalizer visualizer on right side of card
        eq_x = media_rect.x + media_rect.width - 70
        eq_base_y = my + 72
        now_t = time.time() * 8
        bar_heights = [18, 28, 12, 24, 16]
        for bi, bh in enumerate(bar_heights):
            h_anim = int(bh * (0.6 + 0.4 * abs(((now_t + bi * 1.3) % 2) - 1)))
            bx = eq_x + bi * 10
            by = eq_base_y - h_anim
            rl.draw_rectangle_rounded(rl.Rectangle(bx, by, 6, h_anim), 0.5, 4, rl.Color(51, 171, 76, 220))

        # Scrubber
        pbar_y = media_rect.y + media_rect.height - 24
        pbar_w = media_rect.width - 40
        rl.draw_rectangle_rounded(rl.Rectangle(mx, pbar_y, pbar_w, 4), 1.0, 8, rl.Color(60, 60, 60, 255))
        prog = getattr(state, 'music_progress', 0.4)
        rl.draw_rectangle_rounded(rl.Rectangle(mx, pbar_y, int(pbar_w * prog), 4), 1.0, 8, rl.Color(51, 171, 76, 255))

    # ════════════════════════════════════════════════════════════════════════════
    # 4. TOP STRIP - ISO 2575 Telltale Glyphs & Directional Arrows
    # ════════════════════════════════════════════════════════════════════════════
    def _draw_top_strip(self, state, w, h, theme, mouse=None, clicked=False):
        cx = w / 2
        
        # ISO 2575 Compliant Telltales in Center
        # 1. High-Voltage / Powertrain READY Badge
        ready_w = 76
        rl.draw_rectangle_rounded(rl.Rectangle(cx - 140, 6, ready_w, 24), 0.35, 12, rl.Color(51, 171, 76, 255))
        self._draw_text_centered(self.fonts['xs'], "READY", cx - 140 + ready_w / 2, 18, rl.Color(0, 0, 0, 255))
        
        # 2. ISO Headlamp Beam Icon
        headlamp_active = self.headlights
        h_color = rl.Color(51, 171, 76, 255) if headlamp_active else rl.Color(90, 90, 90, 255)
        hx = cx - 20
        hy = 18
        # Draw headlamp dome + rays
        rl.draw_circle(int(hx), int(hy), 8, h_color)
        rl.draw_rectangle(int(hx - 8), int(hy - 8), 8, 16, rl.Color(0, 0, 0, 255))
        for r in range(3):
            rl.draw_line_ex(rl.Vector2(hx + 4, hy - 6 + r * 6), rl.Vector2(hx + 12, hy - 6 + r * 6), 2, h_color)
            
        # 3. ISO Comma Steering Wheel / ALKS Icon
        steer_active = getattr(state, 'acc_active', True)
        s_color = rl.Color(51, 171, 76, 255) if steer_active else rl.Color(90, 90, 90, 255)
        sx = cx + 50
        sy = 18
        rl.draw_circle_lines(int(sx), int(sy), 9, s_color)
        rl.draw_line_ex(rl.Vector2(sx - 9, sy), rl.Vector2(sx + 9, sy), 2, s_color)
        rl.draw_line_ex(rl.Vector2(sx, sy), rl.Vector2(sx, sy + 9), 2, s_color)

        # Flashing Directional Turn Signals (1.5 Hz)
        now = time.time()
        flash_on = (int(now * 3) % 2 == 0)
        
        # Left Turn Arrow
        left_active = (self.turn_left or self.hazard) and flash_on
        ts_l_col = rl.Color(51, 171, 76, 255) if left_active else rl.Color(60, 60, 60, 255)
        p1_l = rl.Vector2(cx - 280, h / 2)
        p2_l = rl.Vector2(cx - 256, h / 2 - 14)
        p3_l = rl.Vector2(cx - 256, h / 2 + 14)
        rl.draw_triangle(p1_l, p3_l, p2_l, ts_l_col)
        
        # Right Turn Arrow
        right_active = (self.turn_right or self.hazard) and flash_on
        ts_r_col = rl.Color(51, 171, 76, 255) if right_active else rl.Color(60, 60, 60, 255)
        p1_r = rl.Vector2(cx + 280, h / 2)
        p2_r = rl.Vector2(cx + 256, h / 2 + 14)
        p3_r = rl.Vector2(cx + 256, h / 2 - 14)
        rl.draw_triangle(p1_r, p3_r, p2_r, ts_r_col)

    # ════════════════════════════════════════════════════════════════════════════
    # 5. BOTTOM STRIP - Docked Capsule Badges
    # ════════════════════════════════════════════════════════════════════════════
    def _draw_bottom_strip(self, state, x, y, w, h, theme, mouse=None, clicked=False):
        # 1. Left Dock: Fuel Level Capsule
        fuel_pct = int(getattr(state, 'fuel_level', 0.82) * 100)
        f_rect = rl.Rectangle(24, y + 10, 160, 36)
        rl.draw_rectangle_rounded(f_rect, 0.4, 16, rl.Color(32, 32, 32, 255))
        fuel_tex = self.textures.get('fuel')
        if fuel_tex and fuel_tex.id > 0:
            scale = 16.0 / max(fuel_tex.width, 1)
            rl.draw_texture_ex(fuel_tex, rl.Vector2(36, y + 20), 0.0, scale, rl.WHITE)
        rl.draw_text_ex(self.fonts['xs'], f"FUEL {fuel_pct}% · 340 MI", rl.Vector2(58, y + 20), self.fonts['xs'].baseSize, 0, rl.Color(255, 255, 255, 255))
        
        # 2. Center: Cluster Drive Mode Status Badge
        modes = ["ECO", "NORMAL", "SPORT"]
        cur_mode = modes[self.drive_mode_idx]
        m_rect = rl.Rectangle(w / 2 - 80, y + 10, 160, 36)
        rl.draw_rectangle_rounded(m_rect, 0.4, 16, rl.Color(32, 32, 32, 255))
        rl.draw_circle(int(w / 2 - 56), int(y + 28), 4, rl.Color(51, 171, 76, 255))
        self._draw_text_centered(self.fonts['xs'], f"MODE · {cur_mode}", w / 2 + 10, y + 28, rl.Color(255, 255, 255, 255))
        
        # 3. Right Dock: Trip Odometer & System Clock
        t_rect = rl.Rectangle(w - 280, y + 10, 256, 36)
        rl.draw_rectangle_rounded(t_rect, 0.4, 16, rl.Color(32, 32, 32, 255))
        dist = getattr(state, 'trip_distance_mi', 127.4)
        clock_str = time.strftime("%I:%M %p")
        rl.draw_text_ex(self.fonts['xs'], f"TRIP {dist:.1f} MI  ·  {clock_str}", rl.Vector2(w - 264, y + 20), self.fonts['xs'].baseSize, 0, rl.Color(255, 255, 255, 255))

    def handle_key(self, key: int, state, theme):
        if key == rl.KeyboardKey.KEY_UP:
            if hasattr(state, 'speed_mph'): state.speed_mph = min(state.speed_mph + 5, 120)
            if hasattr(state, 'rpm'): state.rpm = min(state.rpm + 500, 8000)
        elif key == rl.KeyboardKey.KEY_DOWN:
            if hasattr(state, 'speed_mph'): state.speed_mph = max(state.speed_mph - 5, 0)
            if hasattr(state, 'rpm'): state.rpm = max(state.rpm - 500, 0)
        elif key == rl.KeyboardKey.KEY_LEFT:
            self.turn_left = not self.turn_left
        elif key == rl.KeyboardKey.KEY_RIGHT:
            self.turn_right = not self.turn_right
        elif key == rl.KeyboardKey.KEY_H:
            self.hazard = not self.hazard
        elif key == rl.KeyboardKey.KEY_L:
            self.headlights = not self.headlights
        elif key == rl.KeyboardKey.KEY_A:
            if hasattr(state, 'acc_active'): state.acc_active = not state.acc_active
        elif key == rl.KeyboardKey.KEY_G:
            if hasattr(state, 'gear'): state.gear = (state.gear + 1) % 4

# surfaces/hud.py — Comma 4 Glassmorphic HUD Surface
import pyray as rl
import os
import math
import time
import glass

class HUDSurface:
    def __init__(self, fonts: dict):
        self.fonts = fonts
        
        self._smooth_speed = 65.0
        self._smooth_rpm = 2400.0
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
            ('arrow-up', 'assets/icons/arrow-up_white.png'),
            ('art1', 'assets/music/the_midnight.jpg'),
            ('art2', 'assets/music/tycho.jpg'),
            ('art3', 'assets/music/bonobo.jpg'),
        ]:
            if os.path.exists(path):
                self.textures[name] = rl.load_texture(path)
            else:
                self.textures[name] = None
            
    def _draw_text_centered(self, font, text, x, y, color):
        size = rl.measure_text_ex(font, text, font.baseSize, 0)
        rl.draw_text_ex(font, text, rl.Vector2(x - size.x / 2, y - size.y / 2), font.baseSize, 0, color)

    def _draw_icon_centered(self, name, cx, cy, size, tint=None):
        tex = self.textures.get(name)
        if tex and tex.id > 0:
            scale = float(size) / max(tex.width, 1)
            w = tex.width * scale
            h = tex.height * scale
            rl.draw_texture_ex(tex, rl.Vector2(cx - w / 2, cy - h / 2), 0.0, scale, tint or glass.TEXT_PRIMARY)
        
    def render(self, state, theme):
        w = rl.get_screen_width()
        h = rl.get_screen_height()
        
        glass.draw_ambient_backdrop(w, h)
        
        speed = getattr(state, 'speed_mph', 65.0)
        rpm = getattr(state, 'rpm', 2400.0)
        temp = getattr(state, 'engine_temp_f', 195.0)

        self._smooth_speed += (speed - self._smooth_speed) * 0.12
        self._smooth_rpm += (rpm - self._smooth_rpm) * 0.12
        self._smooth_temp += (temp - self._smooth_temp) * 0.12
        
        top_h = 44
        bottom_h = 48
        side_w = int(w * 0.28)
        center_w = w - side_w * 2
        
        clicked = rl.is_mouse_button_pressed(rl.MouseButton.MOUSE_BUTTON_LEFT)
        mouse = rl.get_mouse_position()

        # 1. 3D Openpilot Road Vision & Horizon
        self._draw_center_road_vision(state, side_w, top_h, center_w, h - top_h - bottom_h)
        
        # 2. Luminous Halo Speedometer & Speed Limit
        self._draw_speedometer(state, side_w, top_h, center_w, h - top_h - bottom_h)
        
        # 3. Left Section - Comma 3X ADAS Glass Pod
        self._draw_left_panel(state, 16, top_h + 8, side_w - 24, h - top_h - bottom_h - 16)
        
        # 4. Right Section - Navigation & Media Glass Pods
        self._draw_right_panel(state, w - side_w + 8, top_h + 8, side_w - 24, h - top_h - bottom_h - 16)
        
        # 5. Top Strip - ISO Telltales in Floating Frosted Capsule
        self._draw_top_strip(state, w, top_h, mouse=mouse, clicked=clicked)
        
        # 6. Bottom Strip - Floating Status Capsules
        self._draw_bottom_strip(state, 0, h - bottom_h, w, bottom_h, mouse=mouse, clicked=clicked)

    # ════════════════════════════════════════════════════════════════════════════
    # 1. CENTER ROAD VISION - 3D Perspective Spline, Grid & Lead Car Wireframe
    # ════════════════════════════════════════════════════════════════════════════
    def _draw_center_road_vision(self, state, x, y, w, h):
        cx = x + w / 2
        horizon_y = y + h * 0.38
        road_bot_y = y + h + 10
        
        # Receding grid depth lines
        for step in [0.2, 0.38, 0.58, 0.78, 0.95]:
            grid_y = horizon_y + (road_bot_y - horizon_y) * (step ** 1.8)
            half_gw = 30 + (w * 0.44) * (step ** 1.4)
            alpha = int(45 * step)
            rl.draw_line_ex(
                rl.Vector2(cx - half_gw, grid_y), 
                rl.Vector2(cx + half_gw, grid_y), 
                1.2, rl.Color(56, 189, 248, alpha)
            )
            
        # Comma Openpilot Vision Corridor (Luminous Neon Path)
        p_top_l = rl.Vector2(cx - 32, horizon_y + 10)
        p_top_r = rl.Vector2(cx + 32, horizon_y + 10)
        p_bot_l = rl.Vector2(cx - 160, road_bot_y)
        p_bot_r = rl.Vector2(cx + 160, road_bot_y)
        
        # Semi-transparent neon green polygon fill
        rl.draw_triangle(p_bot_l, p_bot_r, p_top_r, rl.Color(46, 213, 115, 28))
        rl.draw_triangle(p_bot_l, p_top_r, p_top_l, rl.Color(46, 213, 115, 28))
        
        # Lane boundary lines (Glowing outer borders)
        rl.draw_line_ex(p_top_l, p_bot_l, 6.0, rl.Color(46, 213, 115, 60))
        rl.draw_line_ex(p_top_l, p_bot_l, 2.5, glass.COMMA_GREEN)
        rl.draw_line_ex(p_top_r, p_bot_r, 6.0, rl.Color(46, 213, 115, 60))
        rl.draw_line_ex(p_top_r, p_bot_r, 2.5, glass.COMMA_GREEN)

        # Center dashed spline guide
        dash_t = (time.time() * 3) % 1.0
        for i in range(5):
            d_frac = ((i + dash_t) % 5) / 5.0
            if d_frac < 0.1: continue
            dy = horizon_y + (road_bot_y - horizon_y) * (d_frac ** 1.5)
            dh = max(4.0, 22.0 * d_frac)
            dw = max(2.0, 5.0 * d_frac)
            d_alpha = int(220 * d_frac)
            rl.draw_rectangle_rounded(
                rl.Rectangle(cx - dw/2, dy, dw, dh), 
                0.5, 4, rl.Color(255, 255, 255, d_alpha)
            )

        # 3D Lead Vehicle Box with Radar Lock
        lead_y = horizon_y + 80
        lead_w = 64
        lead_h = 36
        lead_rect = rl.Rectangle(cx - lead_w / 2, lead_y, lead_w, lead_h)
        
        # Radar tracking box aura
        rl.draw_rectangle_rounded(rl.Rectangle(lead_rect.x - 3, lead_rect.y - 3, lead_rect.width + 6, lead_rect.height + 6), 0.35, 12, glass.COMMA_GREEN_GLOW)
        rl.draw_rectangle_rounded(lead_rect, 0.35, 12, rl.Color(16, 32, 24, 220))
        rl.draw_rectangle_rounded_lines_ex(lead_rect, 0.35, 12, 1.8, glass.COMMA_GREEN)
        
        # Car roof polygon inside lead car
        rl.draw_rectangle_rounded(rl.Rectangle(cx - 16, lead_y + 6, 32, 12), 0.3, 6, rl.Color(46, 213, 115, 140))
        # Taillights
        rl.draw_circle(int(cx - 20), int(lead_y + lead_h - 7), 3, glass.CRIMSON_RED)
        rl.draw_circle(int(cx + 20), int(lead_y + lead_h - 7), 3, glass.CRIMSON_RED)
        
        # Lead distance frosted pill badge
        dist_pill = rl.Rectangle(cx - 26, lead_y - 18, 52, 20)
        glass.draw_glass_pill(dist_pill, roundness=0.5, bg=glass.COMMA_GREEN)
        self._draw_text_centered(self.fonts['xs'], "42 m", cx, lead_y - 8, glass.OBSIDIAN_BG)

    # ════════════════════════════════════════════════════════════════════════════
    # 2. LUMINOUS SPEEDOMETER & SPEED LIMIT
    # ════════════════════════════════════════════════════════════════════════════
    def _draw_speedometer(self, state, x, y, w, h):
        cx = x + w / 2
        cy = y + h * 0.36
        
        radius = min(w * 0.25, h * 0.34)
        center = rl.Vector2(cx, cy)
        
        # Background arc track (frosted translucent dark halo)
        rl.draw_ring(center, radius - 8, radius + 2, 135, 405, 64, rl.Color(28, 32, 44, 200))
        rl.draw_ring(center, radius - 2, radius, 135, 405, 64, rl.Color(255, 255, 255, 20))
        
        # Speed fill arc (Glowing Comma Green / Tesla Sky Blue)
        max_speed = 120.0
        pct = max(0.0, min(1.0, self._smooth_speed / max_speed))
        fill_angle = 135.0 + pct * 270.0
        
        if pct > 0.01:
            # Ambient glow behind arc
            rl.draw_ring(center, radius - 12, radius + 6, 135, fill_angle, 64, glass.COMMA_GREEN_GLOW)
            # Crisp luminous arc
            rl.draw_ring(center, radius - 8, radius + 2, 135, fill_angle, 64, glass.COMMA_GREEN)
            
        # Large Crisp Speed Digits
        speed_str = str(int(self._smooth_speed))
        speed_font = self.fonts.get('xxl', self.fonts['xl'])
        self._draw_text_centered(speed_font, speed_str, cx, cy - 24, glass.TEXT_PRIMARY)
        self._draw_text_centered(self.fonts['md'], "MPH", cx, cy + 54, glass.TEXT_SECONDARY)
        
        # Drop-shadowed Speed Limit Sign with 48px clearance
        sign_cx = cx + radius + 48
        sign_cy = cy - 20
        glass.draw_speed_limit_sign(sign_cx, sign_cy, self.target_speed, self.fonts['xs'], self.fonts['bmd'])

    # ════════════════════════════════════════════════════════════════════════════
    # 3. LEFT PANEL - Comma 3X ADAS Hub Glass Pod
    # ════════════════════════════════════════════════════════════════════════════
    def _draw_left_panel(self, state, x, y, w, h):
        glass.draw_glass_card(rl.Rectangle(x, y, w, h), roundness=0.35)
        
        px = x + 20
        pw = w - 40
        
        # Header: Comma 3X Active Status
        rl.draw_circle(int(px + 6), int(y + 24), 5, glass.COMMA_GREEN)
        rl.draw_circle(int(px + 6), int(y + 24), 10, glass.COMMA_GREEN_GLOW)
        rl.draw_text_ex(self.fonts['xs'], "comma 3X · openpilot active", rl.Vector2(px + 20, y + 16), self.fonts['xs'].baseSize, 0, glass.COMMA_GREEN)
        
        # 1. Lead Vehicle Radar Card
        radar_y = y + 46
        radar_rect = rl.Rectangle(px, radar_y, pw, 74)
        glass.draw_glass_pill(radar_rect, roundness=0.28, bg=rl.Color(22, 26, 36, 210))
        
        rl.draw_text_ex(self.fonts['xs'], "RADAR TRACKING", rl.Vector2(px + 16, radar_y + 12), self.fonts['xs'].baseSize, 0, glass.TEXT_MUTED)
        rl.draw_text_ex(self.fonts['bmd'], "LEAD CAR: 42 m", rl.Vector2(px + 16, radar_y + 34), self.fonts['bmd'].baseSize, 0, glass.TEXT_PRIMARY)
        
        # Following Gap Bars
        rl.draw_text_ex(self.fonts['xs'], "GAP 3", rl.Vector2(px + pw - 48, radar_y + 12), self.fonts['xs'].baseSize, 0, glass.COMMA_GREEN)
        for g in range(3):
            g_rect = rl.Rectangle(px + pw - 48 + g * 15, radar_y + 36, 10, 18)
            glass.draw_glass_pill(g_rect, roundness=0.3, active=True)
            
        # 2. Steering Torque Lateral Actuator
        torq_y = radar_y + 88
        rl.draw_text_ex(self.fonts['xs'], "STEERING TORQUE (LATERAL ACTUATOR)", rl.Vector2(px, torq_y), self.fonts['xs'].baseSize, 0, glass.TEXT_MUTED)
        
        t_bar_y = torq_y + 20
        rl.draw_rectangle_rounded(rl.Rectangle(px, t_bar_y, pw, 10), 1.0, 8, rl.Color(32, 36, 48, 255))
        # Center line
        rl.draw_rectangle(int(px + pw / 2 - 1), int(t_bar_y - 3), 2, 16, rl.Color(180, 180, 180, 255))
        # Dynamic fill
        t_fill_w = int((pw / 2) * self._smooth_torque)
        rl.draw_rectangle_rounded(rl.Rectangle(px + pw / 2, t_bar_y, t_fill_w, 10), 1.0, 8, glass.COMMA_GREEN)
        
        # 3. Glare-Resistant PRNDL Strip (ISO 15008 Compliant)
        prndl_y = torq_y + 48
        prndl_rect = rl.Rectangle(px, prndl_y, pw, 60)
        glass.draw_glass_pill(prndl_rect, roundness=0.32, bg=rl.Color(22, 26, 36, 220))
        
        gears = ['P', 'R', 'N', 'D']
        raw_gear = getattr(state, 'gear', 3)
        gear_idx = raw_gear if isinstance(raw_gear, int) and 0 <= raw_gear < 4 else 3
        
        slot_w = pw / 4.0
        for i, g in enumerate(gears):
            gx = px + i * slot_w + slot_w / 2
            gy = prndl_y + 30
            is_active = (i == gear_idx)
            
            if is_active:
                pill_w, pill_h = 52, 42
                active_bg = glass.COMMA_GREEN if g != 'R' else glass.CRIMSON_RED
                pill_r = rl.Rectangle(gx - pill_w/2, gy - pill_h/2, pill_w, pill_h)
                glass.draw_glass_pill(pill_r, roundness=0.35, bg=active_bg, active=True)
                self._draw_text_centered(self.fonts['blg'], g, gx, gy, glass.OBSIDIAN_BG)
            else:
                self._draw_text_centered(self.fonts['blg'], g, gx, gy, glass.TEXT_MUTED)

        # 4. Powertrain: Engine Coolant Temp & RPM
        pt_y = prndl_y + 76
        rl.draw_text_ex(self.fonts['xs'], "ENGINE COOLANT", rl.Vector2(px, pt_y), self.fonts['xs'].baseSize, 0, glass.TEXT_MUTED)
        temp_int = int(self._smooth_temp)
        rl.draw_text_ex(self.fonts['bmd'], f"{temp_int}°F", rl.Vector2(px + pw - 70, pt_y - 2), self.fonts['bmd'].baseSize, 0, glass.TEXT_PRIMARY)
        
        t_bar_y = pt_y + 20
        rl.draw_rectangle_rounded(rl.Rectangle(px, t_bar_y, pw, 8), 1.0, 8, rl.Color(32, 36, 48, 255))
        pct = max(0.0, min(1.0, (self._smooth_temp - 100) / 140.0))
        t_col = glass.COMMA_GREEN if pct < 0.8 else glass.CRIMSON_RED
        rl.draw_rectangle_rounded(rl.Rectangle(px, t_bar_y, int(pw * pct), 8), 1.0, 8, t_col)
        
        rl.draw_text_ex(self.fonts['xs'], "140°F", rl.Vector2(px, t_bar_y + 12), self.fonts['xs'].baseSize, 0, glass.TEXT_MUTED)
        rl.draw_text_ex(self.fonts['xs'], "NOMINAL", rl.Vector2(px + pw / 2 - 24, t_bar_y + 12), self.fonts['xs'].baseSize, 0, glass.COMMA_GREEN)
        rl.draw_text_ex(self.fonts['xs'], "240°F", rl.Vector2(px + pw - 42, t_bar_y + 12), self.fonts['xs'].baseSize, 0, glass.TEXT_MUTED)
        
        # 5. Driver Monitoring & Bus Health Pod (Eliminates negative space)
        dm_y = t_bar_y + 36
        dm_rect = rl.Rectangle(px, dm_y, pw, 58)
        glass.draw_glass_pill(dm_rect, roundness=0.28, bg=rl.Color(20, 24, 34, 210))
        
        rl.draw_circle(int(px + 18), int(dm_y + 18), 4, glass.COMMA_GREEN)
        rl.draw_text_ex(self.fonts['xs'], "DRIVER MONITOR: ATTENTIVE", rl.Vector2(px + 30, dm_y + 11), self.fonts['xs'].baseSize, 0, glass.TEXT_PRIMARY)
        rl.draw_text_ex(self.fonts['xs'], "CAN Bus: 500 kbps · 100 Hz · 0 Drops", rl.Vector2(px + 16, dm_y + 34), self.fonts['xs'].baseSize, 0, glass.TEXT_SECONDARY)
        
        # RPM Live Indicator
        rpm_val = int(self._smooth_rpm)
        rl.draw_text_ex(self.fonts['xs'], f"TACH: {rpm_val:,} RPM", rl.Vector2(px, y + h - 26), self.fonts['xs'].baseSize, 0, glass.TEXT_MUTED)

    # ════════════════════════════════════════════════════════════════════════════
    # 4. RIGHT PANEL - Navigation & Media Glass Pods
    # ════════════════════════════════════════════════════════════════════════════
    def _draw_right_panel(self, state, x, y, w, h):
        nav_h = int((h - 12) * 0.54)
        media_h = h - nav_h - 12
        
        # ── 1. Navigation Glass Pod ───────────────────────────────────────────
        glass.draw_glass_card(rl.Rectangle(x, y, w, nav_h), roundness=0.35)
        
        nx = x + 20
        nw = w - 40
        
        rl.draw_text_ex(self.fonts['xs'], "NAVIGATION", rl.Vector2(nx, y + 16), self.fonts['xs'].baseSize, 0, glass.TEXT_MUTED)
        dest_str = getattr(state, 'destination', 'Downtown SF')
        rl.draw_text_ex(self.fonts['blg'], dest_str, rl.Vector2(nx, y + 36), self.fonts['blg'].baseSize, 0, glass.TEXT_PRIMARY)
        
        # Maneuver Banner with Circular Button
        maneuver_y = y + 84
        glass.draw_circular_button(nx + 20, maneuver_y + 20, 20, bg=glass.COMMA_GREEN, glow=glass.COMMA_GREEN_GLOW)
        self._draw_icon_centered("arrow-up", nx + 20, maneuver_y + 20, 22, glass.OBSIDIAN_BG)
        
        rl.draw_text_ex(self.fonts['bmd'], "In 800 ft, Exit 432B", rl.Vector2(nx + 50, maneuver_y + 2), self.fonts['bmd'].baseSize, 0, glass.TEXT_PRIMARY)
        rl.draw_text_ex(self.fonts['sm'], "Merge onto US-101 North", rl.Vector2(nx + 50, maneuver_y + 24), self.fonts['sm'].baseSize, 0, glass.TEXT_SECONDARY)
        
        # Lane Guidance
        lane_y = maneuver_y + 54
        rl.draw_text_ex(self.fonts['xs'], "LANE GUIDANCE", rl.Vector2(nx, lane_y), self.fonts['xs'].baseSize, 0, glass.TEXT_MUTED)
        
        lanes = ["LEFT", "THRU", "THRU", "EXIT"]
        active_lane = 3
        for idx, lname in enumerate(lanes):
            lx = nx + idx * 52
            is_active_lane = (idx == active_lane)
            l_box = rl.Rectangle(lx, lane_y + 18, 46, 26)
            glass.draw_glass_pill(l_box, roundness=0.3, active=is_active_lane)
            self._draw_text_centered(self.fonts['xs'], lname, lx + 23, lane_y + 30, glass.OBSIDIAN_BG if is_active_lane else glass.TEXT_PRIMARY)
            
        # ETA Capsule Badge
        eta_y = y + nav_h - 36
        eta_pill = rl.Rectangle(nx, eta_y, nw, 26)
        glass.draw_glass_pill(eta_pill, roundness=0.5)
        self._draw_text_centered(self.fonts['xs'], "14 MIN  ·  12.4 MI  ·  5:42 PM", nx + nw / 2, eta_y + 13, glass.COMMA_GREEN)

        # ── 2. Media Glass Pod ────────────────────────────────────────────────
        my = y + nav_h + 12
        glass.draw_glass_card(rl.Rectangle(x, my, w, media_h), roundness=0.35)
        
        rl.draw_text_ex(self.fonts['xs'], "NOW PLAYING", rl.Vector2(nx, my + 16), self.fonts['xs'].baseSize, 0, glass.TEXT_MUTED)
        
        # Spotify Pill
        sp_rect = rl.Rectangle(x + w - 90, my + 12, 70, 22)
        glass.draw_glass_pill(sp_rect, roundness=0.5, active=True, solid=True)
        self._draw_text_centered(self.fonts['xs'], "SPOTIFY", sp_rect.x + 35, my + 23, glass.OBSIDIAN_BG)
        
        # Album Art
        art_keys = ['art1', 'art2', 'art3']
        track_idx = getattr(state, 'music_track', 0) % len(art_keys)
        art_tex = self.textures.get(art_keys[track_idx])
        art_size = 64
        art_y = my + 38
        
        rl.draw_rectangle_rounded(rl.Rectangle(nx - 2, art_y - 1, art_size + 4, art_size + 6), 0.2, 12, glass.SHADOW_CORE)
        if art_tex and art_tex.id > 0:
            scale = art_size / max(art_tex.width, 1)
            rl.draw_texture_ex(art_tex, rl.Vector2(nx, art_y), 0.0, scale, rl.WHITE)
            rl.draw_rectangle_rounded_lines_ex(rl.Rectangle(nx, art_y, art_size, art_size), 0.2, 12, 1.2, glass.GLASS_BORDER)
            
        mx_meta = nx + art_size + 14
        rl.draw_text_ex(self.fonts['bmd'], getattr(state, 'music_title', "Los Angeles"), rl.Vector2(mx_meta, art_y + 2), self.fonts['bmd'].baseSize, 0, glass.TEXT_PRIMARY)
        rl.draw_text_ex(self.fonts['sm'], getattr(state, 'music_artist', "The Midnight"), rl.Vector2(mx_meta, art_y + 28), self.fonts['sm'].baseSize, 0, glass.TEXT_SECONDARY)
        rl.draw_text_ex(self.fonts['xs'], "FLAC 96kHz Lossless", rl.Vector2(mx_meta, art_y + 50), self.fonts['xs'].baseSize, 0, glass.SKY_BLUE)
        
        # Audio spectrum bars
        spec_x = x + w - 74
        spec_y = art_y + 46
        now_t = time.time() * 8
        for b in range(5):
            h_anim = int(18 * (0.35 + 0.65 * abs(((now_t + b * 1.1) % 2) - 1)))
            glass.draw_glass_pill(rl.Rectangle(spec_x + b * 9, spec_y - h_anim, 5, h_anim), roundness=0.5, bg=glass.COMMA_GREEN, border=glass.COMMA_GREEN)
            
        # Progress bar
        p_bar_y = my + media_h - 22
        rl.draw_rectangle_rounded(rl.Rectangle(nx, p_bar_y, nw, 5), 1.0, 8, rl.Color(32, 36, 48, 255))
        f_w = int(nw * getattr(state, 'music_progress', 0.38))
        if f_w > 0:
            rl.draw_rectangle_rounded(rl.Rectangle(nx, p_bar_y, f_w, 5), 1.0, 8, glass.COMMA_GREEN)

    # ════════════════════════════════════════════════════════════════════════════
    # 5. TOP STRIP - ISO Telltales Floating Pill Cluster
    # ════════════════════════════════════════════════════════════════════════════
    def _draw_top_strip(self, state, w, h, mouse, clicked):
        pill_w = 270
        pill_h = 34
        pill_rx = (w - pill_w) / 2
        pill_ry = 6
        
        glass.draw_glass_pill(rl.Rectangle(pill_rx, pill_ry, pill_w, pill_h), roundness=0.5)
        
        t_blink = int(time.time() * 2.5) % 2 == 0
        l_col = glass.COMMA_GREEN if (self.turn_left or self.hazard) and t_blink else glass.TEXT_MUTED
        r_col = glass.COMMA_GREEN if (self.turn_right or self.hazard) and t_blink else glass.TEXT_MUTED
        
        cx = w / 2
        cy = pill_ry + pill_h / 2
        
        # Antialiased Vector Turn Signals
        glass.draw_turn_arrow(cx - 96, cy, 14, left=True, color=l_col)
        glass.draw_turn_arrow(cx + 96, cy, 14, left=False, color=r_col)
        
        # READY badge
        ready_r = rl.Rectangle(cx - 48, cy - 11, 52, 22)
        glass.draw_glass_pill(ready_r, roundness=0.45, active=True, solid=True)
        self._draw_text_centered(self.fonts['xs'], "READY", ready_r.x + 26, cy, glass.OBSIDIAN_BG)
        
        # Headlights indicator
        self._draw_icon_centered("sun", cx + 22, cy, 18, glass.COMMA_GREEN if self.headlights else glass.TEXT_MUTED)
        
        # ADAS steering icon
        self._draw_icon_centered("shield", cx + 52, cy, 18, glass.SKY_BLUE)
        
        if clicked:
            if rl.check_collision_point_rec(mouse, rl.Rectangle(cx - 115, pill_ry, 30, pill_h)): self.turn_left = not self.turn_left
            elif rl.check_collision_point_rec(mouse, rl.Rectangle(cx + 75, pill_ry, 30, pill_h)): self.turn_right = not self.turn_right

    # ════════════════════════════════════════════════════════════════════════════
    # 6. BOTTOM STRIP - Floating Status Capsules
    # ════════════════════════════════════════════════════════════════════════════
    def _draw_bottom_strip(self, state, x, y, w, h, mouse, clicked):
        by = y + 6
        bh = 34
        
        # Left Capsule: Fuel Gauge
        fuel_pct = int(getattr(state, 'fuel_level', 0.82) * 100)
        fuel_w = 170
        fuel_r = rl.Rectangle(20, by, fuel_w, bh)
        glass.draw_glass_pill(fuel_r, roundness=0.5)
        self._draw_icon_centered("fuel", 38, by + bh/2, 16, glass.TEXT_PRIMARY)
        rl.draw_text_ex(self.fonts['xs'], f"FUEL {fuel_pct}% · 340 MI", rl.Vector2(54, by + 10), self.fonts['xs'].baseSize, 0, glass.TEXT_PRIMARY)
        
        # Center Capsule: Drive Mode
        mode_w = 160
        mode_r = rl.Rectangle(w / 2 - mode_w / 2, by, mode_w, bh)
        glass.draw_glass_pill(mode_r, roundness=0.5)
        rl.draw_circle(int(mode_r.x + 24), int(by + bh/2), 4, glass.COMMA_GREEN)
        rl.draw_text_ex(self.fonts['xs'], "MODE · NORMAL", rl.Vector2(mode_r.x + 36, by + 10), self.fonts['xs'].baseSize, 0, glass.TEXT_PRIMARY)
        
        # Right Capsule: Trip & Clock
        trip_w = 190
        trip_r = rl.Rectangle(w - trip_w - 20, by, trip_w, bh)
        glass.draw_glass_pill(trip_r, roundness=0.5)
        clock_str = time.strftime("%I:%M %p")
        self._draw_text_centered(self.fonts['xs'], f"TRIP 127.4 MI  ·  {clock_str}", trip_r.x + trip_w / 2, by + bh/2, glass.TEXT_PRIMARY)

    def handle_key(self, key, state, theme):
        if key == rl.KeyboardKey.KEY_LEFT: self.turn_left = not self.turn_left
        elif key == rl.KeyboardKey.KEY_RIGHT: self.turn_right = not self.turn_right
        elif key == rl.KeyboardKey.KEY_H: self.hazard = not self.hazard
        elif key == rl.KeyboardKey.KEY_L: self.headlights = not self.headlights
        elif key == rl.KeyboardKey.KEY_UP: self.target_speed = min(90, self.target_speed + 5)
        elif key == rl.KeyboardKey.KEY_DOWN: self.target_speed = max(25, self.target_speed - 5)

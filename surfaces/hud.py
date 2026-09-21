import pyray as rl
import os
import math

class HUDSurface:
    def __init__(self, fonts: dict):
        self.fonts = fonts  # xxl(140px bold), xl(96px bold), bxl(120px bold), lg(48px), blg(48px bold), md(32px), bmd(32px bold), sm(22px), xs(16px)
        
        self._smooth_speed = 0.0
        self._smooth_rpm = 0.0
        self._smooth_temp = 150.0
        
        self.turn_left = False
        self.turn_right = False
        self.hazard = False
        self.headlights = False
        self.target_speed = 65
        
        self.textures = {}
        self._load_texture('nav', 'assets/icons/navigation_white.png')
        self._load_texture('music', 'assets/icons/music_white.png')
        self._load_texture('gauge', 'assets/icons/gauge_white.png')
        self._load_texture('fuel', 'assets/icons/fuel_white.png')
        self._load_texture('art1', 'assets/music/the_midnight.jpg')
        self._load_texture('art2', 'assets/music/tycho.jpg')
        self._load_texture('art3', 'assets/music/bonobo.jpg')

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
        
        # Pure black bg
        rl.draw_rectangle(0, 0, w, h, rl.Color(0, 0, 0, 255))
        
        speed = getattr(state, 'speed_mph', 0.0)
        rpm = getattr(state, 'rpm', 0.0)
        temp = getattr(state, 'engine_temp_f', 150.0)

        self._smooth_speed += (speed - self._smooth_speed) * 0.1
        self._smooth_rpm += (rpm - self._smooth_rpm) * 0.1
        self._smooth_temp += (temp - self._smooth_temp) * 0.1
        
        # Layout metrics
        top_h = h * 0.05
        bottom_h = h * 0.07
        left_w = w * 0.28
        center_w = w * 0.44
        right_w = w * 0.28
        
        # Center section - Speed and Road
        self._draw_center_panel(state, left_w, top_h, center_w, h - top_h - bottom_h, theme)
        
        # Left section - RPM and Temp
        self._draw_left_panel(state, 0, top_h, left_w, h - top_h - bottom_h, theme)
        
        # Right section - Nav and Media
        self._draw_right_panel(state, left_w + center_w, top_h, right_w, h - top_h - bottom_h, theme)
        
        # Top strip
        self._draw_top_strip(state, w, top_h, theme)
        
        # Bottom strip
        self._draw_bottom_strip(state, 0, h - bottom_h, w, bottom_h, theme)

    def _draw_left_panel(self, state, x, y, w, h, theme):
        pad = 24
        rect = rl.Rectangle(x + pad, y + pad, w - pad*2, h - pad*2)
        rl.draw_rectangle_rounded(rect, 0.35, 32, rl.Color(41, 41, 41, 255)) # #292929
        
        cx = x + w / 2
        cy = y + h * 0.4
        
        # RPM Arc
        inner_r = w * 0.25
        outer_r = w * 0.30
        
        # Track
        center = rl.Vector2(cx, cy)
        rl.draw_ring(center, inner_r, outer_r, 135, 405, 64, rl.Color(60, 60, 60, 255))
        
        # Fill
        fill_angle = 135 + (self._smooth_rpm / 8000) * 270
        fill_angle = min(max(fill_angle, 135), 405)
        
        if self._smooth_rpm < 4000:
            fill_color = rl.Color(51, 171, 76, 255) # Green
        elif self._smooth_rpm < 6500:
            fill_color = rl.Color(255, 204, 0, 255) # Yellow
        else:
            fill_color = rl.Color(226, 44, 44, 255) # Red
            
        rl.draw_ring(center, inner_r, outer_r, 135, fill_angle, 64, fill_color)
        
        # RPM Text
        rpm_str = str(int(self._smooth_rpm))
        self._draw_text_centered(self.fonts['xl'], rpm_str, cx, cy - 20, rl.Color(255, 255, 255, 255))
        self._draw_text_centered(self.fonts['sm'], "RPM", cx, cy + 40, rl.Color(170, 170, 170, 255))
        
        # Gear
        gears = ['P', 'R', 'N', 'D']
        gear_idx = getattr(state, 'gear', 0)
        gear_char = gears[gear_idx] if 0 <= gear_idx < len(gears) else 'P'
        
        gy = cy + inner_r + 80
        g_color = rl.Color(170, 170, 170, 255)
        if gear_char == 'D': 
            g_color = rl.Color(70, 91, 234, 255) # #465bea
        elif gear_char == 'R': 
            g_color = rl.Color(226, 44, 44, 255) # #e22c2c
            
        self._draw_text_centered(self.fonts['blg'], gear_char, cx, gy, g_color)
        
        # Temp
        ty = rect.y + rect.height - pad - 40
        temp_w = rect.width - 80
        rl.draw_text_ex(self.fonts['xs'], "TEMP", rl.Vector2(x + 40, ty - 25), self.fonts['xs'].baseSize, 0, rl.Color(170, 170, 170, 255))
        
        rl.draw_rectangle(int(x + 40), int(ty), int(temp_w), 10, rl.Color(60, 60, 60, 255))
        
        temp_pct = (self._smooth_temp - 100) / 150.0
        temp_pct = min(max(temp_pct, 0), 1)
        
        t_color = rl.Color(255, 255, 255, 255)
        if temp_pct > 0.8: t_color = rl.Color(226, 44, 44, 255)
        elif temp_pct < 0.2: t_color = rl.Color(70, 91, 234, 255)
            
        rl.draw_rectangle(int(x + 40), int(ty), int(temp_w * temp_pct), 10, t_color)

    def _draw_center_panel(self, state, x, y, w, h, theme):
        cx = x + w / 2
        cy = y + h * 0.4
        
        # Road perspective
        road_w_bot = w * 0.8
        road_w_top = w * 0.2
        road_y_bot = y + h
        road_y_top = cy + 100
        
        # Left line
        rl.draw_line_ex(rl.Vector2(cx - road_w_bot/2, road_y_bot), rl.Vector2(cx - road_w_top/2, road_y_top), 6, rl.Color(255, 255, 255, 100))
        # Right line
        rl.draw_line_ex(rl.Vector2(cx + road_w_bot/2, road_y_bot), rl.Vector2(cx + road_w_top/2, road_y_top), 6, rl.Color(255, 255, 255, 100))
        
        # Speed Arc
        inner_r = w * 0.30
        outer_r = w * 0.35
        center = rl.Vector2(cx, cy)
        
        # Track
        rl.draw_ring(center, inner_r, outer_r, 135, 405, 64, rl.Color(60, 60, 60, 255))
        
        # Fill
        fill_angle = 135 + (self._smooth_speed / 120) * 270
        fill_angle = min(max(fill_angle, 135), 405)
        rl.draw_ring(center, inner_r, outer_r, 135, fill_angle, 64, rl.Color(70, 91, 234, 255))
        
        # Speed Text
        speed_str = str(int(self._smooth_speed))
        if 'xxl' in self.fonts:
            speed_font = self.fonts['xxl']
        else:
            speed_font = self.fonts['xl']
            
        self._draw_text_centered(speed_font, speed_str, cx, cy - 20, rl.Color(255, 255, 255, 255))
        self._draw_text_centered(self.fonts['md'], "mph", cx, cy + 80, rl.Color(170, 170, 170, 255))
        
        # Speed limit sign
        sign_x = cx + outer_r + 20
        sign_y = cy - 40
        rl.draw_rectangle_rounded(rl.Rectangle(sign_x, sign_y, 80, 100), 0.1, 8, rl.Color(255, 255, 255, 255))
        self._draw_text_centered(self.fonts['xs'], "SPEED LIMIT", sign_x + 40, sign_y + 20, rl.Color(0, 0, 0, 255))
        self._draw_text_centered(self.fonts['blg'], str(self.target_speed), sign_x + 40, sign_y + 60, rl.Color(0, 0, 0, 255))

    def _draw_right_panel(self, state, x, y, w, h, theme):
        pad = 24
        
        # Nav card
        nav_h = h * 0.45
        nav_rect = rl.Rectangle(x + pad, y + pad, w - pad*2, nav_h - pad*2)
        rl.draw_rectangle_rounded(nav_rect, 0.35, 32, rl.Color(41, 41, 41, 255))
        
        dest = getattr(state, 'destination', 'Home')
        street = getattr(state, 'nav_instruction', 'Continue on Main St')
        eta = getattr(state, 'eta_seconds', 1200)
        eta_str = f"ETA: {eta // 60} min"
        
        nx = nav_rect.x + pad * 2
        ny = nav_rect.y + pad * 2
        rl.draw_text_ex(self.fonts['blg'], dest, rl.Vector2(nx, ny), self.fonts['blg'].baseSize, 0, rl.Color(255, 255, 255, 255))
        rl.draw_text_ex(self.fonts['md'], street, rl.Vector2(nx, ny + 60), self.fonts['md'].baseSize, 0, rl.Color(255, 255, 255, 255))
        rl.draw_text_ex(self.fonts['sm'], eta_str, rl.Vector2(nx, ny + 110), self.fonts['sm'].baseSize, 0, rl.Color(51, 171, 76, 255))
        
        # Media card
        media_y = y + nav_h
        media_h = h * 0.45
        media_rect = rl.Rectangle(x + pad, media_y + pad, w - pad*2, media_h - pad*2)
        rl.draw_rectangle_rounded(media_rect, 0.35, 32, rl.Color(41, 41, 41, 255))
        
        artist = getattr(state, 'music_artist', 'The Midnight')
        title = getattr(state, 'music_title', 'Sunset')
        
        mx = media_rect.x + pad * 2
        my = media_rect.y + pad * 2
        rl.draw_text_ex(self.fonts['md'], artist, rl.Vector2(mx, my), self.fonts['md'].baseSize, 0, rl.Color(255, 255, 255, 255))
        rl.draw_text_ex(self.fonts['md'], title, rl.Vector2(mx, my + 40), self.fonts['md'].baseSize, 0, rl.Color(255, 255, 255, 255))

    def _draw_top_strip(self, state, w, h, theme):
        # Telltales
        cx = w / 2
        
        # READY, LIGHTS, STEER
        pills = ["READY", "LIGHTS", "STEER"]
        active = [True, self.headlights, getattr(state, 'acc_active', False)]
        
        # Calculate total width to center the pills
        total_w = 0
        sizes = []
        for text in pills:
            size = rl.measure_text_ex(self.fonts['sm'], text, self.fonts['sm'].baseSize, 0)
            sizes.append(size.x)
            total_w += size.x
        total_w += 24 * (len(pills) - 1)
        
        px = cx - total_w / 2
        
        for i, (text, is_act) in enumerate(zip(pills, active)):
            color = rl.Color(51, 171, 76, 255) if is_act else rl.Color(170, 170, 170, 255)
            # draw at current px
            size = sizes[i]
            rl.draw_text_ex(self.fonts['sm'], text, rl.Vector2(px, h / 2 - self.fonts['sm'].baseSize / 2), self.fonts['sm'].baseSize, 0, color)
            px += size + 24
            
        # Turn signals
        ts_color = rl.Color(51, 171, 76, 255) if (self.turn_left or self.hazard) else rl.Color(60, 60, 60, 255)
        rl.draw_circle(int(cx - 300), int(h/2), 10, ts_color)
        
        ts_color_r = rl.Color(51, 171, 76, 255) if (self.turn_right or self.hazard) else rl.Color(60, 60, 60, 255)
        rl.draw_circle(int(cx + 300), int(h/2), 10, ts_color_r)

    def _draw_bottom_strip(self, state, x, y, w, h, theme):
        pad = 24
        
        # Fuel
        fuel = getattr(state, 'fuel_level', 0.8)
        fuel_str = f"Fuel: {int(fuel * 100)}%"
        rl.draw_text_ex(self.fonts['sm'], fuel_str, rl.Vector2(x + pad, y + h/2 - 11), self.fonts['sm'].baseSize, 0, rl.Color(170, 170, 170, 255))
        
        # Drive modes
        modes = ["ECO", "CRUISE", "SPORT"]
        active_idx = 1 # CRUISE default
        
        # Space them in the center
        mx = w / 2 - (120 * 3 + 24 * 2) / 2
        for i, mode in enumerate(modes):
            m_rect = rl.Rectangle(mx + i * (120 + 24), y + h/2 - 20, 120, 40)
            if i == active_idx:
                rl.draw_rectangle_rounded(m_rect, 0.5, 32, rl.Color(51, 171, 76, 255))
                self._draw_text_centered(self.fonts['bmd'] if 'bmd' in self.fonts else self.fonts['sm'], mode, m_rect.x + 60, m_rect.y + 20, rl.Color(0, 0, 0, 255))
            else:
                rl.draw_rectangle_rounded(m_rect, 0.5, 32, rl.Color(41, 41, 41, 255))
                self._draw_text_centered(self.fonts['sm'], mode, m_rect.x + 60, m_rect.y + 20, rl.Color(170, 170, 170, 255))
                
        # Trip & Clock
        dist = getattr(state, 'trip_distance_mi', 12.4)
        trip_str = f"Trip: {dist:.1f} mi"
        rl.draw_text_ex(self.fonts['sm'], trip_str, rl.Vector2(w - 300, y + h/2 - 11), self.fonts['sm'].baseSize, 0, rl.Color(170, 170, 170, 255))
        
        time_str = "10:42 AM"
        rl.draw_text_ex(self.fonts['sm'], time_str, rl.Vector2(w - 150, y + h/2 - 11), self.fonts['sm'].baseSize, 0, rl.Color(255, 255, 255, 255))

    def handle_key(self, key: int, state, theme):
        if key == rl.KeyboardKey.KEY_UP:
            if hasattr(state, 'speed_mph'):
                state.speed_mph = min(state.speed_mph + 5, 120)
            if hasattr(state, 'rpm'):
                state.rpm = min(state.rpm + 500, 8000)
        elif key == rl.KeyboardKey.KEY_DOWN:
            if hasattr(state, 'speed_mph'):
                state.speed_mph = max(state.speed_mph - 5, 0)
            if hasattr(state, 'rpm'):
                state.rpm = max(state.rpm - 500, 0)
        elif key == rl.KeyboardKey.KEY_LEFT:
            self.turn_left = not self.turn_left
        elif key == rl.KeyboardKey.KEY_RIGHT:
            self.turn_right = not self.turn_right
        elif key == rl.KeyboardKey.KEY_H:
            self.hazard = not self.hazard
        elif key == rl.KeyboardKey.KEY_L:
            self.headlights = not self.headlights
        elif key == rl.KeyboardKey.KEY_A:
            if hasattr(state, 'acc_active'):
                state.acc_active = not state.acc_active
        elif key == rl.KeyboardKey.KEY_G:
            if hasattr(state, 'gear'):
                state.gear = (state.gear + 1) % 4

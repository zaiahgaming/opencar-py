# surfaces/hud.py — OpenCar Driver HUD surface
# Renders a modern automotive instrument cluster across 1280×480.
# Layout:  [LEFT 0-300] [CENTER 300-980] [RIGHT 980-1280]
#          [BOTTOM BAR y=440 h=40]

import pyray as rl
import math
import time

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
WINDOW_W = 1280
WINDOW_H = 480

# Gear label map: gear int → display string
GEARS = {0: 'P', 1: 'R', 2: 'N', 3: 'D'}

# Circular gauge geometry (center of canvas)
GAUGE_CX = 640
GAUGE_CY = 215
ARC_INNER = 150
ARC_OUTER = 158
ARC_START = 140.0   # degrees — bottom-left of arc
ARC_SWEEP = 260.0   # total sweep in degrees

# Speed-tick positions in MPH along the gauge sweep
SPEED_TICKS = [0, 20, 40, 60, 80, 100, 120]
MAX_SPEED_DISPLAY = 120.0

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def lerp_color(a: rl.Color, b: rl.Color, t: float) -> rl.Color:
    """Linear interpolation between two raylib Colors, t in [0,1]."""
    t = max(0.0, min(1.0, t))
    return rl.Color(
        int(a.r + (b.r - a.r) * t),
        int(a.g + (b.g - a.g) * t),
        int(a.b + (b.b - a.b) * t),
        255,
    )


def draw_text_centered(font, text: str, cx: float, cy: float,
                       size: float, color: rl.Color, spacing: float = 1.0):
    """Draw text horizontally and vertically centered on (cx, cy)."""
    vec = rl.measure_text_ex(font, text, size, spacing)
    rl.draw_text_ex(
        font, text,
        rl.Vector2(cx - vec.x / 2, cy - vec.y / 2),
        size, spacing, color,
    )


def smooth(current: float, target: float, dt: float, speed: float = 5.0) -> float:
    """Exponential approach — frame-rate independent."""
    return current + (target - current) * min(1.0, dt * speed)


def angle_for_speed(speed: float) -> float:
    """Return the arc angle (degrees) for a given speed value."""
    ratio = max(0.0, min(1.0, speed / MAX_SPEED_DISPLAY))
    return ARC_START + ratio * ARC_SWEEP


def angle_for_rpm(rpm: float, max_rpm: float = 8000.0) -> float:
    """Return the arc angle for RPM."""
    ratio = max(0.0, min(1.0, rpm / max_rpm))
    return ARC_START + ratio * ARC_SWEEP


# ---------------------------------------------------------------------------
# HUDSurface
# ---------------------------------------------------------------------------

class HUDSurface:
    """Driver instrument cluster rendered via native raylib primitives."""

    def __init__(self, fonts: dict):
        self.fonts = fonts

        # Smoothed display values — animated each frame
        self._smooth_speed = 0.0
        self._smooth_rpm   = 0.0
        self._smooth_temp  = 190.0

    # ------------------------------------------------------------------
    # Input handling
    # ------------------------------------------------------------------

    def handle_key(self, key, state, theme):
        """No HUD-specific key bindings at this time."""
        pass

    # ------------------------------------------------------------------
    # Top-level render
    # ------------------------------------------------------------------

    def render(self, state, theme):
        dt = rl.get_frame_time()

        # Advance smoothed values
        self._smooth_speed = smooth(self._smooth_speed, state.speed_mph, dt, speed=4.0)
        self._smooth_rpm   = smooth(self._smooth_rpm,   state.rpm,       dt, speed=5.0)
        self._smooth_temp  = smooth(self._smooth_temp,  state.engine_temp_f, dt, speed=2.0)

        self._draw_left_zone(state, theme)
        self._draw_center_cluster(state, theme)
        self._draw_right_zone(state, theme)
        self._draw_bottom_bar(state, theme)

    # ------------------------------------------------------------------
    # LEFT ZONE — RPM card + Coolant card
    # ------------------------------------------------------------------

    def _draw_left_zone(self, state, theme):
        self._draw_rpm_card(state, theme)
        self._draw_coolant_card(state, theme)

    def _draw_rpm_card(self, state, theme):
        """RPM card: x=20, y=60, w=260, h=160."""
        rx, ry, rw, rh = 20, 60, 260, 160
        rec = rl.Rectangle(rx, ry, rw, rh)
        rl.draw_rectangle_rounded(rec, 0.15, 8, theme.surface)

        fonts = self.fonts

        # "ENGINE" label — top left inside card
        rl.draw_text_ex(
            fonts['xs'], "ENGINE",
            rl.Vector2(rx + 14, ry + 12),
            13, 1, theme.fg2,
        )

        # RPM value — formatted with comma separator
        rpm_val = int(self._smooth_rpm)
        rpm_str = f"{rpm_val:,}"
        draw_text_centered(fonts['md'], rpm_str, rx + rw * 0.42, ry + rh * 0.52, 28, theme.fg)

        # Vertical bar gauge on the right side of card
        bar_x   = rx + rw - 32
        bar_y   = ry + 24
        bar_w   = 10
        bar_h   = 118
        # Track background
        rl.draw_rectangle_rounded(
            rl.Rectangle(bar_x, bar_y, bar_w, bar_h),
            0.5, 4, theme.surface2,
        )
        # Filled portion — grows upward from bottom
        ratio = max(0.0, min(1.0, self._smooth_rpm / 8000.0))
        fill_h = int(bar_h * ratio)
        if fill_h > 0:
            bar_color = lerp_color(theme.accent, theme.warn, ratio)
            fill_y = bar_y + bar_h - fill_h
            rl.draw_rectangle_rounded(
                rl.Rectangle(bar_x, fill_y, bar_w, fill_h),
                0.5, 4, bar_color,
            )

        # "RPM" unit label below bar
        rl.draw_text_ex(
            fonts['xs'], "RPM",
            rl.Vector2(bar_x - 1, bar_y + bar_h + 4),
            11, 1, theme.fg2,
        )

    def _draw_coolant_card(self, state, theme):
        """Coolant temp card: x=20, y=240, w=260, h=120."""
        rx, ry, rw, rh = 20, 240, 260, 120
        rec = rl.Rectangle(rx, ry, rw, rh)
        rl.draw_rectangle_rounded(rec, 0.15, 8, theme.surface)

        fonts = self.fonts
        overtemp = state.engine_temp_f > 215

        # Label
        rl.draw_text_ex(
            fonts['xs'], "COOLANT",
            rl.Vector2(rx + 14, ry + 12),
            13, 1, theme.fg2,
        )

        # Temp value
        temp_str = f"{int(self._smooth_temp)}°F"
        val_color = theme.warn if overtemp else theme.fg
        draw_text_centered(fonts['md'], temp_str, rx + rw / 2, ry + rh * 0.57, 28, val_color)

        # Pulsing warning dot when overtemp
        if overtemp:
            pulse = abs(math.sin(rl.get_time() * 3.0))
            dot_alpha = int(80 + 175 * pulse)
            dot_color = rl.Color(theme.warn.r, theme.warn.g, theme.warn.b, dot_alpha)
            rl.draw_circle(rx + rw - 22, ry + 18, 7, dot_color)

    # ------------------------------------------------------------------
    # CENTER CLUSTER — Circular gauge + speed readout + gear badge
    # ------------------------------------------------------------------

    def _draw_center_cluster(self, state, theme):
        cx = float(GAUGE_CX)
        cy = float(GAUGE_CY)
        center = rl.Vector2(cx, cy)

        # ---- Outer track ring (full arc, decorative) --------------------
        rl.draw_ring(
            center,
            float(ARC_INNER), float(ARC_OUTER),
            ARC_START, ARC_START + ARC_SWEEP,
            60, theme.border,
        )

        # ---- Speed-tick marks around the arc ----------------------------
        self._draw_speed_ticks(cx, cy, theme)

        # ---- RPM-filled arc ring ----------------------------------------
        rpm_ratio = max(0.0, min(1.0, self._smooth_rpm / 8000.0))
        end_rpm_angle = ARC_START + rpm_ratio * ARC_SWEEP
        if rpm_ratio > 0.001:
            rpm_color = lerp_color(theme.accent, theme.warn, rpm_ratio)
            rl.draw_ring(
                center,
                float(ARC_INNER), float(ARC_OUTER),
                ARC_START, end_rpm_angle,
                60, rpm_color,
            )

        # ---- Speed needle dot on outer arc (speed position) -------------
        speed_ratio = max(0.0, min(1.0, self._smooth_speed / MAX_SPEED_DISPLAY))
        needle_angle_deg = ARC_START + speed_ratio * ARC_SWEEP
        needle_angle_rad = math.radians(needle_angle_deg)
        mid_r = (ARC_INNER + ARC_OUTER) / 2.0
        nx = cx + mid_r * math.cos(needle_angle_rad)
        ny = cy + mid_r * math.sin(needle_angle_rad)
        rl.draw_circle(int(nx), int(ny), 6, theme.fg)

        # ---- Speed number -----------------------------------------------
        speed_val = int(round(self._smooth_speed))
        speed_str = str(speed_val)
        draw_text_centered(self.fonts['xl'], speed_str, cx, cy - 10, 96, theme.fg)

        # ---- Unit label (MPH / KPH) right-edge aligned under speed ------
        unit_str = "MPH" if state.units_mph else "KPH"
        unit_vec = rl.measure_text_ex(self.fonts['sm'], unit_str, 18, 1)
        rl.draw_text_ex(
            self.fonts['sm'], unit_str,
            rl.Vector2(cx + 78 - unit_vec.x, cy + 46),
            18, 1, theme.fg2,
        )

        # ---- Gear badge pill --------------------------------------------
        self._draw_gear_badge(state, theme, cx, cy)

    def _draw_speed_ticks(self, cx: float, cy: float, theme):
        """Draw small tick marks around the arc at speed milestones."""
        for spd in SPEED_TICKS:
            ratio = spd / MAX_SPEED_DISPLAY
            angle_deg = ARC_START + ratio * ARC_SWEEP
            angle_rad = math.radians(angle_deg)

            inner_r = ARC_INNER - 10
            outer_r = ARC_INNER - 2
            tx0 = cx + inner_r * math.cos(angle_rad)
            ty0 = cy + inner_r * math.sin(angle_rad)
            tx1 = cx + outer_r * math.cos(angle_rad)
            ty1 = cy + outer_r * math.sin(angle_rad)

            rl.draw_line_ex(
                rl.Vector2(tx0, ty0),
                rl.Vector2(tx1, ty1),
                2.0, theme.border,
            )

            # Speed label at the outermost position
            label_r = ARC_INNER - 22
            lx = cx + label_r * math.cos(angle_rad)
            ly = cy + label_r * math.sin(angle_rad)
            lbl = str(spd)
            vec = rl.measure_text_ex(self.fonts['xs'], lbl, 11, 1)
            rl.draw_text_ex(
                self.fonts['xs'], lbl,
                rl.Vector2(lx - vec.x / 2, ly - vec.y / 2),
                11, 1, theme.fg2,
            )

    def _draw_gear_badge(self, state, theme, cx: float, cy: float):
        """Rounded pill badge below the speed readout showing current gear."""
        gear_label = GEARS.get(state.gear, 'P')

        # Badge color by gear
        if state.gear == 3:      # D
            badge_color = theme.accent
        elif state.gear == 1:    # R
            badge_color = theme.warn
        else:                    # P, N
            badge_color = theme.surface2

        bw, bh = 56, 34
        bx = cx - bw / 2
        by = cy + 60
        rl.draw_rectangle_rounded(rl.Rectangle(bx, by, bw, bh), 0.5, 8, badge_color)

        # Gear letter in bold font, dark-ish text for visibility
        txt_color = theme.bg if state.gear in (3, 1) else theme.fg
        draw_text_centered(self.fonts['blg'], gear_label, cx, by + bh / 2, 32, txt_color)

    # ------------------------------------------------------------------
    # RIGHT ZONE — ADAS panel
    # ------------------------------------------------------------------

    def _draw_right_zone(self, state, theme):
        """One tall ADAS card from y=30 to y=400."""
        rx, ry, rw, rh = 990, 30, 270, 390
        rl.draw_rectangle_rounded(rl.Rectangle(rx, ry, rw, rh), 0.12, 8, theme.surface)

        fonts = self.fonts
        cx = rx + rw / 2  # card center-x

        # Header
        draw_text_centered(fonts['xs'], "DRIVER ASSIST", cx, ry + 18, 13, theme.fg2)

        # Thin separator under header
        sep_y = ry + 32.0
        rl.draw_line_ex(
            rl.Vector2(float(rx + 12), sep_y),
            rl.Vector2(float(rx + rw - 12), sep_y),
            1.0, theme.border,
        )

        # ACC section
        self._draw_acc_section(state, theme, rx, ry + 42, rw)

        # Separator
        sep2_y = ry + 165.0
        rl.draw_line_ex(
            rl.Vector2(float(rx + 12), sep2_y),
            rl.Vector2(float(rx + rw - 12), sep2_y),
            1.0, theme.border,
        )

        # Lane assist section
        self._draw_lane_section(state, theme, rx, ry + 175, rw)

        # Separator
        sep3_y = ry + 295.0
        rl.draw_line_ex(
            rl.Vector2(float(rx + 12), sep3_y),
            rl.Vector2(float(rx + rw - 12), sep3_y),
            1.0, theme.border,
        )

        # Range row
        self._draw_range_row(state, theme, rx, ry + 308, rw)

    def _draw_acc_section(self, state, theme, rx: float, ry: float, rw: float):
        """Adaptive Cruise Control sub-section."""
        fonts = self.fonts
        cx = rx + rw / 2

        # Section label
        rl.draw_text_ex(
            fonts['xs'], "ADAPTIVE CRUISE",
            rl.Vector2(rx + 14, ry),
            11, 1, theme.fg2,
        )

        # Small car icon composed of rounded rectangles
        icon_color = theme.good if state.acc_active else theme.fg2
        self._draw_car_icon(cx, ry + 26, icon_color)

        # ACC state text
        acc_text  = "ACTIVE"  if state.acc_active else "STANDBY"
        acc_color = theme.good if state.acc_active else theme.fg2
        draw_text_centered(fonts['xs'], acc_text, cx, ry + 54, 12, acc_color)

        # Gap dots: 4 circles representing following distance
        gap_filled = max(0, min(4, state.acc_gap))
        dot_r = 5
        dot_spacing = 18
        total_dots_w = 4 * (dot_r * 2) + 3 * (dot_spacing - dot_r * 2)
        dot_start_x = cx - total_dots_w / 2 + dot_r
        dot_y = ry + 80
        for i in range(4):
            dx = dot_start_x + i * dot_spacing
            if i < gap_filled:
                rl.draw_circle(int(dx), int(dot_y), dot_r, theme.accent)
            else:
                rl.draw_circle(int(dx), int(dot_y), dot_r, theme.surface2)

    def _draw_car_icon(self, cx: float, cy: float, color: rl.Color):
        """Minimal car silhouette from rounded rectangles + circles."""
        # Car body
        rl.draw_rectangle_rounded(
            rl.Rectangle(cx - 20, cy + 4, 40, 16), 0.3, 4, color,
        )
        # Roof / cabin
        rl.draw_rectangle_rounded(
            rl.Rectangle(cx - 12, cy, 24, 10), 0.5, 4, color,
        )
        # Wheels
        rl.draw_circle(int(cx - 12), int(cy + 20), 5, color)
        rl.draw_circle(int(cx + 12), int(cy + 20), 5, color)

    def _draw_lane_section(self, state, theme, rx: float, ry: float, rw: float):
        """Lane keep assist sub-section."""
        fonts = self.fonts
        cx = rx + rw / 2

        # Section label
        rl.draw_text_ex(
            fonts['xs'], "LANE ASSIST",
            rl.Vector2(rx + 14, ry),
            11, 1, theme.fg2,
        )

        # Road icon — 3 vertical lines representing lanes
        line_h = 40
        line_w = 4
        gap = 20
        lx_left   = int(cx - gap - line_w / 2)
        lx_center = int(cx - line_w / 2)
        lx_right  = int(cx + gap - line_w / 2)
        icon_y    = int(ry + 18)

        # Choose colors by lane_state
        left_col   = theme.warn   if state.lane_state == 1 else theme.border
        center_col = theme.accent if state.lane_state == 0 else theme.fg2
        right_col  = theme.warn   if state.lane_state == 2 else theme.border

        rl.draw_rectangle_rounded(
            rl.Rectangle(lx_left,   icon_y, line_w, line_h), 0.5, 4, left_col,
        )
        rl.draw_rectangle_rounded(
            rl.Rectangle(lx_center, icon_y, line_w, line_h), 0.5, 4, center_col,
        )
        rl.draw_rectangle_rounded(
            rl.Rectangle(lx_right,  icon_y, line_w, line_h), 0.5, 4, right_col,
        )

        # Lane status text
        if state.lane_state == 0:
            lane_text  = "CENTERED"
            lane_color = theme.good
        elif state.lane_state == 1:
            lane_text  = "DRIFT LEFT"
            lane_color = theme.warn
        else:
            lane_text  = "DRIFT RIGHT"
            lane_color = theme.warn

        draw_text_centered(fonts['xs'], lane_text, cx, ry + 76, 12, lane_color)

    def _draw_range_row(self, state, theme, rx: float, ry: float, rw: float):
        """Estimated range remaining row."""
        fonts = self.fonts
        cx = rx + rw / 2

        est_range = int(300 - state.trip_progress * 120)

        rl.draw_text_ex(
            fonts['xs'], "RANGE",
            rl.Vector2(rx + 14, ry + 2),
            11, 1, theme.fg2,
        )

        range_str = f"{est_range} mi"
        draw_text_centered(fonts['sm'], range_str, cx, ry + 28, 18, theme.fg)

        # Fuel level bar
        bar_y = ry + 44
        bar_x = rx + 14
        bar_w = rw - 28
        bar_h = 6
        rl.draw_rectangle_rounded(
            rl.Rectangle(bar_x, bar_y, bar_w, bar_h), 0.5, 4, theme.surface2,
        )
        fuel = max(0.0, min(1.0, state.fuel_level))
        fuel_color = theme.warn if fuel < 0.2 else theme.accent
        if fuel > 0.01:
            rl.draw_rectangle_rounded(
                rl.Rectangle(bar_x, bar_y, bar_w * fuel, bar_h), 0.5, 4, fuel_color,
            )

    # ------------------------------------------------------------------
    # BOTTOM BAR
    # ------------------------------------------------------------------

    def _draw_bottom_bar(self, state, theme):
        """Full-width status bar at y=440, h=40."""
        bar_y = 440
        bar_h = 40

        # Background fill
        rl.draw_rectangle(0, bar_y, WINDOW_W, bar_h, theme.surface)

        # 1px top divider line
        rl.draw_line_ex(
            rl.Vector2(0.0, float(bar_y)),
            rl.Vector2(float(WINDOW_W), float(bar_y)),
            1.0, theme.border,
        )

        fonts = self.fonts
        mid_y = bar_y + bar_h / 2

        # ---- Left: system clock -----------------------------------------
        clock_str = time.strftime("%I:%M %p")
        rl.draw_text_ex(
            fonts['sm'], clock_str,
            rl.Vector2(16, mid_y - 9),
            18, 1, theme.fg2,
        )

        # ---- Center-left: ambient temperature ---------------------------
        ambient_str = f"{int(state.climate_temp_f)}°F"
        amb_vec = rl.measure_text_ex(fonts['sm'], ambient_str, 18, 1)
        rl.draw_text_ex(
            fonts['sm'], ambient_str,
            rl.Vector2(180, mid_y - 9),
            18, 1, theme.fg2,
        )

        # ---- Center: navigation instruction -----------------------------
        nav_str = state.nav_instruction[:40]
        nav_vec = rl.measure_text_ex(fonts['sm'], nav_str, 18, 1)
        rl.draw_text_ex(
            fonts['sm'], nav_str,
            rl.Vector2(WINDOW_W / 2 - nav_vec.x / 2, mid_y - 9),
            18, 1, theme.fg,
        )

        # ---- Right: drive mode pill -------------------------------------
        self._draw_drive_mode_pill(state, theme, mid_y)

    def _draw_drive_mode_pill(self, state, theme, mid_y: float):
        """Colored pill at the right of the bottom bar showing drive mode."""
        spd = state.speed_mph
        if spd < 45:
            mode_text  = "ECO"
            mode_color = theme.good
        elif spd <= 65:
            mode_text  = "CRUISE"
            mode_color = theme.accent
        else:
            mode_text  = "SPORT"
            mode_color = theme.warn

        fonts = self.fonts
        tv = rl.measure_text_ex(fonts['sm'], mode_text, 18, 1)
        pw = tv.x + 24
        ph = 26.0
        px = WINDOW_W - pw - 16
        py = mid_y - ph / 2

        rl.draw_rectangle_rounded(rl.Rectangle(px, py, pw, ph), 0.5, 8, mode_color)

        txt_color = theme.bg
        rl.draw_text_ex(
            fonts['sm'], mode_text,
            rl.Vector2(px + pw / 2 - tv.x / 2, py + ph / 2 - tv.y / 2),
            18, 1, txt_color,
        )

# glass.py — Comma 4 / Luxury EV Glassmorphic Rendering Engine
import pyray as rl
import math

# Palette constants for authentic Comma 4 / Luxury EV aesthetic
OBSIDIAN_BG      = rl.Color(6, 7, 10, 255)       # Deep rich OLED black
GLASS_CARD_BG    = rl.Color(18, 20, 27, 235)     # Frosted dark obsidian glass
GLASS_CARD_LIT   = rl.Color(26, 30, 42, 245)     # Slightly elevated glass
GLASS_BORDER     = rl.Color(255, 255, 255, 30)   # 12% frosted rim light
GLASS_BORDER_HI  = rl.Color(255, 255, 255, 65)   # 25% rim light on active/hover
GLASS_SHEEN      = rl.Color(255, 255, 255, 10)   # Top specular glass sheen
SHADOW_SOFT      = rl.Color(0, 0, 0, 120)        # Ambient drop shadow
SHADOW_CORE      = rl.Color(0, 0, 0, 200)        # Core contact shadow

COMMA_GREEN      = rl.Color(46, 213, 115, 255)   # Vibrant Comma 4 neon green
COMMA_GREEN_GLOW = rl.Color(46, 213, 115, 50)    # Soft neon aura
SKY_BLUE         = rl.Color(56, 189, 248, 255)   # Tesla sky blue
SKY_BLUE_GLOW    = rl.Color(56, 189, 248, 45)
CRIMSON_RED      = rl.Color(239, 68, 68, 255)    # Floating action red (from reference)
AMBER_WARM       = rl.Color(245, 158, 11, 255)   # Heated seat amber
CYAN_COOL        = rl.Color(6, 182, 212, 255)    # Ventilated seat cool cyan

TEXT_PRIMARY     = rl.Color(255, 255, 255, 255)  # Crisp white
TEXT_SECONDARY   = rl.Color(165, 172, 188, 255)  # Refined slate
TEXT_MUTED       = rl.Color(105, 112, 130, 255)  # Subtle gray
PILL_BG          = rl.Color(255, 255, 255, 16)   # Frosted capsule fill
PILL_BORDER      = rl.Color(255, 255, 255, 28)

def draw_ambient_backdrop(w: int, h: int):
    """Draws a rich dark ambient horizon with subtle optical depth."""
    rl.clear_background(OBSIDIAN_BG)
    # Subtle top ambient indigo glow
    rl.draw_circle_gradient(rl.Vector2(w * 0.25, h * 0.2), float(w * 0.4), rl.Color(22, 32, 60, 40), rl.Color(0, 0, 0, 0))
    # Subtle center-bottom ambient teal glow
    rl.draw_circle_gradient(rl.Vector2(w * 0.5, h * 0.95), float(w * 0.45), rl.Color(12, 40, 50, 35), rl.Color(0, 0, 0, 0))
    # Subtle right ambient cyan glow
    rl.draw_circle_gradient(rl.Vector2(w * 0.8, h * 0.3), float(w * 0.35), rl.Color(18, 30, 55, 30), rl.Color(0, 0, 0, 0))

def draw_glass_card(rect: rl.Rectangle, roundness: float = 0.35, 
                    bg: rl.Color = None, border: rl.Color = None, 
                    glow_color: rl.Color = None, elevation: int = 1):
    """
    Renders an authentic Comma 4 glassmorphic card with multi-stage shadow,
    obsidian translucent body, frosted rim lighting, and specular sheen.
    """
    # 1. Multi-pass ambient drop shadow
    if elevation >= 1:
        rl.draw_rectangle_rounded(
            rl.Rectangle(rect.x - 6, rect.y - 3, rect.width + 12, rect.height + 14), 
            roundness, 32, SHADOW_SOFT
        )
        rl.draw_rectangle_rounded(
            rl.Rectangle(rect.x - 2, rect.y - 1, rect.width + 4, rect.height + 6), 
            roundness, 32, SHADOW_CORE
        )
    
    # Optional active glow
    if glow_color:
        rl.draw_rectangle_rounded(
            rl.Rectangle(rect.x - 4, rect.y - 4, rect.width + 8, rect.height + 8), 
            roundness, 32, glow_color
        )

    # 2. Main frosted glass body
    card_bg = bg or GLASS_CARD_BG
    rl.draw_rectangle_rounded(rect, roundness, 32, card_bg)

    # 3. Specular top highlight (simulates physical curved glass reflection)
    sheen_h = max(24.0, min(64.0, rect.height * 0.28))
    rl.draw_rectangle_rounded(
        rl.Rectangle(rect.x + 2, rect.y + 2, rect.width - 4, sheen_h),
        roundness, 32, GLASS_SHEEN
    )

    # 4. Frosted rim border (light catching the edges)
    rim_col = border or GLASS_BORDER
    rl.draw_rectangle_rounded_lines_ex(rect, roundness, 32, 1.5, rim_col)

def draw_glass_pill(rect: rl.Rectangle, roundness: float = 0.5, 
                    bg: rl.Color = None, border: rl.Color = None, 
                    active: bool = False, solid: bool = False):
    """Renders a sleek frosted capsule pill for tags, status indicators, and tabs."""
    if bg:
        pill_bg = bg
    elif active and solid:
        pill_bg = COMMA_GREEN
    elif active:
        pill_bg = rl.Color(46, 213, 115, 45)
    else:
        pill_bg = PILL_BG
        
    pill_brd = border or (COMMA_GREEN if active else PILL_BORDER)
    
    if active and solid:
        rl.draw_rectangle_rounded(rl.Rectangle(rect.x - 2, rect.y - 1, rect.width + 4, rect.height + 4), roundness, 16, COMMA_GREEN_GLOW)
        
    rl.draw_rectangle_rounded(rect, roundness, 16, pill_bg)
    rl.draw_rectangle_rounded_lines_ex(rect, roundness, 16, 1.2, pill_brd)

def draw_turn_arrow(cx: float, cy: float, size: float, left: bool, color: rl.Color):
    """Draws a clean, antialiased ISO turn signal arrow."""
    half = size / 2.0
    if left:
        p1 = rl.Vector2(cx - half, cy)
        p2 = rl.Vector2(cx + half, cy - half * 0.8)
        p3 = rl.Vector2(cx + half, cy + half * 0.8)
    else:
        p1 = rl.Vector2(cx + half, cy)
        p2 = rl.Vector2(cx - half, cy - half * 0.8)
        p3 = rl.Vector2(cx - half, cy + half * 0.8)
    rl.draw_triangle(p1, p2, p3, color)

def draw_circular_button(cx: float, cy: float, radius: float, 
                         bg: rl.Color = None, border: rl.Color = None, 
                         glow: rl.Color = None):
    """Renders a floating circular glass button (matching the crimson button in reference)."""
    btn_bg = bg or rl.Color(32, 36, 48, 240)
    btn_border = border or rl.Color(255, 255, 255, 45)
    
    # Ambient shadow
    rl.draw_circle(int(cx), int(cy) + 3, radius + 4, SHADOW_SOFT)
    rl.draw_circle(int(cx), int(cy) + 1, radius + 2, SHADOW_CORE)
    if glow:
        rl.draw_circle(int(cx), int(cy), radius + 6, glow)
        
    rl.draw_circle(int(cx), int(cy), radius, btn_bg)
    # Specular ring
    rl.draw_circle_lines(int(cx), int(cy), radius, btn_border)
    # Subtle top crescent light
    rl.draw_circle_lines(int(cx), int(cy) - 1, radius - 2, rl.Color(255, 255, 255, 25))

def draw_speed_limit_sign(cx: float, cy: float, limit: int, font_sm, font_bold):
    """Renders an authentic, beautiful drop-shadowed speed limit sign."""
    w, h = 64, 76
    rx, ry = cx - w / 2, cy - h / 2
    # Drop shadow
    rl.draw_rectangle_rounded(rl.Rectangle(rx - 2, ry - 1, w + 4, h + 6), 0.2, 16, SHADOW_SOFT)
    # White face
    rl.draw_rectangle_rounded(rl.Rectangle(rx, ry, w, h), 0.2, 16, rl.Color(250, 250, 250, 255))
    # Inner border
    rl.draw_rectangle_rounded_lines_ex(rl.Rectangle(rx + 3, ry + 3, w - 6, h - 6), 0.16, 16, 2.0, rl.Color(20, 20, 20, 255))
    
    # Text
    s1 = rl.measure_text_ex(font_sm, "SPEED", font_sm.baseSize, 0)
    rl.draw_text_ex(font_sm, "SPEED", rl.Vector2(cx - s1.x / 2, ry + 9), font_sm.baseSize, 0, rl.Color(20, 20, 20, 255))
    s2 = rl.measure_text_ex(font_sm, "LIMIT", font_sm.baseSize, 0)
    rl.draw_text_ex(font_sm, "LIMIT", rl.Vector2(cx - s2.x / 2, ry + 21), font_sm.baseSize, 0, rl.Color(20, 20, 20, 255))
    
    num_str = str(limit)
    s3 = rl.measure_text_ex(font_bold, num_str, font_bold.baseSize, 0)
    rl.draw_text_ex(font_bold, num_str, rl.Vector2(cx - s3.x / 2, ry + 38), font_bold.baseSize, 0, rl.Color(20, 20, 20, 255))

def draw_car_silhouette_topdown(cx: float, cy: float, length: float = 88.0, width: float = 44.0):
    """Draws a sleek aerodynamic modern EV silhouette with glowing headlamps and glass roof."""
    # Body shell
    rl.draw_rectangle_rounded(rl.Rectangle(cx - width/2, cy - length/2, width, length), 0.45, 16, rl.Color(28, 33, 46, 255))
    rl.draw_rectangle_rounded_lines_ex(rl.Rectangle(cx - width/2, cy - length/2, width, length), 0.45, 16, 1.4, GLASS_BORDER_HI)
    
    # Windshield (sky blue tint)
    rl.draw_rectangle_rounded(rl.Rectangle(cx - width * 0.35, cy - length * 0.28, width * 0.7, length * 0.15), 0.35, 8, rl.Color(56, 189, 248, 120))
    # Panoramic roof glass
    rl.draw_rectangle_rounded(rl.Rectangle(cx - width * 0.33, cy - length * 0.08, width * 0.66, length * 0.28), 0.2, 8, rl.Color(20, 38, 56, 200))
    # Rear glass
    rl.draw_rectangle_rounded(rl.Rectangle(cx - width * 0.35, cy + length * 0.24, width * 0.7, length * 0.12), 0.35, 8, rl.Color(56, 189, 248, 90))
    
    # Front Headlamps (Luminous LED beams)
    rl.draw_circle(int(cx - width * 0.32), int(cy - length/2 + 2), 4, rl.Color(255, 255, 230, 250))
    rl.draw_circle(int(cx + width * 0.32), int(cy - length/2 + 2), 4, rl.Color(255, 255, 230, 250))
    rl.draw_circle(int(cx - width * 0.32), int(cy - length/2 + 2), 8, rl.Color(255, 255, 200, 50))
    rl.draw_circle(int(cx + width * 0.32), int(cy - length/2 + 2), 8, rl.Color(255, 255, 200, 50))
    
    # Rear Taillamps (Ruby LED light strip)
    rl.draw_rectangle_rounded(rl.Rectangle(cx - width * 0.38, cy + length/2 - 4, width * 0.76, 4), 0.5, 4, CRIMSON_RED)
    rl.draw_circle(int(cx - width * 0.32), int(cy + length/2 - 2), 4, CRIMSON_RED)
    rl.draw_circle(int(cx + width * 0.32), int(cy + length/2 - 2), 4, CRIMSON_RED)

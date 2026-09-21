#!/usr/bin/env python3
"""OpenCar v1.0 — Python + Raylib multi-surface automotive UI

Usage:
    python3 main.py [options]

Run  python3 main.py --help  for the full option list.
"""

import sys
import json
import argparse
import configparser
import logging

logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(name)s: %(message)s',
)

# ── CLI argument parsing ─────────────────────────────────────────────────────
parser = argparse.ArgumentParser(
    description='OpenCar v1.0 — Multi-surface Automotive UI',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
)
parser.add_argument('--fullscreen',   action='store_true', help='Fullscreen mode (for car display)')
parser.add_argument('--car',          default='toyota',    help='Vehicle profile: toyota/honda/gm/ford')
parser.add_argument('--can',          action='store_true', help='Use real CAN bus (requires adapter)')
parser.add_argument('--obd',          action='store_true', help='Use OBD-II (ELM327 adapter)')
parser.add_argument('--obd-port',     default=None,        help='OBD port (e.g. /dev/ttyUSB0)')
parser.add_argument('--can-channel',  default=None,        help='CAN channel (e.g. can0)')
parser.add_argument('--can-bus',      default='socketcan', help='CAN bus type')
parser.add_argument('--replay',       default=None,        help='Replay a candump log file')
parser.add_argument('--gpio',         action='store_true', help='Enable GPIO hardware buttons')
parser.add_argument('--surface',      type=int, default=0, help='Start on surface 0=HUD 1=Info 2=Rear')
parser.add_argument('--width',        type=int, default=1280)
parser.add_argument('--height',       type=int, default=480)
parser.add_argument('--detect',       action='store_true', help='Detect hardware and exit')
args = parser.parse_args()

# ── Config file (opencar.conf) — CLI wins over config ───────────────────────
config = configparser.ConfigParser()
config.read('opencar.conf')

if not args.fullscreen:
    args.fullscreen = config.getboolean('display', 'fullscreen', fallback=False)
if args.width == 1280:
    args.width  = config.getint('display', 'width',  fallback=1280)
if args.height == 480:
    args.height = config.getint('display', 'height', fallback=480)
if args.car == 'toyota':
    args.car    = config.get('vehicle', 'profile', fallback='toyota')
if args.surface == 0:
    args.surface = config.getint('ui', 'default_surface', fallback=0)

# ── Hardware detection ───────────────────────────────────────────────────────
from hardware import (
    detect_hardware,
    CANReader,
    OBDReader,
    GPSReader,
    HardwareButtons,
    SteeringWheelControls,
    CommaDeviceReader,
)

if args.detect:
    hw = detect_hardware()
    print(json.dumps(hw, indent=2))
    sys.exit(0)

hw = detect_hardware()
print('[OpenCar] Hardware:', hw)

# ── Data-source startup ──────────────────────────────────────────────────────
# Import STATE here so detect-only path above doesn't touch display code.
from vehicle_state import STATE
import can_sim

reader = None

if hw['comma']:
    print('[OpenCar] Comma device detected — using openpilot data')
    reader = CommaDeviceReader()
    reader.start(STATE)

elif args.replay:
    print(f'[OpenCar] Replay mode: {args.replay}')
    reader = CANReader(channel=None, bustype=args.can_bus, replay_file=args.replay)
    reader.start(STATE, args.car)

elif args.can or hw['can']:
    print(f'[OpenCar] CAN mode: {args.can_bus}:{args.can_channel or "auto"}')
    reader = CANReader(channel=args.can_channel, bustype=args.can_bus)
    if args.can_channel:
        reader.start(STATE, args.car)
    else:
        if reader.auto_detect():
            reader.start(STATE, args.car)
        else:
            print('[OpenCar] No CAN channel found — falling back to simulation')
            can_sim.start()

elif args.obd:
    print(f'[OpenCar] OBD-II mode: {args.obd_port or "auto"}')
    reader = OBDReader(port=args.obd_port)
    reader.start(STATE)

else:
    print('[OpenCar] Simulation mode')
    can_sim.start()

# ── GPS ──────────────────────────────────────────────────────────────────────
gps = None
if hw['gps']:
    gps = GPSReader()
    gps.start(STATE)

# ── GPIO hardware buttons ────────────────────────────────────────────────────
hw_buttons = None
if args.gpio and hw['gpio']:
    hw_buttons = HardwareButtons()
    hw_buttons.start()

# ── Steering wheel controls ──────────────────────────────────────────────────
sw_controls = None
if hw['evdev']:
    sw_controls = SteeringWheelControls()
    sw_controls.start()

# ── Apply vehicle profile to STATE ───────────────────────────────────────────
STATE.set('car_profile', args.car)

# ════════════════════════════════════════════════════════════════════════════
# Raylib window + rendering
# ════════════════════════════════════════════════════════════════════════════
import pyray as rl
import theme as thm


def show_splash(W: int, H: int, fonts: dict, theme):
    """
    Two-second startup splash showing the OpenCar logo and detected
    hardware status with an animated progress bar.
    """
    hw_info = detect_hardware()
    status = [
        f"CAN Bus:  {'\u2705' if hw_info['can']   else '\u274c'}  "
        f"({', '.join(hw_info['can_channels']) or 'none'})",
        f"OBD-II:   {'\u2705' if hw_info['obd']   else '\u274c'}",
        f"GPS:      {'\u2705' if hw_info['gps']   else '\u274c'}",
        f"GPIO:     {'\u2705' if hw_info['gpio']  else '\u274c'}",
        f"Comma:    {'\u2705' if hw_info['comma'] else '\u274c'}",
        f"Platform: {hw_info['platform']}",
    ]

    start = rl.get_time()
    while rl.get_time() - start < 2.0 and not rl.window_should_close():
        rl.begin_drawing()
        rl.clear_background(theme.bg)

        # ── Logo ─────────────────────────────────────────────────────────
        title = 'OpenCar'
        v = rl.measure_text_ex(fonts['xl'], title, 72, 2)
        rl.draw_text_ex(
            fonts['xl'], title,
            rl.Vector2(W / 2 - v.x / 2, H / 2 - 120),
            72, 2, theme.accent,
        )

        # ── Sub-title ────────────────────────────────────────────────────
        sub = 'Multi-surface Automotive UI  ·  v1.0'
        v2 = rl.measure_text_ex(fonts['sm'], sub, 20, 1)
        rl.draw_text_ex(
            fonts['sm'], sub,
            rl.Vector2(W / 2 - v2.x / 2, H / 2 - 40),
            20, 1, theme.fg2,
        )

        # ── Hardware status ───────────────────────────────────────────────
        for i, line in enumerate(status):
            rl.draw_text_ex(
                fonts['xs'], line,
                rl.Vector2(W / 2 - 160, H / 2 + 20 + i * 20),
                14, 1, theme.fg2,
            )

        # ── Progress bar ─────────────────────────────────────────────────
        elapsed = rl.get_time() - start
        bar_w   = int((W - 200) * elapsed / 2.0)
        rl.draw_rectangle_rounded(
            rl.Rectangle(100, H - 30, W - 200, 4), 1.0, 4, theme.surface2)
        rl.draw_rectangle_rounded(
            rl.Rectangle(100, H - 30, max(1, bar_w), 4), 1.0, 4, theme.accent)

        rl.end_drawing()


def main():
    # ── Window flags ──────────────────────────────────────────────────────
    flags = rl.ConfigFlags.FLAG_MSAA_4X_HINT  # Anti-aliasing for smooth curves
    if args.fullscreen:
        flags |= rl.ConfigFlags.FLAG_FULLSCREEN_MODE
    else:
        flags |= rl.ConfigFlags.FLAG_WINDOW_RESIZABLE
    rl.set_config_flags(flags)

    title = f'OpenCar — {args.car.title()}'
    rl.init_window(args.width, args.height, title)
    rl.set_target_fps(config.getint('display', 'fps', fallback=60))

    # If fullscreen, use actual screen dimensions
    if args.fullscreen:
        W = rl.get_screen_width()
        H = rl.get_screen_height()
    else:
        W, H = args.width, args.height

    # ── Font loading — Inter first, DejaVu fallback ───────────────────────
    font_paths = [
        'assets/fonts/Inter-Regular.ttf',
        'assets/fonts/DejaVuSans.ttf',
    ]
    bold_paths = [
        'assets/fonts/Inter-Bold.ttf',
        'assets/fonts/DejaVuSans-Bold.ttf',
        'assets/fonts/DejaVuSans.ttf',
    ]

    # Codepoints: ASCII 32..126 + degree symbol (176) + middle dot (183) + bullet (8226)
    cp_list = list(range(32, 127)) + [176, 183, 8226]
    cp_arr = rl.ffi.new('int[]', cp_list)
    cp_ptr = rl.ffi.cast('int *', cp_arr)
    cp_len = len(cp_list)

    def load_font(paths, size):
        for p in paths:
            try:
                f = rl.load_font_ex(p, size, cp_ptr, cp_len)
                bs = getattr(f, 'baseSize', getattr(f, 'base_size', 0))
                if bs > 0:
                    rl.set_texture_filter(f.texture, rl.TextureFilter.TEXTURE_FILTER_BILINEAR)
                    return f
            except Exception:
                pass
        return rl.get_font_default()

    fonts = {
        'xxl': load_font(bold_paths, 140),   # Speed numbers, hero temps
        'xl':  load_font(bold_paths, 96),     # Large titles
        'lg':  load_font(font_paths, 48),     # Section headers
        'blg': load_font(bold_paths, 48),     # Bold section headers
        'md':  load_font(font_paths, 32),     # Body text
        'bmd': load_font(bold_paths, 32),     # Bold body
        'sm':  load_font(font_paths, 22),     # Subtitles
        'xs':  load_font(font_paths, 16),     # Labels
        'bxl': load_font(bold_paths, 120),    # Bold extra large
    }

    # ── Splash screen ─────────────────────────────────────────────────────
    show_splash(W, H, fonts, thm.current)

    # ── Surface import (lazy — font errors surface early) ─────────────────
    from surfaces.hud          import HUDSurface
    from surfaces.infotainment import InfoSurface
    from surfaces.rear         import RearSurface

    surfaces = [
        HUDSurface(fonts),
        InfoSurface(fonts),
        RearSurface(fonts),
    ]
    active = max(0, min(2, args.surface))

    # ── Main loop ─────────────────────────────────────────────────────────
    while not rl.window_should_close():
        # Keyboard shortcuts
        key = rl.get_key_pressed()
        if key == rl.KeyboardKey.KEY_ONE:   active = 0
        if key == rl.KeyboardKey.KEY_TWO:   active = 1
        if key == rl.KeyboardKey.KEY_THREE: active = 2
        if key == rl.KeyboardKey.KEY_T:     thm.toggle()
        if key == rl.KeyboardKey.KEY_Q:     break

        # Forward remaining keys to active surface
        surfaces[active].handle_key(key, STATE, thm.current)

        # ── GPIO hardware buttons ─────────────────────────────────────────
        if hw_buttons:
            for action, value in hw_buttons.poll():
                if action == 'surface':
                    active = int(value)
                elif action == 'theme':
                    thm.toggle()

        # ── Steering wheel controls ───────────────────────────────────────
        if sw_controls:
            for action, value in sw_controls.poll():
                if action == 'next_track':
                    STATE.set('music_track', (STATE.music_track + 1) % 8)
                elif action == 'prev_track':
                    STATE.set('music_track', (STATE.music_track - 1) % 8)
                elif action == 'play_pause':
                    STATE.set('music_playing', not STATE.music_playing)
                elif action == 'volume_up':
                    STATE.set('brightness', min(100, STATE.brightness + 5))
                elif action == 'volume_down':
                    STATE.set('brightness', max(0,   STATE.brightness - 5))

        # Handle window resize in windowed mode
        if not args.fullscreen and rl.is_window_resized():
            W = rl.get_screen_width()
            H = rl.get_screen_height()

        # ── Render ────────────────────────────────────────────────────────
        rl.begin_drawing()
        rl.clear_background(thm.current.bg)
        surfaces[active].render(STATE, thm.current)
        rl.end_drawing()

    # ── Cleanup ───────────────────────────────────────────────────────────
    if hw_buttons:  hw_buttons.stop()
    if sw_controls: sw_controls.stop()
    if gps:         gps.stop()
    if reader:      reader.stop()
    rl.close_window()


if __name__ == '__main__':
    main()

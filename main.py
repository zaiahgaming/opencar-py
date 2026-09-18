#!/usr/bin/env python3
"""OpenCar v1.0 — Python + Raylib multi-surface automotive UI"""
import sys, threading
import pyray as rl
from vehicle_state import STATE
import theme as thm
import can_sim

WINDOW_W = 1280
WINDOW_H = 480
FPS      = 60

def main():
    rl.init_window(WINDOW_W, WINDOW_H, "OpenCar")
    rl.set_target_fps(FPS)

    # Font loading — try Inter first, fallback to DejaVu
    font_paths = [
        "assets/fonts/Inter-Regular.ttf",
        "assets/fonts/DejaVuSans.ttf",
    ]
    bold_paths = [
        "assets/fonts/Inter-Bold.ttf",
        "assets/fonts/DejaVuSans-Bold.ttf",
        "assets/fonts/DejaVuSans.ttf",
    ]
    def load_font(paths, size):
        for p in paths:
            try:
                f = rl.load_font_ex(p, size, None, 0)
                if f.base_size > 0: return f
            except: pass
        return rl.get_font_default()

    font_xl  = load_font(font_paths, 96)
    font_lg  = load_font(font_paths, 48)
    font_md  = load_font(font_paths, 28)
    font_sm  = load_font(font_paths, 18)
    font_xs  = load_font(font_paths, 13)
    font_blg = load_font(bold_paths, 48)

    fonts = {'xl': font_xl, 'lg': font_lg, 'md': font_md,
             'sm': font_sm, 'xs': font_xs, 'blg': font_blg}

    # Start CAN simulator
    can_sim.start()

    # Import surfaces (lazy, so font errors surface early)
    from surfaces.hud           import HUDSurface
    from surfaces.infotainment  import InfoSurface
    from surfaces.rear          import RearSurface

    surfaces = [
        HUDSurface(fonts),
        InfoSurface(fonts),
        RearSurface(fonts),
    ]
    active = 0  # 0=HUD 1=Info 2=Rear

    while not rl.window_should_close():
        key = rl.get_key_pressed()
        if key == rl.KeyboardKey.KEY_ONE:   active = 0
        if key == rl.KeyboardKey.KEY_TWO:   active = 1
        if key == rl.KeyboardKey.KEY_THREE: active = 2
        if key == rl.KeyboardKey.KEY_T:
            thm.toggle()
        if key == rl.KeyboardKey.KEY_Q:
            break

        # Forward remaining keys to active surface
        surfaces[active].handle_key(key, STATE, thm.current)

        rl.begin_drawing()
        rl.clear_background(thm.current.bg)
        surfaces[active].render(STATE, thm.current)
        rl.end_drawing()

    rl.close_window()

if __name__ == '__main__':
    main()

import os
import sys
import time
import shutil

repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(repo_root)
sys.path.insert(0, repo_root)

import pyray as rl
from vehicle_state import STATE
import theme as thm

def capture_all():
    W, H = 1920, 720
    rl.set_config_flags(rl.ConfigFlags.FLAG_MSAA_4X_HINT | rl.ConfigFlags.FLAG_WINDOW_UNDECORATED)
    rl.init_window(W, H, "OpenCar Capture")
    rl.set_target_fps(60)

    # Codepoints
    cp_list = list(range(32, 127)) + [176, 183, 8226]
    cp_arr = rl.ffi.new('int[]', cp_list)
    cp_ptr = rl.ffi.cast('int *', cp_arr)
    cp_len = len(cp_list)

    font_paths = ['assets/fonts/Inter-Regular.ttf', 'assets/fonts/DejaVuSans.ttf']
    bold_paths = ['assets/fonts/Inter-Bold.ttf', 'assets/fonts/DejaVuSans-Bold.ttf', 'assets/fonts/DejaVuSans.ttf']

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
        'xxl': load_font(bold_paths, 140),
        'xl':  load_font(bold_paths, 96),
        'lg':  load_font(font_paths, 48),
        'blg': load_font(bold_paths, 48),
        'md':  load_font(font_paths, 32),
        'bmd': load_font(bold_paths, 32),
        'sm':  load_font(font_paths, 22),
        'xs':  load_font(font_paths, 16),
        'bxl': load_font(bold_paths, 120),
    }

    from surfaces.hud import HUDSurface
    from surfaces.infotainment import InfoSurface
    from surfaces.rear import RearSurface

    hud = HUDSurface(fonts)
    info = InfoSurface(fonts)
    rear = RearSurface(fonts)

    STATE.speed_mph = 65.0
    STATE.rpm = 2400.0
    STATE.gear = 3 # Drive
    STATE.driver_temp_f = 72.0
    STATE.pass_temp_f = 70.0
    STATE.fan_level = 3
    STATE.ac_on = True
    STATE.destination = "Downtown SF"
    STATE.music_title = "Los Angeles"
    STATE.music_artist = "The Midnight"
    STATE.music_playing = True
    STATE.music_progress = 0.38
    STATE.fuel_level = 0.82
    STATE.car_profile = "toyota"

    out_dir = "/home/zaiah/.gemini/antigravity-cli/brain/37719168-6265-41c8-b964-41b51fa9d6db"
    os.makedirs(out_dir, exist_ok=True)

    shots = [
        ("r4_hud.png", hud, None),
        ("r4_info_home.png", info, lambda: setattr(STATE, 'infotainment_app', 0)),
        ("r4_info_music.png", info, lambda: setattr(STATE, 'infotainment_app', 2)),
        ("r4_info_climate.png", info, lambda: setattr(STATE, 'infotainment_app', 3)),
        ("r4_rear_home.png", rear, lambda: setattr(rear, 'active_tab', 0)),
        ("r4_rear_media.png", rear, lambda: setattr(rear, 'active_tab', 1)),
        ("r4_rear_pong.png", rear, lambda: setattr(rear, 'active_tab', 2)),
    ]

    for fname, surface, setup_fn in shots:
        if setup_fn:
            setup_fn()
        for _ in range(5):
            rl.begin_drawing()
            rl.clear_background(rl.BLACK)
            surface.render(STATE, thm.current)
            rl.end_drawing()
        
        rl.take_screenshot(fname.encode('utf-8'))
        shutil.copy(fname, os.path.join(out_dir, fname))
        print(f"Captured and saved: {fname} -> {out_dir}/{fname}")
        time.sleep(0.1)

    rl.close_window()
    print("All screenshots successfully captured!")

if __name__ == '__main__':
    capture_all()

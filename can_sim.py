# can_sim.py — Simulated CAN bus feeding VehicleState
import threading, time, math
from vehicle_state import STATE

SONG_LIBRARY = [
    ("The Midnight",      "Los Angeles"),
    ("Tame Impala",       "Let It Happen"),
    ("Bonobo",            "Kerala"),
    ("Tycho",             "Awake"),
    ("Caribou",           "Sun"),
    ("Four Tet",          "Angel Echoes"),
    ("Boards of Canada",  "Dayvan Cowboy"),
    ("Aphex Twin",        "Avril 14th"),
]

def _sim_speed_mph(t):
    if t < 5:   return 0.0
    if t < 10:  return (t-5)/5 * 55.0 * (3*((t-5)/5)**2 - 2*((t-5)/5)**3)
    return 50.0 + 12.0 * math.sin(2*math.pi*(t-10)/20.0)

def _sim_rpm(speed, t):
    if t < 5: return 850.0
    return max(750, min(7000, 800 + speed*28 + 200*math.sin(2*math.pi*t/1.3)))

def _sim_lane(t):
    phase = t % 26.0
    if phase < 10:  return 0
    if phase < 13:  return 1
    if phase < 23:  return 0
    return 2

def run():
    start = time.time()
    song_dur = 210.0  # 3.5 min per track
    last_track = -1
    while True:
        elapsed = time.time() - start
        t = elapsed % 60.0

        speed  = _sim_speed_mph(t)
        rpm    = _sim_rpm(speed, t)
        gear   = 0 if t < 5 else 3
        lane   = 0 if t < 5 else _sim_lane(t)
        acc    = t >= 10 and (int(t/15) % 2 == 0)
        gap    = 3
        e_temp = (100 + 90*(min(t,15)/15)) if t < 15 else (190 + 5*math.sin(t/3))
        eta    = max(0, 4920 - int(elapsed))
        prog   = min(1.0, 0.35 + elapsed/(4920*0.65) if 4920 > 0 else 1.0)
        avg    = (speed * 0.5 + STATE.avg_speed_mph * 0.5) if speed > 0 else STATE.avg_speed_mph

        # Music progress
        music_pos = elapsed % song_dur
        track_idx = int(elapsed / song_dur) % len(SONG_LIBRARY)
        m_prog = music_pos / song_dur
        if track_idx != last_track:
            STATE.set('music_artist', SONG_LIBRARY[track_idx][0])
            STATE.set('music_title',  SONG_LIBRARY[track_idx][1])
            last_track = track_idx

        with STATE._lock:
            STATE.speed_mph     = speed
            STATE.rpm           = rpm
            STATE.gear          = gear
            STATE.lane_state    = lane
            STATE.acc_active    = acc
            STATE.acc_gap       = gap
            STATE.engine_temp_f = e_temp
            STATE.eta_seconds   = eta
            STATE.trip_progress = prog
            STATE.avg_speed_mph = avg
            STATE.music_track   = track_idx
            STATE.music_progress= m_prog
            if STATE.music_playing:
                pass  # music_progress updated above

        time.sleep(0.1)  # 10 Hz

def start():
    t = threading.Thread(target=run, daemon=True)
    t.start()

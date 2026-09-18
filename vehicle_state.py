# vehicle_state.py — shared live data, thread-safe
import threading
import time

class VehicleState:
    def __init__(self):
        self._lock = threading.Lock()
        # Drive
        self.speed_mph = 0.0
        self.rpm = 800.0
        self.gear = 0          # 0=P 1=R 2=N 3=D
        self.engine_temp_f = 190.0
        # ADAS
        self.acc_active = False
        self.acc_gap = 3        # 1-5 bars
        self.lane_state = 0     # 0=centered 1=left 2=right
        self.openpilot = False
        # Climate
        self.climate_temp_f = 72.0
        self.driver_temp_f = 72.0
        self.pass_temp_f = 72.0
        self.fan_level = 2
        self.ac_on = True
        self.heated_seats = False
        self.rear_defrost = False
        # Rear climate
        self.rear_driver_temp = 70.0
        self.rear_pass_temp = 70.0
        self.rear_fan = 2
        # Navigation
        self.nav_instruction = "Continue on US-101"
        self.destination = "San Francisco, CA"
        self.eta_seconds = 4920
        self.trip_progress = 0.35
        self.trip_distance_mi = 127.4
        self.avg_speed_mph = 0.0
        # Music
        self.music_playing = True
        self.music_track = 0
        self.music_progress = 0.0
        self.music_artist = "The Midnight"
        self.music_title = "Los Angeles"
        # Infotainment app state
        self.infotainment_app = 0  # 0=home 1=nav 2=music 3=climate 4=phone 5=settings
        # Rear state
        self.rear_app = 0      # 0=home 1=video 2=music 3=pong 4=trip 5=climate
        self.video_progress = 0.0
        self.dvd_bounce = False
        self.fuel_level = 0.72
        self.pong_score_player = 0
        self.pong_score_ai = 0
        # Settings
        self.units_mph = True
        self.theme_dark = True
        self.brightness = 80
        self.car_profile = "toyota"  # toyota/honda/gm/ford

    def get(self, attr):
        with self._lock:
            return getattr(self, attr)

    def set(self, attr, value):
        with self._lock:
            setattr(self, attr, value)

STATE = VehicleState()

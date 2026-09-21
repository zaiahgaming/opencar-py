#!/usr/bin/env python3
"""
hardware.py — OpenCar hardware abstraction layer

Provides detect_hardware() plus reader/controller classes for:
  - CAN bus (python-can, socketcan / CANable)
  - OBD-II  (obd library, ELM327)
  - GPS     (gpsd / gpsd-py3)
  - GPIO    (RPi.GPIO or gpiozero — Raspberry Pi)
  - evdev   steering-wheel controls (Linux input subsystem)
  - Comma 3/3X (openpilot cereal/messaging)

All classes are safe to instantiate even when the underlying
hardware or Python library is not present — they simply return
empty poll() iterators or ignore calls.
"""

import os
import sys
import platform
import threading
import time
import logging

log = logging.getLogger('opencar.hardware')

# ────────────────────────────────────────────────────────────────────────────
# Hardware detection
# ────────────────────────────────────────────────────────────────────────────

def detect_hardware() -> dict:
    """
    Probe the system for available hardware interfaces.

    Returns a dict with boolean flags and platform info:
      {
        'can':      bool,   # CAN adapter available (socketcan / CANable)
        'obd':      bool,   # OBD-II library importable
        'gps':      bool,   # gpsd socket reachable
        'gpio':     bool,   # RPi GPIO (or gpiozero) available
        'evdev':    bool,   # evdev Linux input available
        'comma':    bool,   # Comma 3/3X openpilot msgq detected
        'platform': str,    # short platform description
        'can_channels': list[str],  # detected CAN channel names
      }
    """
    result = {
        'can':          False,
        'obd':          False,
        'gps':          False,
        'gpio':         False,
        'evdev':        False,
        'comma':        False,
        'platform':     _detect_platform(),
        'can_channels': [],
    }

    # ── CAN ──────────────────────────────────────────────────────────────
    try:
        import can  # python-can
        channels = _scan_can_channels()
        result['can'] = bool(channels)
        result['can_channels'] = channels
    except ImportError:
        pass

    # ── OBD-II ───────────────────────────────────────────────────────────
    try:
        import obd  # python-obd
        result['obd'] = True
    except ImportError:
        pass

    # ── GPS ──────────────────────────────────────────────────────────────
    result['gps'] = _check_gpsd()

    # ── GPIO ─────────────────────────────────────────────────────────────
    result['gpio'] = _check_gpio()

    # ── evdev ────────────────────────────────────────────────────────────
    try:
        import evdev  # noqa: F401
        result['evdev'] = True
    except ImportError:
        pass

    # ── Comma device ─────────────────────────────────────────────────────
    result['comma'] = _check_comma()

    return result


def _detect_platform() -> str:
    uname = platform.uname()
    machine = uname.machine.lower()
    node = uname.node.lower()

    if 'tici' in node or 'comma' in node:
        return 'Comma 3/3X'
    if machine in ('aarch64', 'armv7l', 'armv6l'):
        # Check for Raspberry Pi
        try:
            with open('/proc/device-tree/model', 'r') as f:
                model = f.read().strip('\x00').strip()
                return model
        except OSError:
            return f'ARM Linux ({machine})'
    return f'{uname.system} {uname.release} ({machine})'


def _scan_can_channels() -> list:
    """Return a list of socketcan-style network interfaces present."""
    channels = []
    try:
        import socket
        import struct
        import fcntl

        SIOCGIFCONF = 0x8912
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        buf = bytearray(4096)
        ifreq = struct.pack('iP', len(buf), id(buf))
        try:
            fcntl.ioctl(s, SIOCGIFCONF, ifreq)
        finally:
            s.close()
    except Exception:
        pass

    # Simpler: read /sys/class/net
    net_path = '/sys/class/net'
    if os.path.isdir(net_path):
        for iface in os.listdir(net_path):
            if iface.startswith('can') or iface.startswith('vcan'):
                channels.append(iface)
    return sorted(channels)


def _check_gpsd() -> bool:
    """Attempt a TCP connection to gpsd on localhost:2947."""
    import socket
    try:
        s = socket.create_connection(('127.0.0.1', 2947), timeout=0.5)
        s.close()
        return True
    except OSError:
        return False


def _check_gpio() -> bool:
    try:
        import RPi.GPIO  # noqa: F401
        return True
    except ImportError:
        pass
    try:
        import gpiozero  # noqa: F401
        return True
    except ImportError:
        pass
    return False


def _check_comma() -> bool:
    """Detect a Comma 3/3X by looking for openpilot's cereal msgq socket."""
    return (
        os.path.exists('/dev/shm/ubloxGnss')
        or os.path.exists('/tmp/carState')
        or os.path.exists('/data/openpilot')
    )


# ────────────────────────────────────────────────────────────────────────────
# CAN Reader
# ────────────────────────────────────────────────────────────────────────────

# Vehicle-profile DBC signal maps  (PID → (attr, scale, offset))
_VEHICLE_PROFILES = {
    'toyota': {
        0x025: ('speed_mph',   0.02237, 0.0),   # raw in km/h × 100 → mph
        0x0B4: ('engine_temp_f', 0.75, -40.0),  # coolant temp raw → °F
        0x0AA: ('rpm',          0.25,   0.0),   # raw RPM
    },
    'honda': {
        0x158: ('speed_mph',   0.01553, 0.0),
        0x17C: ('rpm',          0.25,   0.0),
        0x54A: ('engine_temp_f', 0.75, -40.0),
    },
    'gm': {
        0x3D1: ('speed_mph',   0.01553, 0.0),
        0x108: ('rpm',          0.25,   0.0),
    },
    'ford': {
        0x217: ('speed_mph',   0.01553, 0.0),
        0x204: ('rpm',          0.25,   0.0),
    },
}


class CANReader:
    """
    Reads live vehicle data from a CAN bus adapter via python-can.

    Falls back gracefully to no-op if python-can is not installed.
    Supports socketcan, PEAK, CANable (slcan), and candump replay.
    """

    def __init__(self, channel: str = None, bustype: str = 'socketcan',
                 replay_file: str = None):
        self.channel     = channel
        self.bustype     = bustype
        self.replay_file = replay_file
        self._thread     = None
        self._stop       = threading.Event()

    def auto_detect(self) -> bool:
        """
        Try to find any CAN channel on the system.
        Sets self.channel on success.  Returns True if found.
        """
        channels = _scan_can_channels()
        if channels:
            self.channel = channels[0]
            log.info('[CAN] Auto-detected channel: %s', self.channel)
            return True
        log.warning('[CAN] No CAN channels found during auto-detect')
        return False

    def start(self, state, profile: str = 'toyota'):
        """Start the CAN reader thread."""
        self._thread = threading.Thread(
            target=self._run, args=(state, profile), daemon=True, name='CANReader'
        )
        self._thread.start()

    def stop(self):
        self._stop.set()

    def _run(self, state, profile: str):
        try:
            import can
        except ImportError:
            log.error('[CAN] python-can not installed — CAN reader disabled')
            return

        signal_map = _VEHICLE_PROFILES.get(profile, _VEHICLE_PROFILES['toyota'])
        state.set('car_profile', profile)

        if self.replay_file:
            self._run_replay(state, signal_map)
            return

        log.info('[CAN] Opening %s on %s', self.channel, self.bustype)
        try:
            bus = can.interface.Bus(channel=self.channel, bustype=self.bustype)
        except Exception as exc:
            log.error('[CAN] Failed to open bus: %s', exc)
            return

        try:
            while not self._stop.is_set():
                msg = bus.recv(timeout=1.0)
                if msg is None:
                    continue
                self._decode(msg, state, signal_map)
        finally:
            bus.shutdown()

    def _run_replay(self, state, signal_map):
        """Replay a candump log file (text or compressed)."""
        import can
        try:
            reader = can.CanutilsLogReader(self.replay_file)
            for msg in reader:
                if self._stop.is_set():
                    break
                self._decode(msg, state, signal_map)
                time.sleep(0.01)
        except Exception as exc:
            log.error('[CAN] Replay error: %s', exc)

    @staticmethod
    def _decode(msg, state, signal_map):
        if msg.arbitration_id in signal_map:
            attr, scale, offset = signal_map[msg.arbitration_id]
            raw = int.from_bytes(msg.data[:2], 'big')
            value = raw * scale + offset
            state.set(attr, value)


# ────────────────────────────────────────────────────────────────────────────
# OBD-II Reader  (ELM327 / python-obd)
# ────────────────────────────────────────────────────────────────────────────

class OBDReader:
    """
    Reads live data from an ELM327 adapter via the python-obd library.

    Auto-detects the serial port if port=None or port='auto'.
    """

    def __init__(self, port: str = None):
        self.port    = port if port and port != 'auto' else None
        self._thread = None
        self._stop   = threading.Event()

    def start(self, state):
        self._thread = threading.Thread(
            target=self._run, args=(state,), daemon=True, name='OBDReader'
        )
        self._thread.start()

    def stop(self):
        self._stop.set()

    def _run(self, state):
        try:
            import obd
        except ImportError:
            log.error('[OBD] python-obd not installed — OBD reader disabled')
            return

        log.info('[OBD] Connecting on %s …', self.port or 'auto')
        try:
            conn = obd.OBD(portstr=self.port, fast=False)
        except Exception as exc:
            log.error('[OBD] Connection failed: %s', exc)
            return

        if not conn.is_connected():
            log.warning('[OBD] Adapter not connected')
            return

        log.info('[OBD] Connected — starting query loop')
        cmds = {
            obd.commands.SPEED:         ('speed_mph',     lambda r: r.value.to('mph').magnitude),
            obd.commands.RPM:           ('rpm',            lambda r: r.value.magnitude),
            obd.commands.COOLANT_TEMP:  ('engine_temp_f', lambda r: r.value.to('degF').magnitude),
            obd.commands.THROTTLE_POS:  ('throttle',      lambda r: r.value.magnitude),
        }
        supported = {cmd: fn for cmd, (attr, fn) in cmds.items()
                     if conn.supports(cmd)}

        while not self._stop.is_set():
            for cmd, (attr, fn) in cmds.items():
                if self._stop.is_set():
                    break
                try:
                    resp = conn.query(cmd)
                    if not resp.is_null():
                        state.set(attr, fn(resp))
                except Exception:
                    pass
            time.sleep(0.2)

        conn.close()


# ────────────────────────────────────────────────────────────────────────────
# GPS Reader  (gpsd)
# ────────────────────────────────────────────────────────────────────────────

class GPSReader:
    """
    Pulls location data from gpsd via the gpsd-py3 library.
    Updates STATE.gps_lat, STATE.gps_lon, STATE.gps_speed_mph.
    """

    def __init__(self):
        self._thread = None
        self._stop   = threading.Event()

    def start(self, state):
        self._thread = threading.Thread(
            target=self._run, args=(state,), daemon=True, name='GPSReader'
        )
        self._thread.start()

    def stop(self):
        self._stop.set()

    def _run(self, state):
        try:
            import gpsd
        except ImportError:
            log.error('[GPS] gpsd-py3 not installed — GPS disabled')
            return

        try:
            gpsd.connect()
        except Exception as exc:
            log.error('[GPS] Cannot connect to gpsd: %s', exc)
            return

        log.info('[GPS] Connected to gpsd')
        while not self._stop.is_set():
            try:
                packet = gpsd.get_current()
                state.set('gps_lat', packet.lat)
                state.set('gps_lon', packet.lon)
                # gpsd speed is in m/s
                state.set('gps_speed_mph', packet.hspeed * 2.23694)
            except Exception:
                pass
            time.sleep(1.0)


# ────────────────────────────────────────────────────────────────────────────
# GPIO Hardware Buttons  (Raspberry Pi)
# ────────────────────────────────────────────────────────────────────────────

# Default pin mapping (BCM numbering)
_GPIO_PINS = {
    17: ('surface', 0),   # HUD
    27: ('surface', 1),   # Infotainment
    22: ('surface', 2),   # Rear
    23: ('theme',   None),
}


class HardwareButtons:
    """
    Polls Raspberry Pi GPIO pins for physical button presses.

    Uses RPi.GPIO (falling-edge interrupt) when available, falls back
    to gpiozero, then no-ops gracefully.

    poll() returns an iterable of (action, value) tuples since last call.
    """

    def __init__(self, pin_map: dict = None):
        self._pin_map = pin_map or _GPIO_PINS
        self._queue   = []
        self._lock    = threading.Lock()
        self._gpio    = None
        self._buttons = {}  # gpiozero button objects

    def start(self):
        if self._try_rpigpio():
            log.info('[GPIO] Using RPi.GPIO')
        elif self._try_gpiozero():
            log.info('[GPIO] Using gpiozero')
        else:
            log.warning('[GPIO] No GPIO library — hardware buttons disabled')

    def poll(self):
        with self._lock:
            events, self._queue = self._queue, []
        return events

    def stop(self):
        if self._gpio:
            try:
                self._gpio.cleanup()
            except Exception:
                pass
        for btn in self._buttons.values():
            try:
                btn.close()
            except Exception:
                pass

    # ── RPi.GPIO backend ─────────────────────────────────────────────────
    def _try_rpigpio(self) -> bool:
        try:
            import RPi.GPIO as GPIO
            self._gpio = GPIO
            GPIO.setmode(GPIO.BCM)
            for pin, (action, value) in self._pin_map.items():
                GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
                GPIO.add_event_detect(
                    pin, GPIO.FALLING,
                    callback=self._make_callback_rpigpio(action, value),
                    bouncetime=200,
                )
            return True
        except Exception:
            return False

    def _make_callback_rpigpio(self, action, value):
        def _cb(channel):
            with self._lock:
                self._queue.append((action, value))
        return _cb

    # ── gpiozero backend ─────────────────────────────────────────────────
    def _try_gpiozero(self) -> bool:
        try:
            from gpiozero import Button
            for pin, (action, value) in self._pin_map.items():
                btn = Button(pin, pull_up=True, bounce_time=0.2)
                btn.when_pressed = self._make_callback_gpiozero(action, value)
                self._buttons[pin] = btn
            return True
        except Exception:
            return False

    def _make_callback_gpiozero(self, action, value):
        def _cb():
            with self._lock:
                self._queue.append((action, value))
        return _cb


# ────────────────────────────────────────────────────────────────────────────
# Steering Wheel Controls  (evdev)
# ────────────────────────────────────────────────────────────────────────────

# evdev key → OpenCar action mapping
_SW_KEY_MAP = {
    # Common HID usage codes for steering-wheel media buttons
    'KEY_NEXTSONG':    ('next_track',  None),
    'KEY_PREVIOUSSONG':('prev_track',  None),
    'KEY_PLAYPAUSE':   ('play_pause',  None),
    'KEY_VOLUMEUP':    ('volume_up',   1),
    'KEY_VOLUMEDOWN':  ('volume_down', -1),
    'KEY_MUTE':        ('mute',        None),
}


class SteeringWheelControls:
    """
    Reads steering-wheel media/HID buttons via the Linux evdev interface.

    Auto-detects the first device advertising at least one mapped key.
    poll() returns (action, value) tuples since last call.
    """

    def __init__(self, device_path: str = None):
        self._device_path = device_path
        self._thread      = None
        self._stop        = threading.Event()
        self._queue       = []
        self._lock        = threading.Lock()

    def start(self):
        self._thread = threading.Thread(
            target=self._run, daemon=True, name='SteeringWheelControls'
        )
        self._thread.start()

    def poll(self):
        with self._lock:
            events, self._queue = self._queue, []
        return events

    def stop(self):
        self._stop.set()

    def _run(self):
        try:
            import evdev
        except ImportError:
            log.error('[evdev] python-evdev not installed — SW controls disabled')
            return

        device = self._find_device(evdev)
        if device is None:
            log.warning('[evdev] No steering-wheel input device found')
            return

        log.info('[evdev] Monitoring: %s (%s)', device.name, device.path)
        mapped_codes = {
            evdev.ecodes.ecodes[k]: (a, v)
            for k, (a, v) in _SW_KEY_MAP.items()
            if k in evdev.ecodes.ecodes
        }

        try:
            for event in device.read_loop():
                if self._stop.is_set():
                    break
                if event.type == evdev.ecodes.EV_KEY and event.value == 1:
                    if event.code in mapped_codes:
                        action, value = mapped_codes[event.code]
                        with self._lock:
                            self._queue.append((action, value))
        except Exception as exc:
            log.warning('[evdev] Read error: %s', exc)
        finally:
            device.close()

    def _find_device(self, evdev):
        if self._device_path:
            try:
                return evdev.InputDevice(self._device_path)
            except Exception:
                return None

        mapped_codes = {
            evdev.ecodes.ecodes[k]
            for k in _SW_KEY_MAP
            if k in evdev.ecodes.ecodes
        }
        for path in sorted(evdev.list_devices()):
            try:
                dev = evdev.InputDevice(path)
                cap = dev.capabilities()
                keys = set(cap.get(evdev.ecodes.EV_KEY, []))
                if keys & mapped_codes:
                    return dev
                dev.close()
            except Exception:
                pass
        return None


# ────────────────────────────────────────────────────────────────────────────
# Comma 3/3X Reader  (openpilot cereal)
# ────────────────────────────────────────────────────────────────────────────

class CommaDeviceReader:
    """
    Reads live vehicle data from an openpilot Comma 3/3X via cereal messaging.

    Subscribes to carState and radarState from openpilot's msgq.
    Falls back gracefully if cereal is not installed.
    """

    def __init__(self):
        self._thread = None
        self._stop   = threading.Event()

    def start(self, state):
        self._thread = threading.Thread(
            target=self._run, args=(state,), daemon=True, name='CommaDeviceReader'
        )
        self._thread.start()

    def stop(self):
        self._stop.set()

    def _run(self, state):
        try:
            import cereal.messaging as messaging
        except ImportError:
            log.error('[Comma] cereal not installed — CommaDeviceReader disabled')
            return

        log.info('[Comma] Subscribing to openpilot carState + radarState')
        sm = messaging.SubMaster(['carState', 'radarState', 'liveLocationKalman'])

        while not self._stop.is_set():
            sm.update(timeout=100)  # ms
            if sm.updated['carState']:
                cs = sm['carState']
                # openpilot reports m/s → convert
                state.set('speed_mph', cs.vEgo * 2.23694)
                state.set('rpm',       getattr(cs, 'engineRpm', 0))
                state.set('gear',      int(getattr(cs, 'gearShifter', 3)))
                state.set('acc_active', cs.cruiseState.enabled)
                state.set('openpilot', True)

            if sm.updated['radarState']:
                rs = sm['radarState']
                leads = rs.radarPoints
                if leads:
                    # dRel = distance to lead car in metres
                    gap = max(1, min(5, int(leads[0].dRel / 10)))
                    state.set('acc_gap', gap)

            if sm.updated['liveLocationKalman']:
                llk = sm['liveLocationKalman']
                state.set('gps_lat', llk.positionGeodetic.value[0])
                state.set('gps_lon', llk.positionGeodetic.value[1])


# ────────────────────────────────────────────────────────────────────────────
# CAN Log Replay  (offline testing / demo mode)
# ────────────────────────────────────────────────────────────────────────────

def _decode_frame_static(msg_id: int, data: bytes, state, profile: dict):
    """
    Decode a single raw CAN frame using a vehicle_profile dict and write
    the result into *state*.  Shared by CANReader and CANLogReplay.

    Byte order: little-endian (matches opendbc signal definitions).
    """
    if msg_id == profile['speed_id']:
        raw = int.from_bytes(data[0:2], 'little')
        kph = raw * profile['speed_factor']
        mph = kph if profile['speed_is_mph'] else kph * 0.621_371
        state.set('speed_mph', mph)

    elif msg_id == profile['rpm_id']:
        # Honda shares speed_id == rpm_id (ENGINE_DATA); RPM is in bytes 2-3
        raw = int.from_bytes(data[2:4], 'little')
        state.set('rpm', raw * profile['rpm_factor'])

    elif msg_id == profile['gear_id']:
        state.set('gear', data[0] & 0x0F)   # lower nibble → P/R/N/D

    elif msg_id == profile['acc_id']:
        state.set('acc_active', bool(data[0] & 0x01))


class CANLogReplay:
    """
    Replay a saved CAN log file in real-time, feeding VehicleState as if
    the data were live from the bus.

    Supported file formats (selected automatically by python-can based on
    file extension):
        .asc  — Vector / CANalyzer ASCII log
        .blf  — Vector Binary Logging Format
        .csv  — Generic CSV
        .db   — SQLite log (python-can)
        .log  — candump / socketcan log

    Usage::

        replay = CANLogReplay('/path/to/capture.log')
        replay.start(STATE, profile_name='toyota')
        # … later …
        replay.stop()
    """

    def __init__(self, filepath: str, loop: bool = True):
        self.filepath  = filepath
        self.loop      = loop
        self._running  = False
        self._thread   = None
        self._profile  = None

    def start(self, state, profile_name: str = 'toyota'):
        """Begin replaying the log file in a daemon thread."""
        from vehicle_profile import PROFILES
        self._profile = PROFILES.get(profile_name, PROFILES['toyota'])
        self._running = True
        self._thread  = threading.Thread(
            target=self._replay_loop,
            args=(state,),
            daemon=True,
            name='CANReplay',
        )
        self._thread.start()

    def stop(self):
        self._running = False

    def _replay_loop(self, state):
        """Read log frames and feed them with correct inter-frame timing."""
        try:
            import can
        except ImportError:
            log.error('[Replay] python-can not installed — replay disabled')
            return

        profile = self._profile
        log.info('[Replay] Starting CAN log: %s', self.filepath)

        while self._running:
            try:
                with can.LogReader(self.filepath) as reader:
                    prev_ts = None
                    for msg in reader:
                        if not self._running:
                            break
                        # Honour inter-frame timing (cap sleep to 1 s)
                        if prev_ts is not None:
                            delta = msg.timestamp - prev_ts
                            if 0 < delta < 1.0:
                                time.sleep(delta)
                        prev_ts = msg.timestamp
                        _decode_frame_static(msg.arbitration_id,
                                             msg.data,
                                             state,
                                             profile)
            except Exception as exc:
                log.error('[Replay] Error reading log: %s', exc)
                break

            if not self.loop:
                break
            log.info('[Replay] Looping CAN log…')

        log.info('[Replay] Done')


# ────────────────────────────────────────────────────────────────────────────
# Top-level factory — auto_start()
# ────────────────────────────────────────────────────────────────────────────

def auto_start(state, args=None):
    """
    Detect the runtime environment and start the highest-priority data source.

    Priority order:
        1. CAN log replay   (if --replay <file> is present in *args*)
        2. Comma device     (if on /EON or /data/openpilot)
        3. Real CAN bus     (if python-can + adapter detected)
        4. OBD-II           (if python-obd + ELM327 adapter)
        5. GPS only         (gpsd — speed fallback)
        6. Simulation       (can_sim.py — always succeeds)

    Additional hardware always started when available:
        • GPIO hardware buttons (HardwareButtons)
        • Steering-wheel controls (SteeringWheelControls)
        • GPS supplement (GPSReader — always started alongside primary source)

    CLI flags consumed from *args*:
        --replay <file>     Use CAN log replay instead of live bus
        --loop              Loop the replay file indefinitely
        --profile <name>    Vehicle profile: toyota | honda | gm | ford
        --can-channel <ch>  Override CAN channel (e.g. can0, can1)
        --can-bustype <bt>  Override CAN bustype (e.g. socketcan, slcan)
        --obd-port <port>   Override OBD serial port
        --evdev-device <p>  Override evdev input device path

    Returns a dict of started reader instances keyed by source name.
    """
    args = args if args is not None else sys.argv[1:]
    hw   = detect_hardware()

    started = {}

    # ── Helper: extract flag value ────────────────────────────────────────
    def flag(name):
        try:
            idx = args.index(name)
            return args[idx + 1] if idx + 1 < len(args) else None
        except ValueError:
            return None

    profile_name = flag('--profile') or 'toyota'

    # 1. CAN log replay ────────────────────────────────────────────────────
    replay_path = flag('--replay')
    if replay_path:
        replay = CANLogReplay(replay_path, loop='--loop' in args)
        replay.start(state, profile_name=profile_name)
        started['replay'] = replay
        log.info('[Hardware] Source: CAN log replay (%s)', replay_path)

    # 2. Comma device ──────────────────────────────────────────────────────
    elif hw['comma']:
        reader = CommaDeviceReader()
        reader.start(state)
        started['comma'] = reader
        log.info('[Hardware] Source: comma device (cereal/messaging)')

    # 3. Real CAN bus ──────────────────────────────────────────────────────
    elif hw['can']:
        channel = flag('--can-channel') or (hw['can_channels'][0] if hw['can_channels'] else None)
        bustype = flag('--can-bustype') or 'socketcan'
        reader  = CANReader(channel=channel, bustype=bustype)
        if reader.auto_detect() or channel:
            reader.start(state, profile=profile_name)
            started['can'] = reader
            log.info('[Hardware] Source: CAN bus (%s:%s)', reader.bustype, reader.channel)
        else:
            # Adapter library present but no physical adapter reachable
            hw['can'] = False

    # 4. OBD-II ────────────────────────────────────────────────────────────
    if not started and hw['obd']:
        port   = flag('--obd-port')
        reader = OBDReader(port=port)
        reader.start(state)
        started['obd'] = reader
        log.info('[Hardware] Source: OBD-II (%s)', port or 'auto')

    # 5. GPS supplement ────────────────────────────────────────────────────
    if hw['gps']:
        gps_reader = GPSReader()
        gps_reader.start(state)
        started['gps'] = gps_reader
        log.info('[Hardware] GPS supplement: gpsd')

    # 6. Simulation fallback ───────────────────────────────────────────────
    if not started:
        import can_sim
        can_sim.start()
        started['sim'] = 'can_sim'
        log.info('[Hardware] Source: simulation (can_sim.py)')

    # ── Hardware input ─────────────────────────────────────────────────────
    if hw['gpio']:
        buttons = HardwareButtons()
        buttons.start()
        started['gpio'] = buttons
        log.info('[Hardware] GPIO hardware buttons active')

    if hw['evdev']:
        swc = SteeringWheelControls(device_path=flag('--evdev-device'))
        swc.start()
        started['evdev'] = swc
        log.info('[Hardware] Steering-wheel controls (evdev) active')

    return started

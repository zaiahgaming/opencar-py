# OpenCar

> Multi-surface Automotive UI — Python · Raylib · CAN · OBD-II · GPIO · Comma 3/3X

---

## Table of Contents

1. [Quick Start (Simulation)](#quick-start)
2. [Command-Line Options](#command-line-options)
3. [Config File](#config-file-opencarconf)
4. [Keyboard Shortcuts](#keyboard-shortcuts)
5. [CAN Bus — CANable USB](#can-bus--canable-usb)
6. [OBD-II — ELM327](#obd-ii--elm327)
7. [GPIO Buttons — Raspberry Pi](#gpio-buttons--raspberry-pi)
8. [Comma 3/3X — openpilot](#comma-33x--openpilot)
9. [GPS Integration](#gps-integration)
10. [Steering Wheel Controls](#steering-wheel-controls)
11. [Auto-start with systemd](#auto-start-with-systemd)
12. [Hardware Detection](#hardware-detection)
13. [Installing Dependencies](#installing-dependencies)

---

## Quick Start

```bash
git clone https://github.com/yourname/opencar-py
cd opencar-py
pip install -r requirements.txt
python3 main.py               # simulation mode
```

---

## Command-Line Options

| Flag | Default | Description |
|---|---|---|
| `--fullscreen` | off | Fullscreen mode (use on car display) |
| `--car` | `toyota` | Vehicle profile: `toyota` / `honda` / `gm` / `ford` |
| `--can` | off | Enable real CAN bus (requires adapter) |
| `--can-channel` | auto | CAN interface name, e.g. `can0` |
| `--can-bus` | `socketcan` | python-can bus type |
| `--obd` | off | Enable OBD-II via ELM327 |
| `--obd-port` | auto | Serial port, e.g. `/dev/ttyUSB0` |
| `--replay` | — | Replay a `candump` log file |
| `--gpio` | off | Enable GPIO hardware buttons (RPi) |
| `--surface` | `0` | Start surface: `0`=HUD `1`=Info `2`=Rear |
| `--width` | `1280` | Window width in pixels |
| `--height` | `480` | Window height in pixels |
| `--detect` | off | Detect hardware and print JSON, then exit |

---

## Config File (`opencar.conf`)

Settings not supplied by CLI flags are read from `opencar.conf` in the project root.
**CLI flags always win.**

```ini
[display]
width      = 1280
height     = 480
fullscreen = false
fps        = 60

[vehicle]
profile    = toyota

[data]
mode         = simulation   ; simulation / can / obd
can_channel  = can0
can_bustype  = socketcan
obd_port     = auto

[ui]
theme           = dark
default_surface = 0         ; 0=HUD  1=Infotainment  2=Rear
units           = mph

[gpio]
enabled   = false
pin_hud   = 17
pin_info  = 27
pin_rear  = 22
pin_theme = 23
```

---

## Keyboard Shortcuts

| Key | Action |
|---|---|
| `1` | Switch to HUD surface |
| `2` | Switch to Infotainment surface |
| `3` | Switch to Rear Entertainment surface |
| `T` | Toggle Dark / Light theme |
| `Q` | Quit |

Surface-specific keys are handled by each surface module.

---

## CAN Bus — CANable USB

### Hardware

- [CANable](https://canable.io/) USB-CAN adapter (or any socketcan-compatible device)
- USB cable to car OBD-II CAN tap or direct harness connector

### Setup

```bash
# Install candlelight firmware on CANable (one-time)
# Then bring up the interface:
sudo ip link set can0 type can bitrate 500000
sudo ip link set can0 up

# Verify
ip -details link show can0
```

### Run

```bash
python3 main.py --can --car toyota
# Or specify channel explicitly:
python3 main.py --can --can-channel can0 --car honda
```

### Replay a candump log

```bash
candump can0 -l          # capture  → candump-2024-...log
python3 main.py --replay candump-2024-01-01.log --car toyota
```

---

## OBD-II — ELM327

### Hardware

- ELM327 USB or Bluetooth adapter plugged into the OBD-II port (under the dash)

### Setup

```bash
pip install obd
# USB: adapter appears as /dev/ttyUSB0
# Bluetooth: pair first, then:
sudo rfcomm bind 0 AA:BB:CC:DD:EE:FF
# adapter → /dev/rfcomm0
```

### Run

```bash
python3 main.py --obd                         # auto-detect port
python3 main.py --obd --obd-port /dev/ttyUSB0 # explicit port
```

---

## GPIO Buttons — Raspberry Pi

### Wiring (BCM pin numbering)

```
Raspberry Pi GPIO header (40-pin)
─────────────────────────────────────────────────────────────────
 3.3V ──── [Button GND side]
 GND  ──── common ground

 BCM 17  (Pin 11) ────[BTN]──── GND   → Surface 0 (HUD)
 BCM 27  (Pin 13) ────[BTN]──── GND   → Surface 1 (Infotainment)
 BCM 22  (Pin 15) ────[BTN]──── GND   → Surface 2 (Rear)
 BCM 23  (Pin 16) ────[BTN]──── GND   → Toggle Theme

 All inputs use internal pull-ups (active LOW).
─────────────────────────────────────────────────────────────────
```

### ASCII Wiring Diagram

```
RPi GPIO                  Buttons (momentary N.O.)
──────────                ────────────────────────
Pin 11 (BCM17)  ──────────[ HUD  btn ]──── GND
Pin 13 (BCM27)  ──────────[ INFO btn ]──── GND
Pin 15 (BCM22)  ──────────[ REAR btn ]──── GND
Pin 16 (BCM23)  ──────────[THEME btn ]──── GND
Pin  6 (GND)    ──────────────────────────┘
```

### Setup

```bash
pip install RPi.GPIO       # or: pip install gpiozero
python3 main.py --gpio
```

Pin assignments can be changed in `opencar.conf` under `[gpio]`.

---

## Comma 3/3X — openpilot

OpenCar auto-detects a Comma device at startup by checking for
openpilot's shared-memory sockets.

### Installation steps

1. Install [openpilot](https://github.com/commaai/openpilot) on the Comma 3/3X.
2. SSH into the device:
   ```bash
   ssh comma@192.168.x.x
   ```
3. Clone OpenCar into `/data/`:
   ```bash
   cd /data && git clone https://github.com/yourname/opencar-py
   ```
4. Install Python deps:
   ```bash
   pip3 install pyray
   ```
5. Run:
   ```bash
   cd /data/opencar-py
   python3 main.py --fullscreen --car toyota
   ```

OpenCar subscribes to `carState`, `radarState`, and `liveLocationKalman`
from openpilot's cereal msgq — no modifications to openpilot required.

---

## GPS Integration

OpenCar reads from [gpsd](https://gpsd.gitlab.io/gpsd/) when available.

```bash
# Install gpsd
sudo apt install gpsd gpsd-clients
pip install gpsd-py3

# Plug in USB GPS dongle, then:
sudo gpsd /dev/ttyACM0 -F /var/run/gpsd.sock

# OpenCar will auto-connect on startup
python3 main.py
```

GPS data populates `STATE.gps_lat`, `STATE.gps_lon`, and `STATE.gps_speed_mph`.

---

## Steering Wheel Controls

OpenCar uses `evdev` to monitor HID steering-wheel buttons on Linux.
No configuration required — it auto-detects the first input device
that reports media keys.

```bash
pip install evdev
```

Mapped keys:

| Kernel key | OpenCar action |
|---|---|
| `KEY_NEXTSONG` | Next track |
| `KEY_PREVIOUSSONG` | Previous track |
| `KEY_PLAYPAUSE` | Play / Pause |
| `KEY_VOLUMEUP` | Volume up |
| `KEY_VOLUMEDOWN` | Volume down |
| `KEY_MUTE` | Mute |

---

## Auto-start with systemd

Create `/etc/systemd/system/opencar.service`:

```ini
[Unit]
Description=OpenCar Automotive UI
After=network.target graphical.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/opencar-py
Environment=DISPLAY=:0
ExecStart=/usr/bin/python3 /home/pi/opencar-py/main.py --fullscreen --car toyota
Restart=on-failure
RestartSec=5

[Install]
WantedBy=graphical.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable opencar
sudo systemctl start opencar
sudo journalctl -u opencar -f   # follow logs
```

---

## Hardware Detection

Run the detector without launching the UI:

```bash
python3 main.py --detect
```

Example output:

```json
{
  "can": true,
  "obd": false,
  "gps": false,
  "gpio": false,
  "evdev": true,
  "comma": false,
  "platform": "Linux 6.1.0 (x86_64)",
  "can_channels": ["can0"]
}
```

---

## Installing Dependencies

```bash
# Core (required)
pip install pyray

# CAN bus
pip install python-can

# OBD-II
pip install obd

# GPS
sudo apt install gpsd
pip install gpsd-py3

# Steering-wheel / evdev
pip install evdev

# Raspberry Pi GPIO
pip install RPi.GPIO
# or:
pip install gpiozero
```

All optional dependencies degrade gracefully — OpenCar falls back to
simulation mode if none are available.

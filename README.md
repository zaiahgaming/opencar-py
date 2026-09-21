# OpenCar

> **Modern Multi-Surface Automotive UI**  
> Python · Raylib · Comma 4 Card Aesthetic · commaai/opendbc · CAN Bus · OBD-II · Android Head Units · Comma 3/3X

[![GitHub Repo](https://img.shields.io/badge/GitHub-zaiahgaming%2Fopencar--py-181717?logo=github)](https://github.com/zaiahgaming/opencar-py)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10%2B-brightgreen.svg)](https://python.org)
[![commaai/opendbc](https://img.shields.io/badge/DBC-commaai%2Fopendbc-black.svg)](https://github.com/commaai/opendbc)

---

OpenCar is a GPU-accelerated automotive dashboard and infotainment suite inspired by the **comma 4 visual design language** (pure black `#000000`, dark rounded cards `#292929`, Inter typography, active green `#33ab4c`, accent blue `#465bea`, and real high-res Lucide icons).

It features three complete independent surfaces with full touchscreen and keyboard navigation:
1. **Instrument Cluster / HUD**: Speedometer (140px bold), tachometer with dynamic color sweep, live road perspective, directional turn indicators, drive mode selector (ECO / NORMAL / SPORT), trip stats, and real-time clock.
2. **Infotainment Center**: 6-slot icon dock, 2x2 home cards, full-screen music player with real album art & scrubber, dual-zone climate control with tactile `+` / `−` adjustments, contact list, and vehicle settings.
3. **Rear Seat Entertainment**: Pill tab bar, trip progress, media player, rear dual climate, and interactive playable Pong.

---

## Architecture & Data Sources

OpenCar connects to real vehicles through multiple automotive data pipelines:

```
                  ┌───────────────────────────────────────────────┐
                  │                   OpenCar                     │
                  │   [HUD]        [Infotainment]         [Rear]  │
                  └───────▲───────────────▲───────────────▲───────┘
                          │               │               │
                 ┌────────┴───────────────┴───────────────┴────────┐
                 │                 VehicleState                    │
                 └───────▲────────────────▲───────────────▲────────┘
                         │                │               │
       ┌─────────────────┴────────┐ ┌─────┴───────┐ ┌─────┴──────────────────┐
       │   commaai/opendbc CAN    │ │   OBD-II    │ │    Openpilot Cereal    │
       │  (SocketCAN / CANable)   │ │  (ELM327)   │ │      (Comma 3/3X)      │
       │                          │ │             │ │                        │
       │ • 60+ vehicle DBC models │ │ • USB Serial│ │ • Native carState      │
       │ • Toyota, Honda, GM, VW  │ │ • Bluetooth │ │ • radarState lead car  │
       │ • ISO 15765-4 OBD-on-CAN │ │ • WiFi (TCP)│ │ • GPS Kalman filter    │
       └──────────────────────────┘ └─────────────┘ └────────────────────────┘
```

---

## Quick Start

```bash
git clone https://github.com/zaiahgaming/opencar-py.git
cd opencar-py
pip install -r requirements.txt

# Run simulation mode
python3 main.py --surface 1 --width 1920 --height 720
```

---

## Real Vehicle & Hardware Setups

### 1. Real CAN Bus & commaai/opendbc Setup
Connect via USB CANable (gs_usb), Waveshare CAN HAT, or PEAK PCAN to the OBD-II port (pins 6 & 14) or internal vehicle CAN bus.

```bash
# Configure socketcan interface at 500 kbps
sudo bash scripts/setup_can.sh can0 500000

# Launch with opendbc vehicle profile (Toyota, Honda, Ford, GM, VW, etc.):
python3 main.py --can --can-channel can0 --car toyota
python3 main.py --can --can-channel can0 --car honda
python3 main.py --can --can-channel can0 --car vw

# Or specify any exact opendbc DBC:
python3 main.py --can --can-channel can0 --dbc toyota_2017_ref_pt
python3 main.py --can --can-channel can0 --dbc vw_mqb
```

> **Universal OBD-2 Port Support**: If your vehicle gateway isolates broadcast CAN messages on the diagnostic port, OpenCar automatically transmits **ISO 15765-4 OBD-II requests (0x7DF)** over CAN to query Speed, RPM, Coolant Temp, and Fuel directly from the engine ECU!

📖 *Full details:* [docs/CAN_BUS_SETUP.md](docs/CAN_BUS_SETUP.md)

---

### 2. OBD-II Setup (ELM327 USB, Bluetooth, WiFi)
Plug any standard ELM327, OBDLink SX/LX/MX+, or vLinker into your car's OBD-II port.

```bash
# Auto-detect USB or Bluetooth adapter
python3 main.py --obd

# USB serial adapter at 38400 or 115200 baud
python3 main.py --obd --obd-port /dev/ttyUSB0 --obd-baud 38400

# Bluetooth OBD-II scanner
python3 main.py --obd --obd-port /dev/rfcomm0

# WiFi OBD-II scanner
python3 main.py --obd --obd-port 192.168.0.10:35000
```

📖 *Full details:* [docs/OBD2_SETUP.md](docs/OBD2_SETUP.md)

---

### 3. Aftermarket Android Head Unit Display
OpenCar is fully compatible with Android car head units (Allwinner, Rockchip, Unisoc) and in-dash touchscreens.

- **1-Click Termux Setup**:
  ```bash
  git clone https://github.com/zaiahgaming/opencar-py.git
  cd opencar-py
  bash scripts/setup_android.sh
  ```
- **Touchscreen First**: Tap dock icons to switch apps, tap Home cards, drag the music scrubber, and adjust dual-zone climate with `+` / `−` touch targets.
- **Frameless Kiosk Display**: Use `--kiosk` to remove desktop window chrome and fill the screen cleanly.

📖 *Full details:* [docs/ANDROID_HEAD_UNIT.md](docs/ANDROID_HEAD_UNIT.md)

---

## Command-Line Options

| Flag | Default | Description |
|---|---|---|
| `--fullscreen` | off | Fullscreen display mode |
| `--kiosk`, `--no-frame` | off | Borderless kiosk window without OS title bar |
| `--surface` | `0` | Default surface: `0`=HUD, `1`=Infotainment, `2`=Rear |
| `--car` | `toyota` | Vehicle profile: `toyota`, `honda`, `gm`, `ford`, `vw`, `hyundai`, `tesla`, `bmw` |
| `--dbc` | auto | Specific opendbc DBC file (e.g. `toyota_2017_ref_pt`, `vw_mqb`) |
| `--can` | off | Enable real CAN bus reader |
| `--can-channel` | auto | CAN interface name (e.g. `can0`, `slcan0`, `vcan0`) |
| `--can-bus` | `socketcan` | python-can bus type (`socketcan`, `slcan`, `pcan`) |
| `--obd` | off | Enable OBD-II mode |
| `--obd-port` | auto | Serial device (`/dev/ttyUSB0`, `/dev/rfcomm0`) or WiFi (`192.168.0.10:35000`) |
| `--obd-baud` | `38400` | Serial baud rate for ELM327 / STN adapters |
| `--replay` | — | Replay a candump log file in real-time |
| `--width` | `1280` | Window width (e.g. `1024`, `1280`, `1920`) |
| `--height` | `480` | Window height (e.g. `600`, `720`, `1080`) |
| `--detect` | off | Probe connected automotive hardware and exit |

---

## Controls & Keybindings

| Key / Action | Destination | Action |
|---|---|---|
| **Touch / Tap** | All Surfaces | Tap sidebar icons, cards, transport buttons, temperature `+` / `−`, and Pong paddle |
| `1` | All | Switch to **Instrument Cluster / HUD** |
| `2` | All | Switch to **Infotainment System** |
| `3` | All | Switch to **Rear Entertainment** |
| `T` | All | Toggle Dark / Light theme |
| `H` | Infotainment | Jump to Home |
| `M` | Infotainment | Jump to Music |
| `C` | Infotainment | Jump to Climate |
| `Space` | Music / Rear | Play / Pause track |
| `Left / Right` | HUD | Toggle Left / Right Turn Signals |
| `Q` | All | Exit application |

---

## License

MIT License. Designed for automotive enthusiasts, builders, and comma.ai openpilot hackers.

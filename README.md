# OpenCar

> **Modern Multi-Surface Automotive Cockpit & Infotainment Suite**  
> Web Cockpit (React + Tailwind + Leaflet) · Python Telemetry Bridge · Comma 4 Card Deck · Tesla Model 3 Digital Twin · commaai/opendbc · CAN Bus & OBD-II · Android Aftermarket Displays

[![GitHub Repo](https://img.shields.io/badge/GitHub-zaiahgaming%2Fopencar--py-181717?logo=github)](https://github.com/zaiahgaming/opencar-py)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10%2B-brightgreen.svg)](https://python.org)
[![Vite 5](https://img.shields.io/badge/Vite-5.4-purple.svg)](https://vitejs.dev)
[![React: 18](https://img.shields.io/badge/React-18-blue.svg)](https://react.dev)
[![commaai/opendbc](https://img.shields.io/badge/DBC-commaai%2Fopendbc-black.svg)](https://github.com/commaai/opendbc)

---

OpenCar is a production-grade automotive cockpit that bridges real-time vehicle CAN bus & OBD-II diagnostics directly into a responsive, hardware-accelerated user interface.

It features four primary surfaces:
1. **Instrument Cluster / Comma 3X Onroad HUD**: 3D vision road perspective with openpilot animated spline corridor, dashed lane stripes, 42m lead car radar tracking, `MAX 65 MPH` cruise capsule, bold speed readout, MUTCD `SPEED LIMIT 65` shield, lateral actuator torque gauge, coolant & tachometer readouts, and Euro NCAP attentiveness monitor.
2. **Tesla Model 3/Y V12 Infotainment Touchscreen**: Clean isometric 3D vehicle digital twin with interactive frunk/trunk/lock triggers, 4-corner TPMS tire pressure monitoring capsules, interactive dark Leaflet map with active GPS routing, floating Comma 4 Bluetooth connected card (with checkmark and circular crimson disconnect button), and a full slide-up dual-zone climate control drawer.
3. **Rear Passenger Entertainment Display**: Highland-inspired 8-inch rear interface with independent rear climate adjustment, passenger trip progress monitor, Spotify mini-player, and interactive Retro Pong arcade cabinet.
4. **Split Cockpit Mode**: Dual-pane ultrawide layout placing the driver cluster on the left and full infotainment on the right with zero speedometer occlusion.

---

## Quick Start (Web Automotive Cockpit)

The Web Cockpit runs natively on Linux and on any aftermarket Android head unit or tablet over WiFi/hotspot:

```bash
git clone https://github.com/zaiahgaming/opencar-py.git
cd opencar-py
pip install -r requirements.txt

# Launch OpenCar Web Server and open fullscreen browser
python3 run_web.py --kiosk

# Or run headless on a car computer (Raspberry Pi / Jetson / mini PC)
python3 run_web.py --no-browser --port 3000
# Then navigate to http://<CAR_IP>:3000 on your Android dashboard display!
```

To run the native Raylib/PyRay desktop client:
```bash
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

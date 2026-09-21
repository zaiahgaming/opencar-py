# OpenCar on Aftermarket Android Head Units

OpenCar is engineered to run on aftermarket Android car head units (Allwinner T3/T5, Rockchip PX5/PX6, Unisoc UIS7862, MTK) and in-dash touchscreens.

---

## 1. Supported Head Unit Form Factors & Resolutions

OpenCar supports standard in-dash aspect ratios with auto-scaling:
- **7" Double-DIN**: `1024x600`
- **9" / 10.1" Floating Head Units**: `1280x720`
- **Ultrawide Dash Screens (BMW/Mercedes/Audi retrofit)**: `1920x720`
- **Standard HD Displays**: `1920x1080`
- **Narrow Instrument Displays**: `1280x480`

Use `--kiosk` (or `--no-frame`) for a clean, borderless display that fills the screen without desktop window chrome.

---

## 2. Running Directly on Android via Termux + Termux:X11

Termux provides a complete Linux userspace on Android without requiring root access.

### Installation Steps:
1. Install **Termux** and **Termux:X11** APKs from F-Droid or GitHub.
2. Open Termux on your head unit and run:
   ```bash
   git clone https://github.com/zaiahgaming/opencar-py.git
   cd opencar-py
   bash scripts/setup_android.sh
   ```
3. Launch OpenCar with one touch:
   ```bash
   ~/launch_opencar.sh
   ```

---

## 3. Touchscreen Interaction Guide

OpenCar features full capacitive touch support designed for in-car use:

### Infotainment Screen:
- **Sidebar Dock (Left)**: Tap any of the 6 icons (`Home`, `Nav`, `Music`, `Climate`, `Phone`, `Settings`) to switch apps instantly.
- **Home 2x2 Grid**: Tap the **Now Playing card** to jump directly to Music, tap **Navigation** for GPS/Map, tap **Climate** for Temperature controls, or tap **Vehicle** for Settings.
- **Music Player**:
  - Tap **Play / Pause** circular button to toggle playback.
  - Tap **Previous / Next** to skip tracks.
  - Touch or drag anywhere along the **progress bar** to scrub track position.
- **Dual-Zone Climate**:
  - Tap the **`+`** or **`−`** circle buttons on the Driver or Passenger cards to adjust cabin temperatures.
  - Tap **A/C**, **HEAT**, **DEF**, or **SYNC** pills to toggle modes.

### HUD / Instrument Cluster:
- **Turn Signals**: Tap the green **`◀`** or **`▶`** chevron arrows in the top cluster to toggle left/right blinkers.
- **Drive Modes**: Tap **ECO**, **NORMAL**, or **SPORT** in the bottom dock to switch drive profiles.

### Rear Seat Entertainment:
- **Tab Bar**: Tap any top tab pill (`Home`, `Video`, `Music`, `Pong`, `Trip`, `Climate`).
- **Touch Pong**: Drag your finger on the left side of the screen to move the player paddle!

---

## 4. Hardware Connection to the Android Head Unit

- **USB OBD-II**: Plug your ELM327 USB or OBDLink SX into the head unit's rear USB OTG port. Android recognizes it as `/dev/ttyUSB0` or `/dev/ttyACM0`.
- **Bluetooth OBD-II**: Pair your Bluetooth scanner (e.g. OBDLink LX, Veepeak) in Android Bluetooth settings.
- **WiFi OBD-II**: Connect the head unit's WiFi to the OBD-II scanner's hotspot (`192.168.0.10:35000`).
- **CANable USB**: Connect CANable in gs_usb / socketcan mode to read live CAN traffic directly.

---

## 5. Auto-Launch on Car Ignition / Boot

To start OpenCar automatically whenever the car starts:
1. Install an automation app such as **Tasker** or **MacroDroid** on your Android head unit.
2. Create a trigger: `Device Boot` or `Power Connected (Ignition ON)`.
3. Action: Run Termux command `~/launch_opencar.sh`.

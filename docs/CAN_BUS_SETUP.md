# OpenCar CAN Bus & commaai/opendbc Setup Guide

This guide explains how to connect OpenCar to a real vehicle CAN bus or OBD-II port, utilizing **[commaai/opendbc](https://github.com/commaai/opendbc)** for decoding.

---

## 1. Physical Hardware Options

### A. USB-to-CAN Adapters (Recommended)
- **CANable / CANable Pro v2** (running Candlelight / gs_usb firmware): Supported natively by Linux SocketCAN without extra drivers.
- **PEAK-System PCAN-USB**: High-reliability industrial adapter.
- **Innomaker USB2CAN**: Plug-and-play USB CAN dongle.

### B. Raspberry Pi / SBC CAN HATs
- **Waveshare RS485/CAN HAT** (SPI MCP2515)
- **PiCAN 2 / PiCAN 3**

### C. Comma 3 / 3X Devices
- If running on a Comma 3/3X device with openpilot installed, OpenCar automatically detects openpilot's cereal messaging queue (`/dev/shm/ubloxGnss`, `/data/openpilot`).

---

## 2. Wiring to the Vehicle

### Standard OBD-II Port Connection (Pins 6 & 14)
Most vehicles (2008+) provide standard High-Speed CAN on the OBD-II diagnostic port:
```
         1   2   3   4   5   6   7   8
       ┌───┬───┬───┬───┬───┬───┬───┬───┐
       │   │   │   │GND│GND│CAN│   │   │
       └───┴───┴───┴───┴───┴───┴───┴───┘
       ┌───┬───┬───┬───┬───┬───┬───┬───┐
       │   │   │   │   │   │CAN│   │+12│
       └───┴───┴───┴───┴───┴───┴───┴───┘
         9  10  11  12  13  14  15  16
```
- **Pin 6**: CAN High (`CAN_H`)
- **Pin 14**: CAN Low (`CAN_L`)
- **Pin 4 or 5**: Chassis / Signal Ground (`GND`)
- **Pin 16**: Battery Power (`+12V` constant)

> **Note on Vehicle Gateways**: Many modern cars (2015+) have a Central Gateway that isolates the OBD-II port from the internal powertrain bus. OpenCar automatically handles this by transmitting periodic standard **ISO 15765-4 OBD-II requests (0x7DF)** over CAN to query Speed, RPM, Coolant Temp, and Fuel Level directly from the engine ECU!

### Direct Powertrain / Chassis Bus Tap
To receive full telemetry, steering angles, radar leads, and wheel speeds, you can tap directly into the vehicle's powertrain CAN bus (often accessible behind the instrument cluster, camera harness, or CAN gateway block).

---

## 3. Configuring SocketCAN on Linux

Use the provided setup script:
```bash
sudo bash scripts/setup_can.sh can0 500000
```

Or configure manually:
```bash
# 1. Bring interface down
sudo ip link set can0 down

# 2. Set bitrate (500 kbps is standard for automotive powertrain)
sudo ip link set can0 type can bitrate 500000

# 3. Bring interface up
sudo ip link set can0 up
```

---

## 4. Decoding with commaai/opendbc

OpenCar integrates directly with **commaai/opendbc** to decode real manufacturer signals.

### Launching OpenCar with opendbc:
```bash
# Launch with vehicle make preset (loads standard DBC automatically):
python3 main.py --can --can-channel can0 --car toyota
python3 main.py --can --can-channel can0 --car honda
python3 main.py --can --can-channel can0 --car ford
python3 main.py --can --can-channel can0 --car gm
python3 main.py --can --can-channel can0 --car hyundai
python3 main.py --can --can-channel can0 --car vw

# Or specify any exact opendbc DBC name:
python3 main.py --can --can-channel can0 --dbc toyota_2017_ref_pt
python3 main.py --can --can-channel can0 --dbc vw_mqb
python3 main.py --can --can-channel can0 --dbc ford_fusion_2018_pt
python3 main.py --can --can-channel can0 --dbc bmw_e9x_e8x
```

### Supported opendbc Profiles Include:
- **Toyota**: `toyota_prius_2010_pt`, `toyota_2017_ref_pt`, `toyota_tss2_adas`
- **Honda / Acura**: `acura_ilx_2016_nidec`
- **Ford**: `ford_fusion_2018_pt`, `ford_cgea1_2_ptcan_2011`
- **GM / Cadillac**: `gm_global_a_chassis`, `cadillac_ct6_powertrain`
- **Hyundai / Kia / Genesis**: `hyundai_kia_generic`, `hyundai_2015_ccan`
- **Volkswagen / Audi / Skoda**: `vw_mqb`, `vw_pq`, `vw_meb`
- **Tesla**: `tesla_can`, `tesla_powertrain`
- **BMW**: `bmw_e9x_e8x`
- **Mazda**: `mazda_2017`, `mazda_3_2019`
- **Nissan**: `nissan_xterra_2011`
- **Chrysler / Dodge / Jeep**: `chrysler_cusw`

# OpenCar OBD-II Setup Guide

OpenCar features a unified OBD-II engine supporting USB, Bluetooth, and WiFi ELM327 / STN-based adapters.

---

## 1. Supported Adapters

1. **USB Serial Adapters**:
   - OBDLink SX / EX (STN1110 / STN2120)
   - Standard ELM327 USB cables (FTDI, CH340, CP2102 chips)
   - Typically detected at `/dev/ttyUSB0` or `/dev/ttyACM0`

2. **Bluetooth Adapters**:
   - OBDLink LX / MX+
   - Veepeak OBDCheck BLE / vLinker FD+
   - BAFX Products Bluetooth OBD Reader
   - Bound to `/dev/rfcomm0`

3. **WiFi Adapters**:
   - Standard ELM327 WiFi scanners
   - Connect via local TCP socket (default: `192.168.0.10:35000`)

---

## 2. Linux Setup & Permissions

Run the helper script to scan adapters and fix permissions:
```bash
sudo bash scripts/setup_obd.sh
```

### Pairing a Bluetooth OBD-II Scanner:
```bash
# 1. Scan for nearby Bluetooth devices
bluetoothctl scan on

# 2. Pair with your adapter MAC address (e.g. 00:1D:A5:68:98:8B)
bluetoothctl pair 00:1D:A5:68:98:8B
# (Enter PIN 1234 or 0000 when prompted)

# 3. Bind to an RFCOMM serial port:
sudo rfcomm bind 0 00:1D:A5:68:98:8B
```

---

## 3. Launching OpenCar in OBD-II Mode

### Auto-Detection (Scans USB and RFCOMM ports):
```bash
python3 main.py --obd
```

### Explicit Serial Port:
```bash
# USB adapter at 38400 baud
python3 main.py --obd --obd-port /dev/ttyUSB0 --obd-baud 38400

# High-speed OBDLink at 115200 or 500000 baud
python3 main.py --obd --obd-port /dev/ttyUSB0 --obd-baud 115200

# Bluetooth adapter
python3 main.py --obd --obd-port /dev/rfcomm0
```

### WiFi OBD-II Adapter:
```bash
python3 main.py --obd --obd-port 192.168.0.10:35000
```

---

## 4. Live PIDs Queried

OpenCar continuously polls the following standard SAE Mode 01 PIDs:
- **010C**: Engine RPM (scaled `/ 4.0`)
- **010D**: Vehicle Speed (km/h converted to mph)
- **0105**: Engine Coolant Temperature (°C converted to °F)
- **0111**: Throttle Position Percentage
- **012F**: Fuel Tank Level Percentage
- **ATRV**: Real-time 12V Battery / Alternator Voltage

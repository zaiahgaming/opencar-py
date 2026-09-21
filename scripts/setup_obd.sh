#!/usr/bin/env bash
# scripts/setup_obd.sh — Configure OBD-II adapters for OpenCar
# Supports: USB ELM327 (/dev/ttyUSB0), Bluetooth (/dev/rfcomm0), WiFi OBD2

PORT="${1:-auto}"
BAUD="${2:-38400}"

echo "========================================================"
echo " OpenCar OBD-II Setup & Diagnostics Utility"
echo "========================================================"

# Check for USB serial OBD adapters
echo "[*] Scanning for connected USB OBD-II adapters..."
USB_PORTS=$(ls /dev/ttyUSB* /dev/ttyACM* 2>/dev/null || true)
if [ -n "$USB_PORTS" ]; then
  echo "[+] Detected USB OBD adapter(s): $USB_PORTS"
  for p in $USB_PORTS; do
    echo "    Fixing permissions on $p..."
    sudo chmod 666 "$p" 2>/dev/null || true
  done
else
  echo "[-] No USB serial adapters detected in /dev/ttyUSB* or /dev/ttyACM*"
fi

# Check for Bluetooth OBD adapters
echo "[*] Checking for Bluetooth OBD-II devices (/dev/rfcomm*)..."
BT_PORTS=$(ls /dev/rfcomm* 2>/dev/null || true)
if [ -n "$BT_PORTS" ]; then
  echo "[+] Detected Bluetooth OBD adapter: $BT_PORTS"
  sudo chmod 666 $BT_PORTS 2>/dev/null || true
else
  echo "[i] To bind a Bluetooth OBD-II scanner (e.g. MAC 00:1D:A5:68:98:8B):"
  echo "    sudo rfcomm bind 0 00:1D:A5:68:98:8B"
fi

echo ""
echo "OpenCar OBD Launch Examples:"
echo "  1) Auto-detect USB/Bluetooth adapter:"
echo "     python3 main.py --obd"
echo ""
echo "  2) Specify USB port explicitly:"
echo "     python3 main.py --obd --obd-port /dev/ttyUSB0 --obd-baud 38400"
echo ""
echo "  3) Bluetooth OBD-II scanner:"
echo "     python3 main.py --obd --obd-port /dev/rfcomm0 --obd-baud 38400"
echo ""
echo "  4) WiFi OBD-II scanner (ELM327 WiFi):"
echo "     python3 main.py --obd --obd-port 192.168.0.10:35000"

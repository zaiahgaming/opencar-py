#!/usr/bin/env bash
# scripts/setup_can.sh — Configure CAN bus interfaces for OpenCar
# Supports: SocketCAN (can0), CANable / Candlelight (slcan0), and Virtual CAN (vcan0)

set -e

CHANNEL="${1:-can0}"
BITRATE="${2:-500000}"

echo "========================================================"
echo " OpenCar CAN Bus Setup Utility"
echo " Channel: $CHANNEL | Bitrate: $BITRATE bps"
echo "========================================================"

if [ "$EUID" -ne 0 ]; then
  echo "[-] Please run as root (sudo bash scripts/setup_can.sh [channel] [bitrate])"
  exit 1
fi

# Load kernel modules
echo "[*] Loading kernel CAN modules (can, can_raw, vcan, slcan)..."
modprobe can 2>/dev/null || true
modprobe can_raw 2>/dev/null || true
modprobe vcan 2>/dev/null || true
modprobe slcan 2>/dev/null || true

# Check if setting up virtual CAN
if [[ "$CHANNEL" == vcan* ]]; then
  echo "[*] Creating Virtual CAN interface: $CHANNEL..."
  ip link add dev "$CHANNEL" type vcan 2>/dev/null || true
  ip link set up "$CHANNEL"
  echo "[+] Virtual CAN interface $CHANNEL is UP!"
  echo "    Test with: python3 main.py --can --can-channel $CHANNEL"
  exit 0
fi

# Check for CANable in SLCAN mode (e.g. /dev/ttyACM0)
if [ -e "/dev/ttyACM0" ] && [[ "$CHANNEL" == slcan* ]]; then
  echo "[*] Attaching USB SLCAN adapter on /dev/ttyACM0 -> $CHANNEL..."
  slcand -o -c -s6 /dev/ttyACM0 "$CHANNEL"
  sleep 1
  ip link set up "$CHANNEL"
  echo "[+] SLCAN interface $CHANNEL is UP!"
  exit 0
fi

# Standard SocketCAN interface (native CAN or CANable in gs_usb mode)
echo "[*] Configuring $CHANNEL at $BITRATE bps..."
ip link set "$CHANNEL" down 2>/dev/null || true
ip link set "$CHANNEL" type can bitrate "$BITRATE"
ip link set "$CHANNEL" up

echo "[+] CAN interface $CHANNEL is now active!"
ip -details link show "$CHANNEL"
echo ""
echo "To launch OpenCar with this CAN interface:"
echo "  python3 main.py --can --can-channel $CHANNEL --car toyota"
echo "  python3 main.py --can --can-channel $CHANNEL --dbc toyota_2017_ref_pt"

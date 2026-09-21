#!/usr/bin/env bash
# scripts/setup_android.sh — Install & Configure OpenCar on Android Head Units
# Uses Termux + Termux:X11 for full native GPU-accelerated touch display

set -e

echo "========================================================"
echo " OpenCar Android Head Unit Setup Utility"
echo " Target: Aftermarket Android Display (Termux Environment)"
echo "========================================================"

if ! command -v pkg &> /dev/null; then
  echo "[!] Note: This script is intended to run inside Termux on your Android Head Unit."
  echo "    See docs/ANDROID_HEAD_UNIT.md for full step-by-step instructions."
fi

echo "[1/4] Updating package repositories..."
pkg update -y || true

echo "[2/4] Installing Python, Clang, X11, and build tools..."
pkg install -y python clang libxml2 libxslt libjpeg-turbo git x11-repo || true
pkg install -y termux-x11-nightly || true

echo "[3/4] Installing Python dependencies (Raylib, opendbc, python-can)..."
pip install --upgrade pip setuptools wheel
pip install raylib opendbc python-can pyserial

echo "[4/4] Creating Head Unit Launch Script (~/launch_opencar.sh)..."
cat << 'EOF' > "$HOME/launch_opencar.sh"
#!/usr/bin/env bash
# Start Termux:X11 display server in background
termux-x11 :0 -ac &
sleep 2

# Auto-detect screen resolution of Android head unit
SCREEN_RES=$(dumpsys window | grep cur= | head -1 | grep -o '[0-9]*x[0-9]*' || echo "1280x720")
WIDTH=$(echo "$SCREEN_RES" | cut -d'x' -f1)
HEIGHT=$(echo "$SCREEN_RES" | cut -d'x' -f2)

export DISPLAY=:0
cd "$HOME/opencar-py" || cd "$HOME"

echo "[OpenCar] Launching on Android Head Unit (${WIDTH}x${HEIGHT})..."
# Default to Infotainment surface (surface 1) with kiosk borderless touch mode
python3 main.py --surface 1 --width "$WIDTH" --height "$HEIGHT" --kiosk --obd "$@"
EOF

chmod +x "$HOME/launch_opencar.sh" 2>/dev/null || true
chmod +x scripts/setup_android.sh 2>/dev/null || true

echo "========================================================"
echo "[+] Android Head Unit Setup Complete!"
echo "    Launch OpenCar anytime by running: ~/launch_opencar.sh"
echo "========================================================"

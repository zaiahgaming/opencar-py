#!/bin/bash

echo "Checking dependencies..."
if ! command -v python3 &> /dev/null; then
    echo "python3 is required but not installed."
    exit 1
fi

if ! python3 -c "import pyray" &> /dev/null; then
    echo "pyray not found. Offering to install..."
    read -p "Install raylib? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        pip3 install raylib
    fi
fi

SURFACE="0"
ARGS=""

for arg in "$@"; do
    case $arg in
        --hud)
        SURFACE="0"
        ;;
        --info)
        SURFACE="1"
        ;;
        --rear)
        SURFACE="2"
        ;;
        *)
        ARGS="$ARGS $arg"
        ;;
    esac
done

echo "╔═══════════════════════════════════════════╗"
echo "║         OpenCar v2.0 — Glass Edition      ║"
echo "║     Next-Gen Automotive Dashboard UI      ║"
echo "╚═══════════════════════════════════════════╝"
echo ""
echo "Keyboard Shortcuts:"
echo "  1/2/3 = Switch surfaces (HUD/Info/Rear)"
echo "  T     = Toggle theme"
echo "  Q     = Quit"
echo "  Surface-specific shortcuts are active"
echo ""
echo "Launching OpenCar in Simulation Mode..."

python3 main.py --surface $SURFACE $ARGS

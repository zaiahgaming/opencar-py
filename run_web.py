#!/usr/bin/env python3
"""
OpenCar Web Launcher
Runs the production web cockpit and telemetry server.
"""

import sys
import time
import argparse
from core.web_server import WebCockpitBridge
from vehicle_state import VehicleState

def main():
    parser = argparse.ArgumentParser(description="OpenCar Digital Cockpit Web Runner")
    parser.add_argument("--kiosk", action="store_true", help="Launch in full-screen borderless kiosk mode")
    parser.add_argument("--no-browser", action="store_true", help="Do not launch local browser")
    parser.add_argument("--port", type=int, default=3000, help="HTTP server port")
    args = parser.parse_args()

    state = VehicleState()
    bridge = WebCockpitBridge(vehicle_state=state, http_port=args.port)
    bridge.start_http()
    bridge.start_ws()

    print(f"\n🚗 OpenCar Web Cockpit is LIVE at http://localhost:{args.port}")
    print(f"📱 Connect any Android aftermarket head unit or tablet to http://<YOUR-IP>:{args.port}\n")

    if not args.no_browser:
        bridge.launch_browser(kiosk=args.kiosk)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping OpenCar...")

if __name__ == "__main__":
    main()

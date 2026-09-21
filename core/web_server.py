"""
OpenCar Web Cockpit Server & Telemetry Bridge
Serves the React/Tailwind automotive UI and streams live CAN/OBD-II vehicle state over WebSockets.
"""

import os
import sys
import json
import asyncio
import logging
import webbrowser
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading

logger = logging.getLogger("opencar.web")

# Paths
WEB_DIST_DIR = Path(__file__).parent.parent / "web" / "dist"

class DistHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB_DIST_DIR), **kwargs)

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-cache")
        super().end_headers()

    def do_GET(self):
        # SPA routing fallback: if file does not exist, serve index.html
        path = self.translate_path(self.path)
        if not os.path.exists(path) and not path.endswith('/'):
            self.path = '/index.html'
        return super().do_GET()


class WebCockpitBridge:
    def __init__(self, vehicle_state=None, host="0.0.0.0", http_port=3000, ws_port=8765):
        self.state = vehicle_state
        self.host = host
        self.http_port = http_port
        self.ws_port = ws_port
        self.http_server = None
        self.ws_server = None
        self.running = False
        self.clients = set()

    def start_http(self):
        if not WEB_DIST_DIR.exists():
            logger.warning(f"Web dist directory not found at {WEB_DIST_DIR}. Building web...")
            os.system(f"cd {WEB_DIST_DIR.parent} && npm run build")

        try:
            self.http_server = HTTPServer((self.host, self.http_port), DistHandler)
            logger.info(f"OpenCar Web UI running at http://{self.host}:{self.http_port}")
            t = threading.Thread(target=self.http_server.serve_forever, daemon=True)
            t.start()
        except Exception as e:
            logger.error(f"Failed to start HTTP server on port {self.http_port}: {e}")

    async def _ws_handler(self, websocket):
        self.clients.add(websocket)
        logger.info(f"New client connected: {websocket.remote_address}")
        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    if self.state:
                        # Handle commands from UI
                        if "gear" in data:
                            self.state.gear = data["gear"]
                        if "driverTemp" in data:
                            self.state.driver_temp = data["driverTemp"]
                        if "isLocked" in data:
                            self.state.doors_locked = data["isLocked"]
                except Exception as e:
                    logger.error(f"Error handling UI message: {e}")
        except Exception:
            pass
        finally:
            self.clients.remove(websocket)

    async def _broadcast_loop(self):
        import websockets
        while self.running:
            if self.clients and self.state:
                telemetry = {
                    "speed": getattr(self.state, "speed_mph", 65),
                    "gear": getattr(self.state, "gear", "D"),
                    "battery": getattr(self.state, "battery_pct", 69),
                    "rpm": getattr(self.state, "rpm", 2400),
                    "coolantTemp": getattr(self.state, "coolant_temp", 192),
                    "leadCarDist": getattr(self.state, "lead_dist_m", 42),
                    "steeringTorque": getattr(self.state, "steering_torque", 0.12),
                    "driverAttentive": getattr(self.state, "driver_attentive", True),
                    "isOpenpilotEngaged": getattr(self.state, "openpilot_engaged", True),
                }
                msg = json.dumps(telemetry)
                await asyncio.gather(*[client.send(msg) for client in self.clients], return_exceptions=True)
            await asyncio.sleep(0.016) # ~60Hz telemetry stream

    def start_ws(self):
        try:
            import websockets
            async def run():
                self.running = True
                async with websockets.serve(self._ws_handler, self.host, self.ws_port):
                    logger.info(f"OpenCar Telemetry WebSocket running on ws://{self.host}:{self.ws_port}")
                    await self._broadcast_loop()

            t = threading.Thread(target=lambda: asyncio.run(run()), daemon=True)
            t.start()
        except ImportError:
            logger.info("websockets module not installed, running in standalone client simulation mode.")

    def launch_browser(self, kiosk=False):
        url = f"http://localhost:{self.http_port}"
        if kiosk:
            # Try to launch Chromium/Chrome or Firefox in kiosk mode
            cmds = [
                f"chromium --kiosk --app={url} --noerrdialogs --disable-infobars 2>/dev/null &",
                f"google-chrome --kiosk --app={url} --noerrdialogs --disable-infobars 2>/dev/null &",
                f"firefox --kiosk {url} 2>/dev/null &",
            ]
            for cmd in cmds:
                if os.system(cmd) == 0:
                    return
        webbrowser.open(url)

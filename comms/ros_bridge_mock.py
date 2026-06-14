"""
ros_bridge_mock.py
==================
Drop-in replacement for ros_bridge.py.
Generates fake telemetry, simulates waypoint ACKs, and fires callbacks
exactly like the real bridge would — no Pi, no ESP32, no ROS needed.

Usage: in app.py just change the import:
    from comms.ros_bridge_mock import RosBridge
"""

import threading
import math
import time
import random


class RosBridge:

    def __init__(self, host="localhost", port=9090):
        self.callbacks = {}
        self._running  = True
        self._wp_index = 0

        # Simulated robot state
        self._heading   = 0.0
        self._distance  = 0.0
        self._lin_err   = 0.0
        self._ang_err   = 0.0
        self._motor_l   = 0
        self._motor_r   = 0
        self._sensor_f  = 80.0   # cm

        # Start fake telemetry thread
        threading.Thread(target=self._telemetry_loop, daemon=True).start()

        # Fire READY after 1 second
        threading.Timer(1.0, self._fire_ready).start()

        print("[MOCK] RosBridge started — no real connection needed")

    # ── Public API (same as real RosBridge) ──────────────────────────────────

    def on(self, topic, callback):
        self.callbacks.setdefault(topic, []).append(callback)

    def send_velocity(self, linear_x, angular_z):
        """Simulate motors responding to velocity command."""
        self._motor_l = int(linear_x * 200 + angular_z * 80)
        self._motor_r = int(linear_x * 200 - angular_z * 80)
        self._motor_l = max(-255, min(255, self._motor_l))
        self._motor_r = max(-255, min(255, self._motor_r))
        print(f"[MOCK] cmd_vel  linear={linear_x:.2f}  angular={angular_z:.2f}")

    def send_waypoint(self, dist_m, angle_deg):
        """Simulate ESP32 accepting and completing a waypoint."""
        idx = self._wp_index
        self._wp_index += 1
        print(f"[MOCK] Waypoint {idx}: dist={dist_m:.2f} m  angle={angle_deg:.1f}°")

        # Fire OK immediately
        threading.Timer(0.1, self._dispatch,
                        args=('/robot/ok', {'data': idx})).start()

        # Simulate travel time, then fire DONE
        travel_time = max(1.5, abs(dist_m) * 2 + abs(angle_deg) / 90)
        threading.Timer(travel_time, self._fire_done,
                        args=(idx, dist_m, angle_deg)).start()

    # ── Internal simulation ───────────────────────────────────────────────────

    def _telemetry_loop(self):
        """Publish fake STATUS at 10 Hz."""
        t = 0.0
        while self._running:
            t += 0.1

            # Slowly drift heading like a real robot
            self._heading  = 45 * math.sin(t * 0.3)
            self._distance = abs(2.5 * math.sin(t * 0.15))
            self._lin_err  = round(random.uniform(-0.05, 0.05), 3)
            self._ang_err  = round(random.uniform(-1.5, 1.5), 2)
            self._sensor_f = round(30 + 50 * abs(math.sin(t * 0.2)), 1)

            # Decay motor values toward 0 when no command
            self._motor_l = int(self._motor_l * 0.92)
            self._motor_r = int(self._motor_r * 0.92)

            msg = {
                'distance_m':  round(self._distance, 3),
                'heading_deg': round(self._heading, 2),
                'lin_err':     self._lin_err,
                'ang_err':     self._ang_err,
                'motor_l':     self._motor_l,
                'motor_r':     self._motor_r,
                'sensor_front': self._sensor_f,
            }
            self._dispatch('/robot/status', msg)
            time.sleep(0.1)

    def _fire_ready(self):
        self._dispatch('/robot/ready', {'data': True})
        print("[MOCK] ESP32 READY fired")

    def _fire_done(self, idx, dist, angle):
        self._dispatch('/robot/done', {'data': idx})
        print(f"[MOCK] Waypoint {idx} DONE")

    def _dispatch(self, topic, msg):
        for cb in self.callbacks.get(topic, []):
            try:
                cb(msg)
            except Exception as e:
                print(f"[MOCK] callback error on {topic}: {e}")

"""
camera_panel_mock.py
====================
Drop-in replacement for camera_panel.py.
Draws an animated test pattern with fake YOLO bounding boxes.
No camera hardware, no ultralytics model download needed.
"""

import customtkinter as ctk
from PIL import Image, ImageDraw, ImageFont
import threading
import time
import random
import math


# Fake detected objects that float around the frame
FAKE_OBJECTS = [
    {"label": "person",  "conf": 0.91, "color": (255, 80,  80)},
    {"label": "chair",   "conf": 0.76, "color": (80,  200, 80)},
    {"label": "laptop",  "conf": 0.83, "color": (80,  80,  255)},
]


class CameraPanel(ctk.CTkFrame):

    def __init__(self, parent, bridge):
        super().__init__(parent)
        self._W = 860
        self._H = 480

        self.label = ctk.CTkLabel(self, text="")
        self.label.pack(expand=True, fill="both", padx=4, pady=10)

        # Status bar
        self.status = ctk.CTkLabel(
            self,
            text="[MOCK] Simulated camera feed  |  3 objects detected",
            font=("Courier", 11)
        )
        self.status.pack(pady=(0, 4))

        self._running = True
        self._t       = 0.0
        threading.Thread(target=self._loop, daemon=True).start()

    def _loop(self):
        while self._running:
            frame = self._make_frame()
            ctk_img = ctk.CTkImage(light_image=frame,
                                   dark_image=frame,
                                   size=(self._W, self._H))
            self.after(0, self.label.configure, {"image": ctk_img})
            self._t += 0.05
            time.sleep(0.033)   # ~30 fps

    def _make_frame(self):
        img  = Image.new("RGB", (self._W, self._H), color=(20, 20, 30))
        draw = ImageDraw.Draw(img)
        t    = self._t

        # ── Animated grid background ────────────────────────────────────────
        grid_off = int(t * 20) % 40
        for x in range(-40, self._W + 40, 40):
            draw.line([(x + grid_off, 0), (x + grid_off, self._H)],
                      fill=(30, 30, 50), width=1)
        for y in range(0, self._H + 40, 40):
            draw.line([(0, y), (self._W, y)], fill=(30, 30, 50), width=1)

        # ── Fake "horizon" line ─────────────────────────────────────────────
        hy = int(self._H * 0.5 + 30 * math.sin(t * 0.4))
        draw.line([(0, hy), (self._W, hy)], fill=(50, 80, 120), width=2)

        # ── Animated scan line ──────────────────────────────────────────────
        scan_y = int((t * 60) % self._H)
        draw.rectangle([(0, scan_y), (self._W, scan_y + 3)],
                        fill=(0, 180, 255, 60))

        # ── Fake YOLO bounding boxes ────────────────────────────────────────
        for i, obj in enumerate(FAKE_OBJECTS):
            phase = t + i * 2.1
            cx = int(self._W * 0.2 + (self._W * 0.6) *
                     (0.5 + 0.4 * math.sin(phase * 0.3 + i)))
            cy = int(self._H * 0.3 + (self._H * 0.4) *
                     (0.5 + 0.35 * math.cos(phase * 0.2 + i * 0.7)))
            bw = random.randint(90, 140)
            bh = random.randint(70, 120)
            x1, y1 = cx - bw // 2, cy - bh // 2
            x2, y2 = cx + bw // 2, cy + bh // 2

            # Clamp to frame
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(self._W - 1, x2), min(self._H - 1, y2)

            color = obj["color"]
            # Box
            draw.rectangle([(x1, y1), (x2, y2)],
                            outline=color, width=2)
            # Corner accents
            cl = 16
            for cx_, cy_, dx, dy in [(x1,y1,1,1),(x2,y1,-1,1),
                                      (x1,y2,1,-1),(x2,y2,-1,-1)]:
                draw.line([(cx_, cy_), (cx_+dx*cl, cy_)], fill=color, width=3)
                draw.line([(cx_, cy_), (cx_, cy_+dy*cl)], fill=color, width=3)
            # Label background
            label_text = f"{obj['label']}  {obj['conf']:.0%}"
            draw.rectangle([(x1, y1 - 20), (x1 + len(label_text) * 7 + 8, y1)],
                            fill=color)
            draw.text((x1 + 4, y1 - 18), label_text,
                       fill=(255, 255, 255))

        # ── Corner overlay text ─────────────────────────────────────────────
        draw.text((10, 10),  "MOCK CAM  640x480  30fps", fill=(0, 200, 100))
        draw.text((10, 28),  f"t = {t:.1f}s", fill=(100, 100, 160))
        draw.text((self._W - 160, 10),
                  f"objects: {len(FAKE_OBJECTS)}", fill=(0, 200, 100))

        # ── Crosshair ───────────────────────────────────────────────────────
        mx, my = self._W // 2, self._H // 2
        draw.line([(mx - 20, my), (mx + 20, my)], fill=(200, 200, 0), width=1)
        draw.line([(mx, my - 20), (mx, my + 20)], fill=(200, 200, 0), width=1)
        draw.ellipse([(mx - 6, my - 6), (mx + 6, my + 6)],
                     outline=(200, 200, 0), width=1)

        return img

    def destroy(self):
        self._running = False
        super().destroy()

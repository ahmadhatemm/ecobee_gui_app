import customtkinter as ctk

SPEED = 0.3
TURN  = 1.0

# Yellow theme configurations
YELLOW_THEME = "#FFCC00" 
YELLOW_HOVER = "#E6B800"

class ManualPanel(ctk.CTkFrame):
    def __init__(self, parent, bridge):
        super().__init__(parent)
        self.bridge = bridge
        self.keys   = set()

        ctk.CTkLabel(self, text="Manual Control", font=("Arial", 14, "bold")).pack(pady=4)

        grid = ctk.CTkFrame(self)
        grid.pack()
        buttons = [
            ("↑", 0, 1, self._fwd),
            ("←", 1, 0, self._left),
            ("■", 1, 1, self._stop),
            ("→", 1, 2, self._right),
            ("↓", 2, 1, self._back),
        ]
        for text, r, c, cmd in buttons:
            # INJECTED YELLOW THEMING HERE: 
            # Added fg_color, hover_color, and changed text to black for better contrast
            ctk.CTkButton(
                grid, text=text, width=56, height=56, command=cmd,
                fg_color=YELLOW_THEME,
                hover_color=YELLOW_HOVER,
                text_color="black",
                font=("Arial", 16, "bold") # Made arrows slightly more prominent
            ).grid(row=r, column=c, padx=4, pady=2)

        self.speed_label = ctk.CTkLabel(self, text="L: 0  R: 0")
        self.speed_label.pack(pady=4)

        parent.winfo_toplevel().bind("<KeyPress>",   self._key_down)
        parent.winfo_toplevel().bind("<KeyRelease>", self._key_up)
        self.after(100, self._key_loop)

    def _key_down(self, e): self.keys.add(e.keysym)
    def _key_up(self,   e): self.keys.discard(e.keysym)

    def _key_loop(self):
        lin, ang = 0.0, 0.0
        if "w" in self.keys or "Up"    in self.keys: lin =  SPEED
        if "s" in self.keys or "Down"  in self.keys: lin = -SPEED
        if "a" in self.keys or "Left"  in self.keys: ang =  TURN
        if "d" in self.keys or "Right" in self.keys: ang = -TURN
        if lin or ang:
            self.bridge.send_velocity(lin, ang)
        self.after(100, self._key_loop)

    def _fwd(self):   self.bridge.send_velocity( SPEED, 0)
    def _back(self):  self.bridge.send_velocity(-SPEED, 0)
    def _left(self):  self.bridge.send_velocity(0,  TURN)
    def _right(self): self.bridge.send_velocity(0, -TURN)
    def _stop(self):  self.bridge.send_velocity(0, 0)
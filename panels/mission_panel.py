import customtkinter as ctk

class MissionPanel(ctk.CTkFrame):
    def __init__(self, parent, bridge):
        super().__init__(parent)
        self.bridge = bridge
        ctk.CTkLabel(self, text="Mission", font=("Arial", 14, "bold")).pack(pady=4)

        row = ctk.CTkFrame(self)
        row.pack(fill="x", padx=6, pady=2)
        self.dist_entry  = ctk.CTkEntry(row, placeholder_text="dist (m)", width=80)
        self.angle_entry = ctk.CTkEntry(row, placeholder_text="angle (°)", width=80)
        self.dist_entry.pack(side="left", padx=4)
        self.angle_entry.pack(side="left", padx=4)
        ctk.CTkButton(row, text="Add WP", width=80,
                      command=self._add_wp).pack(side="left", padx=4)

        self.status_var = ctk.StringVar(value="Waiting for robot...")
        ctk.CTkLabel(self, textvariable=self.status_var).pack(pady=4)

        self.log = ctk.CTkTextbox(self, height=30, state="disabled")
        self.log.pack(fill="both", padx=8, pady=2, expand=True)

        bridge.on('/robot/done',  self._on_done)
        bridge.on('/robot/ready', self._on_ready)

    def _add_wp(self):
        try:
            d = float(self.dist_entry.get())
            a = float(self.angle_entry.get())
            self.bridge.send_waypoint(d, a)
            self._log(f"→ Queued WP: {d:.2f} m, {a:.1f}°")
        except ValueError:
            self._log("ERROR: enter valid numbers")

    def _on_done(self, msg):
        self.after(0, self._log, f"✓ Waypoint {msg['data']} complete")

    def _on_ready(self, msg):
        self.after(0, self.status_var.set, "✓ Robot Ready")

    def _log(self, text):
        self.log.configure(state="normal")
        
        # If the textbox is completely empty, don't add a leading newline
        if self.log.get("1.0", "end-1c") == "":
            self.log.insert("end", text)
        else:
            self.log.insert("end", "\n" + text)
        
        # Now "end" points directly to your text line, not a blank space!
        self.log.see("end")
        self.log.configure(state="disabled")
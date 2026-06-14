import customtkinter as ctk

class TelemetryPanel(ctk.CTkFrame):
    def __init__(self, parent, bridge):
        super().__init__(parent)
        
        # Title
        ctk.CTkLabel(self, text="Telemetry", font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=(5, 2))

        self.vars = {}
        # Cleaned up fields to maximize space efficiency
        fields = [
            ("heading_deg", "Heading"),
            ("distance_m",  "Distance"),
            ("lin_err",     "Lin Error"),
            ("ang_err",     "Ang Error"),
            ("motor_l",     "Motor L"),
            ("motor_r",     "Motor R"),
        ]
        
        # Configure internal grid for ultra-compact label/value pairs
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        for idx, (key, label) in enumerate(fields):
            r = idx + 1
            # Left-aligned clean label text
            ctk.CTkLabel(self, text=label, font=("Arial", 11), anchor="w").grid(row=r, column=0, padx=(10, 2), pady=1, sticky="w")
            
            # Right-aligned streaming numerical value
            var = ctk.StringVar(value="—")
            self.vars[key] = var
            ctk.CTkLabel(self, textvariable=var, font=("Arial", 11, "bold"), anchor="e").grid(row=r, column=1, padx=(2, 10), pady=1, sticky="e")

        bridge.on('/robot/status', self._on_status)

    def _on_status(self, msg):
        self.after(0, self._update_ui, msg)

    def _update_ui(self, msg):
        # Concise layout updates with clean formatting inline
        self.vars["heading_deg"].set(f"{msg['heading_deg']:.1f}°")
        self.vars["distance_m"].set(f"{msg['distance_m']:.2f}m")
        self.vars["lin_err"].set(f"{msg['lin_err']:.2f}")
        self.vars["ang_err"].set(f"{msg['ang_err']:.1f}°")
        self.vars["motor_l"].set(str(msg.get('motor_l', '—')))
        self.vars["motor_r"].set(str(msg.get('motor_r', '—')))
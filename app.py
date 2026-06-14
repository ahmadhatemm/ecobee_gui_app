import customtkinter as ctk
from comms.ros_bridge_mock import RosBridge
from panels.camera_panel_mock import CameraPanel
from panels.telemetry_panel import TelemetryPanel
from panels.manual_panel import ManualPanel
from panels.mission_panel import MissionPanel
from PIL import Image
import os

# Set base app to dark mode (Black background)
ctk.set_appearance_mode("dark")
# We remove the "blue" theme and manually apply Yellow to specific widgets below
YELLOW_THEME = "#FFCC00" 
YELLOW_HOVER = "#E6B800"

class RobotApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Robot Control GUI")
        self.geometry("1400x860")

        self.bridge = RosBridge()

        # ---------------------------------------------------------
        # 1. MAIN WINDOW GRID
        # ---------------------------------------------------------
        self.grid_columnconfigure(0, weight=1, uniform="half")
        self.grid_columnconfigure(1, weight=1, uniform="half")

        # Layout adjustment for Logo (Row 0), Camera (Row 1), Data (Row 2)
        self.grid_rowconfigure(0, weight=0) # Logo takes only minimum space
        self.grid_rowconfigure(1, weight=1) # Camera expands to take all remaining space
        self.grid_rowconfigure(2, weight=0) # Live data is forced to stay small

        # ---------------------------------------------------------
        # 2. LEFT SIDE (Visuals & Live Data)
        # ---------------------------------------------------------
        
        # Row 0: NEW LOGO SPACE (Top Left)
        self.logo_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.logo_frame.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="w")
        
        # Placeholder for your image. Replace text="" and add image=logo_image once you load your file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(current_dir, "C:\\Users\\ahmad_m7ey4b8\\OneDrive - Faculty of Engineering Ain Shams University\\Documents\\robot_gui\\robot_gui\\Ecobee Logo.jpeg")
        if os.path.exists(image_path):
            logo_image = ctk.CTkImage(
                light_image=Image.open(image_path),
                dark_image=Image.open(image_path),
                size=(100, 100) # 3. Adjust these dimensions (Width, Height) in pixels to fit your logo perfectly
            )
            # Create label with the image loaded
            self.logo_label = ctk.CTkLabel(self.logo_frame, image=logo_image, text="")
        else:
            # Fallback backup text if the image file is missing
            self.logo_label = ctk.CTkLabel(self.logo_frame, text="[ LOGO MISSING ]", text_color="#FFCC00", font=("Arial", 16, "bold"))
            
        self.logo_label.pack(side="left")

        # Row 1: Camera Feed
        self.camera = CameraPanel(self, self.bridge)
        self.camera.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        # Row 2: Bottom Left Container
        left_bottom = ctk.CTkFrame(self, fg_color="transparent")
        left_bottom.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="nsew")
        
        left_bottom.grid_columnconfigure(0, weight=1) 
        left_bottom.grid_columnconfigure(1, weight=1) 
        
        # Set weights to 0 so sensors and alerts don't steal height from the camera
        left_bottom.grid_rowconfigure(0, weight=0) 
        left_bottom.grid_rowconfigure(1, weight=0) 

        self.telemetry = TelemetryPanel(left_bottom, self.bridge)
        self.telemetry.grid(row=0, column=0, rowspan=2, padx=5, pady=5, sticky="nsew")

        self.build_sensors_panel(left_bottom)
        self.build_alerts_panel(left_bottom)

        # ---------------------------------------------------------
        # 3. RIGHT SIDE (Controls & Inputs)
        # ---------------------------------------------------------
        right = ctk.CTkFrame(self)
        # Changed rowspan to 3 so it spans beside the Logo, Camera, and Bottom Data
        right.grid(row=0, column=1, rowspan=3, padx=10, pady=10, sticky="nsew")
        right.grid_columnconfigure(0, weight=1)

        # Slot 0: System Controls & Arm Panel
        self.control_panel = RobotControlPanel(right, self)
        self.control_panel.grid(row=0, column=0, padx=8, pady=8, sticky="nsew")

        # Slot 1: Manual Control (D-pad)
        self.manual = ManualPanel(right, self.bridge)
        self.manual.grid(row=1, column=0, padx=8, pady=8, sticky="nsew")

        # Slot 2: Mission Input
        self.mission = MissionPanel(right, self.bridge)
        self.mission.grid(row=2, column=0, padx=8, pady=8, sticky="nsew")

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    # ---------------------------------------------------------
    # UI BUILDERS FOR LEFT-SIDE PANELS
    # ---------------------------------------------------------
    def build_sensors_panel(self, parent):
        self.sensor_frame = ctk.CTkFrame(parent)
        self.sensor_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        self.sensor_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(self.sensor_frame, text="Front Proximity Sensors", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, columnspan=3, padx=10, pady=5, sticky="w")
        
        sensor_names = ["Left", "Center", "Right"]
        for i, name in enumerate(sensor_names):
            ctk.CTkLabel(self.sensor_frame, text=f"{name}:").grid(row=i+1, column=0, padx=10, pady=2, sticky="w")
            
            # Yellow theme applied to progress bars
            bar = ctk.CTkProgressBar(self.sensor_frame, height=10, progress_color=YELLOW_THEME)
            bar.grid(row=i+1, column=1, padx=10, pady=2, sticky="nsew")
            bar.set(0.7)  
            ctk.CTkLabel(self.sensor_frame, text="70 cm", width=40).grid(row=i+1, column=2, padx=10, pady=2, sticky="e")

    def build_alerts_panel(self, parent):
        self.alerts_frame = ctk.CTkFrame(parent)
        self.alerts_frame.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")
        self.alerts_frame.grid_columnconfigure(0, weight=1)
        self.alerts_frame.grid_rowconfigure(1, weight=0) # Keep low profile
        
        ctk.CTkLabel(self.alerts_frame, text="System Alerts Log", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=10, pady=2, sticky="w")
        
        # Explicitly short height so it doesn't crush the camera
        self.txt_alerts = ctk.CTkTextbox(self.alerts_frame, font=("Consolas", 11), height=55)
        self.txt_alerts.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        self.log_alert("INFO: GUI Initialized. Awaiting connection...")

    def log_alert(self, message):
        self.txt_alerts.configure(state="normal")
        self.txt_alerts.insert("end", f"\n> {message}")
        self.txt_alerts.see("end")
        self.txt_alerts.configure(state="disabled")

    def on_close(self):
        self.destroy()


class RobotControlPanel(ctk.CTkFrame):
    def __init__(self, parent, app_instance):
        super().__init__(parent)
        self.app = app_instance 
        
        self.grid_columnconfigure(0, weight=1)
        
        # ---------------------------------------------------------
        # 1. SYSTEM CONTROLS (Start / Stop)
        # ---------------------------------------------------------
        self.controls_frame = ctk.CTkFrame(self)
        self.controls_frame.grid(row=0, column=0, padx=15, pady=10, sticky="nsew")
        self.controls_frame.grid_columnconfigure((0, 1), weight=1)
        
        self.btn_start = ctk.CTkButton(
            self.controls_frame, text="START MISSION", 
            fg_color="#2ecc71", hover_color="#27ae60", text_color="white",
            font=ctk.CTkFont(weight="bold"), command=self.start_robot
        )
        self.btn_start.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        self.btn_stop = ctk.CTkButton(
            self.controls_frame, text="EMERGENCY STOP", 
            fg_color="#e74c3c", hover_color="#c0392b", text_color="white",
            font=ctk.CTkFont(weight="bold"), command=self.stop_robot
        )
        self.btn_stop.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        # ---------------------------------------------------------
        # 2. ROBOTIC ARM MANIPULATION CONTROLS (2 DOF + 1 Finger)
        # ---------------------------------------------------------
        self.arm_frame = ctk.CTkFrame(self)
        self.arm_frame.grid(row=1, column=0, padx=15, pady=10, sticky="nsew")
        self.arm_frame.grid_columnconfigure(1, weight=1)
        
        self.arm_title = ctk.CTkLabel(self.arm_frame, text="Robotic Arm Override", font=ctk.CTkFont(weight="bold"))
        self.arm_title.grid(row=0, column=0, columnspan=2, padx=10, pady=5, sticky="w")
        
        # Yellow theme applied to sliders
        ctk.CTkLabel(self.arm_frame, text="Link 1").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.slider_base = ctk.CTkSlider(self.arm_frame, from_=0, to=180, number_of_steps=180, button_color=YELLOW_THEME, button_hover_color=YELLOW_HOVER, progress_color=YELLOW_THEME)
        self.slider_base.grid(row=1, column=1, padx=10, pady=5, sticky="nsew")
        
        ctk.CTkLabel(self.arm_frame, text="Link 2").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.slider_reach = ctk.CTkSlider(self.arm_frame, from_=0, to=100, button_color=YELLOW_THEME, button_hover_color=YELLOW_HOVER, progress_color=YELLOW_THEME)
        self.slider_reach.grid(row=2, column=1, padx=10, pady=5, sticky="nsew")
        
        ctk.CTkLabel(self.arm_frame, text="Shovel Finger").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.slider_finger = ctk.CTkSlider(self.arm_frame, from_=0, to=100, button_color=YELLOW_THEME, button_hover_color=YELLOW_HOVER, progress_color=YELLOW_THEME)
        self.slider_finger.grid(row=3, column=1, padx=10, pady=5, sticky="nsew")

    def start_robot(self):
        self.app.log_alert("COMMAND: Autonomous routine initiated.")

    def stop_robot(self):
        self.app.log_alert("CRITICAL: Emergency Stop Engaged.")

if __name__ == "__main__":
    app = RobotApp()
    app.mainloop()
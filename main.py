import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import time
from device_comm import DeviceManager, MotorValveController

class DebugWindow:
    def __init__(self, master):
        self.window = tk.Toplevel(master)
        self.window.title("Developer Console - Serial Traffic")
        self.window.geometry("500x300")
        self.text = tk.Text(self.window, bg="black", fg="#00FF00", font=("Courier", 10))
        self.text.pack(fill=tk.BOTH, expand=True)

    def log(self, message):
        try:
            self.text.insert(tk.END, str(message) + "\n")
            self.text.see(tk.END)
        except tk.TclError:
            pass

class ThermocoupleDialog:
    def __init__(self, master, device_mgr):
        self.top = tk.Toplevel(master)
        self.top.title("Thermocouple Config")
        self.top.geometry("300x150")
        self.device_mgr = device_mgr
        
        tk.Label(self.top, text="Select Thermocouple Type:", font=("Arial", 10, "bold")).pack(pady=10)
        
        # Current setting
        current = self.device_mgr.get_thermocouple_type()
        self.lbl_current = tk.Label(self.top, text=f"Current: {current}", fg="blue")
        self.lbl_current.pack()

        btn_frame = tk.Frame(self.top)
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="Type C", width=8, command=lambda: self.set_type("C")).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Type S", width=8, command=lambda: self.set_type("S")).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="mV", width=8, command=lambda: self.set_type("mV")).pack(side=tk.LEFT, padx=5)

    def set_type(self, tc_type):
        self.device_mgr.set_thermocouple_type(tc_type)
        # Verify change
        new_val = self.device_mgr.get_thermocouple_type()
        self.lbl_current.config(text=f"Current: {new_val}")
        print(f"Thermocouple set to {tc_type}")

class ZeroPressureDialog:
    def __init__(self, master, device_mgr):
        self.top = tk.Toplevel(master)
        self.top.title("Zero Pressure Calibration")
        self.top.geometry("400x350")
        self.device_mgr = device_mgr
        
        # Safety Warnings
        warn_frame = tk.LabelFrame(self.top, text="SAFETY CHECKS", fg="red", font=("Arial", 10, "bold"))
        warn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        checks = [
            "Ensure NO physical pressure exists.",
            "Open MAIN PRESS valve.",
            "Open MANUAL ADVANCE valve.",
            "Open MANUAL BLEED valve."
        ]
        
        for check in checks:
            tk.Label(warn_frame, text=f"• {check}", anchor="w").pack(fill=tk.X, padx=5, pady=2)

        # Current Reading
        self.lbl_current = tk.Label(self.top, text="Current Reading: ---", font=("Arial", 12))
        self.lbl_current.pack(pady=10)
        
        # Buttons
        btn_frame = tk.Frame(self.top)
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="ZERO NOW", bg="red", fg="white", command=self.do_zero).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Cancel", command=self.top.destroy).pack(side=tk.LEFT, padx=10)
        
        # Initial read
        self.update_reading()

    def update_reading(self):
        resp = self.device_mgr.send_texmate_cmd(2, "SR")
        if resp:
            self.lbl_current.config(text=f"Current Reading: {resp}")
        elif self.device_mgr.simulated:
            self.lbl_current.config(text="Current Reading: 15 (Sim)")
        else:
            self.lbl_current.config(text="Current Reading: Error")

    def do_zero(self):
        success, msg = self.device_mgr.zero_pressure_port2()
        if success:
            messagebox.showinfo("Success", msg, parent=self.top)
            self.top.destroy()
        else:
            messagebox.showerror("Error", msg, parent=self.top)

class PurgeDialog:
    def __init__(self, master, motor_mgr):
        self.top = tk.Toplevel(master)
        self.top.title("Purge System")
        self.top.geometry("600x550")
        self.motor_mgr = motor_mgr
        
        # Status Label
        self.lbl_status = tk.Label(self.top, text="System Ready", font=("Arial", 12, "bold"), fg="blue")
        self.lbl_status.pack(pady=10)

        # Sequence Buttons
        seq_frame = tk.LabelFrame(self.top, text="Automated Sequences", padx=10, pady=10)
        seq_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(seq_frame, text="START PURGE", bg="green", fg="white", font=("Arial", 10, "bold"), 
                  command=self.start_purge_sequence).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        
        tk.Button(seq_frame, text="STOP / RESET", bg="red", fg="white", font=("Arial", 10, "bold"), 
                  command=self.stop_purge_sequence).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

        # Manual Controls
        man_frame = tk.LabelFrame(self.top, text="Manual Controls", padx=10, pady=10)
        man_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Grid layout for manual controls
        # Up Valve
        tk.Label(man_frame, text="UP Valve").grid(row=0, column=0, padx=5, pady=5)
        tk.Button(man_frame, text="Open", command=lambda: self.send("AA8")).grid(row=0, column=1, padx=5, pady=5)
        tk.Button(man_frame, text="Closed", command=lambda: self.send("AA0")).grid(row=0, column=2, padx=5, pady=5)
        
        # Down Valve
        tk.Label(man_frame, text="DOWN Valve").grid(row=1, column=0, padx=5, pady=5)
        tk.Button(man_frame, text="Open", command=lambda: self.send("BA8")).grid(row=1, column=1, padx=5, pady=5)
        tk.Button(man_frame, text="Closed", command=lambda: self.send("BA0")).grid(row=1, column=2, padx=5, pady=5)
        
        # Up Motor
        tk.Label(man_frame, text="UP Motor").grid(row=2, column=0, padx=5, pady=5)
        tk.Button(man_frame, text="+100", command=lambda: self.send("A+100")).grid(row=2, column=1, padx=5, pady=5)
        tk.Button(man_frame, text="-100", command=lambda: self.send("A-100")).grid(row=2, column=2, padx=5, pady=5)
        
        # Down Motor
        tk.Label(man_frame, text="DOWN Motor").grid(row=3, column=0, padx=5, pady=5)
        tk.Button(man_frame, text="+100", command=lambda: self.send("B+100")).grid(row=3, column=1, padx=5, pady=5)
        tk.Button(man_frame, text="-100", command=lambda: self.send("B-100")).grid(row=3, column=2, padx=5, pady=5)

    def send(self, cmd):
        self.motor_mgr.send_command(cmd)

    def start_purge_sequence(self):
        # Instructions from PurgeAP10.frm Form_Load
        checks = [
            "Close MANUAL advance valves IN and OUT",
            "Close RETRACT valves IN and OUT",
            "Close MASTER press valve"
        ]
        for check in checks:
            if not messagebox.askokcancel("Purge Setup", check, parent=self.top):
                return

        self.lbl_status.config(text="Purging... (Step 1/2)", fg="orange")
        # Step 1: AA8;BA8;A+4000
        self.send("AA8;BA8;A+4000")
        
        # Step 2: Wait 500ms then AA8;BA8;B+5000
        self.top.after(500, self._purge_step_2)

    def _purge_step_2(self):
        self.lbl_status.config(text="Purging... (Step 2/2)", fg="orange")
        self.send("AA8;BA8;B+5000")
        
        # Wait 5000ms then Done
        self.top.after(5000, lambda: self.lbl_status.config(text="Purge Complete. System Pressurized.", fg="green"))

    def stop_purge_sequence(self):
        self.lbl_status.config(text="Resetting... (Step 1/3)", fg="red")
        # Step 1: AA0;A-4000
        self.send("AA0;A-4000")
        
        # Step 2: Wait 500ms then BA8;B-5000
        self.top.after(500, self._stop_step_2)

    def _stop_step_2(self):
        self.lbl_status.config(text="Resetting... (Step 2/3)", fg="red")
        self.send("BA8;B-5000")
        
        # Step 3: Wait 7000ms then BA0
        self.top.after(7000, self._stop_step_3)

    def _stop_step_3(self):
        self.lbl_status.config(text="Resetting... (Step 3/3)", fg="red")
        self.send("BA0")
        self.lbl_status.config(text="Reset Complete.", fg="black")
        
        messagebox.showinfo("Reset Complete", "Open RETRACT valve OUT only\nOpen MASTER press valve", parent=self.top)

class BaseAPGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("EPL MAP Control")
        self.root.configure(bg="#F0F0F0")
        
        self.device_mgr = DeviceManager()
        self.motor_mgr = MotorValveController() # Second serial port controller
        self.target_voltage = 0.0 # Tracks the state for Port 5 (Omega)
        self.polling_active = False
        
        # Graphing State
        self.current_view = "Temperature"
        self.data_history = {"Temperature": [], "Pressure": [], "Wattage": []}
        self.start_time = time.time()

        # Use a main frame for padding and layout
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.create_widgets()
        
        # Attempt connection and start polling
        self.connect_hardware()

    def create_widgets(self):
        # --- Title ---
        title_lbl = tk.Label(self.main_frame, text="EPL Multi Anvil Press Controls", font=("Courier New", 20, "bold"), bg="white", anchor="w", padx=10, pady=5)
        title_lbl.pack(fill=tk.X, pady=(0, 10))

        # --- Top Section (Buttons + Graph + Rescale) ---
        top_frame = ttk.Frame(self.main_frame)
        top_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Left Buttons (Process Control)
        left_btn_frame = ttk.Frame(top_frame)
        left_btn_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        buttons = [
            ("Start Process", "#80FF80", self.on_click),
            ("Stop Process", None, self.on_click),
            ("Purge", None, self.open_purge_dialog),
            ("Zero Pressure", None, self.open_zero_pressure),
            ("Error Display", None, self.on_click)
        ]
        
        for text, color, cmd in buttons:
            btn = tk.Button(left_btn_frame, text=text, command=cmd)
            if color:
                btn.configure(bg=color)
            btn.pack(fill=tk.X, pady=2)

        # Graph Container (Right of buttons)
        graph_container = ttk.Frame(top_frame)
        graph_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Rescale Buttons (Top of Graph)
        rescale_frame = ttk.Frame(graph_container)
        rescale_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 2))
        
        tk.Button(rescale_frame, text="Temperature", bg="#8080FF", height=1, command=lambda: self.set_view("Temperature")).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=1)
        tk.Button(rescale_frame, text="Pressure", bg="#00FF00", height=1, command=lambda: self.set_view("Pressure")).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=1)
        tk.Button(rescale_frame, text="Wattage", bg="#8080FF", height=1, command=lambda: self.set_view("Wattage")).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=1)

        # Graph Area
        self.graph_canvas = tk.Canvas(graph_container, bg="white", height=400, width=600, highlightthickness=1, highlightbackground="black")
        self.graph_canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.graph_canvas.bind("<Configure>", self.draw_graph)

        # --- Middle Section (Readouts) ---
        readout_frame = ttk.LabelFrame(self.main_frame, text="Readouts")
        readout_frame.pack(fill=tk.X, pady=10)

        headers = [
            ("Temp Type", "red"), ("Pressure", "green"), 
            ("Voltage", "blue"), ("Current", "magenta"), ("Resistance", "black")
        ]
        
        self.readout_labels = []
        for i, (text, color) in enumerate(headers):
            lbl = tk.Label(readout_frame, text=text, fg=color, font=("Arial", 10, "bold"))
            lbl.grid(row=0, column=i, padx=10, pady=5, sticky="ew")
            
            val = tk.Label(readout_frame, bg="white", relief="sunken", width=15)
            val.grid(row=1, column=i, padx=10, pady=5)
            self.readout_labels.append(val)
            
            readout_frame.columnconfigure(i, weight=1)

        # --- Bottom Section (Controls) ---
        bottom_frame = ttk.Frame(self.main_frame)
        bottom_frame.pack(fill=tk.X)

        # Column 1: Inputs
        col1 = ttk.Frame(bottom_frame)
        col1.pack(side=tk.LEFT, anchor=tk.N, padx=(0, 10))
        tk.Button(col1, text="Input Temp Values", command=self.open_temp_config).pack(fill=tk.X, pady=2)
        tk.Button(col1, text="Input Pressure Values", command=self.on_click).pack(fill=tk.X, pady=2)
        tk.Button(col1, text="Start Manual Control", command=self.on_click).pack(fill=tk.X, pady=2)

        # Column 2: Start Controls
        col2 = ttk.Frame(bottom_frame)
        col2.pack(side=tk.LEFT, anchor=tk.N, padx=(0, 10))
        tk.Button(col2, text="Start Control Temperature", command=self.on_click).pack(fill=tk.X, pady=2)
        tk.Button(col2, text="Start Control Pressure", command=self.on_click).pack(fill=tk.X, pady=2)
        tk.Button(col2, text="Start Power Control", command=self.on_click).pack(fill=tk.X, pady=2)

        # Column 3: Manual Adjust
        col3 = ttk.LabelFrame(bottom_frame, text="Manual Adjust")
        col3.pack(side=tk.LEFT, anchor=tk.N, padx=(0, 10))
        
        tk.Button(col3, text="Down", command=lambda: self.adjust_voltage(-1)).pack(side=tk.LEFT, padx=5, pady=5)
        self.ent_manual_inc = tk.Entry(col3, width=8)
        self.ent_manual_inc.insert(0, "0.05")
        self.ent_manual_inc.pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(col3, text="Up", command=lambda: self.adjust_voltage(1)).pack(side=tk.LEFT, padx=5, pady=5)

        # Column 4: Valves & Motors
        # col4 = ttk.LabelFrame(bottom_frame, text="Valve Controls")
        # col4.pack(side=tk.LEFT, anchor=tk.N, padx=(0, 10))
        # 
        # # Valves
        # v_frame = ttk.Frame(col4)
        # v_frame.pack(fill=tk.X, pady=2)
        # tk.Button(v_frame, text="Up Valve", command=self.on_click).pack(side=tk.LEFT, padx=2)
        # tk.Button(v_frame, text="Down Valve", command=self.on_click).pack(side=tk.LEFT, padx=2)

        # Motors
        # m_frame = ttk.Frame(col4)
        # m_frame.pack(fill=tk.X, pady=2)
        # 
        # # U Motor
        # u_frame = ttk.Frame(m_frame)
        # u_frame.pack(side=tk.LEFT, padx=5)
        # ttk.Label(u_frame, text="U Motor").pack()
        # tk.Button(u_frame, text="+100", command=self.on_click).pack()
        # tk.Button(u_frame, text="-100", command=self.on_click).pack()
        # 
        # # D Motor
        # d_frame = ttk.Frame(m_frame)
        # d_frame.pack(side=tk.LEFT, padx=5)
        # ttk.Label(d_frame, text="D Motor").pack()
        # tk.Button(d_frame, text="+100", command=self.on_click).pack()
        # tk.Button(d_frame, text="-100", command=self.on_click).pack()

        # Exit
        tk.Button(bottom_frame, text="EXIT", bg="red", fg="white", command=self.cleanup_and_exit).pack(side=tk.RIGHT, anchor=tk.S, padx=10, pady=10)
        
        # Developer Mode
        tk.Button(bottom_frame, text="Dev Mode", bg="orange", command=self.open_developer_mode).pack(side=tk.RIGHT, anchor=tk.S, padx=10, pady=10)

    def set_view(self, view_name):
        self.current_view = view_name
        self.draw_graph()

    def draw_graph(self, event=None):
        self.graph_canvas.delete("all")
        w = self.graph_canvas.winfo_width()
        h = self.graph_canvas.winfo_height()
        
        # Draw Title
        self.graph_canvas.create_text(w/2, 20, text=f"{self.current_view} vs Time", font=("Arial", 12, "bold"), fill="black")

        # Draw Grid
        for i in range(1, 5):
            # Vertical
            x = i * (w / 5)
            self.graph_canvas.create_line(x, 40, x, h-30, fill="#D0D0D0", dash=(2, 4))

            # Horizontal
            y = 40 + i * ((h-70) / 5)
            self.graph_canvas.create_line(40, y, w-20, y, fill="#D0D0D0", dash=(2, 4))

        # Draw Axes
        self.graph_canvas.create_line(40, 40, 40, h-30, width=2) # Y Axis
        self.graph_canvas.create_line(40, h-30, w-20, h-30, width=2) # X Axis
        
        # Axis Labels
        self.graph_canvas.create_text(w/2, h-10, text="Time (s)", font=("Arial", 10))
        self.graph_canvas.create_text(15, h/2, text=self.current_view, angle=90, font=("Arial", 10))

    def on_click(self):
        print("Button clicked")

    def connect_hardware(self):
        """Opens the serial port and starts the polling loop."""
        if self.device_mgr.open():
            print("Serial port opened successfully.")
            
            # Initialize meters based on ModuleAP10.bas
            self.device_mgr.initialize_texmate_meters()
            
            self.polling_active = True
            self.poll_devices()
        else:
            print("Failed to open serial port. Running in offline mode.")
            
        # Attempt to open motor port as well
        if self.motor_mgr.open():
            print("Motor/Valve port opened.")
        else:
            print("Failed to open Motor/Valve port.")

    def poll_devices(self):
        """Periodically reads data from all ports and updates the GUI."""
        if not self.polling_active:
            return

        # Map GUI readout columns to Device Ports
        # 0: Temp Type (Port 1), 1: Pressure (Port 2), 2: Voltage (Port 3), etc.
        # Adjust mapping as per actual hardware setup
        port_mapping = [1, 2, 3, 4, 5] 

        for i, port in enumerate(port_mapping):
            if i < len(self.readout_labels):
                val_str = "---"
                if port == 5:
                    # Omega Device
                    resp = self.device_mgr.send_omega_cmd("$1RD")
                    if resp and len(resp) >= 3:
                        val_str = resp[2:] # Strip prefix if needed
                else:
                    # Texmate Devices
                    resp = self.device_mgr.send_texmate_cmd(port, "SR")
                    if resp:
                        val_str = resp # Raw response or parse it
                
                self.readout_labels[i].config(text=val_str)

        # Schedule next poll (e.g., every 500ms)
        self.root.after(500, self.poll_devices)

    def adjust_voltage(self, direction):
        """
        Adjusts the voltage up or down based on the entry value.
        direction: 1 for Up, -1 for Down
        """
        try:
            step = float(self.ent_manual_inc.get())
        except ValueError:
            step = 0.05 # Default fallback

        self.target_voltage += (step * direction)
        
        # Clamp between 0 and 10V
        self.target_voltage = max(0.0, min(10.0, self.target_voltage))
        
        print(f"Setting Voltage to: {self.target_voltage:.3f} V")
        
        # Send to device
        if self.polling_active:
            self.device_mgr.set_omega_voltage(self.target_voltage)

    def open_temp_config(self):
        """Opens the Thermocouple Configuration Dialog."""
        ThermocoupleDialog(self.root, self.device_mgr)

    def open_zero_pressure(self):
        """Opens the Zero Pressure Dialog."""
        ZeroPressureDialog(self.root, self.device_mgr)

    def open_purge_dialog(self):
        """Opens the Purge System Dialog."""
        PurgeDialog(self.root, self.motor_mgr)

    def open_developer_mode(self):
        """Opens the debug window and enables simulation if needed."""
        if not hasattr(self, 'debug_win') or not self.debug_win.window.winfo_exists():
            self.debug_win = DebugWindow(self.root)
            
            def on_close():
                self.device_mgr.set_log_callback(None)
                self.motor_mgr.set_log_callback(None)
                self.debug_win.window.destroy()
            self.debug_win.window.protocol("WM_DELETE_WINDOW", on_close)
            
            self.device_mgr.set_log_callback(self.debug_win.log)
            self.motor_mgr.set_log_callback(self.debug_win.log)
            self.debug_win.log("Developer Mode Enabled.")

        # If hardware connection failed, force simulation and start polling
        if not self.polling_active:
            self.debug_win.log("Port closed. Enabling Simulation Mode...")
            self.device_mgr.enable_simulation()
            self.motor_mgr.enable_simulation()
            self.polling_active = True
            self.poll_devices()

    def cleanup_and_exit(self):
        self.polling_active = False
        self.device_mgr.close()
        self.motor_mgr.close()
        self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = BaseAPGUI(root)
    root.mainloop()
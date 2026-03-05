import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
import threading
import queue
import time
import os
import datetime
from device_comm import DeviceManager, MotorValveController

try:
    from PIL import Image, ImageTk, ImageDraw
    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False
    print("Warning: Pillow library not found. Install 'pillow' for better logo quality.")

class DebugWindow:
    def __init__(self, master):
        self.window = tk.Toplevel(master)
        self.window.title("Developer Console - Serial Traffic")
        self.window.geometry("500x300")
        self.text = tk.Text(self.window, bg="black", fg="#00FF00", font=("Arial", 10))
        self.text.pack(fill=tk.BOTH, expand=True)

    def log(self, message):
        try:
            self.text.insert(tk.END, str(message) + "\n")
            
            # Limit log size to prevent memory issues over long runs (keep last 2000 lines)
            if int(self.text.index('end-1c').split('.')[0]) > 2000:
                self.text.delete('1.0', '2.0')
                
            self.text.see(tk.END)
        except tk.TclError:
            pass

class ThermocoupleDialog:
    def __init__(self, master, device_mgr, serial_lock):
        self.top = tk.Toplevel(master)
        self.top.title("Thermocouple Config")
        self.top.geometry("300x150")
        self.device_mgr = device_mgr
        self.serial_lock = serial_lock
        
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
        with self.serial_lock:
            self.device_mgr.set_thermocouple_type(tc_type)
            # Verify change
            new_val = self.device_mgr.get_thermocouple_type()
        self.lbl_current.config(text=f"Current: {new_val}")
        print(f"Thermocouple set to {tc_type}")

class ZeroPressureDialog:
    def __init__(self, master, device_mgr, serial_lock):
        self.top = tk.Toplevel(master)
        self.top.title("Zero Pressure Calibration")
        self.top.geometry("400x350")
        self.device_mgr = device_mgr
        self.serial_lock = serial_lock
        
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
        with self.serial_lock:
            resp = self.device_mgr.send_texmate_cmd(2, "SR")
        if resp:
            self.lbl_current.config(text=f"Current Reading: {resp}")
        elif self.device_mgr.simulated:
            self.lbl_current.config(text="Current Reading: 15 (Sim)")
        else:
            self.lbl_current.config(text="Current Reading: Error")

    def do_zero(self):
        with self.serial_lock:
            success, msg = self.device_mgr.zero_pressure_port2()
        if success:
            messagebox.showinfo("Success", msg, parent=self.top)
            self.top.destroy()
        else:
            messagebox.showerror("Error", msg, parent=self.top)

class ProfileEditorDialog:
    def __init__(self, master, profile, on_save, title="Profile Editor", value_label="Pressure (Bars)", rate_label="Rate (Bars/Hr)"):
        self.top = tk.Toplevel(master)
        self.top.title(title)
        self.top.geometry("600x450")
        # Work on a copy of the profile so we can cancel if needed
        self.profile = list(profile) 
        self.on_save = on_save
        self.value_label = value_label
        self.rate_label = rate_label
        
        # --- Input Fields ---
        input_frame = tk.LabelFrame(self.top, text="New Segment", padx=10, pady=10, font=("Arial", 10))
        input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(input_frame, text=f"Start {self.value_label}:", font=("Arial", 10)).grid(row=0, column=0)
        self.ent_start = tk.Entry(input_frame, width=10, font=("Arial", 10))
        self.ent_start.grid(row=1, column=0, padx=5)
        
        tk.Label(input_frame, text=f"Final {self.value_label}:", font=("Arial", 10)).grid(row=0, column=1)
        self.ent_end = tk.Entry(input_frame, width=10, font=("Arial", 10))
        self.ent_end.grid(row=1, column=1, padx=5)
        
        tk.Label(input_frame, text="Duration (hours):", font=("Arial", 10)).grid(row=0, column=2)
        self.ent_duration = tk.Entry(input_frame, width=10, font=("Arial", 10))
        self.ent_duration.grid(row=1, column=2, padx=5)
        
        tk.Button(input_frame, text="Add Segment", command=self.add_segment, font=("Arial", 10)).grid(row=1, column=3, padx=10)

        # --- List Display ---
        list_frame = tk.Frame(self.top)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Style for Treeview
        style = ttk.Style(self.top)
        style.configure("Treeview.Heading", font=("Arial", 10, "bold"))
        style.configure("Treeview", font=("Arial", 10), rowheight=25)

        columns = ("start", "end", "duration", "rate")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=8)
        self.tree.heading("start", text=f"Start {self.value_label}")
        self.tree.heading("end", text=f"Final {self.value_label}")
        self.tree.heading("duration", text="Duration (hours)")
        self.tree.heading("rate", text=self.rate_label)
        
        self.tree.column("start", width=120, anchor="center")
        self.tree.column("end", width=120, anchor="center")
        self.tree.column("duration", width=120, anchor="center")
        self.tree.column("rate", width=120, anchor="center")
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # --- Buttons ---
        btn_frame = tk.Frame(self.top)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Save & Exit", bg="green", fg="white", command=self.save_exit, font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Clear All", bg="red", fg="white", command=self.clear_all, font=("Arial", 10)).pack(side=tk.LEFT, padx=5)

        self.refresh_list()

    def add_segment(self):
        try:
            s = float(self.ent_start.get())
            e = float(self.ent_end.get())
            d = float(self.ent_duration.get())
            
            if d <= 0:
                messagebox.showerror("Error", "Duration must be positive.", parent=self.top)
                return
            
            # Calculate Rate (Bars/hr)
            r = (e - s) / d
            
            self.profile.append({'start': s, 'end': e, 'duration': d, 'rate': r})
            self.refresh_list()
            
            # Auto-fill next start with current end (Convenience)
            self.ent_start.delete(0, tk.END)
            self.ent_start.insert(0, str(e))
            self.ent_end.delete(0, tk.END)
            self.ent_duration.delete(0, tk.END)
            self.ent_end.focus()
        except ValueError:
            messagebox.showerror("Error", "Invalid numbers.", parent=self.top)

    def refresh_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for step in self.profile:
            d = step.get('duration', 0)
            r = step.get('rate', 0)
            self.tree.insert("", tk.END, values=(step['start'], step['end'], d, f"{r:.2f}"))

    def clear_all(self):
        self.profile.clear()
        self.refresh_list()

    def save_exit(self):
        self.on_save(self.profile)
        self.top.destroy()

class PowerControlDialog:
    def __init__(self, master, current_power, target_power, active, on_update):
        self.top = tk.Toplevel(master)
        self.top.title("Power Control")
        self.top.geometry("400x300")
        self.on_update = on_update
        
        # Target Power
        tk.Label(self.top, text="Target Power (Watts):", font=("Arial", 12)).pack(pady=(20, 5))
        self.ent_target = tk.Entry(self.top, font=("Arial", 12), justify='center')
        self.ent_target.insert(0, str(target_power))
        self.ent_target.pack(pady=5)
        
        # Current Power
        self.lbl_power = tk.Label(self.top, text=f"Current Power: {current_power:.2f} W", font=("Arial", 14, "bold"), fg="blue")
        self.lbl_power.pack(pady=20)
        
        # Toggle Button
        btn_text = "STOP Control" if active else "START Control"
        btn_bg = "red" if active else "green"
        self.btn_toggle = tk.Button(self.top, text=btn_text, bg=btn_bg, fg="white", font=("Arial", 12, "bold"), command=self.toggle)
        self.btn_toggle.pack(fill=tk.X, padx=50, pady=10)
        
        self.active = active

    def set_active_state(self, active):
        if self.active != active:
            self.active = active
            btn_text = "STOP Control" if self.active else "START Control"
            btn_bg = "red" if self.active else "green"
            self.btn_toggle.config(text=btn_text, bg=btn_bg)

    def update_readings(self, power, voltage, current):
        self.lbl_power.config(text=f"Power: {power:.2f} W\n({voltage:.2f} V, {current:.2f} A)")

    def toggle(self):
        self.active = not self.active
        try:
            target = float(self.ent_target.get())
        except ValueError:
            target = 0.0
            
        self.btn_toggle.config(text="STOP Control" if self.active else "START Control", bg="red" if self.active else "green")
        self.on_update(self.active, target)

class SystemControlsDialog:
    def __init__(self, master, device_mgr, motor_mgr, serial_lock):
        self.top = tk.Toplevel(master)
        self.top.title("System Controls")
        self.top.geometry("800x600")
        self.device_mgr = device_mgr
        self.motor_mgr = motor_mgr
        self.serial_lock = serial_lock
        
        # Layout: Left Pane (Motors/Purge), Right Pane (Voltage/Calibration)
        left_pane = tk.Frame(self.top)
        left_pane.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        right_pane = tk.Frame(self.top)
        right_pane.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # --- Left Pane: Purge & Motors ---
        # Status Label
        self.lbl_status = tk.Label(left_pane, text="System Ready", font=("Arial", 12, "bold"), fg="blue")
        self.lbl_status.pack(pady=10)

        # Sequence Buttons
        seq_frame = tk.LabelFrame(left_pane, text="Purge Sequences", padx=10, pady=10)
        seq_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(seq_frame, text="START PURGE", bg="green", fg="white", font=("Arial", 10, "bold"), 
                  command=self.start_purge_sequence).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        
        tk.Button(seq_frame, text="STOP / RESET", bg="red", fg="white", font=("Arial", 10, "bold"), 
                  command=self.stop_purge_sequence).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

        # Manual Controls
        man_frame = tk.LabelFrame(left_pane, text="Motor & Valve Controls", padx=10, pady=10)
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

        # Reset Hardware Button
        tk.Button(man_frame, text="RESET HARDWARE", bg="#8B0000", fg="white", command=self.reset_hardware_click).grid(row=4, column=0, columnspan=3, pady=10, sticky="ew")

        # Keyboard Shortcuts
        self.top.bind('<Up>', lambda e: self.send("A+100"))
        self.top.bind('<Down>', lambda e: self.send("A-100"))
        self.top.bind('<Right>', lambda e: self.send("B+100")) 
        self.top.bind('<Left>', lambda e: self.send("B-100"))
        
        tk.Label(man_frame, text="Keys: Up/Down (Up Motor), Left/Right (Down Motor)", font=("Arial", 8, "italic")).grid(row=5, column=0, columnspan=3)

        # --- Right Pane: Calibration ---

        # Calibration
        cal_frame = tk.LabelFrame(right_pane, text="Calibration", padx=10, pady=10)
        cal_frame.pack(fill=tk.X, pady=20)
        
        tk.Button(cal_frame, text="Zero Pressure Calibration", bg="#FFDDDD", command=self.open_zero_pressure).pack(fill=tk.X, pady=5)

    def open_zero_pressure(self):
        ZeroPressureDialog(self.top, self.device_mgr, self.serial_lock)

    def reset_hardware_click(self):
        if messagebox.askyesno("Confirm Reset", "Close valves and reset motors?", parent=self.top):
            self.motor_mgr.reset_hardware()
            self.lbl_status.config(text="Hardware Reset Executed.", fg="black")

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

class SaveSettingsDialog:
    def __init__(self, master, current_dir, current_name, current_interval, on_save):
        self.top = tk.Toplevel(master)
        self.top.title("Save File Settings")
        self.top.geometry("500x350")
        self.on_save = on_save
        self.selected_dir = current_dir

        # Directory Selection
        tk.Label(self.top, text="Save Directory:", font=("Arial", 10, "bold")).pack(anchor="w", padx=20, pady=(20, 5))
        
        dir_frame = tk.Frame(self.top)
        dir_frame.pack(fill=tk.X, padx=20)
        
        self.lbl_dir = tk.Label(dir_frame, text=self.selected_dir, relief="sunken", anchor="w", bg="white", height=2)
        self.lbl_dir.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        tk.Button(dir_frame, text="Browse...", command=self.browse_dir).pack(side=tk.LEFT, padx=(10, 0))

        # Filename Input
        tk.Label(self.top, text="Base File Name:", font=("Arial", 10, "bold")).pack(anchor="w", padx=20, pady=(20, 5))
        
        self.ent_name = tk.Entry(self.top, font=("Arial", 10))
        self.ent_name.insert(0, current_name)
        self.ent_name.pack(fill=tk.X, padx=20)
        
        tk.Label(self.top, text="Format: YYYYMMDD_HHMMSS_FileName.csv", fg="gray", font=("Arial", 8, "italic")).pack(anchor="w", padx=20)

        # Interval Input
        tk.Label(self.top, text="Save Interval (minutes):", font=("Arial", 10, "bold")).pack(anchor="w", padx=20, pady=(20, 5))
        self.ent_interval = tk.Entry(self.top, font=("Arial", 10))
        self.ent_interval.insert(0, str(current_interval))
        self.ent_interval.pack(fill=tk.X, padx=20)

        # Buttons
        btn_frame = tk.Frame(self.top)
        btn_frame.pack(pady=30)
        
        tk.Button(btn_frame, text="Save Settings", bg="green", fg="white", width=15, command=self.save).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Cancel", width=10, command=self.top.destroy).pack(side=tk.LEFT, padx=10)

    def browse_dir(self):
        d = filedialog.askdirectory(initialdir=self.selected_dir)
        if d:
            self.selected_dir = d
            self.lbl_dir.config(text=d)

    def save(self):
        name = self.ent_name.get().strip()
        if not name:
            messagebox.showerror("Error", "File name cannot be empty.", parent=self.top)
            return
            
        try:
            interval = float(self.ent_interval.get())
            if interval <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Interval must be a positive number.", parent=self.top)
            return
        self.on_save(self.selected_dir, name, interval)
        self.top.destroy()

class ToggleSwitch(tk.Canvas):
    """A modern toggle switch widget to replace standard checkboxes."""
    def __init__(self, parent, text, variable, command=None, bg="#2b2b3b", active_color="#00ffff"):
        super().__init__(parent, width=260, height=30, bg=bg, highlightthickness=0)
        self.variable = variable
        self.command = command
        self.active_color = active_color
        self.text = text
        
        self.bind("<Button-1>", self.toggle)
        self.variable.trace_add("write", self.update_ui)
        self.update_ui()

    def toggle(self, event=None):
        self.variable.set(not self.variable.get())
        if self.command:
            self.command()

    def update_ui(self, *args):
        self.delete("all")
        state = self.variable.get()
        
        # Dimensions
        h = 20
        w = 40
        x = 200 # Switch position (right aligned, moved right for more text space)
        y = 5
        
        # Draw Text
        self.create_text(5, 15, text=self.text, fill="white", anchor="w", font=("Arial", 12))
        
        if HAS_PILLOW:
            # Supersampling for smooth edges
            scale = 4
            img_w = int(w * scale)
            img_h = int(h * scale)
            
            # Create transparent image
            image = Image.new("RGBA", (img_w, img_h), (0, 0, 0, 0))
            draw = ImageDraw.Draw(image)
            
            color = self.active_color if state else "#555566"
            
            # Draw Track (Pill shape)
            draw.ellipse((0, 0, h*scale, h*scale), fill=color)
            draw.ellipse(((w-h)*scale, 0, w*scale, h*scale), fill=color)
            draw.rectangle(((h/2)*scale, 0, (w-h/2)*scale, h*scale), fill=color)
            
            # Draw Handle
            pad = 2 * scale
            r = (h * scale) // 2 - pad
            cy = (h * scale) // 2
            cx = (w * scale) - (h * scale) // 2 if state else (h * scale) // 2
                
            draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill="white")
            
            # Resize down with high quality resampling
            resample_method = Image.Resampling.LANCZOS if hasattr(Image, 'Resampling') else Image.LANCZOS
            image = image.resize((w, h), resample_method)
            
            self.tk_image = ImageTk.PhotoImage(image)
            self.create_image(x, y, image=self.tk_image, anchor="nw")
        else:
            # Fallback to standard canvas drawing
            color = self.active_color if state else "#555566"
            self.create_oval(x, y, x+h, y+h, fill=color, outline="")
            self.create_oval(x+w-h, y, x+w, y+h, fill=color, outline="")
            self.create_rectangle(x+h/2, y, x+w-h/2, y+h, fill=color, outline="")
            
            r = h/2 - 2
            cx = x+w-h/2 if state else x+h/2
            cy = y+h/2
            self.create_oval(cx-r, cy-r, cx+r, cy+r, fill="white", outline="")

class BaseAPGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("EPL MAP Control")
        self.root.configure(bg="#F0F0F0")
        
        # --- Theme Colors ---
        self.colors = {
            "bg": "#1e1e2e",        # Main Background (Dark Navy)
            "card": "#2b2b3b",      # Card Background (Lighter Navy)
            "text": "#ffffff",      # Primary Text
            "subtext": "#b0b0b0",   # Secondary Text
            "accent": "#00ffff",    # Cyan Highlight
            "success": "#4caf50",   # Green
            "danger": "#f44336",    # Red
            "btn_bg": "#3e3e4e"     # Button Background
        }

        self.device_mgr = DeviceManager()
        self.motor_mgr = MotorValveController() # Second serial port controller
        self.target_voltage = 0.0 # Tracks the state for Port 5 (Omega)
        
        self.view_mode = "ALL" # "ALL" or "SINGLE"
        
        # Threading synchronization
        self.serial_lock = threading.Lock()
        self.data_queue = queue.Queue()
        self.polling_active = False
        self.pressure_profile = [] # Stores the pressure recipe
        self.temperature_profile = []
        self.power_profile = []
        self.pressure_control_active = False
        self.last_valid_readings = {1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0, 5: 0.0}
        
        self.manual_voltage_active = False
        # Save Settings Defaults
        self.save_dir = os.path.join(os.path.expanduser("~"), "Documents")
        self.base_filename = "PressData"
        self.save_interval_min = 1.0
        self.last_file_save_time = 0.0
        self.last_display_update_time = 0.0
        
        # Power Control State
        self.power_control_active = False
        self.temp_control_active = False
        self.target_power_watts = 0.0
        self.power_dialog = None
        
        # Graphing State
        self.current_view = "Temperature"
        self.data_history = {"Temperature": [], "Pressure": [], "Power": []}
        self.start_time = time.time()
        self.recording_active = False

        # Configure Root
        self.root.configure(bg=self.colors["bg"])
        self.root.geometry("1280x800")

        self.create_widgets()
        
        # Attempt connection and start polling
        self.root.after(200, self.connect_hardware)

    def create_widgets(self):
        # --- Main Layout Containers ---
        # Sidebar (Left)
        self.sidebar = tk.Frame(self.root, bg=self.colors["card"], width=250)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False) # Enforce width

        # Main Content (Right)
        self.main_content = tk.Frame(self.root, bg=self.colors["bg"])
        self.main_content.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=20, pady=20)

        # --- Sidebar Content ---
        # Logo Area
        logo_frame = tk.Frame(self.sidebar, bg=self.colors["card"], height=150)
        logo_frame.pack(fill=tk.X, padx=0, pady=0)

        try:
            logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Logo_CarnegieScience_primary_white_RGB.png")
            if os.path.exists(logo_path):
                if HAS_PILLOW:
                    pil_img = Image.open(logo_path)
                    target_h = 120
                    ratio = target_h / pil_img.height
                    target_w = int(pil_img.width * ratio)
                    pil_img = pil_img.resize((target_w, target_h), Image.Resampling.LANCZOS if hasattr(Image, 'Resampling') else Image.LANCZOS)
                    self.logo_img = ImageTk.PhotoImage(pil_img)
                else:
                    self.logo_img = tk.PhotoImage(file=logo_path)
                    if self.logo_img.height() > 120:
                        self.logo_img = self.logo_img.subsample(self.logo_img.height() // 120)
                tk.Label(logo_frame, image=self.logo_img, bg=self.colors["card"]).pack(pady=10)
        except Exception as e:
            print(f"Logo load error: {e}")

        # Sidebar Menu Label
        # tk.Label(self.sidebar, text="CONTROLS", bg=self.colors["card"], fg=self.colors["subtext"], font=("Arial", 10, "bold"), anchor="w").pack(fill=tk.X, padx=20, pady=(20, 10))

        # Sidebar Buttons
        buttons = [
            ("START PROCESS", self.colors["success"], self.start_process),
            ("STOP PROCESS", self.colors["danger"], self.stop_process),
            ("Save Settings", self.colors["btn_bg"], self.open_save_settings),
            ("System Controls", self.colors["btn_bg"], self.open_system_controls),
            ("Thermocouple Config", self.colors["btn_bg"], self.open_temp_config),
            ("Developer Mode", self.colors["btn_bg"], self.open_developer_mode),
            ("EXIT", self.colors["btn_bg"], self.cleanup_and_exit)
        ]

        for text, color, cmd in buttons:
            btn = tk.Button(self.sidebar, text=text, bg=color, fg="white", font=("Arial", 11), relief="flat", padx=10, pady=8, command=cmd, cursor="hand2")
            btn.pack(fill=tk.X, padx=15, pady=5)

        # --- Main Content Area ---
        
        # Header Title
        title_frame = tk.Frame(self.main_content, bg=self.colors["bg"])
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(title_frame, text="EPL Multi Anvil Press Controls", font=("Arial", 24, "bold"), bg=self.colors["bg"], fg=self.colors["text"]).pack(side=tk.LEFT)
        
        # Status Indicator
        # self.lbl_system_status = tk.Label(title_frame, text="STANDBY", font=("Arial", 12, "bold"), bg=self.colors["bg"], fg=self.colors["danger"])
        # self.lbl_system_status.pack(side=tk.RIGHT, padx=10)
        # tk.Label(title_frame, text="STATUS:", font=("Arial", 10, "bold"), bg=self.colors["bg"], fg=self.colors["subtext"]).pack(side=tk.RIGHT)
        # Status Indicator (Moved to Graph Card)
        # self.lbl_system_status = tk.Label(title_frame, text="STANDBY", font=("Arial", 12, "bold"), bg=self.colors["bg"], fg=self.colors["danger"])
        # self.lbl_system_status.pack(side=tk.RIGHT, padx=10)
        # tk.Label(title_frame, text="STATUS:", font=("Arial", 10, "bold"), bg=self.colors["bg"], fg=self.colors["subtext"]).pack(side=tk.RIGHT)

        # --- Top Row: Readouts ---
        readout_container = tk.Frame(self.main_content, bg=self.colors["bg"])
        readout_container.pack(fill=tk.X, pady=(0, 20))

        headers = [
            ("Temperature (C)", self.colors["accent"]), 
            ("Pressure (Bars)", self.colors["success"]), 
            ("Voltage (V)", "#ff9800"), 
            ("Current (A)", "#e91e63"), 
            ("Power (W)", "#9c27b0")
        ]
        
        self.readout_labels = []
        for i, (text, color) in enumerate(headers):
            card = tk.Frame(readout_container, bg=self.colors["card"], padx=15, pady=10)
            card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0 if i==0 else 10, 0))
            
            tk.Label(card, text=text, fg=color, bg=self.colors["card"], font=("Arial", 14, "bold")).pack(anchor="w")
            val = tk.Label(card, text="---", fg=self.colors["text"], bg=self.colors["card"], font=("Arial", 20, "bold"))
            val.pack(anchor="e", pady=(5, 0))
            self.readout_labels.append(val)

        # --- Middle Row: Graph ---
        graph_card = tk.Frame(self.main_content, bg=self.colors["card"], padx=2, pady=2)
        graph_card.pack(fill=tk.BOTH, expand=True, pady=(0, 20))

        # Graph Controls
        graph_ctrl_frame = tk.Frame(graph_card, bg=self.colors["card"])
        graph_ctrl_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # tk.Label(graph_ctrl_frame, text="LIVE VISUALIZATION", fg=self.colors["subtext"], bg=self.colors["card"], font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        tk.Label(graph_ctrl_frame, text="STATUS:", font=("Arial", 10, "bold"), bg=self.colors["card"], fg=self.colors["subtext"]).pack(side=tk.LEFT)
        self.lbl_system_status = tk.Label(graph_ctrl_frame, text="STANDBY", font=("Arial", 12, "bold"), bg=self.colors["card"], fg=self.colors["danger"])
        self.lbl_system_status.pack(side=tk.LEFT, padx=5)
        
        tk.Button(graph_ctrl_frame, text="RESET VIEW", bg=self.colors["btn_bg"], fg="white", font=("Arial", 9), 
                      command=self.set_all_view, relief="flat").pack(side=tk.RIGHT, padx=2)

        # Canvas Container
        self.graph_container = tk.Frame(graph_card, bg=self.colors["card"])
        self.graph_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        self.canvases = {}
        self.canvas_configs = {
            "Temperature": {"color": self.colors["accent"]},
            "Pressure": {"color": self.colors["success"]},
            "Power": {"color": "#ff9800"}
        }

        for view in ["Temperature", "Pressure", "Power"]:
            cv = tk.Canvas(self.graph_container, bg=self.colors["card"], highlightthickness=1, highlightbackground=self.colors["bg"])
            cv.bind("<Button-1>", lambda event, v=view: self.toggle_maximize(v))
            cv.bind("<Configure>", lambda event, v=view: self.draw_single_graph(v))
            self.canvases[view] = cv
        
        self.update_graph_layout()

        # --- Bottom Row: Controls ---
        controls_container = tk.Frame(self.main_content, bg=self.colors["bg"])
        controls_container.pack(fill=tk.X)

        # Auto Control Card
        auto_card = tk.Frame(controls_container, bg=self.colors["card"], padx=15, pady=15)
        auto_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        tk.Label(auto_card, text="AUTOMATION PROFILES", fg=self.colors["accent"], bg=self.colors["card"], font=("Arial", 14, "bold")).pack(anchor="w", pady=(0, 10))
        
        # Grid for Auto Controls
        auto_grid = tk.Frame(auto_card, bg=self.colors["card"])
        auto_grid.pack(fill=tk.X)

        # Helper for styled buttons
        def style_btn(parent, text, cmd):
            return tk.Button(parent, text=text, command=cmd, bg=self.colors["btn_bg"], fg="white", relief="flat", font=("Arial", 12))

        def style_chk(parent, text, var, cmd, color):
            return ToggleSwitch(parent, text=text, variable=var, command=cmd, bg=self.colors["card"], active_color=color)

        # Temperature
        style_btn(auto_grid, "Load Temp Profile", self.open_temp_profile).grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        self.var_auto_temp = tk.BooleanVar(value=False)
        self.chk_auto_temp = style_chk(auto_grid, "Enable Auto Temp", self.var_auto_temp, self.toggle_temp_control_check, self.colors["accent"])
        self.chk_auto_temp.grid(row=0, column=1, padx=5, pady=8, sticky="w")

        # Pressure
        style_btn(auto_grid, "Load Pressure Profile", self.open_pressure_config).grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        
        self.var_auto_press = tk.BooleanVar(value=False)
        self.chk_auto_press = style_chk(auto_grid, "Enable Auto Pressure", self.var_auto_press, self.toggle_press_control_check, self.colors["success"])
        self.chk_auto_press.grid(row=1, column=1, padx=5, pady=8, sticky="w")

        # Power
        style_btn(auto_grid, "Load Power Profile", self.open_power_profile).grid(row=2, column=0, padx=5, pady=5, sticky="ew")
        
        self.var_auto_power = tk.BooleanVar(value=False)
        self.chk_auto_power = style_chk(auto_grid, "Enable Auto Power", self.var_auto_power, self.toggle_power_control_check, "#ff9800")
        self.chk_auto_power.grid(row=2, column=1, padx=5, pady=8, sticky="w")

        # Manual Control Card
        manual_card = tk.Frame(controls_container, bg=self.colors["card"], padx=15, pady=15)
        manual_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        tk.Label(manual_card, text="MANUAL OVERRIDE", fg=self.colors["accent"], bg=self.colors["card"], font=("Arial", 14, "bold")).pack(anchor="w", pady=(0, 10))

        self.btn_manual_voltage = tk.Button(manual_card, text="Start Manual Control", bg=self.colors["btn_bg"], fg="white", relief="flat", command=self.toggle_manual_voltage, font=("Arial", 12))
        self.btn_manual_voltage.pack(fill=tk.X, padx=5, pady=2)
        
        target_frame = tk.Frame(manual_card, bg=self.colors["card"])
        target_frame.pack(fill=tk.X, pady=2, padx=5)
        
        tk.Label(target_frame, text="Output:", bg=self.colors["card"], fg="white", font=("Arial", 12)).pack(side=tk.LEFT)
        self.ent_target_voltage = tk.Entry(target_frame, width=6, bg=self.colors["bg"], fg="white", insertbackground="white", relief="flat", font=("Arial", 12))
        self.ent_target_voltage.pack(side=tk.LEFT, padx=5)
        self.ent_target_voltage.insert(0, "0.00")
        tk.Button(target_frame, text="SET", bg=self.colors["accent"], fg="black", font=("Arial", 10, "bold"), relief="flat", command=self.set_manual_voltage_direct).pack(side=tk.LEFT)
        
        adj_frame = tk.Frame(manual_card, bg=self.colors["card"])
        adj_frame.pack(fill=tk.X, pady=2)
        
        tk.Button(adj_frame, text="-", width=3, bg=self.colors["btn_bg"], fg="white", relief="flat", command=lambda: self.manual_step_voltage(-1), font=("Arial", 12, "bold")).pack(side=tk.LEFT, padx=5)
        self.ent_manual_inc = tk.Entry(adj_frame, width=5, bg=self.colors["bg"], fg="white", insertbackground="white", relief="flat", justify="center", font=("Arial", 12))
        self.ent_manual_inc.insert(0, "0.05")
        self.ent_manual_inc.pack(side=tk.LEFT, padx=5)
        tk.Button(adj_frame, text="+", width=3, bg=self.colors["btn_bg"], fg="white", relief="flat", command=lambda: self.manual_step_voltage(1), font=("Arial", 12, "bold")).pack(side=tk.LEFT, padx=5)

        # Quench Button
        tk.Button(manual_card, text="ZERO OUTPUT", bg="#D32F2F", fg="white", font=("Arial", 12, "bold"), relief="flat", command=self.quench_output).pack(fill=tk.X, padx=5, pady=(15, 5))

    def toggle_manual_voltage(self):
        self.manual_voltage_active = not self.manual_voltage_active
        if self.manual_voltage_active:
            self.btn_manual_voltage.config(text="STOP MANUAL CONTROL", bg=self.colors["danger"], fg="white")
            # Disable conflicting auto controls
            if self.power_control_active:
                self.var_auto_power.set(False)
                self.power_control_active = False
                print("Auto Power Control disabled for Manual Output Control.")
        else:
            self.btn_manual_voltage.config(text="Start Manual Control", bg=self.colors["btn_bg"], fg="white")

    def manual_step_voltage(self, sign):
        if not self.manual_voltage_active:
            messagebox.showwarning("Manual Control", "Please start Manual Control first.")
            return
            
        try:
            step = float(self.ent_manual_inc.get())
        except ValueError:
            step = 0.05
        
        self.adjust_voltage(sign * step)

    def set_manual_voltage_direct(self):
        if not self.manual_voltage_active:
            messagebox.showwarning("Manual Control", "Please start Manual Control first.")
            return
        try:
            val = float(self.ent_target_voltage.get())
            self.target_voltage = max(0.0, min(10.0, val))
            # Refresh entry in case it was clamped
            self.ent_target_voltage.delete(0, tk.END)
            self.ent_target_voltage.insert(0, f"{self.target_voltage:.2f}")
            
            with self.serial_lock:
                self.device_mgr.set_omega_voltage(self.target_voltage)
        except ValueError:
            messagebox.showerror("Error", "Invalid voltage value.")

    def adjust_voltage(self, delta):
        """Manually adjusts the target voltage."""
        self.target_voltage += delta
        self.target_voltage = max(0.0, min(10.0, self.target_voltage))
        
        self.ent_target_voltage.delete(0, tk.END)
        self.ent_target_voltage.insert(0, f"{self.target_voltage:.2f}")
        
        with self.serial_lock:
            self.device_mgr.set_omega_voltage(self.target_voltage)

    def quench_output(self):
        """Immediately sets output voltage to 0 and stops automation."""
        self.target_voltage = 0.0
        self.ent_target_voltage.delete(0, tk.END)
        self.ent_target_voltage.insert(0, "0.00")
        
        # Disable Auto Power if active
        if self.power_control_active:
            self.power_control_active = False
            self.var_auto_power.set(False)
            
        # Force 0V
        with self.serial_lock:
            self.device_mgr.set_omega_voltage(0.0)
        print("QUENCH executed: Output set to 0V")

    def set_all_view(self):
        self.view_mode = "ALL"
        self.update_graph_layout()
        self.redraw_visible_graphs()

    def toggle_maximize(self, view_name):
        if self.view_mode == "ALL":
            self.view_mode = "SINGLE"
            self.current_view = view_name
        else:
            self.view_mode = "ALL"
        self.update_graph_layout()
        self.redraw_visible_graphs()

    def update_graph_layout(self):
        for cv in self.canvases.values():
            cv.pack_forget()
            
        if self.view_mode == "ALL":
            for view in ["Temperature", "Pressure", "Power"]:
                self.canvases[view].pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=2)
        else:
            self.canvases[self.current_view].pack(fill=tk.BOTH, expand=True)

    def redraw_visible_graphs(self):
        if self.view_mode == "ALL":
            for view in ["Temperature", "Pressure", "Power"]:
                self.draw_single_graph(view)
        else:
            self.draw_single_graph(self.current_view)

    def draw_single_graph(self, view_name, event=None):
        canvas = self.canvases[view_name]
        canvas.delete("all")
        
        w = canvas.winfo_width()
        h = canvas.winfo_height()
        if w < 10 or h < 10: return
        
        # Margins
        x_margin = 40
        y_margin = 30
        plot_w = w - x_margin - 20
        plot_h = h - y_margin - 40
        
        # Display names with units
        display_names = {
            "Temperature": "Temperature (C)",
            "Pressure": "Pressure (Bars)",
            "Power": "Power (W)"
        }
        display_text = display_names.get(view_name, view_name)

        # Draw Title
        canvas.create_text(w/2, 20, text=f"{display_text} vs Time", font=("Arial", 12, "bold"), fill="white")

        # Draw Grid
        for i in range(1, 5):
            # Vertical
            x = i * (w / 5)
            canvas.create_line(x, 40, x, h-30, fill="#444455", dash=(2, 4))

            # Horizontal
            y = 40 + i * ((h-70) / 5)
            canvas.create_line(40, y, w-20, y, fill="#444455", dash=(2, 4))

        # Draw Axes
        canvas.create_rectangle(40, 40, w-20, h-30, outline="white", width=2)
        
        # Axis Labels
        canvas.create_text(w/2, h-10, text="Time (s)", font=("Arial", 10), fill="#b0b0b0")
        canvas.create_text(15, h/2, text=display_text, angle=90, font=("Arial", 10), fill="#b0b0b0")
        
        # Plot Data
        data = self.data_history.get(view_name, [])
        if len(data) > 1:
            times = [p[0] for p in data]
            values = [p[1] for p in data]
            
            # Auto-scale
            min_t, max_t = times[0], times[-1]
            min_v, max_v = min(values), max(values)
            
            # --- Y-Axis Scaling ---
            # Set top of graph 10% higher than max value, per request
            if max_v > 0:
                display_max_v = max_v * 1.1
            elif max_v < 0:
                display_max_v = max_v * 0.9 # Closer to zero
            else: # max_v is 0
                display_max_v = 1.0

            # Pad the bottom slightly for better appearance
            v_range_for_padding = display_max_v - min_v
            display_min_v = min_v - v_range_for_padding * 0.05

            # Handle flat lines or very small ranges
            if (display_max_v - display_min_v) < 1e-6:
                display_max_v = max_v + 0.5
                display_min_v = min_v - 0.5

            # --- X-Axis Scaling ---
            if max_t == min_t: max_t += 1.0

            # --- Draw Axis Ticks and Labels ---
            num_ticks = 5
            # Y-Axis Ticks
            y_plot_range = display_max_v - display_min_v
            for i in range(num_ticks):
                val = display_min_v + (i / (num_ticks - 1)) * y_plot_range
                y_pos = (h - y_margin) - (i / (num_ticks - 1)) * plot_h
                canvas.create_text(x_margin - 5, y_pos, text=f"{val:.1f}", anchor="e", fill="#b0b0b0", font=("Arial", 8))
            
            # X-Axis Ticks
            x_plot_range = max_t - min_t
            for i in range(num_ticks):
                val = min_t + (i / (num_ticks - 1)) * x_plot_range
                x_pos = x_margin + (i / (num_ticks - 1)) * plot_w
                canvas.create_text(x_pos, h - y_margin + 10, text=f"{val:.0f}", anchor="n", fill="#b0b0b0", font=("Arial", 8))

            # --- Plotting ---
            points = []
            for t, v in data:
                x = x_margin + (t - min_t) / x_plot_range * plot_w
                y = (h - y_margin) - (v - display_min_v) / y_plot_range * plot_h
                points.extend([x, y])
            
            canvas.create_line(points, fill=self.canvas_configs[view_name]["color"], width=2)
        else: # Handle case with no or single data point
            canvas.create_text(w/2, h/2, text="No data to display", fill="#666677", font=("Arial", 12))

    def on_click(self):
        print("Button clicked")

    def toggle_temp_control_check(self):
        if self.var_auto_temp.get():
            if not self.temperature_profile:
                messagebox.showwarning("Warning", "No temperature profile loaded.", parent=self.root)
                self.var_auto_temp.set(False)
                return
            self.temp_control_active = True
        else:
            self.temp_control_active = False

    def toggle_press_control_check(self):
        if self.var_auto_press.get():
            if not self.pressure_profile:
                messagebox.showwarning("Warning", "No pressure profile loaded.", parent=self.root)
                self.var_auto_press.set(False)
                return
            self.pressure_control_active = True
        else:
            self.pressure_control_active = False

    def toggle_power_control_check(self):
        if self.var_auto_power.get():
            if not self.power_profile:
                messagebox.showwarning("Warning", "No power profile loaded.", parent=self.root)
                self.var_auto_power.set(False)
                return
            self.power_control_active = True
        else:
            self.power_control_active = False

    def start_process(self):
        """Starts recording data and plotting."""
        self.data_history = {"Temperature": [], "Pressure": [], "Power": []}
        self.start_time = time.time()
        self.recording_active = True

        # Activate Pressure Control if profile exists
        if self.pressure_profile:
            self.pressure_control_active = True
            self.var_auto_press.set(True)
            print(f"Pressure Control Started: {len(self.pressure_profile)} segments.")
        else:
            self.pressure_control_active = False
            self.var_auto_press.set(False)
            
        if self.temperature_profile:
            self.temp_control_active = True
            self.var_auto_temp.set(True)
        else:
            self.temp_control_active = False
            self.var_auto_temp.set(False)
            
        if self.power_profile:
            self.power_control_active = True
            self.var_auto_power.set(True)
        else:
            self.power_control_active = False
            self.var_auto_power.set(False)
        
        # Generate Filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.csv_filename = os.path.join(self.save_dir, f"{timestamp}_{self.base_filename}.csv")
        print(f"Process Started: Recording Data to {self.csv_filename}")
        self.last_file_save_time = 0.0 # Force immediate save on first loop
        self.last_display_update_time = 0.0 # Force immediate graph update

        # Write Header
        try:
            with open(self.csv_filename, "w") as f:
                f.write("Timestamp,Temperature,Pressure,Voltage,Current,Power,Resistance\n")
        except Exception as e:
            print(f"Error creating file: {e}")
            
    def stop_process(self):
        """Stops recording data."""
        self.pressure_control_active = False
        self.var_auto_press.set(False)
        self.power_control_active = False
        self.var_auto_power.set(False)
        self.temp_control_active = False
        self.var_auto_temp.set(False)
        
        self.recording_active = False
        print("Process Stopped.")

    def connect_hardware(self):
        """Opens serial ports or enables simulation mode if they fail."""
        in_simulation_mode = False

        # Attempt to open device manager port
        if self.device_mgr.open():
            print("Device manager port opened successfully.")
            # Initialize meters based on ModuleAP10.bas
            self.device_mgr.initialize_texmate_meters()
        else:
            print("Failed to open device manager port. Enabling simulation for devices.")
            self.device_mgr.enable_simulation()
            in_simulation_mode = True
        
        # print("DAX connection disabled. Enabling simulation for devices.")
        # self.device_mgr.enable_simulation()
        # in_simulation_mode = True
            
        # Attempt to open motor port as well
        if self.motor_mgr.open():
            print("Motor/Valve port opened successfully.")
        else:
            print("Failed to open Motor/Valve port. Enabling simulation for motors.")
            self.motor_mgr.enable_simulation()
            in_simulation_mode = True
        
        # print("DAX (Motor/Valve) connection disabled. Enabling simulation for motors.")
        # self.motor_mgr.enable_simulation()
        # in_simulation_mode = True

        # If any port failed, open the developer console to show simulated traffic
        if in_simulation_mode:
            self.open_developer_mode()

        # Start the polling loop, which will now work in either real or simulated mode
        self.polling_active = True
        # Start background thread for data acquisition
        self.poll_thread = threading.Thread(target=self.data_acquisition_loop, daemon=True)
        self.poll_thread.start()
        # Start UI update loop
        self.update_gui_loop()

    def data_acquisition_loop(self):
        """Background thread to handle blocking serial I/O."""
        while self.polling_active:
            data_snapshot = {}
            port_mapping = [1, 2, 3, 4, 5]
            
            # Read all ports
            for port in port_mapping:
                val_str = "---"
                with self.serial_lock:
                    if port == 5:
                        # Omega Device
                        resp = self.device_mgr.send_omega_cmd("$1RD")
                        if resp and len(resp) >= 3:
                            val_str = resp[2:]
                    else:
                        # Texmate Devices
                        resp = self.device_mgr.send_texmate_cmd(port, "SR")
                        if resp:
                            val_str = resp
                
                data_snapshot[port] = val_str
                # Small delay to ensure Mux is ready for next command
                time.sleep(0.1)

            # Handle Power Control Write (if active)
            if self.power_control_active:
                with self.serial_lock:
                    self.device_mgr.set_omega_voltage(self.target_voltage)

            # Send data to UI
            self.data_queue.put(data_snapshot)
            
            # Loop delay
            time.sleep(0.5)

    def update_gui_loop(self):
        """Reads from queue and updates UI on the main thread."""
        # Variables for Power Control
        meas_temp = self.last_valid_readings[1]
        meas_press = self.last_valid_readings[2]
        meas_volts = self.last_valid_readings[3]
        meas_amps = self.last_valid_readings[4]
        
        # Drain queue to get latest data
        latest_data = None
        while not self.data_queue.empty():
            latest_data = self.data_queue.get()
            
        # Get current time for update checks
        current_time = time.time()

        if latest_data:
            port_mapping = [1, 2, 3, 4, 5]
            for i, port in enumerate(port_mapping):
                val_str = latest_data.get(port, "---")
                
                # Update labels (except Resistance at index 4, which is calculated)
                if i != 4:
                    self.readout_labels[i].config(text=val_str)
                
                # Parse values for control loop (Port 3=Volts, Port 4=Amps)
                try:
                    # Handle simulation or raw strings
                    if "OVER" in val_str:
                        val = 0.0
                    else:
                        clean_val = val_str.replace('+', '').replace('SIM_ACK', '0')
                        val = float(clean_val)
                    
                    self.last_valid_readings[port] = val
                    
                    if port == 1: meas_temp = val
                    if port == 2: meas_press = val
                    if port == 3: meas_volts = val
                    if port == 4: meas_amps = val
                except ValueError:
                    pass
            
        # Calculate Power
        current_power = meas_volts * meas_amps

        # Calculate Resistance (R = V / I)
        meas_res = 0.0
        if abs(meas_amps) > 0.0001:
            meas_res = meas_volts / meas_amps
        self.readout_labels[4].config(text=f"{current_power:.2f}")

        # Pressure Control Loop (Profile Execution)
        if self.pressure_control_active and self.pressure_profile:
            # Calculate elapsed time in hours
            elapsed_hours = (time.time() - self.start_time) / 3600.0
            
            target_pressure = 0.0
            accumulated_time = 0.0
            active_segment = None
            
            for segment in self.pressure_profile:
                duration = segment['duration']
                if elapsed_hours < (accumulated_time + duration):
                    # We are in this segment
                    time_in_seg = elapsed_hours - accumulated_time
                    # Linear interpolation: Start + (Rate * Time)
                    target_pressure = segment['start'] + (segment['rate'] * time_in_seg)
                    active_segment = segment
                    break
                accumulated_time += duration
            
            if active_segment is None:
                print("Pressure Profile Completed.")
                self.pressure_control_active = False
                self.var_auto_press.set(False)

        # Temperature Control Loop (Profile Execution)
        if self.temp_control_active and self.temperature_profile:
            elapsed_hours = (time.time() - self.start_time) / 3600.0
            target_temp = 0.0
            accumulated_time = 0.0
            active_segment = None
            for segment in self.temperature_profile:
                duration = segment['duration']
                if elapsed_hours < (accumulated_time + duration):
                    time_in_seg = elapsed_hours - accumulated_time
                    target_temp = segment['start'] + (segment['rate'] * time_in_seg)
                    active_segment = segment
                    break
                accumulated_time += duration
            if active_segment is None:
                print("Temperature Profile Completed.")
                self.temp_control_active = False
                self.var_auto_temp.set(False)
            # Note: Actual PID control for temp not implemented, just profile calculation

        # Power Control Loop (Profile Execution)
        if self.power_control_active and self.power_profile:
            elapsed_hours = (time.time() - self.start_time) / 3600.0
            target_power = 0.0
            accumulated_time = 0.0
            active_segment = None
            for segment in self.power_profile:
                duration = segment['duration']
                if elapsed_hours < (accumulated_time + duration):
                    time_in_seg = elapsed_hours - accumulated_time
                    target_power = segment['start'] + (segment['rate'] * time_in_seg)
                    active_segment = segment
                    break
                accumulated_time += duration
            if active_segment is None:
                print("Power Profile Completed.")
                self.power_control_active = False
                self.var_auto_power.set(False)
            else:
                self.target_power_watts = target_power
        
        if self.recording_active:
            # 1. Display Update (Graphing) - Every 1 second
            if (current_time - self.last_display_update_time) >= 1.0:
                self.last_display_update_time = current_time
                # Update History
                timestamp = time.time() - self.start_time
                self.data_history["Temperature"].append((timestamp, meas_temp))
                self.data_history["Pressure"].append((timestamp, meas_press))
                self.data_history["Power"].append((timestamp, current_power))
                
                # Keep history manageable (e.g., last 7200 points. At 1 sec/point, this is 2 hours)
                for key in self.data_history:
                    if len(self.data_history[key]) > 7200:
                        self.data_history[key].pop(0)
                
                # Refresh Graph
                self.redraw_visible_graphs()

            # 2. Write to File (Check Interval)
            if (current_time - self.last_file_save_time) >= (self.save_interval_min * 60):
                try:
                    file_timestamp = time.time() - self.start_time
                    with open(self.csv_filename, "a") as f:
                        line = f"{file_timestamp:.2f},{meas_temp:.2f},{meas_press:.2f},{meas_volts:.2f},{meas_amps:.2f},{current_power:.2f},{meas_res:.4f}\n"
                        f.write(line)
                    self.last_file_save_time = current_time
                    print(f"Data saved to file (Interval: {self.save_interval_min}m)")
                except Exception as e:
                    print(f"File Write Error: {e}")
        
        # Update Power Dialog if open
        if self.power_dialog and self.power_dialog.top.winfo_exists():
            self.power_dialog.update_readings(current_power, meas_volts, meas_amps)
            self.power_dialog.set_active_state(self.power_control_active)
        else:
            self.power_dialog = None

        # Power Control Loop
        if self.power_control_active:
            error = self.target_power_watts - current_power
            # Simple Integral Control: Adjust voltage by a small fraction of the error
            # Gain K = 0.01 (Conservative starting point)
            adjustment = error * 0.01
            
            # Apply adjustment
            self.target_voltage += adjustment
            
            # Clamp to safe limits (0-10V)
            self.target_voltage = max(0.0, min(10.0, self.target_voltage))
            
            # Note: The background thread handles the actual writing of self.target_voltage

        # Update Status Bar
        self.update_system_status()

        # Schedule next update
        if self.polling_active:
            self.root.after(100, self.update_gui_loop)

    def update_voltage_state(self, new_voltage):
        """Callback to update target voltage from Manual Control Dialog."""
        self.target_voltage = new_voltage

    def update_system_status(self):
        """Updates the status bar text based on active flags."""
        if not self.recording_active:
            self.lbl_system_status.config(text="STANDBY", fg=self.colors["danger"])
            return

        states = []
        
        if self.pressure_control_active:
            states.append("AUTO PRESS")
        
        if self.power_control_active:
            states.append("AUTO POWER")
        elif self.target_voltage > 0.0:
            states.append(f"MANUAL ({self.target_voltage:.2f}V)")
            
        if self.temp_control_active:
            states.append("AUTO TEMP")
            
        if not states:
            status_text = "MONITORING"
            color = self.colors["accent"]
        else:
            status_text = " | ".join(states)
            color = self.colors["success"]
            
        self.lbl_system_status.config(text=status_text, fg=color)

    def open_save_settings(self):
        """Opens the Save Settings Dialog."""
        SaveSettingsDialog(self.root, self.save_dir, self.base_filename, self.save_interval_min, self.save_settings_callback)

    def save_settings_callback(self, new_dir, new_name, new_interval):
        self.save_dir = new_dir
        self.base_filename = new_name
        self.save_interval_min = new_interval

    def open_temp_config(self):
        """Opens the Thermocouple Configuration Dialog."""
        ThermocoupleDialog(self.root, self.device_mgr, self.serial_lock)

    def open_pressure_config(self):
        """Opens the Pressure Profile Dialog."""
        ProfileEditorDialog(self.root, self.pressure_profile, self.save_pressure_profile, title="Input Pressure Profile", value_label="Pressure (Bars)", rate_label="Rate (Bars/Hr)")

    def save_pressure_profile(self, new_profile):
        self.pressure_profile = new_profile
        print(f"Pressure Profile Saved: {len(self.pressure_profile)} segments")

    def open_temp_profile(self):
        ProfileEditorDialog(self.root, self.temperature_profile, self.save_temp_profile, title="Input Temperature Profile", value_label="Temperature (C)", rate_label="Rate (C/Hr)")

    def save_temp_profile(self, new_profile):
        self.temperature_profile = new_profile
        print(f"Temperature Profile Saved: {len(self.temperature_profile)} segments")

    def open_power_profile(self):
        ProfileEditorDialog(self.root, self.power_profile, self.save_power_profile, title="Input Power Profile", value_label="Power (Watts)", rate_label="Rate (Watts/Hr)")

    def save_power_profile(self, new_profile):
        self.power_profile = new_profile
        print(f"Power Profile Saved: {len(self.power_profile)} segments")

    def open_zero_pressure(self):
        """Opens the Zero Pressure Dialog."""
        ZeroPressureDialog(self.root, self.device_mgr, self.serial_lock)

    def open_power_control(self):
        """Opens the Power Control Dialog."""
        self.power_dialog = PowerControlDialog(self.root, 0.0, self.target_power_watts, self.power_control_active, self.update_power_settings)

    def update_power_settings(self, active, target):
        """Callback from PowerControlDialog."""
        self.power_control_active = active
        self.var_auto_power.set(active)
        self.target_power_watts = target

    def open_system_controls(self):
        """Opens the System Controls Dialog."""
        SystemControlsDialog(self.root, self.device_mgr, self.motor_mgr, self.serial_lock)

    def open_developer_mode(self):
        """Opens the debug window and sets log callbacks."""
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

            # If already in simulation, add a note to the log.
            if self.device_mgr.simulated or self.motor_mgr.simulated:
                self.debug_win.log("NOTE: Running in Simulation Mode due to port connection failure on startup.")

    def cleanup_and_exit(self):
        self.polling_active = False
        self.device_mgr.close()
        self.motor_mgr.close()
        self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = BaseAPGUI(root)
    root.mainloop()
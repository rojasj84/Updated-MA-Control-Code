import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
import threading
import queue
import time
import os
import datetime
import json
import struct
from device_comm import DeviceManager, MotorValveController
from Watlow import WatlowF4T
from Watlow import (
    REG_TEMP_PV, REG_TEMP_SP, REG_TEMP_MANUAL_POWER, REG_TEMP_MODE,
    REG_PRESSURE_PV, REG_PRESSURE_SP, REG_PRESSURE_MANUAL_POWER, REG_PRESSURE_MODE,
    REG_VOLTS, REG_AMPS
)
try:
    from pymodbus.client import ModbusTcpClient as _ModbusTcpClient
    HAS_PYMODBUS = True
except ImportError:
    HAS_PYMODBUS = False

# ---------------------------------------------------------------------------
# F4T Profile Register Map (Profile Step Edit Block, APCE class 80)
# Shared registers (same address regardless of loop)
# ---------------------------------------------------------------------------
_F4T_TYPE_MAP = {
    87: "Soak", 1928: "Ramp Time", 81: "Ramp Rate",
    1542: "Wait For", 1927: "Instant Change", 116: "Jump", 27: "End"
}
# Profile-level (file) management
_REG_PROF_NUMBER     = 18888   # Profile Number to work with (write 1 = Profile 1)
_REG_PROF_FILE_ACT   = 18890   # Profile File Action: Edit=1770, Add=1375, Delete=1772

# Step-level management
_REG_PROF_NUM_STEPS  = 18920   # Number of steps in profile (read)
_REG_PROF_EDIT_ACT   = 18922   # Step Edit Action: Edit=1770, Add=1375, Insert=1771, Delete=1772
_REG_PROF_STEP_SEL   = 18924   # Current Step Number selector
_REG_PROF_STEP_TYPE  = 18926   # Step Type enum
_REG_PROF_TIME_H     = 18928   # Step Time Hours
_REG_PROF_TIME_M     = 18930   # Step Time Minutes
_REG_PROF_TIME_S     = 18932   # Step Time Seconds
_REG_PROF_ACTION     = 18910   # Profile Action register (1782 = Start)

# Loop 1 (Temperature) – read 22 registers from 18926, offsets within that block
_REG_PROF_RATE1      = 18938   # Step Rate 1  (Loop 1 ramp rate,  IEEE float, offset 12)
_REG_PROF_SP1        = 18946   # Step Set Point 1 (Loop 1 setpoint, IEEE float, offset 20)
_REG_PROF_END_ACT1   = 19030   # End Step Loop Action 1 (Loop 1)

# Loop 2 (Pressure) – read 24 registers from 18926, offsets within that block
_REG_PROF_RATE2      = 18940   # Step Rate 2  (Loop 2 ramp rate,  IEEE float, offset 14)
_REG_PROF_SP2        = 18948   # Step Set Point 2 (Loop 2 setpoint, IEEE float, offset 22)
_REG_PROF_END_ACT2   = 19032   # End Step Loop Action 2 (Loop 2)

def _decode_f4t_float(regs):
    """Decode a word-swapped IEEE float from two Modbus registers."""
    if len(regs) < 2:
        return 0.0
    raw = struct.pack('>HH', regs[1], regs[0])
    return struct.unpack('>f', raw)[0]

def _encode_f4t_float(value):
    """Encode a float into [low_word, high_word] for F4T write."""
    packed = struct.pack('>f', value)
    hw, lw = struct.unpack('>HH', packed)
    return [lw, hw]

try:
    from PIL import Image, ImageTk, ImageDraw
    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False
    print("Warning: Pillow library not found. Install 'pillow' for better logo quality.")

class ControllerSelectionDialog:
    """
    Startup dialog: choose Serial or Watlow F4T.
    When Watlow is chosen an IP address entry appears inline so the user
    can confirm or change the address before the connection is attempted.

    The callback receives (controller_type, ip_address).
    controller_type is 'serial', 'watlow', or None (window closed).
    ip_address is a string (meaningful only when controller_type=='watlow').
    """
    _DEFAULT_IP = '192.168.0.222'

    def __init__(self, master, callback):
        self.top = tk.Toplevel(master)
        self.top.title("Select Controller")
        self.top.geometry("420x170")
        self.top.resizable(False, False)
        self.callback = callback
        self.top.protocol("WM_DELETE_WINDOW", self.on_close)

        master.update_idletasks()
        x = master.winfo_x() + (master.winfo_width() // 2) - (420 // 2)
        y = master.winfo_y() + (master.winfo_height() // 2) - (170 // 2)
        self.top.geometry(f"+{x}+{y}")
        self.top.grab_set()

        tk.Label(self.top, text="Please select the control hardware:",
                 font=("Arial", 12)).pack(pady=(18, 10))

        # --- Controller buttons ---
        btn_frame = tk.Frame(self.top)
        btn_frame.pack()
        tk.Button(btn_frame, text="Serial (Texmate/Omega)", width=22,
                  command=self._select_serial).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Watlow F4T (Network)", width=22,
                  command=self._show_ip_row).pack(side=tk.LEFT, padx=10)

        # --- IP row (hidden until Watlow is chosen) ---
        self._ip_frame = tk.Frame(self.top)
        # (not packed yet)

        tk.Label(self._ip_frame, text="Watlow IP Address:", font=("Arial", 10)).pack(side=tk.LEFT, padx=(10, 4))
        self._ip_var = tk.StringVar(value=self._DEFAULT_IP)
        self._ip_entry = tk.Entry(self._ip_frame, textvariable=self._ip_var,
                                  width=16, font=("Arial", 10))
        self._ip_entry.pack(side=tk.LEFT, padx=(0, 8))
        tk.Button(self._ip_frame, text="Connect", width=10,
                  bg="#1a6b1a", fg="white", font=("Arial", 10),
                  command=self._select_watlow).pack(side=tk.LEFT, padx=4)

        self._ip_row_visible = False

    # ------------------------------------------------------------------
    def _show_ip_row(self):
        """Reveal the IP entry + Connect button below the main buttons."""
        if not self._ip_row_visible:
            self._ip_frame.pack(pady=(10, 4))
            self._ip_row_visible = True
            # Grow window to fit the new row
            self.top.geometry("420x215")
        self._ip_entry.focus()
        self._ip_entry.selection_range(0, tk.END)

    def _select_serial(self):
        self.callback('serial', '')
        self.top.destroy()

    def _select_watlow(self):
        ip = self._ip_var.get().strip()
        if not ip:
            messagebox.showwarning("IP Required",
                "Please enter the Watlow F4T IP address.", parent=self.top)
            return
        self.callback('watlow', ip)
        self.top.destroy()

    def on_close(self):
        self.callback(None, '')
        self.top.destroy()

class WatlowIPDialog:
    def __init__(self, master, failed_ip):
        self.top = tk.Toplevel(master)
        self.top.title("Watlow Connection Failed")
        self.top.geometry("400x200")
        self.action = None
        self.new_ip = failed_ip

        master.update_idletasks()
        x = master.winfo_x() + (master.winfo_width() // 2) - (400 // 2)
        y = master.winfo_y() + (master.winfo_height() // 2) - (200 // 2)
        self.top.geometry(f"+{x}+{y}")

        self.top.protocol("WM_DELETE_WINDOW", self.cancel)
        self.top.grab_set()

        tk.Label(self.top, text=f"Could not connect to Watlow F4T at:", font=("Arial", 12)).pack(pady=(20, 5))
        tk.Label(self.top, text=f"{failed_ip}", font=("Arial", 12, "bold"), fg="red").pack()

        ip_frame = tk.Frame(self.top)
        ip_frame.pack(pady=10)
        tk.Label(ip_frame, text="New IP Address:").pack(side=tk.LEFT, padx=5)
        self.ip_entry = tk.Entry(ip_frame, width=15)
        self.ip_entry.insert(0, failed_ip)
        self.ip_entry.pack(side=tk.LEFT)

        btn_frame = tk.Frame(self.top)
        btn_frame.pack(pady=20)

        tk.Button(btn_frame, text="Retry Connection", command=self.retry).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Use Simulation", command=self.simulate).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Exit", command=self.cancel).pack(side=tk.LEFT, padx=10)

        self.top.wait_window()

    def retry(self):
        self.action = 'retry'
        self.new_ip = self.ip_entry.get()
        self.top.destroy()

    def simulate(self):
        self.action = 'simulate'
        self.top.destroy()

    def cancel(self):
        self.action = 'cancel'
        self.top.destroy()

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

class PIDSettingsDialog:
    def __init__(self, master, current_settings, on_save):
        self.top = tk.Toplevel(master)
        self.top.title("PID Settings")
        self.top.geometry("400x350")
        self.top.configure(bg="#1e1e2e")
        self.on_save = on_save
        
        tk.Label(self.top, text="PID Control Configuration", font=("Arial", 14, "bold"), bg="#1e1e2e", fg="white").pack(pady=(15, 10))
        
        main_frame = tk.Frame(self.top, bg="#2b2b3b", padx=20, pady=15)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.entries = {}
        row = 0
        for category, gains in current_settings.items():
            cat_label = category.replace("_", " ").title()
            tk.Label(main_frame, text=cat_label, font=("Arial", 11, "bold"), bg="#2b2b3b", fg="#00ffff").grid(row=row, column=0, columnspan=4, sticky="w", pady=(10 if row>0 else 0, 5))
            row += 1
            
            self.entries[category] = {}
            col = 0
            for gain_name, value in gains.items():
                tk.Label(main_frame, text=gain_name, bg="#2b2b3b", fg="white", font=("Arial", 10)).grid(row=row, column=col, sticky="e", padx=(10 if col>0 else 0, 5))
                ent = tk.Entry(main_frame, width=8, font=("Arial", 10), justify="center")
                ent.insert(0, str(value))
                ent.grid(row=row, column=col+1, sticky="w", padx=5)
                self.entries[category][gain_name] = ent
                col += 2
            row += 1
                
        btn_frame = tk.Frame(self.top, bg="#1e1e2e")
        btn_frame.pack(pady=(0, 20))
        
        tk.Button(btn_frame, text="SAVE TO JSON", bg="#4caf50", fg="white", font=("Arial", 10, "bold"), width=15, command=self.save).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="CANCEL", bg="#f44336", fg="white", font=("Arial", 10, "bold"), width=12, command=self.top.destroy).pack(side=tk.LEFT, padx=10)

    def save(self):
        new_settings = {}
        try:
            for cat, gains in self.entries.items():
                new_settings[cat] = {}
                for g_name, ent in gains.items():
                    new_settings[cat][g_name] = float(ent.get())
        except ValueError:
            messagebox.showerror("Error", "All values must be valid numbers.", parent=self.top)
            return
            
        self.on_save(new_settings)
        self.top.destroy()

class ProfileEditorDialog:
    # Tolerance for treating start == end as a Soak (handles float repr noise)
    _SOAK_EPSILON = 1e-4

    # F4T step type codes
    _TYPE_CODES    = {"Soak": 87, "Ramp Time": 1928, "Ramp Rate": 81}
    _END_ACT_CODES = {"User": 100, "Off": 62, "Hold": 47}

    def __init__(self, master, profile, on_save, title="Profile Editor",
                 value_label="Pressure (Bars)", rate_label="Rate (Bars/Hr)",
                 f4t_ip=None, f4t_connected=False, loop=2):
        """
        f4t_ip        : IP string for live F4T Modbus commands (None = offline)
        f4t_connected : True when a real (non-simulated) F4T is reachable
        loop          : 1 = Temperature (Loop 1), 2 = Pressure (Loop 2)
        """
        self.top = tk.Toplevel(master)
        self.top.title(title)
        self.top.geometry("820x560")
        self.profile = list(profile)
        self.on_save = on_save
        self.value_label = value_label
        self.rate_label = rate_label
        self.f4t_ip = f4t_ip
        self.f4t_connected = f4t_connected and HAS_PYMODBUS and f4t_ip is not None
        self.loop = loop   # 1 = temp (Loop 1), 2 = pressure (Loop 2)

        # Track which field was last edited
        self._last_edited = None   # "duration" | "rate" | None

        # Pull the End-action sentinel out of the profile if present
        initial_end_action = "User"
        if self.profile and self.profile[-1].get("step_type") == "End":
            initial_end_action = self.profile[-1].get("end_action", "User")
            self.profile = self.profile[:-1]

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

        tk.Label(input_frame, text=self.rate_label + ":", font=("Arial", 10)).grid(row=0, column=3)
        self.ent_rate = tk.Entry(input_frame, width=10, font=("Arial", 10))
        self.ent_rate.grid(row=1, column=3, padx=5)

        tk.Button(input_frame, text="Add Segment", command=self.add_segment,
                  font=("Arial", 10)).grid(row=1, column=4, padx=10)

        self.lbl_step_type_hint = tk.Label(input_frame, text="", font=("Arial", 9, "italic"), fg="#555555")
        self.lbl_step_type_hint.grid(row=2, column=0, columnspan=5, pady=(4, 0), sticky="w")

        # Auto-fill bindings
        self.ent_duration.bind("<FocusOut>", self._on_duration_focusout)
        self.ent_rate.bind("<FocusOut>",     self._on_rate_focusout)
        self.ent_duration.bind("<Return>",   self._on_duration_focusout)
        self.ent_rate.bind("<Return>",       self._on_rate_focusout)
        self.ent_start.bind("<FocusOut>", self._on_value_changed)
        self.ent_end.bind("<FocusOut>",   self._on_value_changed)

        # --- End Action dropdown ---
        end_frame = tk.LabelFrame(self.top, text="Profile End Action  (sent to F4T End step)",
                                  padx=10, pady=8, font=("Arial", 10))
        end_frame.pack(fill=tk.X, padx=10, pady=(0, 4))

        tk.Label(end_frame, text="When profile completes:", font=("Arial", 10)).pack(side=tk.LEFT, padx=(0, 8))

        self.end_action_var = tk.StringVar(value=initial_end_action)
        self.cmb_end_action = ttk.Combobox(
            end_frame, textvariable=self.end_action_var,
            values=["User", "Off", "Hold"], state="readonly",
            width=7, font=("Arial", 10))
        self.cmb_end_action.pack(side=tk.LEFT)

        tk.Label(end_frame,
                 text="    User = resume manual control     Off = output off     Hold = hold last setpoint",
                 font=("Arial", 9, "italic"), fg="#444444").pack(side=tk.LEFT, padx=6)

        # Live-F4T status indicator
        f4t_status = "Live F4T: CONNECTED" if self.f4t_connected else "Live F4T: offline (upload on Save)"
        f4t_color  = "#007700" if self.f4t_connected else "#888888"
        tk.Label(end_frame, text=f"   [{f4t_status}]",
                 font=("Arial", 9, "italic"), fg=f4t_color).pack(side=tk.LEFT, padx=6)

        # --- List Display ---
        list_frame = tk.Frame(self.top)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=4)

        style = ttk.Style(self.top)
        style.configure("Treeview.Heading", font=("Arial", 10, "bold"))
        style.configure("Treeview", font=("Arial", 10), rowheight=25)

        columns = ("start", "end", "duration", "rate", "step_type")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=7)
        self.tree.heading("start",     text=f"Start {self.value_label}")
        self.tree.heading("end",       text=f"Final {self.value_label}")
        self.tree.heading("duration",  text="Duration (hours)")
        self.tree.heading("rate",      text=self.rate_label)
        self.tree.heading("step_type", text="F4T Step Type")

        self.tree.column("start",     width=130, anchor="center")
        self.tree.column("end",       width=130, anchor="center")
        self.tree.column("duration",  width=115, anchor="center")
        self.tree.column("rate",      width=115, anchor="center")
        self.tree.column("step_type", width=115, anchor="center")

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # --- Buttons ---
        btn_frame = tk.Frame(self.top)
        btn_frame.pack(pady=8)
        tk.Button(btn_frame, text="Save & Exit", bg="green", fg="white",
                  command=self.save_exit, font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Clear All", bg="red", fg="white",
                  command=self.clear_all, font=("Arial", 10)).pack(side=tk.LEFT, padx=5)

        self.refresh_list()

    # ------------------------------------------------------------------
    # Live F4T helpers
    # ------------------------------------------------------------------

    def _f4t_client(self):
        """Open and return a connected ModbusTcpClient, or None."""
        if not self.f4t_connected:
            return None
        try:
            c = _ModbusTcpClient(self.f4t_ip, port=502, timeout=3)
            return c if c.connect() else None
        except Exception as exc:
            print(f"  ProfileEditor F4T connect error: {exc}")
            return None

    def _f4t_delete_and_create_profile(self):
        """Delete Profile 1 on the F4T then immediately re-create it."""
        client = self._f4t_client()
        if client is None:
            return
        try:
            # Select profile 1
            client.write_register(_REG_PROF_NUMBER, value=1)
            time.sleep(0.05)
            # Delete
            client.write_register(_REG_PROF_FILE_ACT, value=1772)
            time.sleep(0.15)
            # Re-create (Add)
            client.write_register(_REG_PROF_NUMBER, value=1)
            time.sleep(0.05)
            client.write_register(_REG_PROF_FILE_ACT, value=1375)
            time.sleep(0.15)
            print("  F4T Profile 1: deleted and re-created.")
        except Exception as exc:
            print(f"  F4T delete/create error: {exc}")
        finally:
            client.close()

    def _f4t_add_step(self, seg):
        """
        Write a single new step to the F4T using Step Edit Action = Add (1375).
        The F4T appends it after the current last step automatically.
        seg dict: {end, duration (hours), rate, step_type}
        """
        client = self._f4t_client()
        if client is None:
            return

        _TYPE_CODES = self._TYPE_CODES

        def _wr(reg, val):
            try:
                client.write_register(reg, value=val)
            except Exception as exc:
                print(f"    _f4t_add_step write({reg}) error: {exc}")

        def _wrf(reg, value):
            try:
                client.write_registers(reg, _encode_f4t_float(value))
            except Exception as exc:
                print(f"    _f4t_add_step write_float({reg}) error: {exc}")

        try:
            step_type = seg.get("step_type", "Ramp Time")
            type_code = _TYPE_CODES.get(step_type, 1928)

            # Signal Add — F4T allocates a new step slot
            _wr(_REG_PROF_EDIT_ACT, 1375)
            time.sleep(0.05)

            # Write step type
            _wr(_REG_PROF_STEP_TYPE, type_code)
            time.sleep(0.02)

            # Write setpoint (loop-specific)
            sp_reg   = _REG_PROF_SP1   if self.loop == 1 else _REG_PROF_SP2
            rate_reg = _REG_PROF_RATE1 if self.loop == 1 else _REG_PROF_RATE2
            _wrf(sp_reg, float(seg["end"]))

            if step_type == "Ramp Rate":
                _wrf(rate_reg, abs(float(seg["rate"])))
            else:
                total_s = int(round(seg["duration"] * 3600))  # hours -> seconds
                h, rem  = divmod(total_s, 3600)
                m, s    = divmod(rem, 60)
                _wr(_REG_PROF_TIME_H, h)
                _wr(_REG_PROF_TIME_M, m)
                _wr(_REG_PROF_TIME_S, s)

            time.sleep(0.05)
            print(f"  F4T Add step [{step_type}]: end={seg['end']}")
        except Exception as exc:
            print(f"  _f4t_add_step error: {exc}")
        finally:
            client.close()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _try_get_float(self, entry):
        try:
            return float(entry.get().strip())
        except ValueError:
            return None

    def _is_soak(self, s, e):
        if s is None or e is None:
            return False
        return abs(e - s) <= self._SOAK_EPSILON

    def _determine_step_type(self, s, e, last_edited):
        if self._is_soak(s, e):
            return "Soak"
        if last_edited == "rate":
            return "Ramp Rate"
        return "Ramp Time"

    def _update_hint(self, step_type):
        hints = {
            "Soak":      "-> Watlow: Soak  (start = final, holds setpoint for duration)",
            "Ramp Time": "-> Watlow: Ramp Time  (duration entered, rate auto-calculated)",
            "Ramp Rate": "-> Watlow: Ramp Rate  (rate entered, duration auto-calculated)",
        }
        self.lbl_step_type_hint.config(text=hints.get(step_type, ""))

    def _on_value_changed(self, event=None):
        s = self._try_get_float(self.ent_start)
        e = self._try_get_float(self.ent_end)
        if s is not None and e is not None:
            step_type = self._determine_step_type(s, e, self._last_edited)
            self._update_hint(step_type)
            if self._is_soak(s, e):
                self.ent_rate.delete(0, tk.END)
                self.ent_rate.insert(0, "0.00")

    def _on_duration_focusout(self, event=None):
        self._last_edited = "duration"
        s = self._try_get_float(self.ent_start)
        e = self._try_get_float(self.ent_end)
        d = self._try_get_float(self.ent_duration)
        step_type = self._determine_step_type(s, e, "duration")
        self._update_hint(step_type)
        if step_type == "Soak":
            self.ent_rate.delete(0, tk.END)
            self.ent_rate.insert(0, "0.00")
            return
        if d is not None and d > 0 and s is not None and e is not None:
            r = (e - s) / d
            self.ent_rate.delete(0, tk.END)
            self.ent_rate.insert(0, f"{r:.4f}")

    def _on_rate_focusout(self, event=None):
        self._last_edited = "rate"
        s = self._try_get_float(self.ent_start)
        e = self._try_get_float(self.ent_end)
        r = self._try_get_float(self.ent_rate)
        step_type = self._determine_step_type(s, e, "rate")
        self._update_hint(step_type)
        if step_type == "Soak":
            self.ent_rate.delete(0, tk.END)
            self.ent_rate.insert(0, "0.00")
            return
        if r is not None and abs(r) > 1e-9 and s is not None and e is not None:
            d = abs(e - s) / abs(r)
            self.ent_duration.delete(0, tk.END)
            self.ent_duration.insert(0, f"{d:.4f}")

    # ------------------------------------------------------------------
    # Segment management
    # ------------------------------------------------------------------

    def add_segment(self):
        try:
            s = float(self.ent_start.get())
            e = float(self.ent_end.get())

            if self._is_soak(s, e):
                step_type = "Soak"
            else:
                step_type = self._determine_step_type(s, e, self._last_edited)

            if step_type == "Soak":
                d_str = self.ent_duration.get().strip()
                if not d_str:
                    messagebox.showerror("Error", "Please enter a Duration for the Soak step.", parent=self.top)
                    return
                d = float(d_str)
                if d <= 0:
                    messagebox.showerror("Error", "Duration must be positive.", parent=self.top)
                    return
                r = 0.0

            elif step_type == "Ramp Rate":
                r_str = self.ent_rate.get().strip()
                d_str = self.ent_duration.get().strip()
                if not r_str:
                    messagebox.showerror("Error", "Please enter a Rate.", parent=self.top)
                    return
                r = float(r_str)
                if abs(r) < 1e-9:
                    messagebox.showerror("Error", "Rate cannot be zero.", parent=self.top)
                    return
                d = abs(e - s) / abs(r) if abs(e - s) > 1e-9 else (float(d_str) if d_str else 0.0)
                if d <= 0:
                    messagebox.showerror("Error", "Calculated duration is zero or negative.", parent=self.top)
                    return

            else:  # Ramp Time
                d_str = self.ent_duration.get().strip()
                if not d_str:
                    messagebox.showerror("Error", "Please enter a Duration.", parent=self.top)
                    return
                d = float(d_str)
                if d <= 0:
                    messagebox.showerror("Error", "Duration must be positive.", parent=self.top)
                    return
                r = (e - s) / d

            seg = {"start": s, "end": e, "duration": d, "rate": r, "step_type": step_type}
            self.profile.append(seg)
            self.refresh_list()

            # --- Live F4T: send Add step immediately ---
            if self.f4t_connected:
                threading.Thread(
                    target=self._f4t_add_step,
                    args=(seg,),
                    daemon=True
                ).start()

            # Advance to next segment
            self.ent_start.delete(0, tk.END)
            self.ent_start.insert(0, str(e))
            self.ent_end.delete(0, tk.END)
            self.ent_duration.delete(0, tk.END)
            self.ent_rate.delete(0, tk.END)
            self._last_edited = None
            self.lbl_step_type_hint.config(text="")
            self.ent_end.focus()

        except ValueError:
            messagebox.showerror("Error", "Invalid numbers.", parent=self.top)

    def refresh_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for step in self.profile:
            d  = step.get("duration", 0)
            r  = step.get("rate", 0)
            st = step.get("step_type", "Ramp Time")
            self.tree.insert("", tk.END, values=(
                step["start"], step["end"],
                f"{d:.4f}", f"{r:.4f}", st
            ))

    def clear_all(self):
        if not messagebox.askyesno("Clear All", "Clear all segments?\n\n"
                + ("This will also delete and re-create Profile 1 on the F4T."
                   if self.f4t_connected else ""),
                parent=self.top):
            return
        self.profile.clear()
        self.refresh_list()
        # --- Live F4T: delete profile then immediately re-create blank ---
        if self.f4t_connected:
            threading.Thread(
                target=self._f4t_delete_and_create_profile,
                daemon=True
            ).start()

    def save_exit(self):
        # Append End-action sentinel so upload methods can read it
        profile_with_end = list(self.profile) + [{
            "step_type":  "End",
            "end_action": self.end_action_var.get(),
        }]
        self.on_save(profile_with_end)
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
    def __init__(self, master, device_mgr, motor_mgr, serial_lock, controller_type):
        self.top = tk.Toplevel(master)
        self.top.title("System Controls")
        self.top.geometry("800x600")
        self.device_mgr = device_mgr
        self.motor_mgr = motor_mgr
        self.controller_type = controller_type
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
        btn_zero = tk.Button(cal_frame, text="Zero Pressure Calibration", bg="#FFDDDD", command=self.open_zero_pressure)
        btn_zero.pack(fill=tk.X, pady=5)

        if self.controller_type == 'watlow':
            btn_zero.config(state="disabled", text="Zero Pressure (N/A for Watlow)")

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
        self.target_voltage = 0.7 # Tracks the state for Port 5 (Omega)
        
        self.controller_type = None
        self.watlow_controller = None
        self.watlow_ip_address = '192.168.0.222' # Default Watlow IP
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
        self.last_pressure_control_time = 0.0
        self.press_prev_error = None
        
        self.current_target_pressure = None
        self.current_target_temp = None
        self.current_target_power = None
        
        self.current_press_time_remaining = None
        self.current_temp_time_remaining = None
        self.current_power_time_remaining = None

        self.current_press_segment = None
        self.current_temp_segment = None
        self.current_power_segment = None
        self.press_total_segments = 0
        self.temp_total_segments = 0
        self.power_total_segments = 0

        # Power Control State
        self.power_control_active = False
        self.temp_control_active = False
        self.target_power_watts = 0.0
        self.power_dialog = None
        
        # Graphing State
        self.current_view = "Temperature"
        self.data_history = {"Temperature": [], "Pressure": [], "Power": [], "Resistance": []}
        self.start_time = time.time()
        self.recording_active = False
        self.hover_state = {"view": None, "x": None, "y": None}
        self.zoom_limits = {v: None for v in ["Temperature", "Pressure", "Power", "Resistance"]}
        self.current_plot_params = {}
        self.zoom_box_start = None
        
        self.pid_config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pid_config.json")
        self.load_pid_settings()

        # Configure Root
        self.root.configure(bg=self.colors["bg"])
        self.root.geometry("1280x800")

        self.root.withdraw() # Hide main window until controller is selected
        self.create_widgets()
        
        self.select_controller()

    def select_controller(self):
        def callback(selection, ip):
            if selection is None:
                self.root.destroy()
                return

            self.controller_type = selection
            if selection == 'watlow' and ip:
                self.watlow_ip_address = ip
            print(f"Controller selected: {self.controller_type}"
                  + (f"  IP: {self.watlow_ip_address}" if selection == 'watlow' else ""))
            self.root.deiconify()
            self.root.after(200, self.connect_hardware)

        ControllerSelectionDialog(self.root, callback)

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
            ("System Controls", self.colors["btn_bg"], self.open_system_controls),
            ("Thermocouple Config", self.colors["btn_bg"], self.open_temp_config),
            ("PID Settings", self.colors["btn_bg"], self.open_pid_settings),
            ("Developer Mode", self.colors["btn_bg"], self.open_developer_mode),
            ("EXIT", self.colors["btn_bg"], self.cleanup_and_exit)
        ]

        for text, color, cmd in buttons:
            btn = tk.Button(self.sidebar, text=text, bg=color, fg="white", font=("Arial", 11), relief="flat", padx=10, pady=8, command=cmd, cursor="hand2")
            btn.pack(fill=tk.X, padx=15, pady=5)
            if text == "Thermocouple Config":
                self.btn_thermocouple_config = btn

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

        # --- Graph Section ---
        graph_card = tk.Frame(self.main_content, bg=self.colors["card"], padx=2, pady=2)
        graph_card.pack(fill=tk.BOTH, expand=True, pady=(0, 20))

        # Graph Controls
        graph_ctrl_frame = tk.Frame(graph_card, bg=self.colors["card"])
        graph_ctrl_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # tk.Label(graph_ctrl_frame, text="LIVE VISUALIZATION", fg=self.colors["subtext"], bg=self.colors["card"], font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        tk.Label(graph_ctrl_frame, text="STATUS:", font=("Arial", 10, "bold"), bg=self.colors["card"], fg=self.colors["subtext"]).pack(side=tk.LEFT)
        self.lbl_system_status = tk.Label(graph_ctrl_frame, text="STANDBY", font=("Arial", 12, "bold"), bg=self.colors["card"], fg=self.colors["danger"])
        self.lbl_system_status.pack(side=tk.LEFT, padx=5)
        
        tk.Button(graph_ctrl_frame, text="RESET ZOOM / VIEW", bg=self.colors["btn_bg"], fg="white", font=("Arial", 9, "bold"), 
                      command=self.set_all_view, relief="flat").pack(side=tk.RIGHT, padx=2)

        self.time_window_var = tk.StringVar(value="All Time")
        time_cb = ttk.Combobox(graph_ctrl_frame, textvariable=self.time_window_var, values=["All Time", "Last 1 Min", "Last 5 Min", "Last 10 Min", "Last 30 Min", "Last 1 Hour"], width=12, state="readonly")
        time_cb.pack(side=tk.RIGHT, padx=5)
        tk.Label(graph_ctrl_frame, text="TIME WINDOW:", font=("Arial", 9, "bold"), bg=self.colors["card"], fg=self.colors["subtext"]).pack(side=tk.RIGHT, padx=2)
        time_cb.bind("<<ComboboxSelected>>", lambda e: self.redraw_visible_graphs())
        tk.Label(graph_ctrl_frame, text="(Right-click & drag to zoom, single right-click to reset)", font=("Arial", 8, "italic"), bg=self.colors["card"], fg=self.colors["subtext"]).pack(side=tk.LEFT, padx=10)

        # Canvas Container
        self.graph_container = tk.Frame(graph_card, bg=self.colors["card"])
        self.graph_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        self.canvases = {}
        self.canvas_configs = {
            "Temperature": {"color": self.colors["accent"]},
            "Pressure": {"color": self.colors["success"]},
            "Power": {"color": "#ff9800"},
            "Resistance": {"color": "#00bcd4"}
        }

        for view in ["Temperature", "Pressure", "Power", "Resistance"]:
            cv = tk.Canvas(self.graph_container, bg=self.colors["card"], highlightthickness=1, highlightbackground=self.colors["bg"])
            cv.bind("<Button-1>", lambda event, v=view: self.toggle_maximize(v))
            cv.bind("<Configure>", lambda event, v=view: self.draw_single_graph(v))
            cv.bind("<Motion>", lambda event, v=view: self.on_canvas_hover(event, v))
            cv.bind("<Leave>", lambda event, v=view: self.on_canvas_leave(event, v))
            
            cv.bind("<ButtonPress-3>", lambda event, v=view: self.start_zoom_box(event, v))
            cv.bind("<B3-Motion>", lambda event, v=view: self.update_zoom_box(event, v))
            cv.bind("<ButtonRelease-3>", lambda event, v=view: self.end_zoom_box(event, v))
            self.canvases[view] = cv
        
        self.update_graph_layout()

        # --- Readouts Section ---
        readout_container = tk.Frame(self.main_content, bg=self.colors["bg"])
        readout_container.pack(fill=tk.X, pady=(0, 20))

        headers = [
            ("Temperature (°C)", self.colors["accent"]), 
            ("Pressure (Bars)", self.colors["success"]), 
            ("Voltage (V)", "#ff9800"), 
            ("Current (A)", "#e91e63"), 
            ("Power (W)", "#9c27b0"),
            ("Resistance (Ω)", "#00bcd4")
        ]
        
        self.readout_labels = []
        for i, (text, color) in enumerate(headers):
            card = tk.Frame(readout_container, bg=self.colors["card"], padx=15, pady=10)
            card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0 if i==0 else 10, 0))
            
            tk.Label(card, text=text, fg=color, bg=self.colors["card"], font=("Arial", 14, "bold")).pack(anchor="w")
            val = tk.Label(card, text="---", fg=self.colors["text"], bg=self.colors["card"], font=("Arial", 20, "bold"))
            val.pack(anchor="e", pady=(5, 0))
            self.readout_labels.append(val)

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

        def style_time_card(parent, color):
            card = tk.Frame(parent, bg=self.colors["btn_bg"], padx=10, pady=2, relief="flat", highlightbackground=color, highlightthickness=1)
            lbl = tk.Label(card, text="", bg=self.colors["btn_bg"], fg=color, font=("Arial", 10, "bold"))
            lbl.pack()
            return card, lbl

        # Temperature
        style_btn(auto_grid, "Load Temp Profile", self.open_temp_profile).grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        self.var_auto_temp = tk.BooleanVar(value=False)
        self.chk_auto_temp = style_chk(auto_grid, "Enable Auto Temp", self.var_auto_temp, self.toggle_temp_control_check, self.colors["accent"])
        self.chk_auto_temp.grid(row=0, column=1, padx=5, pady=8, sticky="w")

        self.frm_temp_time, self.lbl_temp_time = style_time_card(auto_grid, self.colors["accent"])
        self.frm_temp_time.grid(row=0, column=2, padx=10, pady=5, sticky="w")
        self.frm_temp_time.grid_remove() # Hide initially

        # Pressure
        style_btn(auto_grid, "Load Pressure Profile", self.open_pressure_config).grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        
        self.var_auto_press = tk.BooleanVar(value=False)
        self.chk_auto_press = style_chk(auto_grid, "Enable Auto Pressure", self.var_auto_press, self.toggle_press_control_check, self.colors["success"])
        self.chk_auto_press.grid(row=1, column=1, padx=5, pady=8, sticky="w")

        self.frm_press_time, self.lbl_press_time = style_time_card(auto_grid, self.colors["success"])
        self.frm_press_time.grid(row=1, column=2, padx=10, pady=5, sticky="w")
        self.frm_press_time.grid_remove()

        # Power
        style_btn(auto_grid, "Load Power Profile", self.open_power_profile).grid(row=2, column=0, padx=5, pady=5, sticky="ew")
        
        self.var_auto_power = tk.BooleanVar(value=False)
        self.chk_auto_power = style_chk(auto_grid, "Enable Auto Power", self.var_auto_power, self.toggle_power_control_check, "#ff9800")
        self.chk_auto_power.grid(row=2, column=1, padx=5, pady=8, sticky="w")

        self.frm_power_time, self.lbl_power_time = style_time_card(auto_grid, "#ff9800")
        self.frm_power_time.grid(row=2, column=2, padx=10, pady=5, sticky="w")
        self.frm_power_time.grid_remove()

        # Manual Control Card
        manual_card = tk.Frame(controls_container, bg=self.colors["card"], padx=15, pady=15)
        manual_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        tk.Label(manual_card, text="MANUAL OVERRIDE", fg=self.colors["accent"], bg=self.colors["card"], font=("Arial", 14, "bold")).pack(anchor="w", pady=(0, 10))

        self.btn_manual_voltage = tk.Button(manual_card, text="Start Manual Control", bg=self.colors["success"], fg="white", relief="flat", command=self.toggle_manual_voltage, font=("Arial", 12), cursor="hand2")
        self.btn_manual_voltage.pack(fill=tk.X, padx=5, pady=2)
        
        target_frame = tk.Frame(manual_card, bg=self.colors["card"])
        target_frame.pack(fill=tk.X, pady=2, padx=5)
        self.ent_target_voltage = tk.Entry(target_frame, width=6, bg=self.colors["bg"], fg="white", insertbackground="white", relief="flat", font=("Arial", 12))
        self.ent_target_voltage.pack(side=tk.LEFT, padx=5)
        self.ent_target_voltage.insert(0, "0.70")
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
            self.btn_manual_voltage.config(text="STOP MANUAL CONTROL", bg=self.colors["danger"])
            # Disable conflicting auto controls
            if self.power_control_active:
                self.var_auto_power.set(False) # This will trigger its command to set self.power_control_active = False
                print("Auto Power Control disabled for Manual Output Control.")
            if self.temp_control_active:
                self.var_auto_temp.set(False)
                self.temp_control_active = False
                print("Auto Temp Control disabled for Manual Output Control.")

            if self.controller_type == 'watlow':
                with self.serial_lock:
                    self.watlow_controller.write_uint16(REG_TEMP_MODE, 54) # Manual Mode
                print("Watlow controller set to Manual Power mode.")
        else:
            self.btn_manual_voltage.config(text="Start Manual Control", bg=self.colors["success"])
            if self.controller_type == 'watlow':
                with self.serial_lock:
                    self.watlow_controller.write_uint16(REG_TEMP_MODE, 10) # Auto Mode
                print("Watlow controller set back to Auto mode.")

    def manual_step_voltage(self, sign):
        if not self.manual_voltage_active:
            messagebox.showwarning("Manual Control", "Please start Manual Control first.")
            return
        
        delta = 0
        try:
            step = float(self.ent_manual_inc.get())
            delta = sign * step
        except ValueError:
            messagebox.showerror("Error", "Invalid step value.")
            return

        if self.controller_type == 'watlow':
            with self.serial_lock:
                current_val = self.watlow_controller.read_float(REG_TEMP_MANUAL_POWER)
                if current_val is not None:
                    new_val = max(0.0, min(100.0, current_val + delta))
                    self.watlow_controller.write_float(REG_TEMP_MANUAL_POWER, new_val)
                    self.ent_target_voltage.delete(0, tk.END)
                    self.ent_target_voltage.insert(0, f"{new_val:.2f}")
        else: # serial
            self.target_voltage = max(0.0, min(10.0, self.target_voltage + delta))
            self.ent_target_voltage.delete(0, tk.END)
            self.ent_target_voltage.insert(0, f"{self.target_voltage:.2f}")
            with self.serial_lock:
                self.device_mgr.set_omega_voltage(self.target_voltage)
            

    def set_manual_voltage_direct(self):
        if not self.manual_voltage_active:
            messagebox.showwarning("Manual Control", "Please start Manual Control first.")
            return
        try:
            val = float(self.ent_target_voltage.get())

            
            if self.controller_type == 'watlow':
                val = max(0.0, min(100.0, val)) # Clamp 0-100%
                with self.serial_lock:
                    self.watlow_controller.write_float(REG_TEMP_MANUAL_POWER, val)
            else: # serial
                val = max(0.0, min(10.0, val)) # Clamp 0-10V
                self.target_voltage = val
                with self.serial_lock:
                    self.device_mgr.set_omega_voltage(self.target_voltage)

            self.ent_target_voltage.delete(0, tk.END)
            self.ent_target_voltage.insert(0, f"{val:.2f}")
        except ValueError:
            messagebox.showerror("Error", "Invalid voltage value.")

    def adjust_voltage(self, delta):
        """Manually adjusts the target voltage (serial controller only)."""
        if self.controller_type != 'serial':
            return
        self.target_voltage += delta
        self.target_voltage = max(0.0, min(10.0, self.target_voltage))
        self.ent_target_voltage.delete(0, tk.END)
        self.ent_target_voltage.insert(0, f"{self.target_voltage:.2f}")
        with self.serial_lock:
            self.device_mgr.set_omega_voltage(self.target_voltage)

    def quench_output(self):
        """Immediately sets output to 0 and stops all automation."""
        if self.power_control_active:
            self.power_control_active = False
            self.var_auto_power.set(False)
        if self.temp_control_active:
            self.temp_control_active = False
            self.var_auto_temp.set(False)
        if self.manual_voltage_active:
            self.manual_voltage_active = False
            self.btn_manual_voltage.config(text="Start Manual Control", bg=self.colors["success"])

        self.ent_target_voltage.delete(0, tk.END)
        self.ent_target_voltage.insert(0, "0.00")

        if self.controller_type == 'watlow':
            with self.serial_lock:
                self.watlow_controller.write_uint16(REG_TEMP_MODE, 62) # Mode OFF
            print("QUENCH executed: Watlow loop turned OFF.")
        else: # serial
            self.target_voltage = 0.0
            with self.serial_lock:
                self.device_mgr.set_omega_voltage(0.0)
            print("QUENCH executed: Output set to 0V")

    def set_all_view(self):
        self.view_mode = "ALL"
        if hasattr(self, 'time_window_var'):
            self.time_window_var.set("All Time")
        for v in self.zoom_limits:
            self.zoom_limits[v] = None
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
            cv.grid_forget()
        
        if self.view_mode == "ALL":
            # Grid layout for all four
            self.graph_container.grid_columnconfigure(0, weight=1)
            self.graph_container.grid_columnconfigure(1, weight=1)
            self.graph_container.grid_rowconfigure(0, weight=1)
            self.graph_container.grid_rowconfigure(1, weight=1)
            
            self.canvases["Temperature"].grid(row=0, column=0, sticky="nsew", padx=(0, 5), pady=(0, 5))
            self.canvases["Pressure"].grid(row=0, column=1, sticky="nsew", padx=(5, 0), pady=(0, 5))
            self.canvases["Power"].grid(row=1, column=0, sticky="nsew", padx=(0, 5), pady=(5, 0))
            self.canvases["Resistance"].grid(row=1, column=1, sticky="nsew", padx=(5, 0), pady=(5, 0))
        else: # "SINGLE"
            self.canvases[self.current_view].pack(fill=tk.BOTH, expand=True)

    def draw_single_graph(self, view_name):
        canvas = self.canvases[view_name]
        canvas.delete("all")
        
        w = canvas.winfo_width()
        h = canvas.winfo_height()
        if w < 10 or h < 10: return
        
        # Margins
        x_margin = 40
        y_margin = 45
        plot_w = w - x_margin - 20
        plot_h = h - y_margin - 40
        
        # Display names with units
        display_names = {
            "Temperature": "Temperature (°C)",
            "Pressure": "Oil Pressure (Bar)",
            "Power": "Power (W)",
            "Resistance": "Resistance (Ω)"
        }
        display_text = display_names.get(view_name, view_name)

        # Plot Data
        data = self.data_history.get(view_name, [])
        
        # Time Window Filtering
        window_str = getattr(self, 'time_window_var', tk.StringVar(value="All Time")).get()
        if window_str != "All Time" and data:
            window_map = {"Last 1 Min": 60, "Last 5 Min": 300, "Last 10 Min": 600, "Last 30 Min": 1800, "Last 1 Hour": 3600}
            window_sec = window_map.get(window_str, 0)
            if window_sec > 0:
                latest_t = data[-1][0]
                data = [p for p in data if p[0] >= latest_t - window_sec]

        # Box Zoom Filtering
        zoom = self.zoom_limits.get(view_name)
        if zoom and data:
            z_tmin, z_tmax, z_vmin, z_vmax = zoom
            data_to_plot = [p for p in data if z_tmin - (z_tmax-z_tmin)*0.1 <= p[0] <= z_tmax + (z_tmax-z_tmin)*0.1]
        else:
            data_to_plot = data

        if len(data_to_plot) > 1:
            times = [p[0] for p in data_to_plot]
            values = [p[1] for p in data_to_plot]
            
            if zoom:
                min_t, max_t = z_tmin, z_tmax
                display_min_v, display_max_v = z_vmin, z_vmax
            else:
                min_t, max_t = times[0], times[-1]
                min_v, max_v = min(values), max(values)
                
                if max_v > 0: display_max_v = max_v * 1.1
                elif max_v < 0: display_max_v = max_v * 0.9
                else: display_max_v = 1.0

                v_range_for_padding = display_max_v - min_v
                display_min_v = min_v - v_range_for_padding * 0.05

                if (display_max_v - display_min_v) < 1e-6:
                    display_max_v = max_v + 0.5
                    display_min_v = min_v - 0.5
                if max_t == min_t: max_t += 1.0
                
            x_plot_range = max_t - min_t
            if x_plot_range == 0: x_plot_range = 1.0
            y_plot_range = display_max_v - display_min_v
            if y_plot_range == 0: y_plot_range = 1.0
            
            self.current_plot_params[view_name] = {
                "min_t": min_t, "x_plot_range": x_plot_range, "plot_w": plot_w, "x_margin": x_margin,
                "display_min_v": display_min_v, "y_plot_range": y_plot_range, "plot_h": plot_h,
                "y_margin": y_margin, "h": h
            }

            # --- Draw Data Lines ---
            points = []
            for t, v in data_to_plot:
                x = x_margin + (t - min_t) / x_plot_range * plot_w
                y = (h - y_margin) - (v - display_min_v) / y_plot_range * plot_h
                points.extend([x, y])
            canvas.create_line(points, fill=self.canvas_configs[view_name]["color"], width=2)
            
            # --- Masks to hide overspill ---
            canvas.create_rectangle(0, 0, w, 40, fill=self.colors["card"], outline="") # Top
            canvas.create_rectangle(0, h-y_margin, w, h, fill=self.colors["card"], outline="") # Bottom
            canvas.create_rectangle(0, 0, x_margin, h, fill=self.colors["card"], outline="") # Left
            canvas.create_rectangle(w-20, 0, w, h, fill=self.colors["card"], outline="") # Right

            # --- Title & Labels ---
            canvas.create_text(w/2, 20, text=f"{display_text} vs Time", font=("Arial", 12, "bold"), fill="white")
            canvas.create_text(w/2, h-5, text="Time (HH:MM:SS)", font=("Arial", 10), fill="#b0b0b0", anchor="s")
            canvas.create_text(15, h/2, text=display_text, angle=90, font=("Arial", 10), fill="#b0b0b0")

            # --- Draw Axis Ticks and Labels ---
            num_ticks = 5
            for i in range(num_ticks):
                val = display_min_v + (i / (num_ticks - 1)) * y_plot_range
                y_pos = (h - y_margin) - (i / (num_ticks - 1)) * plot_h
                canvas.create_text(x_margin - 5, y_pos, text=f"{val:.1f}", anchor="e", fill="#b0b0b0", font=("Arial", 8))
            
            for i in range(num_ticks):
                val = min_t + (i / (num_ticks - 1)) * x_plot_range
                x_pos = x_margin + (i / (num_ticks - 1)) * plot_w
                
                time_str = time.strftime("%H:%M:%S", time.localtime(self.start_time + val))
                canvas.create_text(x_pos, h - y_margin + 10, text=time_str, anchor="n", fill="#b0b0b0", font=("Arial", 8))

            # --- Draw Grid ---
            for i in range(1, num_ticks - 1):
                x = x_margin + (i / (num_ticks - 1)) * plot_w
                canvas.create_line(x, 40, x, h-y_margin, fill="#444455", dash=(2, 4))
                y = (h - y_margin) - (i / (num_ticks - 1)) * plot_h
                canvas.create_line(x_margin, y, w-20, y, fill="#444455", dash=(2, 4))

            # --- Draw Axes Rectangle ---
            canvas.create_rectangle(x_margin, 40, w-20, h-y_margin, outline="white", width=2)

        else: # Handle case with no or single data point
            canvas.create_text(w/2, 20, text=f"{display_text} vs Time", font=("Arial", 12, "bold"), fill="white")
            canvas.create_rectangle(x_margin, 40, w-20, h-y_margin, outline="white", width=2)
            canvas.create_text(w/2, h/2, text="No data to display", fill="#666677", font=("Arial", 12))

        self.draw_tooltip(view_name)

    def on_canvas_hover(self, event, view_name):
        self.hover_state = {"view": view_name, "x": event.x, "y": event.y}
        self.draw_tooltip(view_name)

    def on_canvas_leave(self, event, view_name):
        self.hover_state = {"view": None, "x": None, "y": None}
        canvas = self.canvases[view_name]
        canvas.delete("tooltip")

    def draw_tooltip(self, view_name):
        if self.hover_state["view"] != view_name or self.hover_state["x"] is None:
            return
            
        canvas = self.canvases[view_name]
        canvas.delete("tooltip")
        
        plot_info = self.current_plot_params.get(view_name)
        if not plot_info: return
        
        data = self.data_history.get(view_name, [])
        if len(data) < 2: return
        
        w = canvas.winfo_width()
        h = canvas.winfo_height()
        hx = self.hover_state["x"]
        hy = self.hover_state["y"]
        
        min_t, x_plot_range = plot_info["min_t"], plot_info["x_plot_range"]
        display_min_v, y_plot_range = plot_info["display_min_v"], plot_info["y_plot_range"]
        plot_w, plot_h = plot_info["plot_w"], plot_info["plot_h"]
        x_margin, y_margin = plot_info["x_margin"], plot_info["y_margin"]

        # Check if inside plot area
        if hx < x_margin or hx > w - 20 or hy < 40 or hy > h - y_margin:
            return
            
        # Estimate t from hx
        t_est = min_t + ((hx - x_margin) / plot_w) * x_plot_range
        
        # Find closest point
        closest_point = min(data, key=lambda p: abs(p[0] - t_est))
        t_val, v_val = closest_point
        
        px = x_margin + (t_val - min_t) / x_plot_range * plot_w
        py = (h - y_margin) - (v_val - display_min_v) / y_plot_range * plot_h
        
        # Only show tooltip if mouse is reasonably close to the point in X
        if abs(hx - px) > 20:
            return
            
        # Draw dot
        r = 4
        canvas.create_oval(px-r, py-r, px+r, py+r, fill=self.colors["accent"], outline="white", tags="tooltip")
        
        # Tooltip text
        time_str = time.strftime("%H:%M:%S", time.localtime(self.start_time + t_val))
        text = f"Time: {time_str}\nValue: {v_val:.2f}"
        
        # Tooltip positioning
        text_x = px + 10
        text_y = py - 10
        anchor = "sw"
        if text_x > w - 80:
            text_x = px - 10
            anchor = "se"
        if text_y < 60:
            text_y = py + 10
            anchor = "nw" if anchor == "sw" else "ne"
            
        text_id = canvas.create_text(text_x, text_y, text=text, anchor=anchor, fill="white", font=("Arial", 9), tags="tooltip")
        bbox = canvas.bbox(text_id)
        if bbox:
            pad = 4
            bg_id = canvas.create_rectangle(bbox[0]-pad, bbox[1]-pad, bbox[2]+pad, bbox[3]+pad, fill=self.colors["btn_bg"], outline=self.colors["subtext"], tags="tooltip")
            canvas.tag_lower(bg_id, text_id)

    def start_zoom_box(self, event, view_name):
        self.zoom_box_start = (event.x, event.y)

    def update_zoom_box(self, event, view_name):
        canvas = self.canvases[view_name]
        canvas.delete("zoom_box")
        if self.zoom_box_start:
            x0, y0 = self.zoom_box_start
            canvas.create_rectangle(x0, y0, event.x, event.y, outline=self.colors["accent"], dash=(2, 2), tags="zoom_box")

    def end_zoom_box(self, event, view_name):
        canvas = self.canvases[view_name]
        canvas.delete("zoom_box")
        if not self.zoom_box_start: return
        
        x0, y0 = self.zoom_box_start
        x1, y1 = event.x, event.y
        self.zoom_box_start = None
        
        if abs(x1 - x0) < 10 or abs(y1 - y0) < 10:
            self.zoom_limits[view_name] = None
            self.redraw_visible_graphs()
            return

        plot_info = self.current_plot_params.get(view_name)
        if not plot_info: return
        
        w, h = canvas.winfo_width(), canvas.winfo_height()
        x_m, y_m = plot_info["x_margin"], plot_info["y_margin"]
        pw, ph = plot_info["plot_w"], plot_info["plot_h"]
        
        x0, x1 = max(x_m, min(w - 20, x0)), max(x_m, min(w - 20, x1))
        y0, y1 = max(40, min(h - y_m, y0)), max(40, min(h - y_m, y1))
        
        t0 = plot_info["min_t"] + ((min(x0, x1) - x_m) / pw) * plot_info["x_plot_range"]
        t1 = plot_info["min_t"] + ((max(x0, x1) - x_m) / pw) * plot_info["x_plot_range"]
        
        v0 = plot_info["display_min_v"] + ((h - y_m - max(y0, y1)) / ph) * plot_info["y_plot_range"]
        v1 = plot_info["display_min_v"] + ((h - y_m - min(y0, y1)) / ph) * plot_info["y_plot_range"]
        
        self.zoom_limits[view_name] = (t0, t1, v0, v1)
        self.redraw_visible_graphs()

    def redraw_visible_graphs(self):
        """Redraw whichever graph canvases are currently shown."""
        if self.view_mode == "ALL":
            for view_name in self.canvases:
                self.draw_single_graph(view_name)
        else:
            self.draw_single_graph(self.current_view)

    def on_click(self):
        print("Button clicked")

    def toggle_temp_control_check(self):
        if self.var_auto_temp.get():
            if not self.temperature_profile:
                messagebox.showwarning("Warning", "No temperature profile loaded.", parent=self.root)
                self.var_auto_temp.set(False)
                return
            self.temp_control_active = True
            
            # Disable conflicting power control
            if self.power_control_active:
                self.power_control_active = False
                self.var_auto_power.set(False)
                print("Auto Power Control disabled (Temperature Control taking over).")
                
            if not self.recording_active and not self.pressure_control_active and not self.power_control_active:
                self.start_time = time.time()
        else:
            self.temp_control_active = False
            self.current_target_temp = None

    def toggle_press_control_check(self):
        if self.var_auto_press.get():
            if not self.pressure_profile:
                messagebox.showwarning("Warning", "No pressure profile loaded.", parent=self.root)
                self.var_auto_press.set(False)
                return
            self.pressure_control_active = True
            self.press_prev_error = None
            if not self.recording_active and not self.temp_control_active and not self.power_control_active:
                self.start_time = time.time()
        else:
            self.pressure_control_active = False
            self.current_target_pressure = None
            self.press_prev_error = None
            self.motor_mgr.reset_hardware()
            print("Auto Pressure Control Disabled. Valves closed and motors reset.")

    def toggle_power_control_check(self):
        if self.var_auto_power.get():
            if not self.power_profile:
                messagebox.showwarning("Warning", "No power profile loaded.", parent=self.root)
                self.var_auto_power.set(False)
                return
            self.power_control_active = True
            
            # Disable conflicting temperature control
            if self.temp_control_active:
                self.temp_control_active = False
                self.var_auto_temp.set(False)
                print("Auto Temp Control disabled (Power Control taking over).")
                
            if not self.recording_active and not self.temp_control_active and not self.pressure_control_active:
                self.start_time = time.time()
        else:
            self.power_control_active = False
            self.current_target_power = None

    def start_process(self):
        """Opens the Save Settings Dialog to configure logging before starting."""
        SaveSettingsDialog(self.root, self.save_dir, self.base_filename, self.save_interval_min, self.on_start_confirmed)

    def on_start_confirmed(self, new_dir, new_name, new_interval):
        """Callback when user confirms settings in the dialog."""
        self.save_dir = new_dir
        self.base_filename = new_name
        self.save_interval_min = new_interval
        self.execute_start_process()

    def execute_start_process(self):
        """Starts recording data and plotting (called after settings are confirmed)."""
        self.data_history = {"Temperature": [], "Pressure": [], "Power": [], "Resistance": []}
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
                f.write("Date,Time,Temperature,Pressure,Voltage,Current,Power,Resistance\n")
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
        
        self.current_target_pressure = None
        self.current_target_temp = None
        self.current_target_power = None
        
        self.current_press_time_remaining = None
        self.current_temp_time_remaining = None
        self.current_power_time_remaining = None
        
        self.current_press_segment = None
        self.current_temp_segment = None
        self.current_power_segment = None
        self.press_prev_error = None

        self.recording_active = False
        print("Process Stopped.")

    def connect_hardware(self):
        """Opens serial ports or enables simulation mode if they fail."""
        in_simulation_mode = False
        
        if self.controller_type == 'watlow':
            connection_successful = False
            while not connection_successful:
                self.watlow_controller = WatlowF4T(ip=self.watlow_ip_address)
                if self.watlow_controller.connect():
                    print(f"Successfully connected to Watlow F4T at {self.watlow_ip_address}")
                    connection_successful = True
                else:
                    # Connection failed, show dialog to get user action
                    dialog = WatlowIPDialog(self.root, self.watlow_ip_address)
                    
                    if dialog.action == 'retry':
                        self.watlow_ip_address = dialog.new_ip
                        # Loop will continue and try to connect with the new IP
                    elif dialog.action == 'simulate':
                        self.watlow_controller.enable_simulation()
                        in_simulation_mode = True
                        messagebox.showinfo("Simulation Mode", "Watlow controller will be simulated.")
                        connection_successful = True # Exit the loop
                    else: # 'cancel' or window closed
                        self.root.destroy()
                        return

        elif self.controller_type == 'serial':
            if self.device_mgr.open():
                print("Device manager port opened successfully.")
                self.device_mgr.initialize_texmate_meters()
            else:
                print("Failed to open device manager port. Enabling simulation for devices.")
                self.device_mgr.enable_simulation()
                in_simulation_mode = True
        
        if self.motor_mgr.open():
            print("Motor/Valve port opened successfully.")
        else:
            print("Failed to open Motor/Valve port. Enabling simulation for motors.")
            self.motor_mgr.enable_simulation()
            in_simulation_mode = True

        # If any port failed, open the developer console to show simulated traffic
        if in_simulation_mode:
            self.open_developer_mode()

        self.update_ui_for_controller()

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
            
            with self.serial_lock:
                if self.controller_type == 'watlow':
                    data_snapshot[1] = self.watlow_controller.read_float(REG_TEMP_PV)
                    data_snapshot[2] = self.watlow_controller.read_float(REG_PRESSURE_PV)
                    data_snapshot[3] = self.watlow_controller.read_float(REG_VOLTS)
                    data_snapshot[4] = self.watlow_controller.read_float(REG_AMPS)
                    data_snapshot[5] = 0.0 # No equivalent for Omega readback

                elif self.controller_type == 'serial':
                    port_mapping = [1, 2, 3, 4, 5]
                    for port in port_mapping:
                        val_str = "---"
                        if port == 5:
                            resp = self.device_mgr.send_omega_cmd("$1RD")
                            if resp and len(resp) >= 3:
                                val_str = resp[2:]
                        else:
                            resp = self.device_mgr.send_texmate_cmd(port, "SR")
                            if resp:
                                val_str = resp
                        data_snapshot[port] = val_str
                        time.sleep(0.1)

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
                
                # Update labels (skip calculated values for Power/Resistance)
                if i < 4:
                    self.readout_labels[i].config(text=val_str)
                
                # Parse values for control loop (Port 3=Volts, Port 4=Amps)
                try:
                    # Handle simulation or raw strings
                    if "OVER" in str(val_str):
                        val = 0.0
                    else:
                        clean_val = str(val_str).replace('+', '').replace('SIM_ACK', '0')
                        val = float(clean_val)
                    
                    self.last_valid_readings[port] = val
                    
                    if port == 1: meas_temp = val
                    if port == 2: meas_press = val
                    if port == 3: meas_volts = val
                    if port == 4: meas_amps = val
                except (ValueError, TypeError):
                    pass
            
        # Calculate Power
        current_power = meas_volts * meas_amps

        # Calculate Resistance (R = V / I)
        meas_res = 0.0
        if abs(meas_amps) > 0.0001:
            meas_res = meas_volts / meas_amps
            self.readout_labels[5].config(text=f"{meas_res:.4f}")
        else:
            self.readout_labels[5].config(text="---")
            
        self.readout_labels[4].config(text=f"{current_power:.2f}")

        # Pressure Control Loop (Profile Execution)
        if self.pressure_control_active and self.pressure_profile:
            elapsed_hours = (time.time() - self.start_time) / 3600.0
            target_pressure = 0.0
            accumulated_time = 0.0
            active_segment = None
            time_remaining_hours = 0.0
            current_seg_idx = 0
            
            for i, segment in enumerate(self.pressure_profile):
                duration = segment['duration']
                if elapsed_hours < (accumulated_time + duration):
                    time_in_seg = elapsed_hours - accumulated_time
                    target_pressure = segment['start'] + (segment['rate'] * time_in_seg)
                    active_segment = segment
                    time_remaining_hours = (accumulated_time + duration) - elapsed_hours
                    current_seg_idx = i + 1
                    break
                accumulated_time += duration
            
            if active_segment is None:
                print("Pressure Profile Completed.")
                self.pressure_control_active = False
                self.var_auto_press.set(False)
                self.current_target_pressure = None
                self.current_press_time_remaining = None
                self.current_press_segment = None
                self.press_prev_error = None
                self.motor_mgr.reset_hardware()
                print("Hardware Reset Executed.")
            else:
                self.current_target_pressure = target_pressure
                self.current_press_time_remaining = time_remaining_hours * 60.0
                self.current_press_segment = current_seg_idx
                self.press_total_segments = len(self.pressure_profile)
                if self.controller_type == 'watlow':
                    with self.serial_lock:
                        if self.watlow_controller.read_uint16(REG_PRESSURE_MODE) != 10:
                            self.watlow_controller.write_uint16(REG_PRESSURE_MODE, 10)
                        self.watlow_controller.write_float(REG_PRESSURE_SP, target_pressure)
                else: # serial – motor PID control
                    control_interval = 2.0
                    if current_time - self.last_pressure_control_time >= control_interval:
                        dt = current_time - self.last_pressure_control_time
                        self.last_pressure_control_time = current_time

                        current_rate = active_segment['rate']
                        error = target_pressure - meas_press

                        if self.press_prev_error is None:
                            self.press_prev_error = error

                        delta_error = error - self.press_prev_error
                        self.press_prev_error = error

                        max_steps = 150

                        if current_rate >= 0:
                            Kp = self.pid_settings["pressure_up"]["Kp"]
                            Ki = self.pid_settings["pressure_up"]["Ki"]

                            p_term = Kp * delta_error
                            i_term = Ki * error * dt

                            step_size = int(p_term + i_term)
                            step_size = max(-max_steps, min(max_steps, step_size))

                            if step_size >= 0:
                                cmd = f"BA0;AA8;A+{step_size}"
                            else:
                                cmd = f"BA0;AA8;A{step_size}"

                            self.motor_mgr.send_command(cmd)
                            if hasattr(self, 'debug_win') and self.debug_win.window.winfo_exists():
                                self.debug_win.log(f"AutoPress UP: Target={target_pressure:.1f} Meas={meas_press:.1f} Err={error:.2f} -> CMD: {cmd}")

                        else:
                            Kp = self.pid_settings["pressure_down"]["Kp"]
                            Ki = self.pid_settings["pressure_down"]["Ki"]

                            bleed_error = -error
                            delta_bleed_error = -delta_error

                            p_term = Kp * delta_bleed_error
                            i_term = Ki * bleed_error * dt

                            step_size = int(p_term + i_term)
                            step_size = max(-max_steps, min(max_steps, step_size))

                            if step_size >= 0:
                                cmd = f"AA0;BA8;B-{step_size}"
                            else:
                                cmd = f"AA0;BA8;B+{-step_size}"

                            self.motor_mgr.send_command(cmd)
                            if hasattr(self, 'debug_win') and self.debug_win.window.winfo_exists():
                                self.debug_win.log(f"AutoPress DOWN: Target={target_pressure:.1f} Meas={meas_press:.1f} Err={error:.2f} -> CMD: {cmd}")

        # Temperature Control Loop (Profile Execution)
        if self.temp_control_active and self.temperature_profile:
            elapsed_hours = (time.time() - self.start_time) / 3600.0
            target_temp = 0.0
            accumulated_time = 0.0
            active_segment = None
            time_remaining_hours = 0.0
            current_seg_idx = 0
            for i, segment in enumerate(self.temperature_profile):
                duration = segment['duration']
                if elapsed_hours < (accumulated_time + duration):
                    time_in_seg = elapsed_hours - accumulated_time
                    target_temp = segment['start'] + (segment['rate'] * time_in_seg)
                    active_segment = segment
                    time_remaining_hours = (accumulated_time + duration) - elapsed_hours
                    current_seg_idx = i + 1
                    break
                accumulated_time += duration
            if active_segment is None:
                print("Temperature Profile Completed.")
                self.temp_control_active = False
                self.var_auto_temp.set(False)
                self.current_target_temp = None
                self.current_temp_time_remaining = None
                self.current_temp_segment = None
            else:
                self.current_target_temp = target_temp
                self.current_temp_time_remaining = time_remaining_hours * 60.0
                self.current_temp_segment = current_seg_idx
                self.temp_total_segments = len(self.temperature_profile)
                if self.controller_type == 'watlow':
                    with self.serial_lock:
                        if self.watlow_controller.read_uint16(REG_TEMP_MODE) != 10:
                            self.watlow_controller.write_uint16(REG_TEMP_MODE, 10)
                        self.watlow_controller.write_float(REG_TEMP_SP, target_temp)
                else: # serial – voltage PID control
                    error = target_temp - meas_temp
                    Kp = self.pid_settings["temperature_up"]["Kp"]
                    adjustment = error * Kp

                    self.target_voltage += adjustment
                    self.target_voltage = max(0.0, min(10.0, self.target_voltage))

                    new_volts_str = f"{self.target_voltage:.2f}"
                    if not self.manual_voltage_active and self.ent_target_voltage.get() != new_volts_str:
                        self.ent_target_voltage.delete(0, tk.END)
                        self.ent_target_voltage.insert(0, new_volts_str)

        # Power Control Loop (Profile Execution)
        if self.power_control_active and self.power_profile:
            elapsed_hours = (time.time() - self.start_time) / 3600.0
            target_power = 0.0
            accumulated_time = 0.0
            active_segment = None
            time_remaining_hours = 0.0
            current_seg_idx = 0
            for i, segment in enumerate(self.power_profile):
                duration = segment['duration']
                if elapsed_hours < (accumulated_time + duration):
                    time_in_seg = elapsed_hours - accumulated_time
                    target_power = segment['start'] + (segment['rate'] * time_in_seg)
                    active_segment = segment
                    time_remaining_hours = (accumulated_time + duration) - elapsed_hours
                    current_seg_idx = i + 1
                    break
                accumulated_time += duration
            if active_segment is None:
                print("Power Profile Completed.")
                self.power_control_active = False
                self.var_auto_power.set(False)
                self.current_target_power = None
                self.current_power_time_remaining = None
                self.current_power_segment = None
            else:
                self.target_power_watts = target_power
                self.current_target_power = target_power
                self.current_power_time_remaining = time_remaining_hours * 60.0
                self.current_power_segment = current_seg_idx
                self.power_total_segments = len(self.power_profile)
        
        if self.recording_active:
            if (current_time - self.last_display_update_time) >= 1.0:
                self.last_display_update_time = current_time
                timestamp = time.time() - self.start_time
                self.data_history["Temperature"].append((timestamp, meas_temp))
                self.data_history["Pressure"].append((timestamp, meas_press))
                self.data_history["Power"].append((timestamp, current_power))
                self.data_history["Resistance"].append((timestamp, meas_res))
                
                for key in self.data_history:
                    if len(self.data_history[key]) > 7200:
                        self.data_history[key].pop(0)
                
                self.redraw_visible_graphs()

            if (current_time - self.last_file_save_time) >= (self.save_interval_min * 60):
                try:
                    now = datetime.datetime.now()
                    log_date = now.strftime("%m/%d/%Y")
                    log_time = now.strftime("%H:%M:%S")
                    with open(self.csv_filename, "a") as f:
                        line = f"{log_date},{log_time},{meas_temp:.2f},{meas_press:.2f},{meas_volts:.2f},{meas_amps:.2f},{current_power:.2f},{meas_res:.4f}\n"
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
            if self.controller_type == 'watlow':
                with self.serial_lock:
                    if self.watlow_controller.read_uint16(REG_TEMP_MODE) != 54:
                        self.watlow_controller.write_uint16(REG_TEMP_MODE, 54)
                    error = self.target_power_watts - current_power
                    Kp = self.pid_settings["power_up"]["Kp"]
                    adjustment = error * Kp
                    current_pwr_pct = self.watlow_controller.read_float(REG_TEMP_MANUAL_POWER)
                    if current_pwr_pct is not None:
                        new_pwr_pct = max(0.0, min(100.0, current_pwr_pct + adjustment))
                        self.watlow_controller.write_float(REG_TEMP_MANUAL_POWER, new_pwr_pct)
            else: # serial – voltage PID
                error = self.target_power_watts - current_power
                Kp = self.pid_settings["power_up"]["Kp"]
                adjustment = error * Kp
                self.target_voltage = max(0.0, min(10.0, self.target_voltage + adjustment))
                new_volts_str = f"{self.target_voltage:.2f}"
                if not self.manual_voltage_active and self.ent_target_voltage.get() != new_volts_str:
                    self.ent_target_voltage.delete(0, tk.END)
                    self.ent_target_voltage.insert(0, new_volts_str)
                with self.serial_lock:
                    self.device_mgr.set_omega_voltage(self.target_voltage)

        # Update Status Bar
        self.update_system_status()

        # Schedule next update
        if self.polling_active:
            self.root.after(100, self.update_gui_loop)

    def update_ui_for_controller(self):
        """Disables UI elements that are not compatible with the selected controller."""
        if self.controller_type == 'watlow':
            self.btn_thermocouple_config.config(state="disabled")
            # Update labels for manual control
            tk.Label(self.ent_target_voltage.master, text="Output (%):", bg=self.colors["card"], fg="white", font=("Arial", 12)).pack(side=tk.LEFT, before=self.ent_target_voltage)
        else:
            self.btn_thermocouple_config.config(state="normal")
            tk.Label(self.ent_target_voltage.master, text="Output:", bg=self.colors["card"], fg="white", font=("Arial", 12)).pack(side=tk.LEFT, before=self.ent_target_voltage)

    def update_voltage_state(self, new_voltage):
        """Callback to update target voltage from Manual Control Dialog."""
        self.target_voltage = new_voltage

    def update_system_status(self):
        """Updates the status bar text based on active flags."""
        states = []
        
        def format_time(mins):
            if mins is None: return ""
            if mins >= 60:
                h = int(mins // 60)
                m = int(mins % 60)
                return f"{h}h {m}m"
            else:
                m = int(mins)
                s = int((mins * 60) % 60)
                return f"{m}m {s}s"

        if self.pressure_control_active:
            if getattr(self, 'current_target_pressure', None) is not None:
                rem_str = format_time(self.current_press_time_remaining)
                states.append(f"AUTO PRESS ({self.current_target_pressure:.1f} Bar)")
                self.lbl_press_time.config(text=f"Seg {self.current_press_segment}/{self.press_total_segments} ⏱ {rem_str}")
                self.frm_press_time.grid()
            else:
                states.append("AUTO PRESS")
                self.frm_press_time.grid_remove()
        else:
            self.frm_press_time.grid_remove()
        
        if self.power_control_active:
            if getattr(self, 'current_target_power', None) is not None:
                rem_str = format_time(self.current_power_time_remaining)
                states.append(f"AUTO POWER ({self.current_target_power:.1f} W)")
                self.lbl_power_time.config(text=f"Seg {self.current_power_segment}/{self.power_total_segments} ⏱ {rem_str}")
                self.frm_power_time.grid()
            else:
                states.append("AUTO POWER")
                self.frm_power_time.grid_remove()
        elif self.manual_voltage_active:
            states.append("MANUAL POWER")
            self.frm_power_time.grid_remove()
        else:
            self.frm_power_time.grid_remove()
            
        if self.temp_control_active:
            if getattr(self, 'current_target_temp', None) is not None:
                rem_str = format_time(self.current_temp_time_remaining)
                states.append(f"AUTO TEMP ({self.current_target_temp:.1f} °C)")
                self.lbl_temp_time.config(text=f"Seg {self.current_temp_segment}/{self.temp_total_segments} ⏱ {rem_str}")
                self.frm_temp_time.grid()
            else:
                states.append("AUTO TEMP")
                self.frm_temp_time.grid_remove()
        else:
            self.frm_temp_time.grid_remove()

        # Display output if any control loop (or manual) is actively driving it
        if self.controller_type != 'watlow':
            if self.manual_voltage_active or self.temp_control_active or self.power_control_active:
                states.append(f"Output ({self.target_voltage:.2f})")
        else:
            if self.manual_voltage_active:
                out_val = self.ent_target_voltage.get()
                states.append(f"Output ({out_val}%)")

        if not self.recording_active and not states:
            self.lbl_system_status.config(text="STANDBY", fg=self.colors["danger"])
            return
            
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

    def load_pid_settings(self):
        default_settings = {
            "pressure_up": {"Kp": 20.0, "Ki": 2.0},
            "pressure_down": {"Kp": 20.0, "Ki": 2.0},
            "temperature_up": {"Kp": 0.001, "Ki": 0.0},
            "power_up": {"Kp": 0.01, "Ki": 0.0}
        }
        if os.path.exists(self.pid_config_file):
            try:
                with open(self.pid_config_file, "r") as f:
                    loaded = json.load(f)
                    for k in default_settings:
                        if k in loaded:
                            for gk in default_settings[k]:
                                if gk in loaded[k]:
                                    default_settings[k][gk] = loaded[k][gk]
            except Exception as e:
                print(f"Failed to load PID settings: {e}")
        self.pid_settings = default_settings

    def save_pid_settings(self, new_settings):
        self.pid_settings = new_settings
        try:
            with open(self.pid_config_file, "w") as f:
                json.dump(self.pid_settings, f, indent=4)
            print("PID settings saved.")
            messagebox.showinfo("PID Settings", "Settings successfully saved to pid_config.json")
        except Exception as e:
            print(f"Failed to save PID settings: {e}")
            messagebox.showerror("Error", f"Failed to save PID settings:\n{e}")

    def open_pid_settings(self):
        PIDSettingsDialog(self.root, self.pid_settings, self.save_pid_settings)

    def open_temp_config(self):
        """Opens the Thermocouple Configuration Dialog."""
        ThermocoupleDialog(self.root, self.device_mgr, self.serial_lock)

    def open_pressure_config(self):
        """Opens the Pressure Profile Dialog, downloading from F4T first if connected."""
        if self.controller_type == 'watlow' and self.watlow_controller and not self.watlow_controller.simulated:
            # Show a small "Loading…" splash while we read the F4T over Modbus
            splash = tk.Toplevel(self.root)
            splash.title("Reading F4T Profile…")
            splash.geometry("300x80")
            splash.resizable(False, False)
            splash.grab_set()
            splash.update_idletasks()
            x = self.root.winfo_x() + (self.root.winfo_width() - 300) // 2
            y = self.root.winfo_y() + (self.root.winfo_height() - 80) // 2
            splash.geometry(f"+{x}+{y}")
            tk.Label(splash, text="Downloading Profile 1 from Watlow F4T…",
                     font=("Arial", 10), pady=20).pack()
            progress = ttk.Progressbar(splash, mode="indeterminate", length=260)
            progress.pack(pady=(0, 10))
            progress.start(12)
            splash.update()

            result_holder = [None]

            def _do_download():
                with self.serial_lock:
                    result_holder[0] = self.download_profile_from_watlow(profile_id=1)
                self.root.after(0, _download_done)

            def _download_done():
                progress.stop()
                splash.destroy()
                raw_steps = result_holder[0]

                if raw_steps is not None and len(raw_steps) > 0:
                    print(f"Downloaded {len(raw_steps)} steps from Watlow F4T (Loop 2 / Pressure).")
                    converted = self._convert_f4t_steps_to_profile(raw_steps)
                    self.pressure_profile = list(converted)
                    profile_to_edit = converted
                else:
                    if raw_steps is not None and len(raw_steps) == 0:
                        messagebox.showwarning(
                            "Empty Profile",
                            "Profile 1 on the Watlow F4T has no steps (or only an End step).\n"
                            "The editor will open with your local profile.",
                            parent=self.root)
                    else:
                        messagebox.showerror(
                            "Download Failed",
                            "Could not retrieve Profile 1 from the Watlow F4T.\n"
                            "Check the connection and try again.\n\n"
                            "The editor will open with your local profile.",
                            parent=self.root)
                    profile_to_edit = self.pressure_profile

                ProfileEditorDialog(
                    self.root, profile_to_edit, self.save_pressure_profile,
                    title="Input Pressure Profile",
                    value_label="Pressure (Bar)",
                    rate_label="Rate (Bars/Hr)",
                    f4t_ip=self.watlow_ip_address,
                    f4t_connected=True,
                    loop=2)

            threading.Thread(target=_do_download, daemon=True).start()
        else:
            # No Watlow / simulation – just open the editor with whatever we have locally
            ProfileEditorDialog(
                self.root, self.pressure_profile, self.save_pressure_profile,
                title="Input Pressure Profile",
                value_label="Pressure (Bar)",
                rate_label="Rate (Bars/Hr)",
                f4t_ip=None,
                f4t_connected=False,
                loop=2)

    def _convert_f4t_steps_to_profile(self, raw_steps):
        """
        Convert the list of raw F4T step dicts (from download_profile_from_watlow)
        into the {start, end, duration, rate} segment format that ProfileEditorDialog uses.

        raw_steps entries:
            type_name  – str  e.g. "Ramp Time", "Soak", "Ramp Rate", "Instant Change"
            target     – float (Loop 2 setpoint, Bar)
            duration_h – float (total hours)
            rate       – float (ramp rate in units/hr, only meaningful for Ramp Rate steps)
        """
        segments = []
        last_end = 0.0

        for step in raw_steps:
            t = step['type_name']
            target = step['target']
            dur_h  = step['duration_h']

            if t == "Soak":
                # Soak: hold at the same pressure for the duration
                segments.append({
                    'start':    target,
                    'end':      target,
                    'duration': dur_h,
                    'rate':     0.0
                })
            elif t == "Ramp Time":
                # Ramp Time: go from last_end to target over the given duration
                rate = (target - last_end) / dur_h if dur_h > 0 else 0.0
                segments.append({
                    'start':    last_end,
                    'end':      target,
                    'duration': dur_h,
                    'rate':     rate
                })
            elif t == "Ramp Rate":
                # Ramp Rate: step stores the rate directly; derive duration
                rate = step['rate']
                delta = abs(target - last_end)
                dur_h = (delta / rate) if rate > 0 else 0.0
                segments.append({
                    'start':    last_end,
                    'end':      target,
                    'duration': dur_h,
                    'rate':     rate if target >= last_end else -rate
                })
            elif t == "Instant Change":
                # Instant change: jump setpoint immediately (zero duration)
                segments.append({
                    'start':    last_end,
                    'end':      target,
                    'duration': 0.0,
                    'rate':     0.0
                })
            # Wait For / Jump / End steps are metadata-only and don't map to segments
            else:
                continue

            last_end = target

        return segments

    def save_pressure_profile(self, new_profile):
        # Separate the End-action sentinel (last dict) from the real segments
        end_action = "User"
        if new_profile and new_profile[-1].get('step_type') == 'End':
            end_action = new_profile[-1].get('end_action', 'User')
            new_profile = new_profile[:-1]

        self.pressure_profile = new_profile
        print(f"Pressure Profile Saved: {len(self.pressure_profile)} segments  "
              f"End Action: {end_action}")

        if self.controller_type == 'watlow' and self.watlow_controller:
            if messagebox.askyesno("Watlow F4T", "Upload this profile to Watlow F4T (Profile 1)?", parent=self.root):
                steps = []
                for seg in new_profile:
                    steps.append({
                        'end':       seg['end'],
                        'duration':  seg['duration'] * 60.0,   # hours → minutes
                        'rate':      seg.get('rate', 0.0),
                        'step_type': seg.get('step_type', 'Ramp Time'),
                    })

                with self.serial_lock:
                    success = self.upload_profile_to_watlow(steps, end_action=end_action)

                if success:
                    messagebox.showinfo("Success", "Profile uploaded successfully.", parent=self.root)
                    if messagebox.askyesno("Success", "Profile uploaded successfully.\n\nStart Profile 1 now?", parent=self.root):
                        with self.serial_lock:
                            self.watlow_controller.write_uint16(_REG_PROF_ACTION, 1782)
                else:
                    messagebox.showerror("Error", "Failed to upload profile.", parent=self.root)

    def download_profile_from_watlow(self, profile_id=1):
        """
        Download all steps from F4T Profile 1 (Loop 2 / Pressure) using the
        register map validated in profile_pressure.py.

        Returns a list of step dicts on success, [] for an empty/End-only profile,
        or None on communication failure.
        """
        if not HAS_PYMODBUS:
            print("pymodbus not available – cannot download F4T profile.")
            return None

        steps = []
        # Open a fresh, dedicated Modbus connection (avoids contention with the
        # WatlowF4T client that uses a different read/write abstraction).
        client = _ModbusTcpClient(self.watlow_ip_address, port=502, timeout=3)
        if not client.connect():
            print(f"F4T profile download: could not connect to {self.watlow_ip_address}:502")
            return None

        def _safe_read(reg, count):
            try:
                r = client.read_holding_registers(reg, count=count)
                return r if (r and not r.isError()) else None
            except Exception as exc:
                print(f"  _safe_read({reg}) error: {exc}")
                return None

        def _safe_write(reg, val):
            try:
                return client.write_register(reg, value=val)
            except Exception as exc:
                print(f"  _safe_write({reg}) error: {exc}")
                return None

        try:
            # How many steps does the profile have?
            res = _safe_read(_REG_PROF_NUM_STEPS, 1)
            if res is None:
                print("F4T profile download: could not read step count.")
                return None

            total_steps = res.registers[0]
            print(f"  F4T reports {total_steps} step(s) in Profile 1.")

            for i in range(1, total_steps + 1):
                # Select the step
                _safe_write(_REG_PROF_STEP_SEL, i)
                time.sleep(0.05)   # give the controller time to latch

                # Read 24 registers starting at 18926 to cover all Loop 2 fields:
                #   offset  0 – Step Type   (18926)
                #   offset  2 – Hours       (18928)
                #   offset  4 – Minutes     (18930)
                #   offset  6 – Seconds     (18932)
                #   offset 14 – Rate 2      (18940, float, 2 regs)
                #   offset 22 – SetPoint 2  (18948, float, 2 regs)
                data = _safe_read(_REG_PROF_STEP_TYPE, 24)
                if data is None:
                    print(f"  Step {i}: read failed, skipping.")
                    continue

                r = data.registers
                t_val     = r[0]
                t_name    = _F4T_TYPE_MAP.get(t_val, f"Code {t_val}")
                hours     = r[2]
                minutes   = r[4]
                seconds   = r[6]
                duration_h = hours + minutes / 60.0 + seconds / 3600.0
                rate      = _decode_f4t_float(r[14:16])   # Loop 2 ramp rate
                target    = _decode_f4t_float(r[22:24])   # Loop 2 setpoint

                print(f"  Step {i}: {t_name}  target={target:.3f}  "
                      f"dur={hours:02d}:{minutes:02d}:{seconds:02d}  rate={rate:.3f}")

                if t_val == 27:   # End step – stop here
                    break

                steps.append({
                    'type_val':   t_val,
                    'type_name':  t_name,
                    'target':     target,
                    'duration_h': duration_h,
                    'rate':       rate,
                    'hours':      hours,
                    'minutes':    minutes,
                    'seconds':    seconds,
                })

            return steps

        except Exception as exc:
            print(f"F4T profile download exception: {exc}")
            return None
        finally:
            client.close()

    def upload_profile_to_watlow(self, steps, profile_id=1, end_action="User"):
        """
        Upload profile segments to F4T Profile 1 (Loop 2 / Pressure).

        Each step dict contains:
            'end'       – float  target setpoint (Bar)
            'duration'  – float  duration in minutes  (used for Soak / Ramp Time)
            'rate'      – float  ramp rate in Bar/hr   (used for Ramp Rate)
            'step_type' – str    "Soak" | "Ramp Time" | "Ramp Rate"

        end_action: "User" | "Off" | "Hold"  — written to reg 19032 on the End step.
        F4T step type codes:  Soak=87, Ramp Time=1928, Ramp Rate=81
        """
        if not HAS_PYMODBUS:
            print("pymodbus not available – cannot upload F4T profile.")
            return False

        _TYPE_CODES     = {"Soak": 87, "Ramp Time": 1928, "Ramp Rate": 81}
        _END_ACT_CODES  = {"User": 100, "Off": 62, "Hold": 47}

        client = _ModbusTcpClient(self.watlow_ip_address, port=502, timeout=3)
        if not client.connect():
            print(f"F4T profile upload: could not connect to {self.watlow_ip_address}:502")
            return False

        def _write(reg, val):
            try:
                return client.write_register(reg, value=val)
            except Exception as exc:
                print(f"  upload _write({reg}) error: {exc}")
                return None

        def _write_float(reg, value):
            try:
                words = _encode_f4t_float(value)
                return client.write_registers(reg, words)
            except Exception as exc:
                print(f"  upload _write_float({reg}) error: {exc}")
                return None

        try:
            for i, step in enumerate(steps):
                step_num  = i + 1
                step_type = step.get('step_type', 'Ramp Time')
                type_code = _TYPE_CODES.get(step_type, 1928)

                _write(_REG_PROF_STEP_SEL, step_num)
                time.sleep(0.04)
                _write(_REG_PROF_EDIT_ACT, 1770)
                time.sleep(0.02)

                _write(_REG_PROF_STEP_TYPE, type_code)
                _write_float(_REG_PROF_SP2, float(step['end']))

                if step_type == "Ramp Rate":
                    _write_float(_REG_PROF_RATE2, abs(float(step['rate'])))
                    print(f"  Uploaded step {step_num} [{step_type}]: "
                          f"target={step['end']:.2f} Bar  rate={step['rate']:.4f} Bar/hr")
                else:
                    total_s = int(round(step['duration'] * 60))   # minutes → seconds
                    h, rem  = divmod(total_s, 3600)
                    m, s    = divmod(rem, 60)
                    _write(_REG_PROF_TIME_H, h)
                    _write(_REG_PROF_TIME_M, m)
                    _write(_REG_PROF_TIME_S, s)
                    print(f"  Uploaded step {step_num} [{step_type}]: "
                          f"target={step['end']:.2f} Bar  dur={h:02d}:{m:02d}:{s:02d}")

                time.sleep(0.04)

            # Write End step
            end_step_num = len(steps) + 1
            _write(_REG_PROF_STEP_SEL, end_step_num)
            time.sleep(0.04)
            _write(_REG_PROF_EDIT_ACT, 1770)
            time.sleep(0.02)
            _write(_REG_PROF_STEP_TYPE, 27)   # 27 = End
            # Write Loop 2 End Action
            ea_code = _END_ACT_CODES.get(end_action, 100)
            _write(_REG_PROF_END_ACT2, ea_code)
            print(f"  Uploaded End step at position {end_step_num}  "
                  f"End Action={end_action} ({ea_code}).")
            return True

        except Exception as exc:
            print(f"F4T profile upload exception: {exc}")
            return False
        finally:
            client.close()

    def open_temp_profile(self):
        """Opens the Temperature Profile Dialog, downloading from F4T first if connected."""
        if self.controller_type == 'watlow' and self.watlow_controller and not self.watlow_controller.simulated:
            # Show a small "Loading…" splash while we read the F4T over Modbus
            splash = tk.Toplevel(self.root)
            splash.title("Reading F4T Profile…")
            splash.geometry("300x80")
            splash.resizable(False, False)
            splash.grab_set()
            splash.update_idletasks()
            x = self.root.winfo_x() + (self.root.winfo_width() - 300) // 2
            y = self.root.winfo_y() + (self.root.winfo_height() - 80) // 2
            splash.geometry(f"+{x}+{y}")
            tk.Label(splash, text="Downloading Profile 1 from Watlow F4T…",
                     font=("Arial", 10), pady=20).pack()
            progress = ttk.Progressbar(splash, mode="indeterminate", length=260)
            progress.pack(pady=(0, 10))
            progress.start(12)
            splash.update()

            result_holder = [None]

            def _do_download():
                with self.serial_lock:
                    result_holder[0] = self.download_temp_profile_from_watlow(profile_id=1)
                self.root.after(0, _download_done)

            def _download_done():
                progress.stop()
                splash.destroy()
                raw_steps = result_holder[0]

                if raw_steps is not None and len(raw_steps) > 0:
                    print(f"Downloaded {len(raw_steps)} steps from Watlow F4T (Loop 1 / Temperature).")
                    converted = self._convert_f4t_steps_to_profile(raw_steps)
                    self.temperature_profile = list(converted)
                    profile_to_edit = converted
                else:
                    if raw_steps is not None and len(raw_steps) == 0:
                        messagebox.showwarning(
                            "Empty Profile",
                            "Profile 1 on the Watlow F4T has no steps (or only an End step).\n"
                            "The editor will open with your local profile.",
                            parent=self.root)
                    else:
                        messagebox.showerror(
                            "Download Failed",
                            "Could not retrieve Profile 1 from the Watlow F4T.\n"
                            "Check the connection and try again.\n\n"
                            "The editor will open with your local profile.",
                            parent=self.root)
                    profile_to_edit = self.temperature_profile

                ProfileEditorDialog(
                    self.root, profile_to_edit, self.save_temp_profile,
                    title="Input Temperature Profile",
                    value_label="Temperature (°C)",
                    rate_label="Rate (°C/Hr)",
                    f4t_ip=self.watlow_ip_address,
                    f4t_connected=True,
                    loop=1)

            threading.Thread(target=_do_download, daemon=True).start()
        else:
            # No Watlow / simulation – open editor with whatever is stored locally
            ProfileEditorDialog(
                self.root, self.temperature_profile, self.save_temp_profile,
                title="Input Temperature Profile",
                value_label="Temperature (°C)",
                rate_label="Rate (°C/Hr)",
                f4t_ip=None,
                f4t_connected=False,
                loop=1)

    def save_temp_profile(self, new_profile):
        # Separate the End-action sentinel from the real segments
        end_action = "User"
        if new_profile and new_profile[-1].get('step_type') == 'End':
            end_action = new_profile[-1].get('end_action', 'User')
            new_profile = new_profile[:-1]

        self.temperature_profile = new_profile
        print(f"Temperature Profile Saved: {len(self.temperature_profile)} segments  "
              f"End Action: {end_action}")

        if self.controller_type == 'watlow' and self.watlow_controller:
            if messagebox.askyesno("Watlow F4T", "Upload this profile to Watlow F4T (Profile 1)?", parent=self.root):
                steps = []
                for seg in new_profile:
                    steps.append({
                        'end':       seg['end'],
                        'duration':  seg['duration'] * 60.0,   # hours → minutes
                        'rate':      seg.get('rate', 0.0),
                        'step_type': seg.get('step_type', 'Ramp Time'),
                    })

                with self.serial_lock:
                    success = self.upload_temp_profile_to_watlow(steps, end_action=end_action)

                if success:
                    if messagebox.askyesno("Success", "Profile uploaded successfully.\n\nStart Profile 1 now?", parent=self.root):
                        with self.serial_lock:
                            self.watlow_controller.write_uint16(_REG_PROF_ACTION, 1782)
                else:
                    messagebox.showerror("Error", "Failed to upload temperature profile.", parent=self.root)

    def download_temp_profile_from_watlow(self, profile_id=1):
        """
        Download all steps from F4T Profile 1 (Loop 1 / Temperature) using the
        register map validated in profile_temp.py.

        Returns a list of step dicts on success, [] for an empty/End-only profile,
        or None on communication failure.
        """
        if not HAS_PYMODBUS:
            print("pymodbus not available – cannot download F4T temperature profile.")
            return None

        steps = []
        client = _ModbusTcpClient(self.watlow_ip_address, port=502, timeout=3)
        if not client.connect():
            print(f"F4T temp profile download: could not connect to {self.watlow_ip_address}:502")
            return None

        def _safe_read(reg, count):
            try:
                r = client.read_holding_registers(reg, count=count)
                return r if (r and not r.isError()) else None
            except Exception as exc:
                print(f"  _safe_read({reg}) error: {exc}")
                return None

        def _safe_write(reg, val):
            try:
                return client.write_register(reg, value=val)
            except Exception as exc:
                print(f"  _safe_write({reg}) error: {exc}")
                return None

        try:
            res = _safe_read(_REG_PROF_NUM_STEPS, 1)
            if res is None:
                print("F4T temp profile download: could not read step count.")
                return None

            total_steps = res.registers[0]
            print(f"  F4T reports {total_steps} step(s) in Profile 1 (Temperature).")

            for i in range(1, total_steps + 1):
                _safe_write(_REG_PROF_STEP_SEL, i)
                time.sleep(0.05)

                # Read 22 registers from 18926 to cover Loop 1 fields:
                #   offset  0 – Step Type   (18926)
                #   offset  2 – Hours       (18928)
                #   offset  4 – Minutes     (18930)
                #   offset  6 – Seconds     (18932)
                #   offset 12 – Rate 1      (18938, float, 2 regs)
                #   offset 20 – SetPoint 1  (18946, float, 2 regs)
                data = _safe_read(_REG_PROF_STEP_TYPE, 22)
                if data is None:
                    print(f"  Step {i}: read failed, skipping.")
                    continue

                r = data.registers
                t_val      = r[0]
                t_name     = _F4T_TYPE_MAP.get(t_val, f"Code {t_val}")
                hours      = r[2]
                minutes    = r[4]
                seconds    = r[6]
                duration_h = hours + minutes / 60.0 + seconds / 3600.0
                rate       = _decode_f4t_float(r[12:14])   # Loop 1 ramp rate
                target     = _decode_f4t_float(r[20:22])   # Loop 1 setpoint

                print(f"  Step {i}: {t_name}  target={target:.3f} °C  "
                      f"dur={hours:02d}:{minutes:02d}:{seconds:02d}  rate={rate:.3f}")

                if t_val == 27:   # End step – stop here
                    break

                steps.append({
                    'type_val':   t_val,
                    'type_name':  t_name,
                    'target':     target,
                    'duration_h': duration_h,
                    'rate':       rate,
                    'hours':      hours,
                    'minutes':    minutes,
                    'seconds':    seconds,
                })

            return steps

        except Exception as exc:
            print(f"F4T temp profile download exception: {exc}")
            return None
        finally:
            client.close()

    def upload_temp_profile_to_watlow(self, steps, profile_id=1, end_action="User"):
        """
        Upload profile segments to F4T Profile 1 (Loop 1 / Temperature).

        Each step dict contains:
            'end'       – float  target setpoint (°C)
            'duration'  – float  duration in minutes  (used for Soak / Ramp Time)
            'rate'      – float  ramp rate in °C/hr    (used for Ramp Rate)
            'step_type' – str    "Soak" | "Ramp Time" | "Ramp Rate"

        end_action: "User" | "Off" | "Hold"  — written to reg 19030 on the End step.
        F4T step type codes:  Soak=87, Ramp Time=1928, Ramp Rate=81
        """
        if not HAS_PYMODBUS:
            print("pymodbus not available – cannot upload F4T temperature profile.")
            return False

        _TYPE_CODES    = {"Soak": 87, "Ramp Time": 1928, "Ramp Rate": 81}
        _END_ACT_CODES = {"User": 100, "Off": 62, "Hold": 47}

        client = _ModbusTcpClient(self.watlow_ip_address, port=502, timeout=3)
        if not client.connect():
            print(f"F4T temp profile upload: could not connect to {self.watlow_ip_address}:502")
            return False

        def _write(reg, val):
            try:
                return client.write_register(reg, value=val)
            except Exception as exc:
                print(f"  upload _write({reg}) error: {exc}")
                return None

        def _write_float(reg, value):
            try:
                words = _encode_f4t_float(value)
                return client.write_registers(reg, words)
            except Exception as exc:
                print(f"  upload _write_float({reg}) error: {exc}")
                return None

        try:
            for i, step in enumerate(steps):
                step_num  = i + 1
                step_type = step.get('step_type', 'Ramp Time')
                type_code = _TYPE_CODES.get(step_type, 1928)

                _write(_REG_PROF_STEP_SEL, step_num)
                time.sleep(0.04)
                _write(_REG_PROF_EDIT_ACT, 1770)
                time.sleep(0.02)

                _write(_REG_PROF_STEP_TYPE, type_code)
                _write_float(_REG_PROF_SP1, float(step['end']))

                if step_type == "Ramp Rate":
                    _write_float(_REG_PROF_RATE1, abs(float(step['rate'])))
                    print(f"  Uploaded step {step_num} [{step_type}]: "
                          f"target={step['end']:.2f} °C  rate={step['rate']:.4f} °C/hr")
                else:
                    total_s = int(round(step['duration'] * 60))   # minutes → seconds
                    h, rem  = divmod(total_s, 3600)
                    m, s    = divmod(rem, 60)
                    _write(_REG_PROF_TIME_H, h)
                    _write(_REG_PROF_TIME_M, m)
                    _write(_REG_PROF_TIME_S, s)
                    print(f"  Uploaded step {step_num} [{step_type}]: "
                          f"target={step['end']:.2f} °C  dur={h:02d}:{m:02d}:{s:02d}")

                time.sleep(0.04)

            # Write End step
            end_step_num = len(steps) + 1
            _write(_REG_PROF_STEP_SEL, end_step_num)
            time.sleep(0.04)
            _write(_REG_PROF_EDIT_ACT, 1770)
            time.sleep(0.02)
            _write(_REG_PROF_STEP_TYPE, 27)   # 27 = End
            # Write Loop 1 End Action
            ea_code = _END_ACT_CODES.get(end_action, 100)
            _write(_REG_PROF_END_ACT1, ea_code)
            print(f"  Uploaded End step at position {end_step_num}  "
                  f"End Action={end_action} ({ea_code}).")
            return True

        except Exception as exc:
            print(f"F4T temp profile upload exception: {exc}")
            return False
        finally:
            client.close()

    def open_power_profile(self):
        ProfileEditorDialog(self.root, self.power_profile, self.save_power_profile, title="Input Power Profile", value_label="Power (Watts)", rate_label="Rate (Watts/Hr)")

    def save_power_profile(self, new_profile):
        # Strip End-action sentinel if present (ProfileEditorDialog always appends one)
        if new_profile and new_profile[-1].get('step_type') == 'End':
            new_profile = new_profile[:-1]
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
        SystemControlsDialog(self.root, self.device_mgr, self.motor_mgr, self.serial_lock, self.controller_type)

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
            if self.device_mgr.simulated or self.motor_mgr.simulated or (self.watlow_controller and self.watlow_controller.simulated):
                self.debug_win.log("NOTE: Running in Simulation Mode due to port connection failure on startup.")

    def cleanup_and_exit(self):
        self.polling_active = False
        if self.controller_type == 'watlow' and self.watlow_controller:
            self.watlow_controller.client.close() if self.watlow_controller.client else None
        else:
            self.device_mgr.close()
        self.motor_mgr.close()
        self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = BaseAPGUI(root)
    root.mainloop()
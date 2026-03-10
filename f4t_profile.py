import tkinter as tk
from tkinter import ttk, messagebox
import struct
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from pymodbus.client import ModbusTcpClient

class F4TApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Watlow F4T Master Control")
        self.client = None
        self.profiles = {"Current Session": []}
        self.current_profile_name = "Current Session"
        self.type_map = {"Soak": 0, "Ramp Time": 1, "Ramp Rate": 2, "Instant Change": 3, "End": 6}
        self.inv_type_map = {v: k for k, v in self.type_map.items()}
        
        self.setup_ui()
        self.poll_loop() # Start the background status checker

    # --- THE "FIX" FOR VERSION ERRORS ---
    def safe_write(self, reg, val):
        """Tries 'slave' keyword, then falls back to positional to avoid 'unit' errors."""
        try:
            return self.client.write_register(reg, val, slave=1)
        except TypeError:
            # If 'slave' fails, try passing it as a positional argument or just the reg/val
            return self.client.write_register(reg, val)

    def safe_write_mult(self, reg, vals):
        try:
            return self.client.write_registers(reg, vals, slave=1)
        except TypeError:
            return self.client.write_registers(reg, vals)

    def safe_read(self, reg, count):
        try:
            return self.client.read_holding_registers(reg, count, slave=1)
        except TypeError:
            return self.client.read_holding_registers(reg, count)

    # --- DATA CONVERSIONS ---
    def float_to_regs(self, val):
        packed = struct.pack('>f', float(val))
        regs = struct.unpack('>HH', packed)
        return [regs[1], regs[0]] # F4T standard Word Swap

    def regs_to_float(self, regs):
        packed = struct.pack('>HH', regs[1], regs[0])
        return round(struct.unpack('>f', packed)[0], 2)

    # --- CONNECTION & ENGINE CONTROL ---
    def toggle_connect(self):
        if self.client and self.client.connected:
            self.client.close()
            self.status_label.config(text="Disconnected", foreground="red")
        else:
            self.client = ModbusTcpClient(self.ip_var.get(), port=502, timeout=2)
            if self.client.connect():
                self.status_label.config(text="Connected", foreground="green")
            else:
                messagebox.showerror("Conn Error", "F4T not found at this IP.")

    def run_profile(self):
        if not self.client or not self.client.connected: return
        self.safe_write(16510, 1) # Ensure Profile 1 is active
        self.safe_write(16562, 1) # Action: Start

    def stop_profile(self):
        if self.client and self.client.connected:
            self.safe_write(16562, 4) # Action: Terminate

    # --- UPLOAD & READ ---
    def upload_all(self):
        if not self.client or not self.client.connected: return
        steps = self.profiles[self.current_profile_name]
        try:
            self.safe_write(16510, 1)
            for i, step in enumerate(steps):
                s_id = i + 1
                self.safe_write(16512, s_id)
                self.safe_write(16514, self.type_map[step['type']])
                self.safe_write_mult(16516, self.float_to_regs(step['value']))
                self.safe_write_mult(16520, self.float_to_regs(step['mins']))
            messagebox.showinfo("F4T", "Profile Uploaded Successfully")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # --- POLLING LOOP ---
    def poll_loop(self):
        if self.client and self.client.connected:
            try:
                # Read Engine State (16560) and Current Step (16570)
                res = self.safe_read(16560, 12)
                if not res.isError():
                    state = res.registers[0]
                    curr_step = res.registers[10]
                    states = {0: "Idle", 1: "Running", 2: "Paused", 4: "Done"}
                    self.engine_label.config(text=f"Engine: {states.get(state, '??')}")
                    self.step_info.config(text=f"F4T Step: {curr_step}")
            except: pass
        self.root.after(2000, self.poll_loop)

    # --- UI SETUP ---
    def setup_ui(self):
        # Connection Frame
        c_fr = ttk.LabelFrame(self.root, text="F4T Network", padding=5)
        c_fr.pack(fill="x", padx=10, pady=5)
        self.ip_var = tk.StringVar(value="192.168.0.222")
        ttk.Entry(c_fr, textvariable=self.ip_var, width=15).pack(side="left", padx=5)
        ttk.Button(c_fr, text="Connect", command=self.toggle_connect).pack(side="left")
        self.status_label = ttk.Label(c_fr, text="Disconnected", foreground="red")
        self.status_label.pack(side="left", padx=10)

        # Control Frame
        ctrl_fr = ttk.Frame(self.root, padding=5)
        ctrl_fr.pack(fill="x")
        ttk.Button(ctrl_fr, text="▶ START", command=self.run_profile).pack(side="left", padx=5)
        ttk.Button(ctrl_fr, text="⏹ STOP", command=self.stop_profile).pack(side="left", padx=5)
        self.engine_label = ttk.Label(ctrl_fr, text="Engine: --")
        self.engine_label.pack(side="right", padx=10)
        self.step_info = ttk.Label(ctrl_fr, text="F4T Step: --")
        self.step_info.pack(side="right", padx=10)

        # Main Layout
        panes = ttk.PanedWindow(self.root, orient="horizontal")
        panes.pack(fill="both", expand=True)
        self.s_fr = ttk.LabelFrame(panes, text="Editor"); panes.add(self.s_fr, weight=1)
        self.c_fr = ttk.LabelFrame(panes, text="Chart"); panes.add(self.c_fr, weight=2)

        self.fig, self.ax = plt.subplots(figsize=(4, 3))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.c_fr)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        ttk.Button(self.s_fr, text="+ Add Step", command=self.add_step).pack(fill="x")
        ttk.Button(self.s_fr, text="UPLOAD TO F4T", command=self.upload_all).pack(fill="x", pady=5)
        self.steps_cont = ttk.Frame(self.s_fr); self.steps_cont.pack(fill="both")
        
        self.refresh_ui()

    def add_step(self):
        self.profiles[self.current_profile_name].append({'type': 'Soak', 'value': 25.0, 'mins': 10})
        self.refresh_ui()

    def refresh_ui(self):
        for w in self.steps_cont.winfo_children(): w.destroy()
        for i, s in enumerate(self.profiles[self.current_profile_name]):
            row = ttk.Frame(self.steps_cont); row.pack(fill="x")
            cb = ttk.Combobox(row, values=list(self.type_map.keys()), width=10)
            cb.set(s['type']); cb.pack(side="left")
            cb.bind("<<ComboboxSelected>>", lambda e, idx=i, v=cb: self.upd(idx, 'type', v.get()))
            v_e = ttk.Entry(row, width=6); v_e.insert(0, s['value']); v_e.pack(side="left", padx=2)
            v_e.bind("<FocusOut>", lambda e, idx=i, v=v_e: self.upd(idx, 'value', v.get()))
            t_e = ttk.Entry(row, width=6); t_e.insert(0, s['mins']); t_e.pack(side="left")
            t_e.bind("<FocusOut>", lambda e, idx=i, v=t_e: self.upd(idx, 'mins', v.get()))

        self.update_chart()

    def upd(self, idx, k, v):
        try:
            self.profiles[self.current_profile_name][idx][k] = float(v) if k != 'type' else v
            self.update_chart()
        except: pass

    def update_chart(self):
        self.ax.clear()
        steps = self.profiles[self.current_profile_name]
        if steps:
            t_p, v_p, cur_t = [0], [steps[0]['value']], 0
            for s in steps:
                cur_t += s['mins']; t_p.append(cur_t); v_p.append(s['value'])
            self.ax.plot(t_p, v_p, 'b-o')
        self.ax.grid(True); self.canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    F4TApp(root)
    root.mainloop() # Start the GUI event loop
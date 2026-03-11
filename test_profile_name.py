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
        self.root.title("Watlow F4T Master - 18888 Map")
        
        # Internal Data
        self.profiles = {"Current Session": []}
        self.current_profile_name = "Current Session"
        self.type_map = {"Soak": 0, "Ramp Time": 1, "Ramp Rate": 2, "Instant Change": 3, "End": 6}
        
        self.setup_ui()
        
        # --- AUTO-CONNECT LOGIC ---
        self.client = ModbusTcpClient("10.4.11.144", port=502, timeout=2)
        self.attempt_auto_connect() # Fixed typo here
        
        # Cleanup on close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.poll_loop()

    def on_closing(self):
        if self.client: self.client.close()
        self.root.destroy()

    def attempt_auto_connect(self):
        if self.client.connect():
            self.status_label.config(text="Connected: 10.4.11.144", foreground="green")
            self.log("System initialized. Connected to F4T at 10.4.11.144")
        else:
            self.status_label.config(text="OFFLINE", foreground="red")
            self.log("Error: Target 10.4.11.144 unreachable.")

    def log(self, message):
        self.log_box.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {message}\n")
        self.log_box.see(tk.END)

    # --- VERSION-PROOF WRAPPERS (Keyword-Only) ---
    def safe_read(self, reg, count):
        try:
            return self.client.read_holding_registers(reg, count=count)
        except Exception:
            return None

    def safe_write(self, reg, val):
        try:
            return self.client.write_register(reg, value=val)
        except Exception:
            return None

    def safe_write_mult(self, reg, vals):
        try:
            return self.client.write_registers(reg, values=vals)
        except Exception:
            return None

    # --- NAME HANDLING (1 Char per Register) ---
    def write_profile_name_only(self):
        self.write_profile_name(self.name_var.get())

    def write_profile_name(self, name_str):
        if not self.client or not self.client.connected: return
        
        # Handshake/Select Profile
        self.safe_write(18888, 1) 
        time.sleep(0.1)
        
        # Convert string to ASCII
        registers = [ord(c) for c in name_str[:20]]
        
        # IMPORTANT: Pad with 32 (Space) instead of 0 to avoid underscores
        while len(registers) < 20:
            registers.append(32) 
            
        if self.safe_write_mult(16886, registers):
            self.log(f"Profile Name '{name_str}' updated with space padding.")

    def read_profile_name(self):
        if not self.client or not self.client.connected: return
        # Read 20 registers starting at 16886 (one for each char)
        res = self.safe_read(16886, 20)
        if res and hasattr(res, 'registers'):
            chars = []
            for r in res.registers:
                if 32 <= r <= 126: # Filter for printable ASCII
                    chars.append(chr(r))
                elif r == 0: # Stop at null terminator
                    break
            name = "".join(chars).strip()
            self.name_var.set(name)
            self.log(f"Hardware confirms name: {name}")

    # --- PROFILE UPLOAD ---
    def upload_all(self):
        if not self.client or not self.client.connected: return
        try:
            self.safe_write(18888, 1) # Set Target
            self.write_profile_name(self.name_var.get())
            
            steps = self.profiles[self.current_profile_name]
            for i, step in enumerate(steps):
                s_id = i + 1
                self.safe_write(18890, s_id)                             # Step Number
                self.safe_write(18892, self.type_map[step['type']])      # Step Type
                
                # Target & Minutes (32-bit Floats with F4T word swap)
                t_regs = struct.unpack('>HH', struct.pack('>f', float(step['value'])))
                self.safe_write_mult(18894, [t_regs[1], t_regs[0]])
                
                m_regs = struct.unpack('>HH', struct.pack('>f', float(step['mins'])))
                self.safe_write_mult(18898, [m_regs[1], m_regs[0]])
                self.log(f"Step {s_id} OK.")
                
            messagebox.showinfo("Success", "Hardware Sync Complete.")
        except Exception as e:
            self.log(f"Upload error: {e}")

    # --- UI SETUP ---
    def setup_ui(self):
        top = ttk.Frame(self.root, padding=10); top.pack(fill="x")
        ttk.Label(top, text="Profile Name:").pack(side="left")
        self.name_var = tk.StringVar(value="TEST_PROFILE")
        ttk.Entry(top, textvariable=self.name_var, width=20).pack(side="left", padx=5)
        ttk.Button(top, text="Read Name", command=self.read_profile_name).pack(side="left", padx=2)
        ttk.Button(top, text="Write Name", command=self.write_profile_name_only).pack(side="left", padx=2)
        
        self.pv_label = ttk.Label(top, text="PV: -- °F", font=('Arial', 10, 'bold'), foreground="blue")
        self.pv_label.pack(side="right", padx=10)
        self.status_label = ttk.Label(top, text="Connecting...", foreground="gray")
        self.status_label.pack(side="right", padx=5)

        ctrl = ttk.Frame(self.root, padding=5); ctrl.pack(fill="x")
        ttk.Button(ctrl, text="UPLOAD ALL", command=self.upload_all).pack(side="left", padx=5)
        ttk.Button(ctrl, text="START", command=lambda: self.safe_write(16562, 1)).pack(side="left", padx=2)
        ttk.Button(ctrl, text="STOP", command=lambda: self.safe_write(16562, 4)).pack(side="left", padx=2)
        self.engine_label = ttk.Label(ctrl, text="Engine: --"); self.engine_label.pack(side="right", padx=10)

        panes = ttk.PanedWindow(self.root, orient="horizontal")
        panes.pack(fill="both", expand=True, padx=10)
        self.s_fr = ttk.LabelFrame(panes, text="Step Editor", padding=5); panes.add(self.s_fr, weight=1)
        self.steps_cont = ttk.Frame(self.s_fr); self.steps_cont.pack(fill="both")
        ttk.Button(self.s_fr, text="+ Add Step", command=self.add_step).pack(fill="x", pady=5)
        
        self.c_fr = ttk.LabelFrame(panes, text="Visualization"); panes.add(self.c_fr, weight=2)
        self.fig, self.ax = plt.subplots(figsize=(4, 3))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.c_fr); self.canvas.get_tk_widget().pack(fill="both", expand=True)
        
        self.log_box = tk.Text(self.root, height=6, bg="#f0f0f0", font=('Consolas', 9)); self.log_box.pack(fill="x", padx=10, pady=5)

    def add_step(self):
        self.profiles[self.current_profile_name].append({'type': 'Soak', 'value': 25.0, 'mins': 10})
        self.refresh_ui()

    def refresh_ui(self):
        for w in self.steps_cont.winfo_children(): w.destroy()
        for i, s in enumerate(self.profiles[self.current_profile_name]):
            row = ttk.Frame(self.steps_cont); row.pack(fill="x", pady=1)
            cb = ttk.Combobox(row, values=list(self.type_map.keys()), width=10); cb.set(s['type']); cb.pack(side="left")
            cb.bind("<<ComboboxSelected>>", lambda e, idx=i, v=cb: self.upd(idx, 'type', v.get()))
            v_e = ttk.Entry(row, width=7); v_e.insert(0, s['value']); v_e.pack(side="left", padx=2)
            v_e.bind("<FocusOut>", lambda e, idx=i, v=v_e: self.upd(idx, 'value', v.get()))
            t_e = ttk.Entry(row, width=7); t_e.insert(0, s['mins']); t_e.pack(side="left")
            t_e.bind("<FocusOut>", lambda e, idx=i, v=t_e: self.upd(idx, 'mins', v.get()))
        self.update_chart()

    def upd(self, idx, k, v):
        try: self.profiles[self.current_profile_name][idx][k] = float(v) if k != 'type' else v; self.update_chart()
        except: pass

    def update_chart(self):
        self.ax.clear(); steps = self.profiles[self.current_profile_name]
        if steps:
            t_p, v_p, cur_t = [0], [steps[0]['value']], 0
            for s in steps: cur_t += s['mins']; t_p.append(cur_t); v_p.append(s['value'])
            self.ax.plot(t_p, v_p, 'r-o')
        self.ax.grid(True); self.canvas.draw()

    def poll_loop(self):
        if not self.root.winfo_exists(): return
        if self.client and self.client.connected:
            try:
                # 1. Read PV (Temp) from Analog Input 1 (27542)
                pv_res = self.safe_read(27542, 2)
                if pv_res and hasattr(pv_res, 'registers'):
                    raw = struct.pack('>HH', pv_res.registers[1], pv_res.registers[0])
                    self.pv_label.config(text=f"Temp: {struct.unpack('>f', raw)[0]:.1f}°F")
                # 2. Read Engine State (16560)
                res = self.safe_read(16560, 1)
                if res and hasattr(res, 'registers'):
                    s_map = {0: "Idle", 1: "Running", 2: "Paused", 4: "Completed"}
                    self.engine_label.config(text=f"Engine: {s_map.get(res.registers[0], '??')}")
            except: pass
        self.root.after(1000, self.poll_loop)
    
    def on_closing(self):
        # 1. Stop the scheduled after loop
        if hasattr(self, 'poll_job'):
            self.root.after_cancel(self.poll_job)
    
        # 2. Close the Modbus connection
        if self.client:
            self.client.close()
        
        # 3. Destroy the window
        self.root.quit()  # Stop the mainloop
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk(); F4TApp(root); root.mainloop()
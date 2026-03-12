import tkinter as tk
from tkinter import ttk, messagebox
import struct
import time
from pymodbus.client import ModbusTcpClient

class F4TApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Watlow F4T Master - Loop 1 (Temperature)")
        
        self.type_map = {
            87: "Soak", 1928: "Ramp Time", 81: "Ramp Rate", 
            1542: "Wait For", 1927: "Instant Change", 116: "Jump", 27: "End"
        }
        self.name_to_code = {v: k for k, v in self.type_map.items()}
        
        self.poll_job = None
        self.setup_ui()
        
        self.client = ModbusTcpClient("10.4.11.144", port=502, timeout=2)
        if self.client.connect():
            self.status_label.config(text="Status: Connected", foreground="green")
            self.root.after(500, self.initial_load)
        else:
            self.status_label.config(text="Status: OFFLINE", foreground="red")
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.poll_loop()

    def setup_ui(self):
        top = ttk.Frame(self.root, padding=10); top.pack(fill="x")
        ttk.Label(top, text="Profile Name:").pack(side="left")
        self.name_var = tk.StringVar(value="...")
        ttk.Entry(top, textvariable=self.name_var, width=20).pack(side="left", padx=5)
        ttk.Button(top, text="Read", width=6, command=self.read_profile_name).pack(side="left", padx=2)
        ttk.Button(top, text="Write", width=6, command=self.write_profile_name_only).pack(side="left", padx=2)
        
        self.pv_label = ttk.Label(top, text="PV1: --.-", font=('Arial', 10, 'bold'), foreground="blue")
        self.pv_label.pack(side="right", padx=10)
        self.status_label = ttk.Label(top, text="Connecting..."); self.status_label.pack(side="right")
        
        table_frame = tk.Frame(self.root); table_frame.pack(pady=10, fill="both", expand=True, padx=10)
        self.cols = ("Step", "Type", "Target", "Duration", "RampRate")
        self.tree = ttk.Treeview(table_frame, columns=self.cols, show="headings", height=12)
        
        self.tree.heading("Step", text="Step #")
        self.tree.heading("Type", text="Type")
        self.tree.heading("Target", text="Setpoint")
        self.tree.heading("Duration", text="Time (H:M:S)")
        self.tree.heading("RampRate", text="Rate / End Action")
        
        for col in self.cols: self.tree.column(col, width=110, anchor="center")
        self.tree.pack(side="left", fill="both", expand=True)

        self.tree.bind("<Button-1>", self.on_table_click)
        self.log_box = tk.Text(self.root, height=5, bg="#f0f0f0", font=('Consolas', 9))
        self.log_box.pack(fill="x", padx=10, pady=5)

    def on_table_click(self, event):
        """Universal cell editor launcher"""
        if hasattr(self, 'active_editor') and self.active_editor.winfo_exists():
            self.active_editor.destroy()

        region = self.tree.identify_region(event.x, event.y)
        if region != "cell": return
        
        column = self.tree.identify_column(event.x)
        item_id = self.tree.identify_row(event.y)
        col_idx = int(column[1:]) - 1  # Convert #1, #2 to 0, 1...
        
        if col_idx == 0: return # Step # is read-only
        
        x, y, width, height = self.tree.bbox(item_id, column)
        current_val = self.tree.item(item_id, "values")[col_idx]

        step_type = self.tree.item(item_id, "values")[1]

        if col_idx == 1: # Type Column -> Combobox
            self.active_editor = ttk.Combobox(self.tree, values=list(self.name_to_code.keys()), state="readonly")
            self.active_editor.bind("<<ComboboxSelected>>", lambda e: self.finish_edit(item_id, col_idx))
        elif col_idx == 4 and step_type == "End": # End Action -> Combobox
            self.active_editor = ttk.Combobox(self.tree, values=["User", "Off", "Hold"], state="readonly")
            self.active_editor.set(current_val if current_val in ("User", "Off", "Hold") else "User")
            self.active_editor.bind("<<ComboboxSelected>>", lambda e: self.finish_edit(item_id, col_idx))
        else: # Other Columns -> Entry
            self.active_editor = ttk.Entry(self.tree)
            self.active_editor.insert(0, "" if current_val == "--" else current_val)
            self.active_editor.bind("<Return>", lambda e: self.finish_edit(item_id, col_idx))

        self.active_editor.place(x=x, y=y, width=width, height=height)
        self.active_editor.focus_set()
        self.editor_init_time = time.time()
        self.active_editor.bind("<FocusOut>", self.on_focus_out)

    def on_focus_out(self, event):
        if time.time() - self.editor_init_time > 0.4:
            if hasattr(self, 'active_editor'): self.active_editor.destroy()

    def finish_edit(self, item_id, col_idx):
        try:
            val = self.active_editor.get()
            step_num = int(self.tree.item(item_id, "values")[0])
            self.safe_write(18924, step_num) # Select Step
            
            if col_idx == 1: # TYPE
                self.safe_write(18926, self.name_to_code[val])
            
            elif col_idx == 2: # SETPOINT (Float)
                self.write_f4t_float(18946, float(val))
            
            elif col_idx == 3: # DURATION (H:M:S)
                h, m, s = map(int, val.split(':'))
                self.safe_write(18928, h); self.safe_write(18930, m); self.safe_write(18932, s)
            
            elif col_idx == 4: # RAMP RATE or END ACTION
                step_type = self.tree.item(item_id, "values")[1]
                if step_type == "End":
                    end_action_map = {"User": 100, "Off": 62, "Hold": 47}
                    self.safe_write(19030, end_action_map.get(val, 100))
                else:
                    self.write_f4t_float(18938, float(val))

            self.log(f"Step {step_num} updated.")
            if hasattr(self, 'active_editor'): self.active_editor.destroy()
            self.root.after(400, self.fetch_profile_table)
        except Exception as e:
            messagebox.showerror("Input Error", f"Invalid format: {e}")

    def write_f4t_float(self, reg, value):
        packed = struct.pack('>f', value)
        regs = struct.unpack('>HH', packed)
        # F4T Word Swap: Low word, then High word
        self.client.write_registers(reg, [regs[1], regs[0]])

    def safe_read(self, reg, count):
        try: return self.client.read_holding_registers(reg, count=count)
        except: return None

    def safe_write(self, reg, val):
        try: return self.client.write_register(reg, value=val)
        except: return None

    def decode_f4t_float(self, regs):
        if len(regs) < 2: return 0.0
        raw = struct.pack('>HH', regs[1], regs[0])
        return struct.unpack('>f', raw)[0]

    def read_profile_name(self):
        res = self.safe_read(16886, 20)
        if res and hasattr(res, 'registers'):
            chars = [chr(r) for r in res.registers if 32 <= r <= 126]
            self.name_var.set("".join(chars).strip())

    def write_profile_name_only(self):
        name_str = self.name_var.get()
        self.safe_write(18888, 1) 
        time.sleep(0.1)
        registers = [ord(c) for c in name_str[:20]]
        while len(registers) < 20: registers.append(32)
        self.client.write_registers(16886, values=registers)
        self.log(f"Name saved: {name_str}")

    def fetch_profile_table(self):
        res = self.safe_read(18920, 1)
        if not res or res.isError(): return
        total_steps = res.registers[0]
        for item in self.tree.get_children(): self.tree.delete(item)
        for i in range(total_steps):
            step_num = i + 1
            self.safe_write(18924, step_num)
            time.sleep(0.04) 
            data = self.safe_read(18926, 22)
            if data and not data.isError():
                r = data.registers
                t_val, t_name = r[0], self.type_map.get(r[0], f"Code {r[0]}")
                duration = f"{r[2]:02}:{r[4]:02}:{r[6]:02}"
                rate, target = self.decode_f4t_float(r[12:14]), self.decode_f4t_float(r[20:22])
                d_rate = f"{rate:.1f}" if t_val == 81 else "--"
                d_target = f"{target:.1f}" if t_val in [87, 1928, 81, 1927] else "--"
                d_dur = duration if t_val in [87, 1928, 81] else "--"
                if t_val == 27:  # End step - read End Step Loop Action 1 (reg 19030)
                    end_action_map = {100: "User", 62: "Off", 47: "Hold"}
                    ea_res = self.safe_read(19030, 1)
                    d_rate = end_action_map.get(ea_res.registers[0], "User") if ea_res and not ea_res.isError() else "User"
                self.tree.insert("", "end", values=(step_num, t_name, d_target, d_dur, d_rate))

    def log(self, msg):
        self.log_box.insert("end", f"[{time.strftime('%H:%M:%S')}] {msg}\n"); self.log_box.see("end")

    def poll_loop(self):
        if not self.root.winfo_exists(): return
        if self.client and self.client.connected:
            pv_res = self.safe_read(2820, 2)  # Loop 1 PV - CLP2 instance 1, member 66
            if pv_res and hasattr(pv_res, 'registers'):
                self.pv_label.config(text=f"PV1: {self.decode_f4t_float(pv_res.registers):.1f}")
        self.poll_job = self.root.after(1000, self.poll_loop)

    def on_closing(self):
        if self.poll_job: self.root.after_cancel(self.poll_job)
        if self.client: self.client.close()
        self.root.destroy()

    def initial_load(self):
        self.read_profile_name()
        self.fetch_profile_table()

if __name__ == "__main__":
    root = tk.Tk(); app = F4TApp(root); root.mainloop()
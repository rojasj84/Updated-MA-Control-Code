import tkinter as tk
from tkinter import ttk, messagebox
import time
from pymodbus.client import ModbusTcpClient

class F4TDebugTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Watlow F4T Debugger - Pymodbus 3.5+ Final Fix")
        self.root.geometry("500x600")
        
        self.client = None
        self.setup_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.exit_app)

    def setup_ui(self):
        # --- Connection Area ---
        conn_frame = ttk.LabelFrame(self.root, text="1. Connection", padding=10)
        conn_frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(conn_frame, text="IP Address:").grid(row=0, column=0, sticky="w")
        self.ip_var = tk.StringVar(value="10.4.11.144")
        ttk.Entry(conn_frame, textvariable=self.ip_var, width=15).grid(row=0, column=1, padx=5)

        ttk.Label(conn_frame, text="Unit ID (Slave):").grid(row=1, column=0, sticky="w")
        self.unit_var = tk.IntVar(value=1)
        ttk.Entry(conn_frame, textvariable=self.unit_var, width=5).grid(row=1, column=1, padx=5, sticky="w")

        self.conn_btn = ttk.Button(conn_frame, text="Connect", command=self.toggle_connection)
        self.conn_btn.grid(row=0, column=2, rowspan=2, padx=5)

        self.status_label = ttk.Label(conn_frame, text="Status: DISCONNECTED", foreground="red", font=("Arial", 9, "bold"))
        self.status_label.grid(row=2, column=0, columnspan=3, pady=5)

        # --- Register Area ---
        reg_frame = ttk.LabelFrame(self.root, text="2. Register Control", padding=10)
        reg_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(reg_frame, text="Register Address:").grid(row=0, column=0, sticky="w")
        self.reg_var = tk.StringVar()
        ttk.Entry(reg_frame, textvariable=self.reg_var, width=15).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(reg_frame, text="Data/Value:").grid(row=1, column=0, sticky="w")
        self.data_var = tk.StringVar()
        ttk.Entry(reg_frame, textvariable=self.data_var, width=15).grid(row=1, column=1, padx=5, pady=5)

        btn_box = ttk.Frame(reg_frame)
        btn_box.grid(row=2, column=0, columnspan=2, pady=10)
        ttk.Button(btn_box, text="Read", command=self.read_reg).pack(side="left", padx=5)
        ttk.Button(btn_box, text="Write", command=self.write_reg).pack(side="left", padx=5)

        self.log_box = tk.Text(self.root, height=12, bg="black", fg="lime", font=("Consolas", 10))
        self.log_box.pack(fill="both", expand=True, padx=10, pady=5)

        ttk.Button(self.root, text="Exit Application", command=self.exit_app).pack(pady=10)

    def log(self, message):
        t = time.strftime("%H:%M:%S")
        self.log_box.insert(tk.END, f"[{t}] {message}\n")
        self.log_box.see(tk.END)

    def toggle_connection(self):
        if self.client and self.client.connected:
            self.client.close()
            self.status_label.config(text="Status: DISCONNECTED", foreground="red")
            self.conn_btn.config(text="Connect")
            self.log("Disconnected.")
        else:
            ip = self.ip_var.get()
            self.client = ModbusTcpClient(ip, port=502)
            if self.client.connect():
                self.status_label.config(text="Status: CONNECTED", foreground="green")
                self.conn_btn.config(text="Disconnect")
                self.log(f"Connected to {ip}")
            else:
                self.log("Connection Failed.")

    def read_reg(self):
        if not self.client or not self.client.connected: return
        try:
            addr = int(self.reg_var.get())
            # MODBUS 3.5+ STRICT SYNTAX:
            # We use ONLY keywords for everything after the address to avoid positional count errors.
            # If 'slave' is rejected, we fall back to the internal default.
            res = self.client.read_holding_registers(address=addr, count=1, slave=self.unit_var.get())
            
            if res.isError():
                self.log(f"Modbus Error: {res}")
            else:
                val = res.registers[0]
                self.data_var.set(val)
                self.log(f"READ: Reg {addr} = {val}")
        except TypeError:
            # Fallback for versions that moved the slave parameter
            res = self.client.read_holding_registers(address=addr, count=1)
            self.data_var.set(res.registers[0])
            self.log(f"READ (Default Slave): {addr} = {res.registers[0]}")
        except Exception as e:
            self.log(f"Error: {e}")

    def write_reg(self):
        if not self.client or not self.client.connected: return
        try:
            addr = int(self.reg_var.get())
            val = int(self.data_var.get())
            # FIX: Explicit keywords for Pymodbus 3.5+
            res = self.client.write_register(address=addr, value=val, slave=self.unit_var.get())
            
            if res.isError():
                self.log(f"Write Error: {res}")
            else:
                self.log(f"WRITE SUCCESS: Reg {addr} set to {val}")
        except TypeError:
            res = self.client.write_register(address=addr, value=val)
            self.log(f"WRITE (Default Slave): {addr} set to {val}")
        except Exception as e:
            self.log(f"Error: {e}")

    def exit_app(self):
        if self.client: self.client.close()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = F4TDebugTool(root)
    root.mainloop()
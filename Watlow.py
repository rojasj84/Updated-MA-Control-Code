import sys
import struct
import random
import tkinter as tk
from tkinter import messagebox

try:
    from pymodbus.client import ModbusTcpClient
    PYMODBUS_V3 = True
except ImportError:
    try:
        from pymodbus.client.sync import ModbusTcpClient  # type: ignore
        PYMODBUS_V3 = False
    except ImportError as e:
        print(f"CRITICAL: Failed to import pymodbus.\nError: {e}")
        sys.exit(1)

# --- CONFIGURATION ---
BYPASS_MODBUS = False # This will be superseded by an instance variable
DEFAULT_IP = '192.168.0.222'
DEFAULT_PORT = 502
DEFAULT_SLAVE_ID = 1

# --- REGISTER MAP ---
REG_DEV_NAME = 46
REG_TEMP_PV = 27592
REG_TEMP_SP = 2782
REG_TEMP_MANUAL_POWER = 2784
REG_TEMP_MODE = 2730
REG_TEMP_SP_MIN = 2774
REG_TEMP_SP_MAX = 2776
REG_PRESSURE_PV = 11612
REG_PRESSURE_SP = 2942
REG_PRESSURE_MANUAL_POWER = 2944
REG_PRESSURE_MODE = 2890
REG_PRESSURE_SP_MIN = 3094
REG_PRESSURE_SP_MAX = 3096
REG_VOLTS = 28906
REG_AMPS = 29346

class WatlowF4T:
    def __init__(self, ip=DEFAULT_IP, port=DEFAULT_PORT, slave_id=DEFAULT_SLAVE_ID):
        self.ip = ip
        self.port = port
        self.slave_id = slave_id
        self.client = None
        self.simulated = BYPASS_MODBUS
        if not self.simulated:
            self.client = ModbusTcpClient(self.ip, port=self.port)

    def enable_simulation(self, enable=True):
        """Enables or disables simulation mode, bypassing actual modbus calls."""
        self.simulated = enable
        if self.client:
            self.client.close()
        self.client = None

    def set_ip(self, ip):
        """Updates the IP address and re-creates the client instance."""
        self.ip = ip
        if not self.simulated:
            if self.client:
                self.client.close()
            self.client = ModbusTcpClient(self.ip, port=self.port)

    def connect(self):
        if self.simulated:
            return True
        if self.client:
            return self.client.connect()
        return False

    def run_modbus_cmd(self, method_name, address, *args, **kwargs):
        if not self.client:
            return None
        method = getattr(self.client, method_name)
        try:
            return method(address, *args, slave=self.slave_id, **kwargs)
        except TypeError:
            pass
        try:
            return method(address, *args, unit=self.slave_id, **kwargs)
        except TypeError:
            pass
        try:
            return method(address, *args, **kwargs)
        except Exception as e:
            print(f"Modbus command failed: {e}")
            return None

    def read_string(self, address, length=10):
        if self.simulated:
            return "Simulated Watlow F4T"
        if not self.connect():
            return "Offline"
        try:
            result = self.run_modbus_cmd('read_holding_registers', address, count=length)
            if result is None or result.isError():
                return "Read Error"
            string_bytes = b''.join(struct.pack('>H', r) for r in result.registers)
            return string_bytes.decode('ascii', errors='ignore').rstrip('\x00').strip()
        except Exception:
            return "Error"

    def read_float(self, address):
        if self.simulated:
            return round(random.uniform(20.0, 25.0), 2)
        if not self.connect():
            return None
        result = self.run_modbus_cmd('read_holding_registers', address, count=2)
        if result is None or result.isError():
            return None
        low_word = result.registers[0]
        high_word = result.registers[1]
        raw_bytes = struct.pack('>HH', high_word, low_word)
        return round(struct.unpack('>f', raw_bytes)[0], 2)

    def write_float(self, address, value):
        if self.simulated:
            return True
        if not self.connect():
            return False
        try:
            raw_bytes = struct.pack('>f', value)
            high_word, low_word = struct.unpack('>HH', raw_bytes)
            payload = [low_word, high_word]
            result = self.run_modbus_cmd('write_registers', address, payload)
            if result is None:
                return "No response from device"
            if result.isError():
                return result
            return True
        except Exception as e:
            print(f"Write exception: {e}")
            return e

    def read_uint16(self, address):
        if self.simulated:
            return 62
        if not self.connect():
            return None
        result = self.run_modbus_cmd('read_holding_registers', address, count=1)
        if result is None or result.isError():
            return None
        return result.registers[0]

    def write_uint16(self, address, value):
        if self.simulated:
            return True
        if not self.connect():
            return False
        try:
            result = self.run_modbus_cmd('write_register', address, int(value))
            if result is None:
                return "No response from device"
            if result.isError():
                return result
            return True
        except Exception as e:
            print(f"Write exception: {e}")
            return e

    def get_sp_limits(self, min_addr, max_addr):
        if min_addr is None or max_addr is None:
            return None, None
        min_val = self.read_float(min_addr)
        max_val = self.read_float(max_addr)
        return min_val, max_val

class WatlowF4TGui:
    def __init__(self, root, device):
        self.root = root
        self.device = device
        self.root.title("Watlow F4T Basic Control")
        self.temp_mode_val = None
        self.pressure_mode_val = None
        self.is_polling = False

        # --- Connection UI ---
        conn_frame = tk.Frame(root)
        conn_frame.grid(row=0, column=0, columnspan=3, pady=(5, 10), sticky="ew")
        tk.Label(conn_frame, text="Controller IP:").pack(side=tk.LEFT, padx=(10, 5))
        self.ip_var = tk.StringVar(value=DEFAULT_IP)
        ip_entry = tk.Entry(conn_frame, textvariable=self.ip_var, width=15)
        ip_entry.pack(side=tk.LEFT, padx=5)
        connect_btn = tk.Button(conn_frame, text="Connect", command=self.connect_to_controller)
        connect_btn.pack(side=tk.LEFT, padx=5)
        
        tk.Label(root, text="Device Info:", font=("Arial", 10, "bold")).grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.info_label = tk.Label(root, text="Not Connected", font=("Arial", 10))
        self.info_label.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        tk.Label(root, text="Temperature PV:", font=("Arial", 12)).grid(row=2, column=0, padx=10, pady=5)
        self.pv_label = tk.Label(root, text="---", font=("Arial", 12, "bold"))
        self.pv_label.grid(row=2, column=1, padx=10, pady=5)

        tk.Label(root, text="Temperature SP:", font=("Arial", 12)).grid(row=3, column=0, padx=10, pady=5)
        self.sp_entry = tk.Entry(root)
        self.sp_entry.grid(row=3, column=1, padx=10, pady=5)

        self.sp_fb_label = tk.Label(root, text="(Current: ---)", font=("Arial", 10))
        self.sp_fb_label.grid(row=3, column=2, padx=5, pady=5)

        self.update_btn = tk.Button(root, text="Update Temp SP", command=self.write_setpoint)
        self.update_btn.grid(row=4, column=0, columnspan=2, pady=5)

        self.default_btn_bg = self.update_btn.cget("bg")
        self.temp_toggle_btn = tk.Button(root, text="Loading...", width=10, command=lambda: self.toggle_mode(REG_TEMP_MODE, self.temp_mode_val, "Temperature"))
        self.temp_toggle_btn.grid(row=4, column=2, padx=5, pady=5)

        tk.Label(root, text="Pressure PV:", font=("Arial", 12)).grid(row=5, column=0, padx=10, pady=5)
        self.pressure_pv_label = tk.Label(root, text="---", font=("Arial", 12, "bold"))
        self.pressure_pv_label.grid(row=5, column=1, padx=10, pady=5)

        tk.Label(root, text="Pressure SP:", font=("Arial", 12)).grid(row=6, column=0, padx=10, pady=5)
        self.pressure_sp_entry = tk.Entry(root)
        self.pressure_sp_entry.grid(row=6, column=1, padx=10, pady=5)

        self.pressure_sp_fb_label = tk.Label(root, text="(Current: ---)", font=("Arial", 10))
        self.pressure_sp_fb_label.grid(row=6, column=2, padx=5, pady=5)

        self.update_pressure_btn = tk.Button(root, text="Update Pressure SP", command=self.write_pressure_setpoint)
        self.update_pressure_btn.grid(row=7, column=0, columnspan=2, pady=5)

        self.pressure_toggle_btn = tk.Button(root, text="Loading...", width=10, command=lambda: self.toggle_mode(REG_PRESSURE_MODE, self.pressure_mode_val, "Pressure"))
        self.pressure_toggle_btn.grid(row=7, column=2, padx=5, pady=5)

        tk.Label(root, text="Volts:", font=("Arial", 12)).grid(row=8, column=0, padx=10, pady=5)
        self.volts_label = tk.Label(root, text="---", font=("Arial", 12, "bold"))
        self.volts_label.grid(row=8, column=1, padx=10, pady=5)

        tk.Label(root, text="Amps:", font=("Arial", 12)).grid(row=9, column=0, padx=10, pady=5)
        self.amps_label = tk.Label(root, text="---", font=("Arial", 12, "bold"))
        self.amps_label.grid(row=9, column=1, padx=10, pady=5)

    def connect_to_controller(self):
        """Establishes a connection with the controller using the provided IP."""
        ip = self.ip_var.get()
        if not ip:
            messagebox.showerror("Error", "IP Address cannot be empty.")
            return

        self.device.set_ip(ip)

        if self.device.connect():
            messagebox.showinfo("Success", f"Successfully connected to {ip}")
            self.update_device_info()
            if not self.is_polling:
                self.is_polling = True
                self.update_pv()
        else:
            messagebox.showerror("Connection Failed", f"Could not connect to {ip}.\nCheck IP and network connection.")
            self.info_label.config(text="OFFLINE")

    def write_setpoint_safe(self, sp_addr, min_addr, max_addr, entry_widget, name):
        try:
            val = float(entry_widget.get())
            if self.device.simulated:
                messagebox.showinfo("Success (Bypass)", f"{name} set point updated to {val}")
                return
            min_val, max_val = self.device.get_sp_limits(min_addr, max_addr)
            if min_val is not None and max_val is not None and min_val < max_val:
                if not (min_val <= val <= max_val):
                    messagebox.showerror("Range Error", f"Value {val} is out of range.\nAllowed: {min_val} to {max_val}")
                    return
            result = self.device.write_float(sp_addr, val)
            if result is not True:
                messagebox.showerror("Write Error", f"Failed to write {name}.\nError: {result}")
            else:
                messagebox.showinfo("Success", f"{name} set point changed to {val}")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number")

    def write_setpoint(self):
        if self.temp_mode_val == 54:
            self.write_setpoint_safe(REG_TEMP_MANUAL_POWER, None, None, self.sp_entry, "Temperature Manual Power")
        else:
            self.write_setpoint_safe(REG_TEMP_SP, REG_TEMP_SP_MIN, REG_TEMP_SP_MAX, self.sp_entry, "Temperature Set Point")

    def write_pressure_setpoint(self):
        if self.pressure_mode_val == 54:
            self.write_setpoint_safe(REG_PRESSURE_MANUAL_POWER, None, None, self.pressure_sp_entry, "Pressure Manual Power")
        else:
            self.write_setpoint_safe(REG_PRESSURE_SP, REG_PRESSURE_SP_MIN, REG_PRESSURE_SP_MAX, self.pressure_sp_entry, "Pressure Set Point")

    def toggle_mode(self, address, current_val, name):
        if current_val is None: return
        c_val = int(current_val)
        new_val = 10
        if c_val == 62: new_val = 10
        elif c_val == 10: new_val = 54
        elif c_val == 54: new_val = 62
        
        result = self.device.write_uint16(address, new_val)
        if result is True:
            self.update_pv()
        else:
            messagebox.showerror("Error", f"Failed to set {name} mode.\nError: {result}")

    def update_toggle_button(self, btn, mode_val):
        if mode_val == 10: btn.config(text="ON (Auto)", bg="red", fg="white")
        elif mode_val == 54: btn.config(text="ON (Man)", bg="red", fg="white")
        else: btn.config(text="OFF", bg=self.default_btn_bg, fg="black")

    def update_device_info(self):
        info = self.device.read_string(REG_DEV_NAME, 20)
        self.info_label.config(text=info)

    def update_pv(self):
        temp = self.device.read_float(REG_TEMP_PV)
        if temp is not None:
            mode_val = self.device.read_uint16(REG_TEMP_MODE)
            mode_str = self.decode_mode(mode_val)
            self.temp_mode_val = mode_val
            self.update_toggle_button(self.temp_toggle_btn, mode_val)
            self.pv_label.config(text=f"{temp} °C ({mode_str})")
        else:
            self.pv_label.config(text="OFFLINE")

        if self.temp_mode_val == 54:
            temp_pwr = self.device.read_float(REG_TEMP_MANUAL_POWER)
            if temp_pwr is not None: self.sp_fb_label.config(text=f"(Power: {temp_pwr}%)")
        else:
            temp_sp = self.device.read_float(REG_TEMP_SP)
            if temp_sp is not None: self.sp_fb_label.config(text=f"(Current: {temp_sp})")

        pressure = self.device.read_float(REG_PRESSURE_PV)
        p_min = self.device.read_float(REG_PRESSURE_SP_MIN)
        p_max = self.device.read_float(REG_PRESSURE_SP_MAX)
        p_config_err = (p_min == 0.0 and p_max == 0.0)

        if pressure is not None:
            mode_val = self.device.read_uint16(REG_PRESSURE_MODE)
            mode_str = self.decode_mode(mode_val)
            self.pressure_mode_val = mode_val
            self.update_toggle_button(self.pressure_toggle_btn, mode_val)
            if p_config_err:
                self.pressure_pv_label.config(text=f"{pressure} bars (No Loop)", fg="red")
                self.update_pressure_btn.config(state="disabled")
            else:
                self.pressure_pv_label.config(text=f"{pressure} bars ({mode_str})", fg="black")
                self.update_pressure_btn.config(state="normal")
        else:
            self.pressure_pv_label.config(text="---")

        if p_config_err:
            self.pressure_sp_fb_label.config(text="(Check Config)", fg="red")
        else:
            if self.pressure_mode_val == 54:
                press_pwr = self.device.read_float(REG_PRESSURE_MANUAL_POWER)
                if press_pwr is not None: self.pressure_sp_fb_label.config(text=f"(Power: {press_pwr}%)", fg="black")
            else:
                pressure_sp = self.device.read_float(REG_PRESSURE_SP)
                if pressure_sp is not None: self.pressure_sp_fb_label.config(text=f"(Current: {pressure_sp})", fg="black")

        volts = self.device.read_float(REG_VOLTS)
        if volts is not None: self.volts_label.config(text=f"{volts} V")
        else: self.volts_label.config(text="---")

        amps = self.device.read_float(REG_AMPS)
        if amps is not None: self.amps_label.config(text=f"{amps} A")
        else: self.amps_label.config(text="---")

        self.root.after(2000, self.update_pv)

    def decode_mode(self, val):
        if val == 62: return "Off"
        if val == 10: return "Auto"
        if val == 54: return "Manual"
        if val is None: return "?"
        return str(val)

def main():
    root = tk.Tk()
    device = WatlowF4T()
    app = WatlowF4TGui(root, device)
    root.mainloop()

if __name__ == "__main__":
    main()
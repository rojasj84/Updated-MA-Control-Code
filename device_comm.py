import serial
import time

class DeviceManager:
    def __init__(self, port='/dev/ttyUSB0', baudrate=9600, timeout=0.5):
        """
        Initialize the DeviceManager for communicating with Texmate and Omega devices.
        
        Args:
            port (str): Serial port path (e.g., '/dev/ttyUSB0' or 'COM1').
            baudrate (int): Baud rate (default 9600).
            timeout (float): Read timeout in seconds.
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.ser = None
        
        # Map port numbers (1-5) to Device IDs (A-E)
        self.device_map = {
            1: 'A', # Texmate Port 1
            2: 'B', # Texmate Port 2
            3: 'C', # Texmate Port 3
            4: 'D', # Texmate Port 4
            5: 'E'  # Omega Port 5
        }
        self.simulated = False
        self.log_callback = None

    def set_log_callback(self, callback):
        """Sets a callback function to log transmitted data."""
        self.log_callback = callback

    def enable_simulation(self):
        """Enables simulation mode to run without hardware."""
        self.simulated = True

    def open(self):
        """Opens the serial connection."""
        try:
            self.ser = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=self.timeout
            )
            return True
        except serial.SerialException as e:
            print(f"Error opening serial port {self.port}: {e}")
            return False

    def close(self):
        """Closes the serial connection."""
        if self.ser and self.ser.is_open:
            self.ser.close()

    def _send_raw(self, data):
        """Sends raw bytes and reads response."""
        if self.log_callback:
            self.log_callback(f"TX: {data}")

        if self.simulated:
            # Return dummy response so GUI keeps running
            return "SIM_ACK"

        if not self.ser or not self.ser.is_open:
            return ""
        
        try:
            self.ser.reset_input_buffer()
            self.ser.write(data)
            time.sleep(0.1) # Wait for device processing
            
            response = self.ser.read_all()
            return response.decode('ascii', errors='ignore').strip()
        except Exception as e:
            print(f"Serial communication error: {e}")
            return ""

    def send_texmate_cmd(self, port_num, command="SR"):
        """
        Sends a command to a Texmate device (Ports 1-4).
        
        Args:
            port_num (int): 1 to 4.
            command (str): Command string (e.g., "SR22"). Default "SR".
            
        Returns:
            str: Device response.
        """
        if port_num not in range(1, 5):
            print(f"Invalid Texmate port: {port_num}")
            return ""
            
        addr = self.device_map[port_num]
        # Protocol: ESC + STX + Addr + Command + *
        # Example: \x1b\x02ASR22*
        full_cmd = f"\x1b\x02{addr}{command}*"
        return self._send_raw(full_cmd.encode('ascii'))

    def get_thermocouple_type(self):
        """
        Reads the current thermocouple configuration from Port 1.
        Returns: 'C', 'S', 'mV', or 'Unknown'
        """
        # Command from TempAP10.frm: SR170*
        resp = self.send_texmate_cmd(1, "SR170")
        
        # VB6 Logic: 253=C, 252=S, 251=mV
        if "253" in resp: return "C"
        if "252" in resp: return "S"
        if "251" in resp: return "mV"
        return "Unknown"

    def set_thermocouple_type(self, type_char):
        """
        Sets the thermocouple type on Port 1.
        Args: type_char (str): 'C', 'S', or 'mV'
        """
        cmd_map = {
            'C': "SW170 253",
            'S': "SW170 252",
            'mV': "SW170 251"
        }
        
        if type_char not in cmd_map:
            print(f"Invalid type: {type_char}")
            return False
            
        # Send write command
        return self.send_texmate_cmd(1, cmd_map[type_char])

    def zero_pressure_port2(self):
        """
        Reads current pressure on Port 2 and sets offset (Register 028) to zero it out.
        Returns: (bool success, str message)
        """
        # 1. Read current value
        resp = self.send_texmate_cmd(2, "SR")
        if not resp:
            return False, "No response from Pressure Meter (Port 2)"
            
        try:
            if self.simulated and resp == "SIM_ACK":
                current_val = 15 # Dummy value for simulation
            else:
                # Parse integer from response (e.g., "+00015" -> 15)
                current_val = int(resp)
        except ValueError:
            return False, f"Invalid pressure data received: {resp}"
            
        # 2. Calculate offset (negative of current reading)
        offset = -current_val
        
        # 3. Write to Register 028 (Tare/Offset)
        # Command: SW028 <value>
        cmd = f"SW028 {offset}"
        self.send_texmate_cmd(2, cmd)
        
        time.sleep(0.2)
        
        # 4. Verify
        new_resp = self.send_texmate_cmd(2, "SR")
        return True, f"Zeroed. Offset applied: {offset}. New Reading: {new_resp}"

    def send_omega_cmd(self, command):
        """
        Sends a command to the Omega device (Port 5).
        
        Args:
            command (str): Command string (e.g., "$1RD").
            
        Returns:
            str: Device response.
        """
        # Protocol: ESC + STX + 'E' + Command + CR
        # Example: \x1b\x02E$1RD\r
        full_cmd = f"\x1b\x02E{command}\r"
        return self._send_raw(full_cmd.encode('ascii'))

    def set_omega_voltage(self, voltage):
        """
        Sets the analog output voltage for the Omega device (Port 5).
        
        Args:
            voltage (float): Voltage between 0.0 and 10.0.
            
        Returns:
            str: Verification response (reading back the value).
        """
        voltage = max(0.0, min(10.0, voltage))
        mvolts = int(voltage * 1000)
        
        # Format: $1AO+05000.00
        # Matches VB6 logic: + followed by 5 digits of integer part, then .00
        volts_str = f"+{mvolts:05d}.00"
        cmd = f"$1AO{volts_str}"
        
        self.send_omega_cmd(cmd)
        time.sleep(0.1)
        return self.send_omega_cmd("$1RD")

    def initialize_omega(self):
        """
        Initializes the Omega device.
        Detects if it's at 9600 baud. If not, tries 300 baud and reconfigures it to 9600.
        
        Returns:
            tuple: (bool success, str message)
        """
        if not self.ser or not self.ser.is_open:
            return False, "Serial port not open"

        # 1. Try 9600 (current)
        resp = self.send_omega_cmd("$1RD")
        if resp:
            return True, "Omega detected at 9600 baud."

        # 2. Try 300
        print("Omega not responding. Switching to 300 baud...")
        self.ser.close()
        self.ser.baudrate = 300
        try:
            self.ser.open()
        except:
            self.ser.baudrate = 9600
            return False, "Could not open port at 300 baud."

        resp = self.send_omega_cmd("$1RD")
        if not resp:
            self.ser.close()
            self.ser.baudrate = 9600
            self.ser.open()
            return False, "Omega not detected at 300 baud."

        # 3. Reconfigure sequence
        print("Omega found at 300 baud. Reconfiguring to 9600...")
        cmds = [
            "$1RS",             # Read Setup
            "$1WE",             # Write Enable
            "$1SU31020180",     # Set Baud to 9600
            "$1RS",             # Read Setup
            "$1WE",             # Write Enable
            "$1RR"              # Remote Reset
        ]
        
        for cmd in cmds:
            self.send_omega_cmd(cmd)
            time.sleep(0.5)
            
        # 4. Switch back to 9600
        self.ser.close()
        self.ser.baudrate = 9600
        self.ser.open()
        time.sleep(1.0) # Wait for reset

        # 5. Verify
        resp = self.send_omega_cmd("$1RD")
        if resp:
            return True, "Omega successfully initialized to 9600 baud."
        else:
            return False, "Omega failed to respond at 9600 baud after reset."

    def scan_ports(self):
        """
        Scans all 5 ports to see which are active.
        
        Returns:
            dict: {port_num: bool_is_active}
        """
        status = {}
        # Scan Texmate (1-4)
        for i in range(1, 5):
            # Send a basic read command. VB6 uses "SR*"
            resp = self.send_texmate_cmd(i, "SR")
            status[i] = bool(resp)
            
        # Scan Omega (5)
        resp = self.send_omega_cmd("$1RD")
        status[5] = bool(resp)
        
        return status

if __name__ == "__main__":
    # Simple test routine
    mgr = DeviceManager()
    if mgr.open():
        print("Port opened.")
        print("Scanning ports...")
        print(mgr.scan_ports())
        mgr.close()
    else:
        print("Could not open port.")

class MotorValveController:
    def __init__(self, port='/dev/ttyUSB1', baudrate=9600, timeout=0.5):
        """
        Controller for the Motor and Valve hardware (PurgeAP10).
        Uses a separate serial port from the meters.
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.ser = None
        self.simulated = False
        self.log_callback = None

    def set_log_callback(self, callback):
        self.log_callback = callback

    def enable_simulation(self):
        self.simulated = True

    def open(self):
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
            return True
        except Exception as e:
            print(f"Error opening motor port {self.port}: {e}")
            return False

    def close(self):
        if self.ser and self.ser.is_open:
            self.ser.close()

    def send_command(self, cmd):
        """Sends a command string appended with CR (e.g., 'AA8' -> 'AA8\\r')."""
        full_cmd = f"{cmd}\r"
        
        if self.log_callback:
            self.log_callback(f"MV_TX: {full_cmd.strip()}")
            
        if self.simulated:
            return True

        if self.ser and self.ser.is_open:
            try:
                self.ser.write(full_cmd.encode('ascii'))
                return True
            except Exception as e:
                print(f"Motor Serial error: {e}")
        return False
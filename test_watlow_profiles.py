import argparse
import json
import sys
import tkinter as tk
from tkinter import messagebox, ttk

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from Watlow import DEFAULT_IP, REG_PRESSURE_PV, WatlowF4T

APCE_PROFILE_1_STEP_TYPE = 19094
APCE_PROFILE_STRIDE = 170
APCE_PROFILE_NUMBER_REGISTER = 18888
APCE_CURRENT_STEP_REGISTER = 18924
APCE_PROFILE_EDIT_ACTION_REGISTER = 18890
APCE_STEP_HOURS_OFFSET = 2
APCE_STEP_MINUTES_OFFSET = 4
APCE_STEP_SECONDS_OFFSET = 6
APCE_SETPOINT_1_OFFSET = 20
MAX_PROFILE_STEPS = 50

APCE_EDIT_ACTION_EDIT = 1770
APCE_STEP_EDIT_ACTION_OFFSET = 84

STEP_TYPE_NAMES = {
    27: "End",
    81: "Ramp Rate",
    87: "Soak",
    116: "Jump",
    1927: "Instant Change",
    1928: "Ramp Time",
    1542: "Wait",
}

STEP_TYPE_CODES = {
    "Ramp Time": 1928,
    "Soak": 87,
    "Ramp Rate": 81,
    "Instant Change": 1927,
    "End": 27,
}

EDITABLE_STEP_TYPES = tuple(STEP_TYPE_CODES.keys())
READABLE_STEP_TYPES = {27, 81, 87, 1927, 1928}
END_STEP_TYPES = {0, 27}


def parse_args():
    parser = argparse.ArgumentParser(
        description="Native APCE profile manager for a Watlow F4T."
    )
    parser.add_argument("--ip", default=DEFAULT_IP)
    parser.add_argument("--port", type=int, default=502)
    parser.add_argument("--slave-id", type=int, default=1)
    parser.add_argument(
        "--profile",
        type=int,
        default=1,
        help="Initial profile number to load in the GUI (default: 1).",
    )
    parser.add_argument(
        "--loop",
        "--instance",
        dest="loop",
        type=int,
        default=2,
        help="Control loop/setpoint index to read/write (default: 2 for pressure).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print the selected profile as JSON instead of opening the GUI.",
    )
    return parser.parse_args()


def target_offset_for_loop(loop_number):
    return APCE_SETPOINT_1_OFFSET + ((loop_number - 1) * 2)


def get_step_registers(profile_id, loop_number):
    base = APCE_PROFILE_1_STEP_TYPE + ((profile_id - 1) * APCE_PROFILE_STRIDE)
    return {
        "profile_number": APCE_PROFILE_NUMBER_REGISTER,
        "profile_edit_action": APCE_PROFILE_EDIT_ACTION_REGISTER,
        "current_step": APCE_CURRENT_STEP_REGISTER,
        "step_edit_action": base + APCE_STEP_EDIT_ACTION_OFFSET,
        "step_type": base,
        "hours": base + APCE_STEP_HOURS_OFFSET,
        "minutes": base + APCE_STEP_MINUTES_OFFSET,
        "seconds": base + APCE_STEP_SECONDS_OFFSET,
        "target": base + target_offset_for_loop(loop_number),
    }


def duration_to_parts(duration_minutes):
    total_seconds = max(0, int(round(duration_minutes * 60.0)))
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return hours, minutes, seconds


def normalize_steps_for_write(steps):
    normalized = []
    for index, step in enumerate(steps, start=1):
        step_type_name = step["step_type_name"]
        step_type = STEP_TYPE_CODES[step_type_name]
        normalized.append(
            {
                "step_number": index,
                "step_type": step_type,
                "step_type_name": step_type_name,
                "end": float(step.get("end", 0.0)),
                "duration": float(step.get("duration", 0.0)),
            }
        )

    if not normalized or normalized[-1]["step_type"] != 27:
        normalized.append(
            {
                "step_number": len(normalized) + 1,
                "step_type": 27,
                "step_type_name": "End",
                "end": normalized[-1]["end"] if normalized else 0.0,
                "duration": 0.0,
            }
        )

    return normalized


def read_profile_steps(controller, profile_id, loop_number, max_steps=MAX_PROFILE_STEPS):
    registers = get_step_registers(profile_id, loop_number)
    steps = []

    if controller.write_uint16(registers["profile_number"], profile_id) is not True:
        return None

    for step_number in range(1, max_steps + 1):
        if controller.write_uint16(registers["current_step"], step_number) is not True:
            return None if step_number == 1 else steps

        step_type = controller.read_uint16(registers["step_type"])
        hours = controller.read_uint16(registers["hours"])
        minutes = controller.read_uint16(registers["minutes"])
        seconds = controller.read_uint16(registers["seconds"])
        target = controller.read_float(registers["target"])
        if None in (step_type, hours, minutes, seconds) or target is None:
            return None if step_number == 1 else steps

        duration = float(hours * 60) + float(minutes) + (float(seconds) / 60.0)

        if step_type in END_STEP_TYPES:
            steps.append(
                {
                    "step_number": step_number,
                    "step_type": 27,
                    "step_type_name": "End",
                    "end": target,
                    "duration": 0.0,
                }
            )
            break

        if step_type not in READABLE_STEP_TYPES:
            continue

        if target == 0.0 and duration == 0.0 and step_type in (87, 1928, 1927, 81):
            break

        steps.append(
            {
                "step_number": step_number,
                "step_type": step_type,
                "step_type_name": STEP_TYPE_NAMES.get(step_type, f"Type {step_type}"),
                "end": target,
                "duration": duration,
            }
        )

    return steps


def write_profile_steps(controller, profile_id, loop_number, steps):
    registers = get_step_registers(profile_id, loop_number)
    normalized = normalize_steps_for_write(steps)

    if controller.write_uint16(registers["profile_number"], profile_id) is not True:
        return False
    if controller.write_uint16(registers["profile_edit_action"], APCE_EDIT_ACTION_EDIT) is not True:
        return False

    for step in normalized:
        hours, minutes, seconds = duration_to_parts(step["duration"])
        if controller.write_uint16(registers["current_step"], step["step_number"]) is not True:
            return False
        if controller.write_uint16(registers["step_edit_action"], APCE_EDIT_ACTION_EDIT) is not True:
            return False
        if controller.write_uint16(registers["step_type"], step["step_type"]) is not True:
            return False
        if controller.write_uint16(registers["hours"], hours) is not True:
            return False
        if controller.write_uint16(registers["minutes"], minutes) is not True:
            return False
        if controller.write_uint16(registers["seconds"], seconds) is not True:
            return False
        if step["step_type"] != 27:
            if controller.write_float(registers["target"], step["end"]) is not True:
                return False

    return True


def read_profile_payload(controller, profile_id, loop_number):
    steps = read_profile_steps(controller, profile_id, loop_number)
    return {
        "profile_id": profile_id,
        "loop": loop_number,
        "download_ok": steps is not None,
        "step_count": len(steps) if steps is not None else 0,
        "steps": steps or [],
    }


def build_profile_series(steps, initial_value):
    times = [0.0]
    values = [initial_value]
    annotations = []
    current_time = 0.0
    current_value = initial_value

    for step in steps:
        step_type = step["step_type"]
        end_value = step["end"]
        duration = step["duration"]
        label = f"{step['step_number']} {step['step_type_name']}"

        if step_type == 27:
            annotations.append((current_time, current_value, label))
            break

        start_time = current_time
        if step_type == 87:
            current_time += duration
            times.append(current_time)
            values.append(current_value)
        else:
            times.append(current_time)
            values.append(current_value)
            current_time += duration
            current_value = end_value
            times.append(current_time)
            values.append(current_value)

        annotations.append((((start_time + current_time) / 2.0), current_value, label))
        if step_type == 87:
            current_value = end_value

    return times[: len(values)], values, annotations


class ProfileManagerApp:
    def __init__(self, args):
        self.args = args
        self.controller = WatlowF4T(ip=args.ip, port=args.port, slave_id=args.slave_id)
        self.root = tk.Tk()
        self.root.title("Watlow F4T Profile Manager")
        self.root.geometry("1200x760")

        self.ip_var = tk.StringVar(value=args.ip)
        self.port_var = tk.StringVar(value=str(args.port))
        self.slave_var = tk.StringVar(value=str(args.slave_id))
        self.profile_var = tk.IntVar(value=args.profile)
        self.loop_var = tk.IntVar(value=args.loop)
        self.status_var = tk.StringVar(value="Disconnected")
        self.current_pressure = 0.0
        self.steps = []

        self.tree = None
        self.figure = None
        self.axis = None
        self.canvas = None
        self.step_type_var = tk.StringVar(value="Ramp Time")
        self.target_var = tk.StringVar(value="0.0")
        self.duration_var = tk.StringVar(value="0.0")

        self._build_ui()
        self.connect_controller()
        self.load_profile()
        self.root.protocol("WM_DELETE_WINDOW", self.close)

    def _build_ui(self):
        self.root.columnconfigure(0, weight=3)
        self.root.columnconfigure(1, weight=2)
        self.root.rowconfigure(1, weight=1)

        top = ttk.Frame(self.root, padding=10)
        top.grid(row=0, column=0, columnspan=2, sticky="ew")
        for column in range(10):
            top.columnconfigure(column, weight=1)

        ttk.Label(top, text="IP").grid(row=0, column=0, sticky="w")
        ttk.Entry(top, textvariable=self.ip_var, width=14).grid(row=1, column=0, padx=4, sticky="ew")
        ttk.Label(top, text="Port").grid(row=0, column=1, sticky="w")
        ttk.Entry(top, textvariable=self.port_var, width=8).grid(row=1, column=1, padx=4, sticky="ew")
        ttk.Label(top, text="Slave ID").grid(row=0, column=2, sticky="w")
        ttk.Entry(top, textvariable=self.slave_var, width=8).grid(row=1, column=2, padx=4, sticky="ew")
        ttk.Label(top, text="Profile").grid(row=0, column=3, sticky="w")
        ttk.Spinbox(top, from_=1, to=50, textvariable=self.profile_var, width=6).grid(row=1, column=3, padx=4, sticky="ew")
        ttk.Label(top, text="Loop").grid(row=0, column=4, sticky="w")
        ttk.Spinbox(top, from_=1, to=4, textvariable=self.loop_var, width=6).grid(row=1, column=4, padx=4, sticky="ew")
        ttk.Button(top, text="Connect", command=self.connect_controller).grid(row=1, column=5, padx=4, sticky="ew")
        ttk.Button(top, text="Load Profile", command=self.load_profile).grid(row=1, column=6, padx=4, sticky="ew")
        ttk.Button(top, text="New Profile", command=self.new_profile).grid(row=1, column=7, padx=4, sticky="ew")
        ttk.Button(top, text="Upload Profile", command=self.upload_profile).grid(row=1, column=8, padx=4, sticky="ew")
        ttk.Label(top, textvariable=self.status_var).grid(row=1, column=9, padx=4, sticky="e")

        left = ttk.Frame(self.root, padding=(10, 0, 10, 10))
        left.grid(row=1, column=0, sticky="nsew")
        left.rowconfigure(0, weight=3)
        left.rowconfigure(1, weight=2)
        left.columnconfigure(0, weight=1)

        list_frame = ttk.LabelFrame(left, text="Profile Steps", padding=8)
        list_frame.grid(row=0, column=0, sticky="nsew")
        list_frame.rowconfigure(0, weight=1)
        list_frame.columnconfigure(0, weight=1)

        columns = ("step", "type", "target", "duration")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=12)
        self.tree.heading("step", text="Step")
        self.tree.heading("type", text="Type")
        self.tree.heading("target", text="Target")
        self.tree.heading("duration", text="Duration (min)")
        self.tree.column("step", width=70, anchor="center")
        self.tree.column("type", width=140, anchor="w")
        self.tree.column("target", width=110, anchor="e")
        self.tree.column("duration", width=110, anchor="e")
        self.tree.grid(row=0, column=0, sticky="nsew")
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)

        editor = ttk.LabelFrame(left, text="Step Editor", padding=8)
        editor.grid(row=1, column=0, sticky="nsew", pady=(10, 0))
        for column in range(4):
            editor.columnconfigure(column, weight=1)

        ttk.Label(editor, text="Type").grid(row=0, column=0, sticky="w")
        type_combo = ttk.Combobox(editor, textvariable=self.step_type_var, values=EDITABLE_STEP_TYPES, state="readonly")
        type_combo.grid(row=1, column=0, columnspan=2, padx=4, pady=4, sticky="ew")

        ttk.Label(editor, text="Target").grid(row=0, column=2, sticky="w")
        ttk.Entry(editor, textvariable=self.target_var).grid(row=1, column=2, padx=4, pady=4, sticky="ew")

        ttk.Label(editor, text="Duration (min)").grid(row=0, column=3, sticky="w")
        ttk.Entry(editor, textvariable=self.duration_var).grid(row=1, column=3, padx=4, pady=4, sticky="ew")

        ttk.Button(editor, text="Apply To Selected", command=self.apply_selected_step).grid(
            row=2, column=0, columnspan=2, padx=4, pady=(8, 0), sticky="ew"
        )
        ttk.Button(editor, text="Add Step", command=self.add_step).grid(
            row=2, column=2, padx=4, pady=(8, 0), sticky="ew"
        )
        ttk.Button(editor, text="Delete Selected", command=self.delete_selected_step).grid(
            row=2, column=3, padx=4, pady=(8, 0), sticky="ew"
        )

        right = ttk.LabelFrame(self.root, text="Chart", padding=10)
        right.grid(row=1, column=1, sticky="nsew", padx=(0, 10), pady=(0, 10))
        right.rowconfigure(0, weight=1)
        right.columnconfigure(0, weight=1)

        self.figure, self.axis = plt.subplots(figsize=(5.5, 4.5))
        self.canvas = FigureCanvasTkAgg(self.figure, master=right)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")

    def connect_controller(self):
        try:
            port = int(self.port_var.get())
            slave_id = int(self.slave_var.get())
        except ValueError:
            messagebox.showerror("Invalid Settings", "Port and slave ID must be integers.", parent=self.root)
            return False

        if self.controller.client:
            self.controller.client.close()

        self.controller = WatlowF4T(ip=self.ip_var.get(), port=port, slave_id=slave_id)
        if not self.controller.connect():
            self.status_var.set("Disconnected")
            messagebox.showerror(
                "Connection Failed",
                f"Unable to connect to {self.ip_var.get()}:{port}.",
                parent=self.root,
            )
            return False

        self.status_var.set("Connected")
        return True

    def load_profile(self):
        if not self.connect_controller():
            return

        profile_id = self.profile_var.get()
        loop_number = self.loop_var.get()
        payload = read_profile_payload(self.controller, profile_id, loop_number)
        if not payload["download_ok"]:
            messagebox.showerror("Read Failed", f"Could not read Profile {profile_id}.", parent=self.root)
            return

        self.current_pressure = self.controller.read_float(REG_PRESSURE_PV) or 0.0
        self.steps = payload["steps"]
        self.status_var.set(
            f"Connected | Profile {profile_id} | {payload['step_count']} step(s) | PV {self.current_pressure:.2f}"
        )
        self.refresh_tree()
        self.refresh_chart()

    def new_profile(self):
        self.steps = [
            {"step_number": 1, "step_type": 1928, "step_type_name": "Ramp Time", "end": self.current_pressure, "duration": 10.0},
            {"step_number": 2, "step_type": 87, "step_type_name": "Soak", "end": self.current_pressure, "duration": 10.0},
            {"step_number": 3, "step_type": 27, "step_type_name": "End", "end": self.current_pressure, "duration": 0.0},
        ]
        self.refresh_tree()
        self.refresh_chart()

    def upload_profile(self):
        if not self.connect_controller():
            return

        if not self.steps:
            messagebox.showwarning("No Steps", "Create or load a profile first.", parent=self.root)
            return

        ok = write_profile_steps(self.controller, self.profile_var.get(), self.loop_var.get(), self.steps)
        if not ok:
            messagebox.showerror("Upload Failed", "Could not write the profile to the controller.", parent=self.root)
            return

        self.steps = normalize_steps_for_write(self.steps)
        self.load_profile()
        self.refresh_tree()
        self.refresh_chart()
        messagebox.showinfo("Uploaded", f"Profile {self.profile_var.get()} uploaded.", parent=self.root)

    def refresh_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        normalized = normalize_steps_for_write(self.steps) if self.steps else []
        self.steps = normalized
        for step in self.steps:
            self.tree.insert(
                "",
                "end",
                iid=str(step["step_number"]),
                values=(
                    step["step_number"],
                    step["step_type_name"],
                    f"{step['end']:.2f}",
                    f"{step['duration']:.2f}",
                ),
            )

        if self.steps:
            first = str(self.steps[0]["step_number"])
            self.tree.selection_set(first)
            self.on_tree_select()

    def refresh_chart(self):
        self.axis.clear()
        if self.steps:
            times, values, annotations = build_profile_series(self.steps, self.current_pressure)
            self.axis.plot(times, values, marker="o", linewidth=2, color="#1f5f8b")
            for x_pos, y_pos, label in annotations:
                self.axis.annotate(label, (x_pos, y_pos), textcoords="offset points", xytext=(0, 8), ha="center", fontsize=8)
        self.axis.set_title(f"Profile {self.profile_var.get()} Loop {self.loop_var.get()}")
        self.axis.set_xlabel("Time (minutes)")
        self.axis.set_ylabel("Pressure Target")
        self.axis.grid(True, alpha=0.3)
        self.figure.tight_layout()
        self.canvas.draw_idle()

    def get_selected_index(self):
        selection = self.tree.selection()
        if not selection:
            return None
        return int(selection[0]) - 1

    def on_tree_select(self, _event=None):
        index = self.get_selected_index()
        if index is None or index >= len(self.steps):
            return
        step = self.steps[index]
        self.step_type_var.set(step["step_type_name"])
        self.target_var.set(f"{step['end']:.2f}")
        self.duration_var.set(f"{step['duration']:.2f}")

    def apply_selected_step(self):
        index = self.get_selected_index()
        if index is None:
            messagebox.showwarning("No Selection", "Select a step first.", parent=self.root)
            return

        try:
            target = float(self.target_var.get())
            duration = float(self.duration_var.get())
        except ValueError:
            messagebox.showerror("Invalid Input", "Target and duration must be numeric.", parent=self.root)
            return

        step_type_name = self.step_type_var.get()
        self.steps[index]["step_type_name"] = step_type_name
        self.steps[index]["step_type"] = STEP_TYPE_CODES[step_type_name]
        self.steps[index]["end"] = target
        self.steps[index]["duration"] = 0.0 if step_type_name == "End" else max(0.0, duration)
        self.refresh_tree()
        self.tree.selection_set(str(index + 1))
        self.refresh_chart()

    def add_step(self):
        insertion_index = self.get_selected_index()
        if insertion_index is None:
            insertion_index = len([step for step in self.steps if step["step_type"] != 27])
        else:
            insertion_index += 1

        non_end_steps = [dict(step) for step in self.steps if step["step_type"] != 27]
        new_step = {
            "step_number": 0,
            "step_type": 1928,
            "step_type_name": "Ramp Time",
            "end": self.current_pressure,
            "duration": 10.0,
        }
        non_end_steps.insert(insertion_index, new_step)
        self.steps = non_end_steps
        self.refresh_tree()
        self.tree.selection_set(str(insertion_index + 1))
        self.refresh_chart()

    def delete_selected_step(self):
        index = self.get_selected_index()
        if index is None:
            return
        if self.steps[index]["step_type"] == 27:
            return

        self.steps.pop(index)
        self.refresh_tree()
        self.refresh_chart()

    def close(self):
        if self.controller.client:
            self.controller.client.close()
        self.root.destroy()

    def run(self):
        self.root.mainloop()


def run_json_mode(args):
    controller = WatlowF4T(ip=args.ip, port=args.port, slave_id=args.slave_id)
    if not controller.connect():
        print(f"Unable to connect to Watlow F4T at {args.ip}:{args.port}.", file=sys.stderr)
        return 1

    device_name = controller.read_string(46)
    payload = read_profile_payload(controller, args.profile, args.loop)
    if controller.client:
        controller.client.close()

    print(
        json.dumps(
            {
                "device_name": device_name,
                "ip": args.ip,
                "port": args.port,
                "slave_id": args.slave_id,
                "profile_id": args.profile,
                "loop": args.loop,
                "profile": payload,
            },
            indent=2,
        )
    )
    return 0


def main():
    args = parse_args()

    if args.profile < 1 or args.profile > 50:
        print("Profile must be between 1 and 50.", file=sys.stderr)
        return 2
    if args.loop < 1 or args.loop > 4:
        print("Loop must be between 1 and 4.", file=sys.stderr)
        return 2

    if args.json:
        return run_json_mode(args)

    app = ProfileManagerApp(args)
    app.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

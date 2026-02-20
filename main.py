import tkinter as tk
from tkinter import ttk

class BaseAPGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("EPL MAP Control")
        self.root.configure(bg="#F0F0F0")

        # Use a main frame for padding and layout
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.create_widgets()

    def create_widgets(self):
        # --- Title ---
        title_lbl = tk.Label(self.main_frame, text="Carnegie Institution Anvil Press V10-", font=("Arial", 14, "bold"), bg="#F0F0F0")
        title_lbl.pack(pady=(0, 10))

        # --- Top Section (Buttons + Graph + Rescale) ---
        top_frame = ttk.Frame(self.main_frame)
        top_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Left Buttons (Process Control)
        left_btn_frame = ttk.Frame(top_frame)
        left_btn_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        buttons = [
            ("Start Process", "#80FF80"),
            ("Stop Process", None),
            ("Purge", None),
            ("Zero Pressure", None),
            ("Error Display", None)
        ]
        
        for text, color in buttons:
            btn = tk.Button(left_btn_frame, text=text, command=self.on_click)
            if color:
                btn.configure(bg=color)
            btn.pack(fill=tk.X, pady=2)

        # Graph Area
        self.graph_canvas = tk.Canvas(top_frame, bg="white", height=400, width=600, highlightthickness=1, highlightbackground="black")
        self.graph_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.graph_canvas.bind("<Configure>", self.draw_grid)

        # Right Side (Rescale)
        right_panel = ttk.Frame(top_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        
        ttk.Label(right_panel, text="Rescale").pack(pady=(0,5))
        rescale_frame = ttk.Frame(right_panel)
        rescale_frame.pack()
        tk.Button(rescale_frame, text="T", bg="#8080FF", width=3, command=self.on_click).pack(side=tk.LEFT, padx=1)
        tk.Button(rescale_frame, text="P", bg="#00FF00", width=3, command=self.on_click).pack(side=tk.LEFT, padx=1)
        tk.Button(rescale_frame, text="W", bg="#8080FF", width=3, command=self.on_click).pack(side=tk.LEFT, padx=1)

        # --- Middle Section (Readouts) ---
        readout_frame = ttk.LabelFrame(self.main_frame, text="Readouts")
        readout_frame.pack(fill=tk.X, pady=10)

        headers = [
            ("Temp Type", "red"), ("Pressure", "green"), 
            ("Voltage", "blue"), ("Current", "magenta"), ("Resistance", "black")
        ]
        
        for i, (text, color) in enumerate(headers):
            lbl = tk.Label(readout_frame, text=text, fg=color, font=("Arial", 10, "bold"))
            lbl.grid(row=0, column=i, padx=10, pady=5, sticky="ew")
            
            val = tk.Label(readout_frame, bg="white", relief="sunken", width=15)
            val.grid(row=1, column=i, padx=10, pady=5)
            
            readout_frame.columnconfigure(i, weight=1)

        # --- Bottom Section (Controls) ---
        bottom_frame = ttk.Frame(self.main_frame)
        bottom_frame.pack(fill=tk.X)

        # Column 1: Inputs
        col1 = ttk.Frame(bottom_frame)
        col1.pack(side=tk.LEFT, anchor=tk.N, padx=(0, 10))
        tk.Button(col1, text="Input Temp Values", command=self.on_click).pack(fill=tk.X, pady=2)
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
        
        tk.Button(col3, text="Down", command=self.on_click).pack(side=tk.LEFT, padx=5, pady=5)
        self.ent_manual_inc = tk.Entry(col3, width=8)
        self.ent_manual_inc.insert(0, "0.05")
        self.ent_manual_inc.pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(col3, text="Up", command=self.on_click).pack(side=tk.LEFT, padx=5, pady=5)

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
        tk.Button(bottom_frame, text="EXIT", bg="red", fg="white", command=self.root.quit).pack(side=tk.RIGHT, anchor=tk.S, padx=10, pady=10)

    def draw_grid(self, event=None):
        self.graph_canvas.delete("grid_line")
        w = self.graph_canvas.winfo_width()
        h = self.graph_canvas.winfo_height()

        for i in range(1, 8):
            # Vertical
            x = i * (w / 8)
            if i % 2 == 0:  # Quarters (2/8, 4/8, 6/8)
                self.graph_canvas.create_line(x, 0, x, h, fill="#A0A0A0", width=1, tags="grid_line")
            else:  # Eighths
                self.graph_canvas.create_line(x, 0, x, h, fill="#D0D0D0", dash=(2, 4), tags="grid_line")

            # Horizontal
            y = i * (h / 8)
            if i % 2 == 0:  # Quarters
                self.graph_canvas.create_line(0, y, w, y, fill="#A0A0A0", width=1, tags="grid_line")
            else:  # Eighths
                self.graph_canvas.create_line(0, y, w, y, fill="#D0D0D0", dash=(2, 4), tags="grid_line")

    def on_click(self):
        print("Button clicked")

if __name__ == "__main__":
    root = tk.Tk()
    app = BaseAPGUI(root)
    root.mainloop()
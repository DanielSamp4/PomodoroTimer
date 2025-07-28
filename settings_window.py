import tkinter as tk
from tkinter import ttk, colorchooser, messagebox
import json
import os

class SettingsWindow(tk.Toplevel):
    def __init__(self, parent_root, on_save_callback):
        super().__init__(parent_root)
        self.parent_root = parent_root
        self.on_save_callback = on_save_callback 
        self.title("Pomodoro Settings")
        # Increased height for the new item
        self.geometry("400x480") 
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.hide_window)

        self.config_file = "config.json"
        self.load_configurations()
        self.create_widgets()
        self.withdraw() 

    def load_configurations(self):
        """Loads saved configurations or sets defaults."""
        if os.path.exists(self.config_file):
            with open(self.config_file, "r") as f:
                self.config = json.load(f)
        else:
            self.config = {}

        # Ensure all default values exist
        self.config.setdefault("work_mins", 25)
        self.config.setdefault("break_mins", 5)
        self.config.setdefault("work_color", "white")
        self.config.setdefault("break_color", "#FF6347")
        self.config.setdefault("transparency", 0.1)
        self.config.setdefault("allow_move", False)
        self.config.setdefault("font_size", 100) # NEW: Default value

    def save_configurations(self):
        """Saves current configurations."""
        try:
            self.config["work_mins"] = int(self.work_mins_var.get())
            self.config["break_mins"] = int(self.break_mins_var.get())
            
            transparency_val = float(self.transparency_var.get())
            if not (0.0 <= transparency_val <= 1.0):
                raise ValueError("Transparency must be between 0.0 and 1.0.")
            self.config["transparency"] = transparency_val

            # NEW: Saves font size with validation
            font_size_val = int(self.font_size_var.get())
            if not (10 <= font_size_val <= 500):
                raise ValueError("Font size must be a number between 10 and 500.")
            self.config["font_size"] = font_size_val
            
            self.config["allow_move"] = self.allow_move_var.get() 

            with open(self.config_file, "w") as f:
                json.dump(self.config, f, indent=4)
            messagebox.showinfo("Success", "Settings saved successfully!")
            
            self.parent_root.after(0, lambda: self.on_save_callback(self.config)) 
            self.hide_window()
        except ValueError as ve:
            messagebox.showerror("Validation Error", str(ve))
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while saving: {e}")

    def create_widgets(self):
        """Creates the interface elements of the settings window."""
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Work Time
        ttk.Label(main_frame, text="Work Time (minutes):").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.work_mins_var = tk.StringVar(value=str(self.config.get("work_mins", 25)))
        ttk.Entry(main_frame, textvariable=self.work_mins_var).grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=5)

        # Break Time
        ttk.Label(main_frame, text="Break Time (minutes):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.break_mins_var = tk.StringVar(value=str(self.config.get("break_mins", 5)))
        ttk.Entry(main_frame, textvariable=self.break_mins_var).grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=5)

        # Work Color
        ttk.Label(main_frame, text="Work Color:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.work_color_label = tk.Label(main_frame, text=self.config.get("work_color", "white"), bg=self.config.get("work_color", "white"), relief=tk.SUNKEN)
        self.work_color_label.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=5)
        ttk.Button(main_frame, text="Choose Color", command=self.choose_work_color).grid(row=2, column=2, padx=5)

        # Break Color
        ttk.Label(main_frame, text="Break Color:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.break_color_label = tk.Label(main_frame, text=self.config.get("break_color", "#FF6347"), bg=self.config.get("break_color", "#FF6347"), relief=tk.SUNKEN)
        self.break_color_label.grid(row=3, column=1, sticky=(tk.W, tk.E), padx=5)
        ttk.Button(main_frame, text="Choose Color", command=self.choose_break_color).grid(row=3, column=2, padx=5)

        # Transparency
        ttk.Label(main_frame, text="Transparency (0.0 to 1.0):").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.transparency_var = tk.StringVar(value=str(self.config.get("transparency", 0.1)))
        ttk.Entry(main_frame, textvariable=self.transparency_var).grid(row=4, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=5)

        # NEW: Font Size
        ttk.Label(main_frame, text="Font Size:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.font_size_var = tk.StringVar(value=str(self.config.get("font_size", 100)))
        ttk.Entry(main_frame, textvariable=self.font_size_var).grid(row=5, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=5)

        # Checkbox to allow moving
        ttk.Label(main_frame, text="Allow Timer Movement:").grid(row=6, column=0, sticky=tk.W, pady=5)
        self.allow_move_var = tk.BooleanVar(value=self.config.get("allow_move", True))
        ttk.Checkbutton(main_frame, variable=self.allow_move_var).grid(row=6, column=1, sticky=tk.W, padx=5)

        # Save Button
        ttk.Button(main_frame, text="Save Settings", command=self.save_configurations).grid(row=7, column=0, columnspan=3, pady=20)

        main_frame.columnconfigure(1, weight=1)

    def choose_work_color(self):
        """Opens the color picker for work color."""
        color_code = colorchooser.askcolor(title="Choose Work Color", initialcolor=self.config.get("work_color"))
        if color_code[1]: # color_code[1] is the hexadecimal value
            self.config["work_color"] = color_code[1]
            self.work_color_label.config(text=color_code[1], bg=color_code[1])

    def choose_break_color(self):
        """Opens the color picker for break color."""
        color_code = colorchooser.askcolor(title="Choose Break Color", initialcolor=self.config.get("break_color"))
        if color_code[1]:
            self.config["break_color"] = color_code[1]
            self.break_color_label.config(text=color_code[1], bg=color_code[1])

    def show_window(self):
        """Displays the settings window."""
        self.deiconify()
        self.lift()
        self.focus_set()

    def hide_window(self):
        """Hides the settings window."""
        self.withdraw()
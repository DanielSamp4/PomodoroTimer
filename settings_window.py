import tkinter as tk
from tkinter import ttk, colorchooser, messagebox
import json
import os

class SettingsWindow(tk.Toplevel):
    def __init__(self, parent_root, on_save_callback):
        super().__init__(parent_root)
        self.parent_root = parent_root
        self.on_save_callback = on_save_callback 
        self.title("Configurações do Pomodoro")
        self.geometry("400x450") # Aumentei um pouco a altura para o novo item
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.hide_window)

        self.config_file = "config.json"
        self.load_configurations()
        self.create_widgets()
        self.withdraw() 

    def load_configurations(self):
        """Carrega as configurações salvas ou define padrões."""
        if os.path.exists(self.config_file):
            with open(self.config_file, "r") as f:
                self.config = json.load(f)
        else:
            self.config = {
                "work_mins": 25,
                "break_mins": 5,
                "work_color": "white",
                "break_color": "#FF6347",
                "transparency": 0.1,
                "allow_move": False # NOVO: Permissão para mover
            }

    def save_configurations(self):
        """Salva as configurações atuais."""
        try:
            self.config["work_mins"] = int(self.work_mins_var.get())
            self.config["break_mins"] = int(self.break_mins_var.get())
            
            transparency_val = float(self.transparency_var.get())
            if not (0.0 <= transparency_val <= 1.0):
                raise ValueError("A transparência deve ser entre 0.0 e 1.0.")
            self.config["transparency"] = transparency_val

            # NOVO: Salva o estado da permissão de mover
            self.config["allow_move"] = self.allow_move_var.get() 

            with open(self.config_file, "w") as f:
                json.dump(self.config, f, indent=4)
            messagebox.showinfo("Sucesso", "Configurações salvas com sucesso!")
            
            self.parent_root.after(0, lambda: self.on_save_callback(self.config)) 
            self.hide_window()
        except ValueError as ve:
            messagebox.showerror("Erro de Validação", str(ve))
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro ao salvar: {e}")

    def create_widgets(self):
        """Cria os elementos da interface da janela de configurações."""
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Work Time
        ttk.Label(main_frame, text="Tempo de Trabalho (minutos):").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.work_mins_var = tk.StringVar(value=str(self.config.get("work_mins", 25)))
        ttk.Entry(main_frame, textvariable=self.work_mins_var).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)

        # Break Time
        ttk.Label(main_frame, text="Tempo de Descanso (minutos):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.break_mins_var = tk.StringVar(value=str(self.config.get("break_mins", 5)))
        ttk.Entry(main_frame, textvariable=self.break_mins_var).grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5)

        # Work Color
        ttk.Label(main_frame, text="Cor do Trabalho:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.work_color_label = tk.Label(main_frame, text=self.config.get("work_color", "white"), bg=self.config.get("work_color", "white"), relief=tk.SUNKEN)
        self.work_color_label.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=5)
        ttk.Button(main_frame, text="Escolher Cor", command=self.choose_work_color).grid(row=2, column=2, padx=5)

        # Break Color
        ttk.Label(main_frame, text="Cor do Descanso:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.break_color_label = tk.Label(main_frame, text=self.config.get("break_color", "#FF6347"), bg=self.config.get("break_color", "#FF6347"), relief=tk.SUNKEN)
        self.break_color_label.grid(row=3, column=1, sticky=(tk.W, tk.E), padx=5)
        ttk.Button(main_frame, text="Escolher Cor", command=self.choose_break_color).grid(row=3, column=2, padx=5)

        # Transparency
        ttk.Label(main_frame, text="Transparência (0.0 a 1.0):").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.transparency_var = tk.StringVar(value=str(self.config.get("transparency", 0.1)))
        ttk.Entry(main_frame, textvariable=self.transparency_var).grid(row=4, column=1, sticky=(tk.W, tk.E), padx=5)

        # NOVO: Checkbox para permitir mover
        ttk.Label(main_frame, text="Permitir Mover Timer:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.allow_move_var = tk.BooleanVar(value=self.config.get("allow_move", True))
        ttk.Checkbutton(main_frame, variable=self.allow_move_var).grid(row=5, column=1, sticky=tk.W, padx=5)


        # Save Button
        ttk.Button(main_frame, text="Salvar Configurações", command=self.save_configurations).grid(row=6, column=0, columnspan=3, pady=20)

        main_frame.columnconfigure(1, weight=1)

    def choose_work_color(self):
        """Abre o seletor de cores para a cor de trabalho."""
        color_code = colorchooser.askcolor(title="Escolha a Cor de Trabalho", initialcolor=self.config.get("work_color"))
        if color_code[1]: # color_code[1] é o valor hexadecimal
            self.config["work_color"] = color_code[1]
            self.work_color_label.config(text=color_code[1], bg=color_code[1])

    def choose_break_color(self):
        """Abre o seletor de cores para a cor de descanso."""
        color_code = colorchooser.askcolor(title="Escolha a Cor de Descanso", initialcolor=self.config.get("break_color"))
        if color_code[1]:
            self.config["break_color"] = color_code[1]
            self.break_color_label.config(text=color_code[1], bg=color_code[1])

    def show_window(self):
        """Exibe a janela de configurações."""
        self.deiconify()
        self.lift()
        self.focus_set()

    def hide_window(self):
        """Esconde a janela de configurações (minimiza para a bandeja)."""
        self.withdraw()
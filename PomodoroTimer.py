import tkinter as tk
import time
from threading import Thread, Event
import json
import os
from PIL import Image
from pystray import Icon, Menu, MenuItem
from settings_window import SettingsWindow

# --- Carregar Configurações Iniciais ---
CONFIG_FILE = "config.json"

def load_initial_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
            config.setdefault("work_mins", 25)
            config.setdefault("break_mins", 5)
            config.setdefault("work_color", "white")
            config.setdefault("break_color", "#FF6347")
            config.setdefault("transparency", 0.1)
            config.setdefault("allow_move", False)
            config.setdefault("font_size", 100)
            return config
    return {
        "work_mins": 25,
        "break_mins": 5,
        "work_color": "white",
        "break_color": "#FF6347",
        "transparency": 0.1,
        "allow_move": False,
        "font_size": 100
    }

class PomodoroTimer:
    def __init__(self, root):
        self.root = root
        self.running = False
        self.showing = True
        self.settings_window = None
        self.system_tray_icon = None
        
        self.config = load_initial_config()
        self.is_work_time = True
        self.time_left = self.config["work_mins"] * 60 

        self.create_overlay()
        self.setup_system_tray()
        
        self.app_exit_event = Event() 
        self.root.protocol("WM_DELETE_WINDOW", self.exit_application)

    def update_with_new_config(self, new_config):
        """
        Atualiza as configurações do timer com as novas configurações salvas.
        """
        self.config.update(new_config)
        
        self.root.attributes("-alpha", self.config["transparency"])
        self.timer_label.config(font=("Helvetica", self.config.get("font_size", 100)))
        
        # Redefine a geometria e centraliza a janela
        self._update_geometry()

        if self.is_work_time:
            self.timer_label.config(fg=self.config["work_color"])
        else:
            self.timer_label.config(fg=self.config["break_color"])

        if not self.running:
            if self.is_work_time:
                self.time_left = self.config["work_mins"] * 60
            else:
                self.time_left = self.config["break_mins"] * 60
            self.update_timer_display()

        self._bind_movement_events()
        print("Configurações aplicadas: ", self.config)

    def _update_geometry(self):
        """
        Calcula o tamanho da janela e a posiciona no centro da tela.
        """
        font_size = self.config.get("font_size", 100)
        new_width = int(font_size * 5)
        new_height = int(font_size * 2)

        # Obtém as dimensões da tela
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Calcula a posição X e Y para centralizar a janela
        position_x = (screen_width // 2) - (new_width // 2)
        position_y = (screen_height // 2) - (new_height // 2)

        self.root.geometry(f"{new_width}x{new_height}+{position_x}+{position_y}")

    def create_overlay(self):
        """Configura a janela de overlay."""
        self.root.overrideredirect(True)
        
        # Apenas chama a função de geometria para centralizar na criação
        self._update_geometry()

        self.root.configure(bg='black')
        self.root.attributes("-topmost", True)
        self.root.attributes("-transparentcolor", "black")
        self.root.attributes("-alpha", self.config["transparency"]) 
        self.root.title("Pomodoro Timer")

        initial_time = f"{self.config['work_mins']:02d}:00"
        self.timer_label = tk.Label(
            self.root, 
            text=initial_time, 
            font=("Helvetica", self.config.get("font_size", 100)), 
            fg=self.config["work_color"], 
            bg="black"
        )
        self.timer_label.pack(fill=tk.BOTH, expand=True, pady=20)

        self._bind_movement_events()
        self.timer_label.bind("<Button-3>", self.show_context_menu)
        self.root.bind("<Button-3>", self.show_context_menu)
        self.root.bind("<Unmap>", self.on_minimize)

    def _bind_movement_events(self):
        if self.config.get("allow_move", True):
            self.timer_label.bind("<ButtonPress-1>", self.start_move)
            self.timer_label.bind("<B1-Motion>", self.do_move)
        else:
            self.timer_label.unbind("<ButtonPress-1>")
            self.timer_label.unbind("<B1-Motion>")

    def on_minimize(self, event=None):
        if self.root.wm_state() == 'iconic':
            self.root.withdraw()
            print("Janela minimizada para a bandeja.")
        elif self.root.wm_state() == 'normal':
             self.root.withdraw()
             print("Janela escondida para a bandeja.")

    def start_move(self, event):
        if self.config.get("allow_move", True): 
            self.x = event.x
            self.y = event.y

    def do_move(self, event):
        if self.config.get("allow_move", True):
            deltax = event.x - self.x
            deltay = event.y - self.y
            x = self.root.winfo_x() + deltax
            y = self.root.winfo_y() + deltay
            self.root.geometry(f"+{x}+{y}")

    def show_context_menu(self, event):
        menu = tk.Menu(self.root, tearoff=0)
        # NOVO: Rótulos em inglês
        menu.add_command(label="Start", command=self.start_timer, state=tk.DISABLED if self.running else tk.NORMAL)
        menu.add_command(label="Stop", command=self.stop_timer, state=tk.NORMAL if self.running else tk.DISABLED)
        menu.add_separator()
        menu.add_command(label="Settings", command=self.open_settings)
        menu.add_command(label="Hide", command=self.hide_timer_window)
        menu.add_command(label="Exit", command=self.exit_application)
        menu.post(event.x_root, event.y_root)

    def breathing_animation(self, color):
        animation_window = tk.Toplevel(self.root)
        animation_window.overrideredirect(True)
        
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        animation_window.geometry(f"{screen_width}x{screen_height}+0+0")
        
        animation_window.configure(bg=color)
        animation_window.attributes("-topmost", True)
        animation_window.attributes("-alpha", 0.0)

        duration_ms = 2000
        steps = 80
        max_alpha = 0.6     
        
        fade_in_interval = (duration_ms // 2) // steps
        fade_out_interval = (duration_ms // 2) // steps
        alpha_step = max_alpha / steps

        def fade_in(current_step=0):
            alpha = alpha_step * current_step
            if alpha <= max_alpha:
                animation_window.attributes("-alpha", alpha)
                self.root.after(fade_in_interval, fade_in, current_step + 1)
            else:
                fade_out()

        def fade_out(current_step=steps):
            alpha = alpha_step * current_step
            if alpha >= 0:
                animation_window.attributes("-alpha", alpha)
                self.root.after(fade_out_interval, fade_out, current_step - 1)
            else:
                animation_window.destroy()
        
        fade_in()
        
        return duration_ms

    def update_timer_display(self):
        mins, secs = divmod(self.time_left, 60)
        time_str = f"{mins:02d}:{secs:02d}"
        self.timer_label.config(text=time_str)

    def update_timer(self):
        if self.running:
            self.update_timer_display()

            if self.time_left > 0:
                self.time_left -= 1
                self.root.after(1000, self.update_timer)
            else:
                self.switch_cycle()

    def switch_cycle(self):
        flash_color = ""
        next_timer_color = ""

        if self.is_work_time:
            self.is_work_time = False
            self.time_left = self.config["break_mins"] * 60 
            flash_color = self.config["break_color"]
            next_timer_color = self.config["break_color"]
        else:
            self.is_work_time = True
            self.time_left = self.config["work_mins"] * 60 
            flash_color = self.config["work_color"]
            next_timer_color = self.config["work_color"]
        
        animation_duration = self.breathing_animation(flash_color)
        self.timer_label.config(fg=next_timer_color)
        self.root.after(animation_duration, self.update_timer)

    def start_timer(self):
        if not self.running:
            self.running = True
            self.update_timer()

    def stop_timer(self):
        if self.running: 
            self.running = False

    def toggle_timer(self):
        if self.running:
            self.stop_timer()
        else:
            self.start_timer()
        
    def open_settings(self):
        if self.settings_window is None or not self.settings_window.winfo_exists():
            self.root.after(0, lambda: self._create_settings_window())
        else:
            self.root.after(0, self.settings_window.show_window)

    def _create_settings_window(self):
        self.settings_window = SettingsWindow(self.root, self.update_with_new_config)
        self.settings_window.show_window()

    def exit_application(self):
        self.app_exit_event.set()
        
        if self.system_tray_icon:
            try:
                self.system_tray_icon.stop() 
                self.system_tray_icon = None
            except Exception as e:
                print(f"Erro ao parar o ícone da bandeja: {e}")

        if self.root:
            try:
                self.root.quit() 
            except Exception as e:
                print(f"Erro ao tentar parar o mainloop do Tkinter: {e}")
    
    def setup_system_tray(self):
        """Configura o ícone na bandeja do sistema."""
        try:
            icon_path = "favicon.ico" 
            if os.path.exists(icon_path):
                image = Image.open(icon_path)
            else:
                image = Image.new('RGB', (64, 64), color = 'red')
            
            # NOVO: Rótulos do menu em inglês
            self._tray_menu = Menu(
                MenuItem(
                    lambda text: 'Hide Timer' if self.showing else 'Show Timer', 
                    self._toggle_show_timer_from_tray_callback
                ),
                MenuItem(
                    lambda text: 'Pause' if self.running else 'Start', 
                    self._toggle_timer_from_tray_callback
                ),
                MenuItem('Settings', self._open_settings_from_tray_callback),
                MenuItem('Exit', self._exit_application_from_tray_callback)
            )
            self.system_tray_icon = Icon("Pomodoro Timer", image, "Pomodoro Timer", self._tray_menu)
            tray_thread = Thread(target=self.system_tray_icon.run, daemon=True)
            tray_thread.start()

        except Exception as e:
            print(f"Erro ao configurar o ícone da bandeja: {e}")
            print("Certifique-se de ter 'pystray' e 'Pillow' instalados (pip install pystray Pillow).")

    def _toggle_show_timer_from_tray_callback(self, icon, item):
        self.root.after(0, self.toggle_show_hide_window)

    def _open_settings_from_tray_callback(self, icon, item):
        self.root.after(0, self.open_settings)

    def _toggle_timer_from_tray_callback(self, icon, item):
        self.root.after(0, self.toggle_timer)

    def _exit_application_from_tray_callback(self, icon, item):
        self.root.after(0, self.exit_application)
    
    def hide_timer_window(self):
        self.showing = False
        self.root.withdraw()

    def toggle_show_hide_window(self):
        self.showing = not self.showing
        if self.showing:
            self.root.deiconify()
            self.root.lift()
            self.root.focus_set()
        else: 
            self.root.withdraw()


def start_pomodoro():
    root = tk.Tk()
    timer = PomodoroTimer(root)
    root.mainloop()


if __name__ == "__main__":
    main_thread = Thread(target=start_pomodoro, daemon=True)
    main_thread.start()

    print("Pomodoro timer está rodando em segundo plano. Verifique o ícone na bandeja do sistema.")
    print("Use o menu de contexto (clique direito) no timer ou no ícone da bandeja para controlar.")
    
    try:
        main_thread.join()
    except KeyboardInterrupt:
        print("\nEncerrando o timer.")
        if tk._default_root:
             tk._default_root.after(0, lambda: tk._default_root.quit())
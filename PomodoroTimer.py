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
            return json.load(f)
    return {
        "work_mins": 25,
        "break_mins": 5,
        "work_color": "white",
        "break_color": "#FF6347",
        "transparency": 0.1,
        "allow_move": False # Padrão para permitir mover
    }

class PomodoroTimer:
    def __init__(self, root):
        self.root = root
        self.running = False
        self.showing = False
        self.settings_window = None
        self.system_tray_icon = None
        
        # Armazena a configuração carregada na instância
        self.config = load_initial_config()

        self.is_work_time = True
        # Inicializa o tempo restante com base na configuração da instância
        self.time_left = self.config["work_mins"] * 60 
        self.root.withdraw() # Inicia a janela principal escondida

        self.create_overlay()
        self.setup_system_tray()
        
        self.app_exit_event = Event() 
        self.root.protocol("WM_DELETE_WINDOW", self.exit_application)

    def update_with_new_config(self, new_config):
        """
        Atualiza as configurações do timer com as novas configurações salvas.
        """
        # Atualiza o dicionário de configuração da instância
        self.config.update(new_config)
        
        # Aplica a nova transparência imediatamente à janela
        self.root.attributes("-alpha", self.config["transparency"])
        
        # ATUALIZA A COR DA LABEL IMEDIATAMENTE COM BASE NO CICLO ATUAL
        if self.is_work_time:
            self.timer_label.config(fg=self.config["work_color"])
        else:
            self.timer_label.config(fg=self.config["break_color"])

        # Se o timer estiver parado, resetamos o tempo para o novo valor
        if not self.running:
            if self.is_work_time:
                self.time_left = self.config["work_mins"] * 60
            else:
                self.time_left = self.config["break_mins"] * 60
            self.update_timer_display()

        # Re-bind dos eventos de movimento se a permissão mudou
        self._bind_movement_events()

        print("Configurações aplicadas: ", self.config)


    def create_overlay(self):
        """Configura a janela de overlay."""
        self.root.overrideredirect(True)
        self.root.geometry("500x200+710+400")
        self.root.configure(bg='black')
        self.root.attributes("-topmost", True)
        self.root.attributes("-transparentcolor", "black")
        # Usa a configuração da instância para a transparência inicial
        self.root.attributes("-alpha", self.config["transparency"]) 
        self.root.title("Pomodoro Timer")

        # Usa a configuração da instância para a cor inicial
        initial_time = f"{self.config['work_mins']:02d}:00"
        self.timer_label = tk.Label(
            self.root, 
            text=initial_time, 
            font=("Helvetica", 100), 
            # Usa a configuração da instância para a cor inicial
            fg=self.config["work_color"], 
            bg="black"
        )
        self.timer_label.pack(fill=tk.BOTH, expand=True, pady=20)

        # Bind dos eventos de movimento controlado por permissão
        self._bind_movement_events()

        self.timer_label.bind("<Button-3>", self.show_context_menu)
        self.root.bind("<Button-3>", self.show_context_menu)

        self.root.bind("<Unmap>", self.on_minimize)

    def _bind_movement_events(self):
        """Conecta ou desconecta os eventos de movimento com base na configuração."""
        if self.config.get("allow_move", True): # Assume True se a chave não existir (padrão antigo)
            self.timer_label.bind("<ButtonPress-1>", self.start_move)
            self.timer_label.bind("<B1-Motion>", self.do_move)
        else:
            # Desconecta os binds se não for permitido mover
            self.timer_label.unbind("<ButtonPress-1>")
            self.timer_label.unbind("<B1-Motion>")

    def on_minimize(self, event=None):
        """Esconde a janela quando ela é minimizada (para a bandeja)."""
        if self.root.wm_state() == 'iconic':
            self.root.withdraw()
            print("Janela minimizada para a bandeja.")
        elif self.root.wm_state() == 'normal':
             self.root.withdraw()
             print("Janela escondida para a bandeja.")

    def start_move(self, event):
        """Inicia o movimento da janela se permitido."""
        # A verificação 'allow_move' já está sendo feita no _bind_movement_events,
        # mas adicionar uma verificação aqui é uma segurança extra.
        if self.config.get("allow_move", True): 
            self.x = event.x
            self.y = event.y

    def do_move(self, event):
        """Executa o movimento da janela se permitido."""
        if self.config.get("allow_move", True):
            deltax = event.x - self.x
            deltay = event.y - self.y
            x = self.root.winfo_x() + deltax
            y = self.root.winfo_y() + deltay
            self.root.geometry(f"+{x}+{y}")

    def show_context_menu(self, event):
        """Exibe um menu de contexto ao clicar com o botão direito."""
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="Iniciar", command=self.start_timer, state=tk.DISABLED if self.running else tk.NORMAL)
        menu.add_command(label="Parar", command=self.stop_timer, state=tk.NORMAL if self.running else tk.DISABLED)
        menu.add_separator()
        menu.add_command(label="Configurações", command=self.open_settings)
        menu.add_command(label="Esconder", command=self.on_minimize)
        menu.add_command(label="Sair", command=self.exit_application)
        menu.post(event.x_root, event.y_root)

    def breathing_animation(self, color):
        """Cria uma animação de pulsar em tela cheia para alertar a troca de ciclo."""
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
        """Atualiza apenas a exibição do tempo no label."""
        mins, secs = divmod(self.time_left, 60)
        time_str = f"{mins:02d}:{secs:02d}"
        self.timer_label.config(text=time_str)

    def update_timer(self):
        """Função principal que atualiza o contador a cada segundo."""
        if self.running:
            self.update_timer_display()

            if self.time_left > 0:
                self.time_left -= 1
                self.root.after(1000, self.update_timer)
            else:
                self.switch_cycle()

    def switch_cycle(self):
        """Alterna entre os ciclos com uma animação de pulsar."""
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
        """Inicia o timer se ele não estiver rodando."""
        if not self.running:
            self.running = True
            self.update_timer()

    def stop_timer(self):
        """Para o timer."""
        if self.running: 
            self.running = False

    def toggle_timer(self):
        """Alterna entre iniciar e parar o timer."""
        if self.running:
            self.stop_timer()
        else:
            self.start_timer()
        
    def open_settings(self):
        """Abre a janela de configurações ou a traz para frente se já estiver aberta."""
        if self.settings_window is None or not self.settings_window.winfo_exists():
            self.root.after(0, lambda: self._create_settings_window())
        else:
            self.root.after(0, self.settings_window.show_window)

    def _create_settings_window(self):
        """Cria a instância da janela de configurações na thread principal."""
        self.settings_window = SettingsWindow(self.root, self.update_with_new_config)
        self.settings_window.show_window()

    def exit_application(self):
        # """Encerra a aplicação de forma segura."""
        # if self.system_tray_icon:
        #     self.system_tray_icon.stop()
        # self.app_exit_event.set()
        # self.root.quit()
        # self.root.destroy()
        """
        Encerra a aplicação de forma segura, parando threads e liberando recursos.
        """
        # print("Encerrando a aplicação...")
        
        # 1. Sinaliza o evento de saída para que outras threads possam reagir.
        self.app_exit_event.set()
        
        # 2. Para a thread do ícone da bandeja. ISSO É CRÍTICO para evitar erros do pystray.
        if self.system_tray_icon:
            try:
                self.system_tray_icon.stop() 
                self.system_tray_icon = None # Remove a referência para auxiliar o garbage collection
            except Exception as e:
                print(f"Erro ao parar o ícone da bandeja: {e}")

        # 3. Interrompe o loop principal do Tkinter.
        # Isso precisa acontecer na thread principal do Tkinter.
        # Garante que `mainloop()` pare.
        if self.root: # Verifica se root ainda existe antes de tentar quit/destroy
            try:
                self.root.quit() 
                # Não chame destroy() aqui imediatamente. Deixe o mainloop finalizar e o garbage collection
                # do Python fazer seu trabalho em um ambiente mais seguro após o mainloop encerrar.
                # Se `destroy()` for chamado muito cedo ou de forma incorreta, pode causar os erros.
            except Exception as e:
                print(f"Erro ao tentar parar o mainloop do Tkinter: {e}")
        
        # A aplicação sairá quando a `main_thread.join()` no `if __name__ == "__main__":`
        # for completada após o `root.quit()`.
        # Evite os._exit(0) se possível, pois ele não limpa recursos.

    # --- Funções para integração com a bandeja do sistema ---
    def setup_system_tray(self):
        """Configura o ícone na bandeja do sistema."""
        try:
            icon_path = "favicon.ico" 
            if os.path.exists(icon_path):
                image = Image.open(icon_path)
            else:
                image = Image.new('RGB', (64, 64), color = 'red')
                
            self._tray_menu = Menu(
                MenuItem(lambda text:'Esconder Timer' if self.showing else 'Mostrar Timer', self._toggle_show_timer_from_tray_callback),
                MenuItem(lambda text: 'Pausar' if self.running else 'Iniciar', self._toggle_timer_from_tray_callback),
                MenuItem('Configurações', self._open_settings_from_tray_callback),
                MenuItem('Sair', self._exit_application_from_tray_callback)
            )
            self.system_tray_icon = Icon("Pomodoro Timer", image, "Pomodoro Timer", self._tray_menu)
            tray_thread = Thread(target=self.system_tray_icon.run, daemon=True)
            tray_thread.start()

        except Exception as e:
            print(f"Erro ao configurar o ícone da bandeja: {e}")
            print("Certifique-se de ter 'pystray' e 'Pillow' instalados (pip install pystray Pillow).")

    def _toggle_show_timer_from_tray_callback(self, icon, item):
        self.showing = not self.showing
        self.root.after(0, self.show_timer_window)

    def _open_settings_from_tray_callback(self, icon, item):
        self.root.after(0, self.open_settings)

    def _toggle_timer_from_tray_callback(self, icon, item):
        """Callback para o item Iniciar/Pausar na bandeja."""
        self.root.after(0, self.toggle_timer)

    def _exit_application_from_tray_callback(self, icon, item):
        self.root.after(0, self.exit_application)

    def show_timer_window(self):
        if self.showing:
            """Mostra e traz para frente a janela principal do timer."""
            self.root.deiconify()
            self.root.lift()
            self.root.focus_set()
        else: 
            """Esconde a janela principal do timer."""
            self.root.withdraw()


def start_pomodoro():
    """Cria a janela Tkinter e inicia o timer."""
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
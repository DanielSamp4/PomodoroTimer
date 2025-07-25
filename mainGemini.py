import tkinter as tk
import time
from threading import Thread

# --- Constantes para facilitar a configuração ---
WORK_MINS = 25
BREAK_MINS = 5
# Para testes rápidos, você pode usar valores menores:
# WORK_MINS = 1
# BREAK_MINS = 1

# --- Cores para os ciclos ---
WORK_COLOR = "white"
BREAK_COLOR = "#FF6347" # Vermelho Tomate (um vermelho mais suave)

class PomodoroTimer:
    def __init__(self, root):
        self.root = root
        self.running = False
        
        # Estado inicial: começando com o tempo de trabalho
        self.is_work_time = True
        self.time_left = WORK_MINS * 60
        
        self.create_overlay()
        # Não chamamos update_timer aqui, esperamos o start_timer

    def create_overlay(self):
        """Configura a janela de overlay."""
        self.root.overrideredirect(True)
        self.root.geometry("500x200+710+400")
        self.root.configure(bg='black')
        self.root.attributes("-topmost", True)
        self.root.attributes("-transparentcolor", "black")
        self.root.attributes("-alpha", 0.7)
        self.root.title("Pomodoro Timer") # Este é o título que pode aparecer em alguns gerenciadores

        initial_time = f"{WORK_MINS:02d}:00"
        self.timer_label = tk.Label(
            self.root, 
            text=initial_time, 
            font=("Helvetica", 100), 
            fg=WORK_COLOR,
            bg="black"
        )
        self.timer_label.pack(fill=tk.BOTH, expand=True, pady=20)

    def breathing_animation(self, color):
        """Cria uma animação de pulsar em tela cheia para alertar a troca de ciclo."""
        animation_window = tk.Toplevel(self.root)
        animation_window.overrideredirect(True)
        
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        animation_window.geometry(f"{screen_width}x{screen_height}+0+0")
        
        animation_window.configure(bg=color)
        animation_window.attributes("-topmost", True)
        animation_window.attributes("-alpha", 0.0) # Começa totalmente transparente

        # Parâmetros da animação
        duration_ms = 1200  # Duração total da animação em milissegundos
        steps = 30          # Número de passos para fade-in e fade-out
        max_alpha = 0.5     # Opacidade máxima do pulso
        
        fade_in_interval = (duration_ms // 2) // steps
        fade_out_interval = (duration_ms // 2) // steps
        alpha_step = max_alpha / steps

        def fade_in(current_step=0):
            """Aumenta gradualmente a opacidade."""
            alpha = alpha_step * current_step
            if alpha <= max_alpha:
                animation_window.attributes("-alpha", alpha)
                self.root.after(fade_in_interval, fade_in, current_step + 1)
            else:
                # Inicia o fade-out quando o fade-in termina
                fade_out()

        def fade_out(current_step=steps):
            """Diminui gradualmente a opacidade."""
            alpha = alpha_step * current_step
            if alpha >= 0:
                animation_window.attributes("-alpha", alpha)
                self.root.after(fade_out_interval, fade_out, current_step - 1)
            else:
                # Destroi a janela ao final da animação
                animation_window.destroy()
        
        # Inicia a animação
        fade_in()
        
        return duration_ms

    def update_timer(self):
        """Função principal que atualiza o contador a cada segundo."""
        if self.running:
            mins, secs = divmod(self.time_left, 60)
            time_str = f"{mins:02d}:{secs:02d}"
            self.timer_label.config(text=time_str)

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
            # O trabalho acabou, iniciar o descanso
            self.is_work_time = False
            self.time_left = BREAK_MINS * 60
            flash_color = BREAK_COLOR
            next_timer_color = BREAK_COLOR
        else:
            # O descanso acabou, iniciar o trabalho
            self.is_work_time = True
            self.time_left = WORK_MINS * 60
            flash_color = WORK_COLOR
            next_timer_color = WORK_COLOR
        
        # 1. Executa a animação de pulsar
        animation_duration = self.breathing_animation(flash_color)
        
        # 2. Atualiza a cor do timer para a do próximo ciclo
        self.timer_label.config(fg=next_timer_color)
        
        # 3. Agenda o reinício do loop do timer para DEPOIS que a animação terminar
        self.root.after(animation_duration, self.update_timer)

    def start_timer(self):
        """Inicia o timer se ele não estiver rodando."""
        if not self.running:
            self.running = True
            self.update_timer()

    def stop_timer(self):
        """Para o timer."""
        self.running = False

def start_pomodoro():
    """Cria a janela Tkinter e inicia o timer."""
    root = tk.Tk()
    timer = PomodoroTimer(root)
    timer.start_timer()
    root.mainloop()

if __name__ == "__main__":
    timer_thread = Thread(target=start_pomodoro, daemon=True)
    timer_thread.start()

    print("Pomodoro timer está rodando em segundo plano.")
    print("Feche a janela do terminal para encerrar o timer.")
    try:
        timer_thread.join()
    except KeyboardInterrupt:
        print("\nEncerrando o timer.")
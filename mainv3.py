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
        self.root.geometry("500x200+710+400") # Altura reduzida
        self.root.configure(bg='black')
        self.root.attributes("-topmost", True)
        self.root.attributes("-transparentcolor", "black")
        self.root.attributes("-alpha", 0.3) # Transparência de 70%
        self.root.title("Pomodoro Timer")

        # Label principal do timer
        initial_time = f"{WORK_MINS:02d}:00"
        self.timer_label = tk.Label(
            self.root, 
            text=initial_time, 
            font=("Helvetica", 100), 
            fg=WORK_COLOR, # Cor inicial para o trabalho
            bg="black"
        )
        self.timer_label.pack(fill=tk.BOTH, expand=True, pady=20) # Adicionado padding

    def update_timer(self):
        """Função principal que atualiza o contador a cada segundo."""
        if self.running:
            # Formata o tempo restante para MM:SS
            mins, secs = divmod(self.time_left, 60)
            time_str = f"{mins:02d}:{secs:02d}"
            self.timer_label.config(text=time_str)

            # Se ainda há tempo, continua a contagem regressiva
            if self.time_left > 0:
                self.time_left -= 1
                self.root.after(1000, self.update_timer)
            else:
                # O tempo acabou, vamos alternar para o próximo ciclo
                self.switch_cycle()

    def switch_cycle(self):
        """Alterna entre os ciclos de trabalho e descanso, mudando a cor do timer."""
        if self.is_work_time:
            # O tempo de trabalho acabou, iniciar o descanso
            self.is_work_time = False
            self.time_left = BREAK_MINS * 60
            self.timer_label.config(fg=BREAK_COLOR) # Muda a cor para a de descanso
        else:
            # O tempo de descanso acabou, iniciar o trabalho
            self.is_work_time = True
            self.time_left = WORK_MINS * 60
            self.timer_label.config(fg=WORK_COLOR) # Muda a cor para a de trabalho
        
        # Continua o loop do timer com o novo ciclo
        self.update_timer()

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
    
    # Inicia o timer automaticamente quando o script é executado
    timer.start_timer()

    root.mainloop()

if __name__ == "__main__":
    # Roda o timer em uma thread separada para não travar outras aplicações
    timer_thread = Thread(target=start_pomodoro, daemon=True)
    timer_thread.start()

    # O script principal pode continuar rodando ou simplesmente esperar.
    # Adicionamos um input para que o script não feche imediatamente.
    print("Pomodoro timer está rodando em segundo plano.")
    print("Feche a janela do terminal para encerrar o timer.")
    try:
        # Mantém o script principal vivo
        timer_thread.join()
    except KeyboardInterrupt:
        print("\nEncerrando o timer.")

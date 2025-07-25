import tkinter as tk
import time
from threading import Thread

# Pomodoro Timer Functionality
class PomodoroTimer:
    def __init__(self, root):
        self.root = root
        self.running = False
        self.time_left = 25 * 60  # Default Pomodoro time (25 minutes)
        self.create_overlay()
        self.update_timer()

    def create_overlay(self):
        # Remove the title bar and control buttons (minimize, maximize, close)
        self.root.overrideredirect(True)  # Remove title bar and controls
        self.root.geometry("500x200+710+400")  # Fixed size and position
        self.root.configure(bg='black')
        self.root.attributes("-topmost", True)  # Keep window on top
        self.root.attributes("-transparentcolor", "black")  # Make black transparent
        self.root.title("Pomodoro Timer")

        # Timer label
        self.timer_label = tk.Label(self.root, text="25:00", font=("Helvetica", 100), fg="white", bg="black")
        self.timer_label.pack(fill=tk.BOTH, expand=True)

    def update_timer(self):
        # Update the timer every second
        if self.running:
            mins, secs = divmod(self.time_left, 60)
            time_str = f"{mins:02d}:{secs:02d}"
            self.timer_label.config(text=time_str)

            if self.time_left > 0:
                self.time_left -= 1
                self.root.after(1000, self.update_timer)
            else:
                self.time_left = 25 * 60  # Reset for next Pomodoro session
                self.running = False
                self.timer_label.config(text="Time's Up!")

    def start_timer(self):
        if not self.running:
            self.running = True
            self.update_timer()

    def stop_timer(self):
        self.running = False

# Start the Pomodoro timer in a separate thread to avoid blocking the UI
def start_pomodoro():
    root = tk.Tk()  # Create the root Tkinter window
    timer = PomodoroTimer(root)
    timer.start_timer()

    root.mainloop()

# Create a separate thread for the Pomodoro timer to run in the background
if __name__ == "__main__":
    timer_thread = Thread(target=start_pomodoro)
    timer_thread.start()

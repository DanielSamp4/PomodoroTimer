-----

# Pomodoro Timer

This is a simple yet effective Pomodoro Timer application built with Python's Tkinter library. It helps you stay focused during work sessions and reminds you to take regular breaks, following the principles of the **Pomodoro Technique**. The timer is designed to be customizable, allowing you to adjust work and break durations, colors, transparency, and even font size.

## Features

  * **Customizable Work and Break Durations:** Set your ideal focus and rest times.
  * **Adjustable Colors:** Personalize the timer's colors for both work and break states.
  * **Transparency Control:** Make the timer more or less transparent to suit your desktop environment.
  * **Movable Window:** Choose whether the timer window can be dragged around your screen.
  * **Font Size Adjustment:** Control the size of the displayed timer text.
  * **Persistent Settings:** Your configurations are saved and loaded automatically.
  * **User-Friendly Interface:** Intuitive controls for easy timer management.
  * **Runs in Background:** The timer can run silently in the background, keeping you on track without being obtrusive.

## How to Use

1.  **Download and Run:** Simply download the latest executable from the [releases page](https://www.google.com/search?q=link-to-releases) and run it.
2.  **Start the Timer:** Click the **"Start"** button to begin a work session.
3.  **Pause/Resume:** Click the **"Pause"** button to temporarily stop the timer, and click it again to resume.
4.  **Reset:** The **"Reset"** button will return the timer to its initial state for the current phase (work or break).
5.  **Skip:** The **"Skip"** button will immediately transition to the next phase (e.g., from work to break, or break to work).
6.  **Settings:** Click the **"Settings"** button (⚙️) to open the configuration window.

## Settings Explained

The settings window allows you to fine-tune your Pomodoro experience:

  * **Work Time (minutes):** Set the duration of your focus periods. Default is `25` minutes.
  * **Break Time (minutes):** Set the duration of your short breaks. Default is `5` minutes.
  * **Work Color:** Choose the background color for your work sessions. Default is `#ffffff` (white).
  * **Break Color:** Choose the background color for your break sessions. Default is `#FF6347` (Tomato).
  * **Transparency (0.0 to 1.0):** Control the opacity of the timer window. `0.0` is fully transparent, `1.0` is fully opaque. Default is `0.1`.
  * **Font Size:** Adjust the size of the timer's displayed text. Recommended range is `10` to `500`. Default is `100`.
  * **Allow Timer Movement:** Check this box if you want to be able to drag and reposition the timer window on your screen. Default is `False`.

After making changes in the settings, click **"Save Settings"** to apply them.

## Project Structure

  * `main.py`: The main application file containing the `PomodoroApp` class.
  * `settings_window.py`: Contains the `SettingsWindow` class for managing configurations.
  * `config.json`: (Automatically created) Stores your personalized settings.

## Contributing

Feel free to fork this repository, make improvements, and submit pull requests. Any contributions are welcome\!

## License

This project is open-source and available under the [MIT License](https://www.google.com/search?q=LICENSE).

-----
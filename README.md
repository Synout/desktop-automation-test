# Desktop Data Entry Automation

This project is a simple demonstration of Windows automation using `pyautogui` and `botcity`. It automates desktop data entry tasks to showcase the capabilities of these tools.

## Features

- Automates repetitive desktop tasks.
- Uses `pyautogui` for GUI automation.
- Integrates with `botcity` for enhanced automation capabilities.

## Limitations

- The computer cannot be used while the automation is running, as it directly interacts with the GUI.
- The automation is unaware if the target window loses focus, which may cause unexpected behavior.
- Further improvements and tweaking are required for more robust and reliable automation.

## Requirements

- Python 3.7 or higher
- `pyautogui` library
- `botcity-framework-core` library

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/your-username/desktop-data-entry.git
    cd desktop-data-entry
    ```

2. Install dependencies:
    ```bash
    pip install pyautogui botcity-framework-core
    ```

## Usage

1. Run the script:
    ```bash
    python main.py
    ```

2. Follow the on-screen instructions to observe the automation in action.

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

## License

This project is licensed under the [MIT License](LICENSE).

## Acknowledgments

- [PyAutoGUI Documentation](https://pyautogui.readthedocs.io/)
- [BotCity Documentation](https://botcity.dev/)

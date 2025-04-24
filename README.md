# Desktop Data Entry Automation [WIP]

This project is a simple demonstration of Windows automation using `pyautogui` and `botcity`. It automates desktop data entry tasks to showcase the capabilities of these tools.

## Features

- Simulates adding text to notepad
- Created two classes that use pyautogui and botcity, just for contrast.
- Script will read json palceholder content and save to text files on desktop

## Limitations

- The computer cannot be used while the automation is running, as it directly interacts with the GUI.
- The automation is unaware if the target window loses focus, which may cause unexpected behavior.
- The automation may require an update of the resource files if the Windows theme or dpi is different.
- Further improvements and tweaking are required for more robust and reliable automation.

## Requirements

- Python 3.13 or higher
- `pyautogui` and `botcity-framework-core` library

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/Synout/desktop-automation-test.git
    cd desktop-data-entry
    ```

2. Install dependencies:
    ```bash
    pip install pyautogui botcity-framework-core
    ```

## Usage

1. Run the script:
    ```bash
    python notepad-auto.py
    ```

2. Follow the on-screen instructions to observe the automation in action.


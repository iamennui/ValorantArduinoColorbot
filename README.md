## DISCLAIMER

- **Cheat Detection**: This project was not aimed to be undetected and will never aim to do so.
- **Compatibility**: This software is designed for Arduino Leonardo boards only.
- **Responsibility**: This software is intended for educational purposes only. I am not responsible for any account bans, penalties, or any other consequences that may result from using this tool. Use it at your own risk and be aware of the potential implications.

## Setup Instructions

1. **Install Requirements**:
   - Install all necessary dependencies by running:
     ```bash
     pip install -r requirements.txt
     ```
     
2. **Spoof Arduino**:
   - Spoof your Arduino Leonardo board to your mouse's VID and PID by running:
     ```bash
     py spoofer.py
     ```

3. **Configure `settings.ini`**:
   - Adjust the settings in `settings.ini` according to your preferences, if you want to change keybinds you can find the values [here](https://learn.microsoft.com/windows/win32/inputdev/virtual-key-codes).

4. **In-Game Settings**:
   - Set your in-game sensitivity to **0.5**.
   - Change the enemy highlight color to **Purple**.
     
5. **Run the Colorbot**:
   - Execute the main script by running:
     ```bash
     py main.py
     ```

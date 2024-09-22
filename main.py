import pyautogui
import os
from colorbot import Colorbot
from settings import Settings

class Main:
    """
    The Main class initializes the application, sets up the necessary parameters, 
    and runs the Colorbot.
    """

    def __init__(self):
        """
        Initializes the Main class by setting up screen parameters and the Colorbot instance.

        Attributes:
            settings (Settings): The settings instance for reading configuration files.
            monitor (tuple): The screen resolution.
            center_x (int): The center X-coordinate of the screen.
            center_y (int): The center Y-coordinate of the screen.
            x_fov (int): The width of the capture area.
            y_fov (int): The height of the capture area.
            colorbot (Colorbot): The Colorbot instance for screen capturing and color detection.
        """
        self.settings = Settings()

        self.monitor = pyautogui.size()
        self.center_x, self.center_y = self.monitor.width // 2, self.monitor.height // 2
        self.x_fov = self.settings.get_int('Aimbot', 'xFov')
        self.y_fov = self.settings.get_int('Aimbot', 'yFov')

        self.colorbot = Colorbot(
            self.center_x - self.x_fov // 2, 
            self.center_y - self.y_fov // 2, 
            self.x_fov, 
            self.y_fov
        )

    def run(self):
        """
        Prints the application title and color settings, then starts the Colorbot.
        """
        os.system('cls')
        os.system('title github.com/iamennui/ValorantArduinoColorbot')
        print('Enemy Outline Color: Purple')
        self.colorbot.listen()

if __name__ == '__main__':
    Main().run()
import time
import threading
import serial
import serial.tools.list_ports
from settings import Settings

class Mouse:
    """
    The Mouse class is responsible for managing the connection to an Arduino-based mouse controller
    and sending movement commands via a serial port.

    Attributes:
        settings (Settings): An instance of the Settings class to retrieve configuration settings.
        serial_port (serial.Serial): The serial port connection to the Arduino.
        remainder_x (float): The accumulated remainder of x-axis movement.
        remainder_y (float): The accumulated remainder of y-axis movement.
    """
    
    def __init__(self):
        """
        Initializes the Mouse class by setting up the serial port connection to the Arduino
        and initializing the remainder attributes.
        """
        self.settings = Settings()
        self.lock = threading.Lock()
        self.serial_port = serial.Serial()
        self.serial_port.baudrate = 115200
        self.serial_port.timeout = 0
        self.serial_port.port = self.find_serial_port()
        self.remainder_x = 0.0
        self.remainder_y = 0.0
        try:
            self.serial_port.open()
        except serial.SerialException:
            print("Colorbot is already open or Arduino is being used by another app.\nExiting in 10 seconds...")
            time.sleep(10)
            exit()

    def find_serial_port(self):
        """
        Finds and returns the serial port connected to the Arduino based on the configuration settings.

        Returns:
            str: The device name of the connected serial port.

        Raises:
            SystemExit: If the specified Arduino COM port cannot be found.
        """
        com_port = self.settings.get('Settings', 'COM-Port')
        port = next((port for port in serial.tools.list_ports.comports() if com_port in port.description), None)
        if port is not None:
            return port.device
        else:
            print(f"Unable to detect your specified Arduino ({com_port}).\nPlease check its connection and the settings.ini file, then try again.\nExiting in 10 seconds...")
            time.sleep(10)
            exit()

    def move(self, x, y):
        """
        Sends a mouse movement command to the Arduino, handling fractional movements by storing remainders.

        Args:
            x (float): The movement along the x-axis.
            y (float): The movement along the y-axis.
        """
        # Add the remainder from the previous calculation
        x += self.remainder_x
        y += self.remainder_y

        # Round x and y, and calculate the new remainder
        move_x = int(x)
        move_y = int(y)
        self.remainder_x = x - move_x
        self.remainder_y = y - move_y

        if move_x != 0 or move_y != 0:
            with self.lock:
                self.serial_port.write(f'M{move_x},{move_y}\n'.encode())

    def click(self):
        """
        Sends a mouse click command to the Arduino.
        """
        with self.lock: 
            self.serial_port.write('C\n'.encode())
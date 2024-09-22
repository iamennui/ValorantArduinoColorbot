import time
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
    """
    
    def __init__(self):
        """
        Initializes the Mouse class by setting up the serial port connection to the Arduino.
        """
        self.settings = Settings()
        self.serial_port = serial.Serial()
        self.serial_port.baudrate = 115200
        self.serial_port.timeout = 0
        self.serial_port.port = self.find_serial_port()
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
        Sends a mouse movement command to the Arduino.

        Args:
            x (int): The movement along the x-axis.
            y (int): The movement along the y-axis.
        """
        self.serial_port.write(f'M{x},{y}\n'.encode())

    def click(self):
        """
        Sends a mouse click command to the Arduino.
        """
        self.serial_port.write('C\n'.encode())
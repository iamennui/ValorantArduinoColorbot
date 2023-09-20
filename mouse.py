import sys
import time
import serial
import serial.tools.list_ports
from settings import Settings

class Mouse:
    settings = Settings()
    
    def __init__(self):
        self.serial_port = serial.Serial()
        self.serial_port.baudrate = 115200
        self.serial_port.timeout = 0
        self.serial_port.port = self.find_serial_port()
        try:
            self.serial_port.open()
        except serial.SerialException:
            print('Colorbot is already open or Arduino is being used by another app.')
            print('Exiting...')
            time.sleep(10)
            sys.exit()

    def find_serial_port(self):
        com_port = self.settings.get('Settings', 'COM-Port')
        port = next((port for port in serial.tools.list_ports.comports() if com_port in port.description), None)
        if port is not None:
            return port.device
        else:
            print(f'Unable to detect your specified Arduino ({com_port}). Please check its connection & the COM-Port setting in \nsettings.ini file then try again.')
            print('Exiting...')
            time.sleep(10)
            sys.exit()

    def move(self, x, y):
        self.serial_port.write(f'M{x},{y}\n'.encode())
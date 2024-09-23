import os
import re
import time
import random
import requests
import zipfile
import subprocess
import win32com.client

class Spoofer:
    """
    The Spoofer class handles setting up the Arduino CLI, detecting connected mouse devices,
    configuring Arduino Leonardo board settings, and compiling/uploading the Arduino sketch.
    """

    SKETCH_FILE = "arduino/arduino.ino"
    BOARDS_TXT_PATH = os.path.expandvars("%LOCALAPPDATA%/Arduino15/packages/arduino/hardware/avr/1.8.6/boards.txt")

    def __init__(self):
        """
        Initializes the Spoofer class, setting up the Arduino CLI path.
        """
        self.arduino_cli_path = os.path.join(os.getcwd(), "arduino/arduino-cli.exe")

    def download_arduino_cli(self):
        """
        Downloads and extracts the Arduino CLI if it doesn't already exist.
        """
        # Create 'arduino' directory if it doesn't exist
        os.makedirs("arduino", exist_ok=True)

        # Skip download if Arduino CLI already exists
        if os.path.exists(self.arduino_cli_path):
            return

        # Download the Arduino CLI
        if not os.path.exists(os.path.join(os.getcwd(), "arduino/arduino-cli.zip")):
            print("Downloading Arduino CLI...")
            response = requests.get("https://downloads.arduino.cc/arduino-cli/arduino-cli_latest_Windows_64bit.zip", stream=True)
            with open("arduino/arduino-cli.zip", "wb") as fd:
                for chunk in response.iter_content(chunk_size=128):
                    fd.write(chunk)

        # Extract the Arduino CLI
        with zipfile.ZipFile("arduino/arduino-cli.zip", 'r') as zip_ref:
            zip_ref.extractall("./arduino/")

    def update_boards(self, vendor_id, product_id):
        """
        Updates the 'boards.txt' file to replace the VID and PID for the Arduino Leonardo board.
        
        Args:
            vendor_id (str): Vendor ID (VID) in hexadecimal format (e.g., '0x2341').
            product_id (str): Product ID (PID) in hexadecimal format (e.g., '0x8036').
        """
        # Read the 'boards.txt' file
        with open(self.BOARDS_TXT_PATH, 'r') as boards_file:
            board_config_lines = boards_file.readlines()

        # Generate a random name for the Arduino Leonardo board
        random_name = ''.join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=6))

        # Update the VID and PID for the Arduino Leonardo board
        for index, line in enumerate(board_config_lines):
            if line.startswith("leonardo.name="):
                board_config_lines[index] = f"leonardo.name={random_name}\n"
            elif line.startswith("leonardo.vid."):
                suffix = line.split("leonardo.vid.")[1].split("=")[0]
                board_config_lines[index] = f"leonardo.vid.{suffix}={vendor_id}\n"
            elif line.startswith("leonardo.pid."):
                suffix = line.split("leonardo.pid.")[1].split("=")[0]
                board_config_lines[index] = f"leonardo.pid.{suffix}={product_id}\n"
            elif line.startswith("leonardo.build.vid="):
                board_config_lines[index] = f"leonardo.build.vid={vendor_id}\n"
            elif line.startswith("leonardo.build.pid="):
                board_config_lines[index] = f"leonardo.build.pid={product_id}\n"
            elif line.startswith("leonardo.build.usb_product="):
                board_config_lines[index] = f"leonardo.build.usb_product=\"{random_name}\"\n"

        # Write the updated 'boards.txt' file
        with open(self.BOARDS_TXT_PATH, 'w') as boards_file:
            boards_file.writelines(board_config_lines)

    def detect_mouse_devices(self):
        """
        Detects all connected mouse devices using WMI and returns a list of tuples containing the device name, VID, and PID.

        Returns:
            list: A list of tuples where each tuple contains the device name, VID, and PID.
        """
        # Connect to the WMI service
        wmi_service = win32com.client.GetObject("winmgmts:")
        # Get all pointing devices
        mouse_devices = wmi_service.InstancesOf("Win32_PointingDevice")
        # List of detected mice
        detected_mice = []

        # Iterate through each pointing device
        for device in mouse_devices:
            # Get the device name
            device_name = device.Name
            # Extract the VID and PID from the PNPDeviceID
            id_match = re.search(r'VID_(\w+)&PID_(\w+)', device.PNPDeviceID)
            # Append the device name, VID, and PID to the list
            vid, pid = id_match.groups() if id_match else (None, None)
            detected_mice.append((device_name, vid, pid))

        # Return the list of detected mice
        return detected_mice

    def prompt_mouse_selection(self):
        """
        Prompts the user to select a mouse device and configures the Arduino Leonardo board settings accordingly.
        """
        # Detect all connected mouse devices
        detected_mice = self.detect_mouse_devices()

        # If no mouse devices are detected, exit after 10 seconds
        if not detected_mice:
            print("No mouse device found.\nExiting in 10 seconds...")
            time.sleep(10)
            exit()

        os.system('cls')

        # Filter and store valid USB input devices
        valid_mice = {}
        for device_name, vid, pid in detected_mice:
            if "USB Input Device" in device_name and vid and pid:
                device_key = (vid, pid)
                if device_key not in valid_mice:  # Avoid duplicates
                    valid_mice[device_key] = device_name

        # If no valid mouse devices are found, exit
        if not valid_mice:
            print("No valid USB Input Device found.\nExiting in 10 seconds...")
            time.sleep(10)
            exit()

        # Display the detected USB input devices
        for index, ((vid, pid), device_name) in enumerate(valid_mice.items(), 1):
            print(f"{index} → {device_name}\tVID: {vid}, PID: {pid}")

        # Prompt the user to select a mouse device 
        selected_mouse_index = int(input("\nSelect your mouse number: ")) - 1
        selected_device_key = list(valid_mice.keys())[selected_mouse_index]
        selected_vid, selected_pid = selected_device_key
        # Update the Arduino Leonardo board settings
        self.update_boards("0x" + selected_vid, "0x" + selected_pid)

    def install_avr_core(self):
        """
        Checks if the AVR core and Mouse library are already installed. If not, installs them using the Arduino CLI.
        """
        # Run the 'core list' command to check installed cores
        result = subprocess.run([self.arduino_cli_path, "core", "list"], capture_output=True, text=True)

        # Check if 'arduino:avr' with version '1.8.6' is in the output
        if "arduino:avr" not in result.stdout and not "1.8.6" in result.stdout:
            print("Installing AVR core 1.8.6...")
            os.system(f"{self.arduino_cli_path} core install arduino:avr@1.8.6 >NUL 2>&1")

        # Run the 'lib list' command to check installed libraries
        result = subprocess.run([self.arduino_cli_path, "lib", "list"], capture_output=True, text=True)

        # Check if 'Mouse' is in the output
        if "Mouse" not in result.stdout:
            print("Installing Mouse library...")
            os.system(f"{self.arduino_cli_path} lib install Mouse >NUL 2>&1")

    def compile_sketch(self):
        """
        Compiles the Arduino sketch using the Arduino CLI.
        """
        os.system('cls')
        
        # Prompt the user to enter the COM port of the Arduino Leonardo
        com_port = input("Enter your Arduino Leonardo COM-Port (e.g., COM3): ")

        print("Compiling sketch...")

        # Check if the sketch file exists
        if not os.path.exists(self.SKETCH_FILE):
            print(f"Error: Sketch file '{self.SKETCH_FILE}' not found!")
            return
        
        os.system(f"{self.arduino_cli_path} compile --fqbn arduino:avr:leonardo {self.SKETCH_FILE} >NUL 2>&1")
        self.upload_sketch(com_port)

    def upload_sketch(self, com_port):
        """
        Uploads the compiled sketch to the Arduino Leonardo board.
        """
        # Check if the sketch file exists
        if not os.path.exists(self.SKETCH_FILE):
            print(f"Error: Sketch file '{self.SKETCH_FILE}' not found!")
            return
        
        print("Uploading sketch to Arduino...")
        
        # Construct the upload command
        upload_command = f"{self.arduino_cli_path} upload -p {com_port} --fqbn arduino:avr:leonardo {self.SKETCH_FILE}"
        
        # Execute the upload command and capture the output
        exit_code = os.system(upload_command)
        
        # Check if the upload was successful
        if exit_code == 0:
            print("Spoof finished successfully, you can now use the colorbot!")
        else:
            # Provide additional troubleshooting information
            print(f"Failed to upload sketch. Error code: {exit_code}")
            print("Make sure the Arduino is connected and the COM port is correct.")

    def run(self):
        """
        Executes the entire process of setting up and configuring the Arduino Leonardo.
        """
        self.download_arduino_cli()
        self.install_avr_core()
        self.prompt_mouse_selection()
        self.compile_sketch()

if __name__ == "__main__":
    os.system('cls')
    os.system("title github.com/iamennui/ValorantArduinoColorbot")
    Spoofer().run()
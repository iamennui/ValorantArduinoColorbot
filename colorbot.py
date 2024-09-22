import cv2
import numpy as np
import win32api
import random
import threading
import time
from capture import Capture
from mouse import Mouse
from settings import Settings

class Colorbot:
    """
    The Colorbot class handles screen capturing, color detection, and mouse control.
    It supports aiming at specific colors on the screen and triggering actions when
    the color is within a defined region.
    """

    def __init__(self, x, y, x_fov, y_fov):
        """
        Initializes the Colorbot with screen capture parameters.

        Args:
            x (int): X-coordinate for the capture starting point.
            y (int): Y-coordinate for the capture starting point.
            x_fov (int): Width of the capture area.
            y_fov (int): Height of the capture area.
        """
        self.capturer = Capture(x, y, x_fov, y_fov)
        self.mouse = Mouse()
        self.settings = Settings()

        # Color detection settings (HSV)
        self.lower_color = np.array([150, 76,  123])
        self.upper_color = np.array([160, 197, 255])

        # Aimbot settings
        self.aim_enabled = self.settings.get_boolean('Aimbot', 'Enabled')
        self.aim_key = int(self.settings.get('Aimbot', 'toggleKey'), 16)
        self.x_speed = self.settings.get_float('Aimbot', 'xSpeed')
        self.y_speed = self.settings.get_float('Aimbot', 'ySpeed')
        self.x_fov = self.settings.get_int('Aimbot', 'xFov')
        self.y_fov = self.settings.get_int('Aimbot', 'yFov')
        self.target_offset = self.settings.get_float('Aimbot', 'targetOffset')

        # Triggerbot settings
        self.trigger_enabled = self.settings.get_boolean('Triggerbot', 'Enabled')
        self.trigger_key = int(self.settings.get('Triggerbot', 'toggleKey'), 16)
        self.min_delay = self.settings.get_int('Triggerbot', 'minDelay')
        self.max_delay = self.settings.get_int('Triggerbot', 'maxDelay')
        self.x_range = self.settings.get_int('Triggerbot', 'xRange')
        self.y_range = self.settings.get_int('Triggerbot', 'yRange')

        # Precomputed values
        self.kernel = np.ones((3, 3), np.uint8)
        self.screen_center = (self.x_fov // 2, self.y_fov // 2)

    def listen_aimbot(self):
        """
        Continuously listens for the aimbot key press and processes aiming.
        """
        while True:
            if win32api.GetAsyncKeyState(self.aim_key) < 0:
                self.process("move")
            time.sleep(0.01)  # Small sleep to prevent high CPU usage

    def listen_triggerbot(self):
        """
        Continuously listens for the triggerbot key press and processes clicking.
        """
        while True:
            if win32api.GetAsyncKeyState(self.trigger_key) < 0:
                self.process("click")
            time.sleep(0.01)  # Small sleep to prevent high CPU usage

    def listen(self):
        """
        Initializes listeners for both aimbot and triggerbot functionalities.
        """
        if self.aim_enabled:
            threading.Thread(target=self.listen_aimbot).start()
        if self.trigger_enabled:
            threading.Thread(target=self.listen_triggerbot).start()

    def process(self, action):
        """
        Processes the captured screen to detect the specified color and performs actions based on the detected target.

        Args:
            action (str): The action to perform, either "move" to move the mouse or "click" to trigger a click.
        """
        # Convert the captured screen to HSV color space
        hsv = cv2.cvtColor(self.capturer.get_screen(), cv2.COLOR_BGR2HSV)
        
        # Create a binary mask where detected colors are white, and everything else is black
        mask = cv2.inRange(hsv, self.lower_color, self.upper_color)
        
        # Dilate the mask to make detected regions more prominent
        dilated = cv2.dilate(mask, self.kernel, iterations=5)
        
        # Apply thresholding to get a binary image
        thresh = cv2.threshold(dilated, 60, 255, cv2.THRESH_BINARY)[1]
        
        # Find contours in the binary image
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Process the detected contours
        if contours:
            min_distance = float('inf')
            closest_center = None
            
            for contour in contours:
                # Find the contour closest to the center of the screen using moments
                moments = cv2.moments(contour)
                if moments['m00'] != 0:  # Avoid division by zero
                    center = (int(moments['m10'] / moments['m00']), int(moments['m01'] / moments['m00']))
                    distance = np.sqrt((center[0] - self.screen_center[0]) ** 2 + (center[1] - self.screen_center[1]) ** 2)

                    # Update the closest center if the distance is smaller
                    if distance < min_distance:
                        min_distance = distance
                        closest_center = center

            if closest_center is not None:
                # Get the coordinates of the closest center and apply target offset
                cX, cY = closest_center
                cY -= int(self.target_offset)

                if action == "move":
                    # Calculate the difference between the center of the screen and the detected target
                    x_diff = cX - self.screen_center[0]
                    y_diff = cY - self.screen_center[1]

                    # Move the mouse towards the target
                    self.mouse.move(self.x_speed * x_diff, self.y_speed * y_diff)

                elif action == "click":
                    # Check if the detected target is within the trigger range
                    if (abs(cX - self.screen_center[0]) <= self.x_range and
                        abs(cY - self.screen_center[1]) <= self.y_range):
                        # Random delay before triggering a click
                        time.sleep(random.uniform(self.min_delay / 1000.0, self.max_delay / 1000.0))
                        self.mouse.click()
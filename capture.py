import numpy as np
from mss import mss

class Capture:
    """
    The Capture class is responsible for capturing a specified region of the screen.
    """

    def __init__(self, x, y, x_fov, y_fov):
        """
        Initializes the Capture class with screen capture parameters.

        Args:
            x (int): X-coordinate for the capture starting point.
            y (int): Y-coordinate for the capture starting point.
            x_fov (int): Width of the capture area.
            y_fov (int): Height of the capture area.
        """
        self.monitor = {
            "top": y,
            "left": x,
            "width": x_fov,
            "height": y_fov
        }
        
    def get_screen(self):
        """
        Captures the screen based on the specified region and returns it as a numpy array.

        Returns:
            np.ndarray: The captured screen region as a numpy array.
        """
        with mss() as sct:
            screenshot = sct.grab(self.monitor)
            return np.array(screenshot)
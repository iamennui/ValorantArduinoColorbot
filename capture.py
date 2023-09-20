import numpy as np
from mss import mss

class Capture:
    def __init__(self, x, y, xfov, yfov):
        self.mss = mss()
        self.monitor = {'top': y, 'left': x, 'width': xfov, 'height': yfov}
        self.xfov = xfov
        self.yfov = yfov

    def get_screen(self):
        screenshot = self.mss.grab(self.monitor)
        return np.array(screenshot)

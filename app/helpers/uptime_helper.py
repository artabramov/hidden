"""
The module provides functionality for tracking the app's uptime.
"""

import time


class Uptime:
    """
    Tracks the uptime of the app by recording the start time and
    providing a method to calculate the elapsed time since start.
    """
    def __init__(self):
        self.started_time = time.time()

    def get_uptime(self):
        """
        Returns the uptime in seconds as an integer by calculating the
        difference between the current time and the recorded start time.
        """
        return int(time.time() - self.started_time)

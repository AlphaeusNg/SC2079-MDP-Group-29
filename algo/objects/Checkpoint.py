from algo import utils

class Checkpoint:
    def __init__(self, x: float, y: float, theta: float) -> None:
        """Checkpoint constructor

        Args:
            x (float): x coordinate of checkpoint
            y (float): y coordinate of checkpoint
            theta (float): desired angle when reaching checkpoint

        Parameters:
            completed (bool): whether checkpoint has been reached
        """

        self.x = x
        self.y = y
        self.theta = theta
        self.completed = False

        
import numpy as np
from algo import utils

class Obstacle:
    def __init__(self, x_g: int, y_g: int, facing: str) -> None:
        """Obstacle constructor

        Args:
            x_g (int): x coordinate of obstacle (bottom left grid)
            y_g (int): y coordinate of obstacle (bottom left grid)
            facing (str): {'N', 'S', 'E', 'W'} direction of image

        Parameters:
            theta (float): direction of image in radians
        """

        self.x_g = x_g
        self.y_g = y_g
        self.facing = facing
        self.theta = utils.facing_to_rad(facing)
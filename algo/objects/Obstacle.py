import numpy as np

class Obstacle:
    def __init__(self, x_g: int, y_g: int, face: str) -> None:
        """Obstacle constructor

        Args:
            x_g (int): x coordinate of obstacle (grid)
            y_g (int): y coordinate of obstacle (grid)
            face (str): {'N', 'S', 'E', 'W'} direction of image

        Parameters:
            theta (float): direction of image in radians
        """

        self.x_g = x_g
        self.y_g = y_g
        self.face = face
        if face == 'E':
            self.theta = 0
        elif face == 'N':
            self.theta = np.pi/2
        elif face == 'W':
            self.theta = np.pi
        elif face == 'S':
            self.theta = -np.pi/2
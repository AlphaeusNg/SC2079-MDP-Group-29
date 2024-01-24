from algo import utils

class Checkpoint:
    def __init__(self, x_g: float, y_g: float, theta: float) -> None:
        """Checkpoint constructor

        Args:
            x_g (float): x (grid vertices) coordinate of checkpoint
            y_g (float): y (grid vertices) coordinate of checkpoint
            theta (float): desired angle when reaching checkpoint

        Parameters:
            completed (bool): whether checkpoint has been reached
        """

        self.x_g = x_g
        self.y_g = y_g
        self.x = utils.grid_to_coords(x_g)
        self.y = utils.grid_to_coords(y_g)
        self.theta = theta
        self.completed = False

        
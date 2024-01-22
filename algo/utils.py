import numpy as np

def grid_to_coords(x_g: int, y_g: int):
    """ Convert grid number to continuous coordinates (assuming position in middle of grid)
    Args:
        x_g (int): x coordinate (grid)
        y_g (int): y coordinate (grid)

    Returns:
        x (float): x coordinate (continuous)
        y (float): y coordinate (continuous)
    """

    return x_g*10 + 5, y_g*10 + 5

def coords_to_grid(x: float, y: float) -> (int, int):
    """Convert continuous coordinates to grid number

    Args:
        x (float): x coordinate (continuous)
        y (float): y coordinate (continuous)

    Returns:
        x_g (int): x coordinate (grid)
        y_g (int): y coordinate (grid)
    """
    return x//10, y//10
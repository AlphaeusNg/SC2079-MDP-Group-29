import numpy as np

def grid_to_coords(x_g: int, y_g: int):
    """ Convert grid vertices coordinates to continuous coordinates

    Args:
        x_g (int): x coordinate (grid vertices)
        y_g (int): y coordinate (grid vertices)

    Returns:
        x (float): x coordinate (continuous)
        y (float): y coordinate (continuous)
    """

    return x_g*5, y_g*5

def coords_to_grid(x: float, y: float) -> (int, int):
    """Convert continuous coordinates to grid vertices coordinates

    Args:
        x (float): x coordinate (continuous)
        y (float): y coordinate (continuous)

    Returns:
        x_g (int): x coordinate (grid vertices)
        y_g (int): y coordinate (grid vertices)
    """
    return x//5, y//5

def facing_to_rad(facing: str) -> float:
    """Convert {N, S, E, W} to radians

    Args:
        facing (str): direction in {N, S, E, W}

    Returns:
        float: direction in radians
    """

    assert facing in ['N', 'S', 'E', 'W']

    if facing == 'E':
        return 0
    elif facing == 'N':
        return np.pi/2
    elif facing == 'W':
        return np.pi
    elif facing == 'S':
        return -np.pi/2
    
def rad_to_facing(rad: float) -> str:
    """Convert radians to {N, S, E, W}

    Args:
        rad (float): direction in radians

    Returns:
        str: direction in {N, S, E, W}
    """

    assert abs(rad) <= np.pi

    if np.pi/4 < rad <= 3*np.pi/4:
        return 'N'
    elif -np.pi/4 < rad <= np.pi/4:
        return 'E'
    elif -3*np.pi/4 < rad <= -np.pi/4:
        return 'S'
    else:
        return 'W'
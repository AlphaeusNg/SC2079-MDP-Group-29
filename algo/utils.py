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
    
def coords_to_pixelcoords(x_g:int, y_g:int, map_x0=50, map_y0=50, map_width=800, map_height=800):
    """Convert grid numbers to pixel coordinates

    Args:
        x_g (int): x coordinate of obstacle (bottom left grid)
        y_g (int): y coordinate of obstacle (bottom left grid)
        map_x0 (int, optional): x pixel coordinate of map (top left) in pixels. Defaults to 50.
        map_y0 (int, optional): y pixel coordinate of map (top left) in pixels. Defaults to 50.
        map_width (int, optional): map width in pixels. Defaults to 800.
        map_height (int, optional): map height in pixels. Defaults to 800.
    """
    x, y = grid_to_coords(x_g, y_g)
    new_x = map_x0 + x*map_width/200
    new_y = map_y0 + map_height - y*map_height/200

    return new_x, new_y
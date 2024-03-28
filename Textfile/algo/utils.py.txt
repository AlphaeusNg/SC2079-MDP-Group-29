import numpy as np
import algo.constants as c
import math

def grid_to_coords(x_g: int, y_g: int):
    """ Convert grid vertices coordinates to continuous coordinates

    Args:
        x_g (int): x coordinate (grid vertices)
        y_g (int): y coordinate (grid vertices)

    Returns:
        x (float): x coordinate (continuous)
        y (float): y coordinate (continuous)
    """

    return x_g*200/c.GRID_SIZE, y_g*200/c.GRID_SIZE

def coords_to_grid(x: float, y: float):
    """Convert continuous coordinates to grid vertices coordinates

    Args:
        x (float): x coordinate (continuous)
        y (float): y coordinate (continuous)

    Returns:
        x_g (int): x coordinate (grid vertices)
        y_g (int): y coordinate (grid vertices)
    """
    return int(x//(200/c.GRID_SIZE)), int(y//(200/c.GRID_SIZE))

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
    
def coords_to_pixelcoords(x_g:int=0, y_g:int=0, x: float=None, y: float=None, map_x0=50, map_y0=50, map_width=800, map_height=800):
    """Convert grid numbers to pixel coordinates

    Args:
        x_g (int): x coordinate of obstacle (bottom left grid)
        y_g (int): y coordinate of obstacle (bottom left grid)
        map_x0 (int, optional): x pixel coordinate of map (top left) in pixels. Defaults to 50.
        map_y0 (int, optional): y pixel coordinate of map (top left) in pixels. Defaults to 50.
        map_width (int, optional): map width in pixels. Defaults to 800.
        map_height (int, optional): map height in pixels. Defaults to 800.
    """
    if x == None:
        x, y = grid_to_coords(x_g, y_g)

    new_x = map_x0 + x*map_width/200
    new_y = map_y0 + map_height - y*map_height/200

    return int(new_x), int(new_y)

def l1 (x1: float, y1: float, x2: float, y2: float) -> float:
    """L1 distance between 2 points in R2
    """

    return abs(x1 - x2) + abs(y1 - y2)

def l2 (x1: float, y1: float, x2: float, y2: float) -> float:
    """L2 distance between 2 points in R2
    """

    return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)

def diag_dist(x1: float, y1: float, x2: float, y2: float) -> float:
    dx = abs(x1 - x2)
    dy = abs(y1 - y2)
    return math.sqrt(2*min(dx, dy)**2) + abs(dx - dy)

def normalise_theta(theta: float):
    revolutions = int((theta + np.sign(theta) * np.pi) / (2 * np.pi))

    p1 = truncated_remainder(theta + np.sign(theta) * np.pi, 2 * np.pi)
    p2 = (np.sign(np.sign(theta)
                  + 2 * (np.sign(math.fabs((truncated_remainder(theta + np.pi, 2 * np.pi))
                                      / (2 * np.pi))) - 1))) * np.pi

    output_angle = p1 - p2

    return output_angle

def truncated_remainder(dividend, divisor):
    divided_number = dividend / divisor
    divided_number = \
        -int(-divided_number) if divided_number < 0 else int(divided_number)

    remainder = dividend - divisor * divided_number

    return remainder

def M(theta):
    """
    Return the angle phi = theta mod (2 pi) such that -pi <= theta < pi.
    """
    theta = theta % (2*math.pi)
    if theta < -math.pi: return theta + 2*math.pi
    if theta >= math.pi: return theta - 2*math.pi
    return theta

def R(x, y):
    """
    Return the polar coordinates (r, theta) of the point (x, y).
    """
    r = math.sqrt(x*x + y*y)
    theta = math.atan2(y, x)
    return r, theta

def change_of_basis(p1, p2):
    """
    Given p1 = (x1, y1, theta1) and p2 = (x2, y2, theta2) represented in a
    coordinate system with origin (0, 0) and rotation 0 (in degrees), return
    the position and rotation of p2 in the coordinate system which origin
    (x1, y1) and rotation theta1.
    """
    theta1 = deg_to_rad(p1[2])
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    new_x = dx * math.cos(theta1) + dy * math.sin(theta1)
    new_y = -dx * math.sin(theta1) + dy * math.cos(theta1)
    new_theta = p2[2] - p1[2]
    return new_x, new_y, new_theta

def deg_to_rad(deg):
    return math.pi * deg / 180
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__ + '\..')))

from objects.Obstacle import Obstacle
import utils
import numpy as np
from typing import List
import matplotlib.pyplot as plt
from simulation.testing import get_maps

class OccupancyMap:
    def __init__(self, obstacles: List[Obstacle]=[]) -> None:
        """OccupancyMap Constructor

        Args:
            obstacles (List[Obstacle]): list of obstacle objects

        Parameters:
            xmin (float): left border
            xmax (float): right border
            ymin (float): bottom border
            ymax (float): top border
            start_g ((int, int)): starting grid numbers
            grid_vertices (np.array): 41x41 np array grid vertices for path planning (agent travels along grid lines)
            grid_display (np.array): 40x40 np array grid representing map for display purposes
            checkpoints (List[Checkpoint]): list of checkpoint objects
        """

        assert len(obstacles) <= 8      # ensure list has at most 8 obstacles
        self.xmin, self.xmax, self.ymin, self.ymax = 0., 200., 0., 200.
        self.obstacles = []

        self.occupancy_grid = np.zeros((40, 40))  # 40x40 occupancy grid
        
        self.add_obstacles_to_grids(obstacles)

    def add_obstacles_to_grids(self, obstacles: List[Obstacle]) -> None:
        """Function to update grids and checkpoints from list of obstacles

        Args:
            obstacles (List[Obstacle]): list of obstacle objects to add to the map
        """
        assert len(self.obstacles) + len(obstacles) <= 8    # ensure list has at most 8 obstacles

        self.obstacles += obstacles     # add obstacles to obstacle list

        for obstacle in obstacles:
            # add obstacle to grid vertices (including virtual wall)
            i_start = max(obstacle.x_g - 3, 0)      # 0: first index
            i_end = min(obstacle.x_g + 4, 39)       # 39: last index
            j_start = max(obstacle.y_g - 3, 0)      # 0: first index
            j_end = min(obstacle.y_g + 4, 39)       # 39: last index
            self.occupancy_grid[i_start:i_end+1, j_start:j_end+1] = 1

        self.occupancy_grid[:2, :] = 1
        self.occupancy_grid[-2:, :] = 1
        self.occupancy_grid[:, :2] = 1
        self.occupancy_grid[:, -2:] = 1

    def collide_with_point(self, x, y):
        x_g, y_g = utils.coords_to_grid(x, y)
        return self.occupancy_grid[x_g, y_g]

if __name__ == '__main__':
    maps = get_maps()
    map = OccupancyMap(maps[0])

    print(map.collide_with_point(150, 150))

    np.set_printoptions(threshold=sys.maxsize)
    print(map.occupancy_grid)

    plt.imshow(map.occupancy_grid, interpolation='none', origin='lower')
    plt.show()
    
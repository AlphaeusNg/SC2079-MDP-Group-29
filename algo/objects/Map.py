from algo.objects.Obstacle import Obstacle
from algo.objects.Agent import Agent
from algo.objects.Checkpoint import Checkpoint
import numpy as np
from typing import List

class Map:
    def __init__(self, obstacles: List[Obstacle], agent:Agent) -> None:
        """Map Constructor

        Args:
            obstacles (List[Obstacle]): list of obstacle objects
            agent (Agent): agent object

        Parameters:
            xmin (float): left border
            xmax (float): right border
            ymin (float): bottom border
            ymax (float): top border
            start_g ((int, int)): starting grid numbers
            grid (np.array): 40x40 np array grid representing map, includes virtual walls used for path planning
            grid_display (np.array): 40x40 np array grid representing map for display purposes
            checkpoints (List[Checkpoint]): list of checkpoint objects
        """

        assert len(obstacles) <= 8      # ensure list has at most 8 obstacles
        self.xmin, self.xmax, self.ymin, self.ymax = 0., 200., 0., 200.
        self.start_g = (0,0)
        self.obstacles = []
        self.agent = agent

        self.grid = np.ones((40, 40))           # 40x40 grid for computation
        self.grid_display = np.ones((40, 40))   # 40x40 grid for display
        self.checkpoints = []
        
        self.add_obstacles_to_grids(obstacles)

    def add_obstacles_to_grids(self, obstacles: List[Obstacle]) -> None:
        """Function to update grids and checkpoints from list of obstacles

        Args:
            obstacles (List[Obstacle]): list of obstacle objects to add to the map
        """
        assert len(self.obstacles) + len(obstacles) <= 8    # ensure list has at most 8 obstacles

        self.obstacles += obstacles     # add obstacles to obstacle list

        for obstacle in obstacles:
            # add obstacle to grid display
            i_start = obstacle.x_g
            i_end = min(i_start + 1, 39)          # 39: last index
            j_start = obstacle.y_g
            j_end = min(j_start + 1, 39)          # 39: last index
            for i in range(i_start, i_end + 1):
                for j in range(j_start, j_end + 1):
                    self.grid_display[i, j] = 0
            
            # add obstacle to grid
            i_start = max(obstacle.x_g - 3, 0)      # 0: first index
            i_end = min(obstacle.x_g + 4, 39)       # 39: last index
            j_start = max(obstacle.y_g - 3, 0)      # 0: first index
            j_end = min(obstacle.y_g + 4, 39)       # 39: last index
            for i in range(i_start, i_end + 1):
                for j in range(j_start, j_end + 1):
                    self.grid[i, j] = 0
            
            # add checkpoints
            self.checkpoints.append(Checkpoint(obstacle.x_g, obstacle.y_g))

            
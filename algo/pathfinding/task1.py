from pathcommands import *
from hamiltonian import Hamiltonian
from hybrid_astar import HybridAStar
from objects.OccupancyMap import OccupancyMap

class task1():
    def __init__(self, message):
        self.checkpoints = []
        self.paths = []
        self.commands = []
        obstacles = []

        L=25*np.pi/4/5
        minR=25

        for obstacle in message["data"]["obstacles"]:
            obstacles.append(Obstacle(obstacle["x"] * 2, obstacle["y"] * 2, obstacle["dir"]))

        map = OccupancyMap(obstacles)
        tsp = Hamiltonian(obstacles, 15, 15, np.pi/2, -np.pi/2, 'euclidean', minR)
        current_pos = tsp.start
        checkpoints = tsp.find_nearest_neighbor_path()
        for idx, checkpoint in enumerate(checkpoints):
            algo = HybridAStar(map, current_pos[0], current_pos[1], current_pos[2], checkpoint[0], checkpoint[1], checkpoint[2], 10, 10, L, minR, 'euclidean', False, 24)
            path, pathHistory = algo.find_path()
            self.paths.append(path)
            current_pos = (path[-1].x, path[-1].y, path[-1].theta)
            commands, pathDisplay = construct_path(path, L, minR)
            self.commands.append(commands)
    
    def get_command_to_next_obstacle(self):
        nextCommand = self.commands.pop()
        return construct_json(nextCommand)
    
    def has_task_ended(self):
        return self.commands.empty()

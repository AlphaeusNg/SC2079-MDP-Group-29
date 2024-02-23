from algo.pathfinding.pathcommands import *
from algo.pathfinding.hamiltonian import Hamiltonian
from algo.pathfinding.hybrid_astar import HybridAStar
from algo.objects.OccupancyMap import OccupancyMap

class task1():
    def __init__(self):
        self.checkpoints = []
        self.paths = []
        self.commands = []
        self.android = []
        
    def generate_path(self, message):
        obstacles = []
        L=25*np.pi/4/5
        minR=25

        for obstacle in message["data"]["obstacles"]:
            if obstacle["dir"] == "N":
                obstacle["dir"] = "S"
            if obstacle["dir"] == "S":
                obstacle["dir"] = "N"
            if obstacle["dir"] == "W":
                obstacle["dir"] = "E"
            if obstacle["dir"] == "E":
                obstacle["dir"] = "W"
            obstacles.append(Obstacle(obstacle["x"] * 2, obstacle["y"] * 2, obstacle["dir"]))

        map = OccupancyMap(obstacles)
        tsp = Hamiltonian(obstacles, 15, 15, np.pi/2, -np.pi/2, 'euclidean', minR) # N:np.pi/2 
        current_pos = tsp.start
        checkpoints = tsp.find_nearest_neighbor_path()
        for idx, checkpoint in enumerate(checkpoints):
            algo = HybridAStar(map=map, 
                           x_0=current_pos[0], y_0=current_pos[1], theta_0=current_pos[2], 
                           x_f=checkpoint[0], y_f=checkpoint[1], 
                           theta_f=checkpoint[2], steeringChangeCost=10, gearChangeCost=10, 
                           L=L, minR=minR, heuristic='euclidean', simulate=False, thetaBins=24)
            path, pathHistory = algo.find_path()
            self.paths.append(path)
            current_pos = (path[-1].x, path[-1].y, path[-1].theta)
            commands, pathDisplay = construct_path(path, L, minR)
            self.commands.append(commands)
            self.android.append(pathDisplay)
    
    def get_command_to_next_obstacle(self):
        nextCommand = self.commands.pop(0)
        nextPath = self.android.pop(0)
        return construct_json(nextCommand, nextPath)

    
    def has_task_ended(self):
        return not self.commands

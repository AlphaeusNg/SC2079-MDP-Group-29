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
        self.obstacleID = []
        
    def generate_path(self, message):
        obstacles = []
        L=26.5*np.pi/4/5
        minR=26.5

        for obstacle in message["data"]["obstacles"]:
            obsDIR = obstacle["dir"]
            if obsDIR == "N":
                invertObs = "S"
            elif obsDIR == "S":
                invertObs = "N"
            elif obsDIR == "W":
                invertObs = "E"
            elif obsDIR == "E":
                invertObs = "W"
            obstacles.append(Obstacle(obstacle["x"] * 2, obstacle["y"] * 2, invertObs, int(obstacle["id"])))

        map = OccupancyMap(obstacles)
        tsp = Hamiltonian(obstacles, 5, 15, 0, -np.pi/2, 'euclidean', minR) # 3rd element: (N: np.pi/2, E: 0)
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
            commands, pathDisplay = construct_path_2(path, L, minR)
            self.commands.append(commands)
            self.android.append(pathDisplay)
            self.obstacleID.append(checkpoint[3])
            print_path(path)
        
    
    def get_command_to_next_obstacle(self):
        nextCommand = self.commands.pop(0)
        nextPath = self.android.pop(0)
        return construct_json(nextCommand, nextPath)

    def get_obstacle_id(self):
        obstacle_id = self.obstacleID.pop(0)
        return obstacle_id
    
    def has_task_ended(self):
        return not self.commands


if __name__ == "__main__":
    message = {"type": "START_TASK", "data": {"task": "EXPLORATION", "robot": {"id": "R", "x": 1, "y": 1, "dir": 'N'},
                                               "obstacles": [{"id": "00", "x": 8, "y": 5, "dir": 'S'},
                                                             {"id": "01", "x": 10, "y": 17, "dir": 'W'},
                                                             {"id": "02", "x": 15, "y": 10, "dir": 'N'}]}}
    main = task1()
    main.generate_path(message)
    while not main.has_task_ended():
        print(main.get_command_to_next_obstacle())
        print("ID: " + str(main.get_obstacle_id()))

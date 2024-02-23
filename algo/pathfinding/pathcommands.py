import numpy as np
from algo.enumerations import Gear, Steering
from algo.objects.Obstacle import Obstacle
from algo.pathfinding.hamiltonian import Hamiltonian
from algo.pathfinding.hybrid_astar import HybridAStar
import algo.objects.OccupancyMap as om


def print_path(path):
    for node in path:
        print(
            f"Current Node (x:{node.x:.2f}, y: {node.y:.2f}, " + f"theta: {node.theta * 180 / np.pi:.2f}), Action: {node.prevAction}")


def distance(prev, node):
    return np.sqrt((node.x - prev.x) ** 2 + (node.y - prev.y) ** 2)


def construct_path(path, L, Radius):
    LF, SF, RF, LB, SB, RB = 0, 0, 0, 0, 0, 0
    approx = 10
    command = []
    droid = []
    prev = path[0]
    dis = 0
    for node in path:
        droid.append([round(node.x / approx)-1, round(node.y / approx)-1])
        dis += distance(prev, node)
        if node.prevAction == (Gear.FORWARD, Steering.LEFT):
            LF += 1
        else:
            if LF >= 1:
                LF *= (L / (2 * np.pi * Radius)) * 360
                command.append(f"LF{int(LF):03d}")
                command.append(f"SF{int(dis):03d}")
                LF = 0
                dis = 0
        # Gear.FORWARD + Steering.STRAIGHT
        if node.prevAction == (Gear.FORWARD, Steering.STRAIGHT):
            SF += 1
        else:
            if SF >= 1:
                SF *= L
                command.append(f"SF{int(SF):03d}")
                SF = 0
                dis = 0
        # Gear.FORWARD + Steering.RIGHT
        if node.prevAction == (Gear.FORWARD, Steering.RIGHT):
            RF += 1
        else:
            if RF >= 1:
                RF *= (L / (2 * np.pi * Radius)) * 360
                command.append(f"RF{int(RF):03d}")
                command.append(f"SF{int(dis):03d}")
                RF = 0
                dis = 0
        # Gear.REVERSE + Steering.LEFT
        if node.prevAction == (Gear.REVERSE, Steering.LEFT):
            LB += 1
        else:
            if LB >= 1:
                LB *= (L / (2 * np.pi * Radius)) * 360
                command.append(f"LB{int(LB):03d}")
                command.append(f"SB{int(dis):03d}")
                LB = 0
                dis = 0
        # Gear.REVERSE + Steering.STRAIGHT
        if node.prevAction == (Gear.REVERSE, Steering.STRAIGHT):
            SB += 1
        else:
            if SB >= 1:
                SB *= L
                command.append(f"SB{int(SB):03d}")
                SB = 0
                dis = 0
        # Gear.REVERSE + Steering.RIGHT
        if node.prevAction == (Gear.REVERSE, Steering.RIGHT):
            RB += 1
        else:
            if RB >= 1:
                RB *= (L / (2 * np.pi * Radius)) * 360
                command.append(f"RB{int(RB):03d}")
                command.append(f"SB{int(dis):03d}")
                RB = 0
                dis = 0
        prev = node

    if LF >= 1:
        LF *= (L / (2 * np.pi * Radius)) * 360
        command.append(f"LF{int(LF):03d}")
        command.append(f"SF{int(dis):03d}")
    if SF >= 1:
        SF *= L
        command.append(f"SF{int(SF):03d}")
    if RF >= 1:
        RF *= (L / (2 * np.pi * Radius)) * 360
        command.append(f"RF{int(RF):03d}")
        command.append(f"SF{int(dis):03d}")
    if LB >= 1:
        LB *= (L / (2 * np.pi * Radius)) * 360
        command.append(f"LB{int(LB):03d}")
        command.append(f"SB{int(dis):03d}")
    if SB >= 1:
        SB *= L
        command.append(f"SB{int(SB):03d}")
    if RB >= 1:
        RB *= (L / (2 * np.pi * Radius)) * 360
        command.append(f"RB{int(RB):03d}")
        command.append(f"SB{int(dis):03d}")
    

    print(command)
    print(droid)
    return command, droid


def construct_path_2(path, L, Radius):
    commands = []
    gridPath = []
    unitDist = L
    unitAngle = (L / (2 * np.pi * Radius)) * 360

    prevGear = path[0].prevAction[0]
    prevSteering = path[0].prevAction[1]
    sameCommandCount = 1
    gridPath.append([round(path[0].x / 10), round(path[0].y / 10)])

    for pathElement in path[1:]:
        curX = round(pathElement.x / 10)
        curY = round(pathElement.y / 10)

        if curX != gridPath[-1][0] or curY != gridPath[-1][1]:
            gridPath.append([curX, curY])

        gear = pathElement.prevAction[0]
        steering = pathElement.prevAction[1]

        if gear == prevGear and steering == prevSteering:
            sameCommandCount += 1
            continue
        
        else:
            if steering == Steering.STRAIGHT:
                commands.append(f"S{"F" if gear == Gear.FORWARD else "B"}{int(sameCommandCount*unitDist):03d}")
            else:
                commands.append(f"{"L" if steering == Steering.LEFT else "R"}{"F" if gear == Gear.FORWARD else "B"}{int(sameCommandCount*unitAngle):03d}")
            
            sameCommandCount = 1
            prevGear = gear
            prevSteering = steering

    return commands, gridPath

def construct_json(command, path):
    json_file = {
        "type": "NAVIGATION",
        "data":
            {
                "commands": command,
                "path": path
            }
    }
    return json_file


def call_algo(message, L=25*np.pi/4/5, minR=25):
    obstacles = []
    full_commands = []
    full_path = []
    data_obstacles = message["data"]["obstacles"]
    for obstacle in data_obstacles:
        if obstacle["dir"] == "N":
            obstacle["dir"] = "S"
        if obstacle["dir"] == "S":
            obstacle["dir"] = "N"
        if obstacle["dir"] == "W":
            obstacle["dir"] = "E"
        if obstacle["dir"] == "E":
            obstacle["dir"] = "W"
        obstacles.append(Obstacle(obstacle["x"] * 2, obstacle["y"] * 2, obstacle["dir"]))
    # Run algo
    map = om.OccupancyMap(obstacles)
    tsp = Hamiltonian(obstacles, 15, 15, np.pi/2, -np.pi/2, 'euclidean', minR)
    current_pos = tsp.start
    checkpoints = tsp.find_brute_force_path()
    for idx, checkpoint in enumerate(checkpoints):
        # (self, map: OccupancyMap, x_0: float=15, y_0: float=10, theta_0: float=np.pi/2, 
        #          x_f: float=15, y_f: float=180, theta_f: float=np.pi/2, theta_offset: float=0, steeringChangeCost=10, gearChangeCost=20,
        #             L: float=5, minR: float=25, heuristic: str='hybriddiag', simulate: bool=False, thetaBins=24)
        algo = HybridAStar(map=map, 
                           x_0=current_pos[0], y_0=current_pos[1], theta_0=current_pos[2], 
                           x_f=checkpoint[0], y_f=checkpoint[1], 
                           theta_f=checkpoint[2], steeringChangeCost=10, gearChangeCost=10, 
                           L=L, minR=minR, heuristic='euclidean', simulate=False, thetaBins=24)
        path, pathHistory = algo.find_path()
        print_path(path)
        current_pos = (path[-1].x, path[-1].y, path[-1].theta)
        commands, droid = construct_path(path, L, minR)
        full_commands.extend(commands)
        full_path.extend(droid)
    # Convert to json
    json_file = construct_json(full_commands, full_path)
    return json_file


if __name__ == "__main__":
    message = {"type": "START_TASK", "data": {"task": "EXPLORATION", "robot": {"id": "R", "x": 1, "y": 1, "dir": 'N'},
                                               "obstacles": [{"id": "00", "x": 8, "y": 5, "dir": 'S'},
                                                             {"id": "01", "x": 10, "y": 17, "dir": 'W'}]}}
    print(call_algo(message))

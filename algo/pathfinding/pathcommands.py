import numpy as np
from enumerations import Gear, Steering
from objects.Obstacle import Obstacle
from pathfinding.hamiltonian import Hamiltonian
from pathfinding.hybrid_astar import HybridAStar
import algo.objects.OccupancyMap as om


def print_path(path):
    for node in path:
        print(
            f"Current Node (x:{node.x:.2f}, y: {node.y:.2f}, " + f"theta: {node.theta * 180 / np.pi:.2f}), Action: {node.prevAction}")


def construct_path(path, L, Radius):
    LF, SF, RF, LR, SB, RB = 0, 0, 0, 0, 0, 0
    approx = 10
    command = []
    droid = []
    for node in path:
        droid.append([round(node.x / approx), round(node.y / approx)])
        if node.prevAction == (Gear.FORWARD, Steering.LEFT):
            LF += 1
        else:
            if LF >= 1:
                LF *= (L / (2 * np.pi * Radius)) * 360
                command.append(f"LF{int(LF):03d}")
                LF = 0
        # Gear.FORWARD + Steering.STRAIGHT
        if node.prevAction == (Gear.FORWARD, Steering.STRAIGHT):
            SF += 1
        else:
            if SF >= 1:
                SF *= L
                command.append(f"SF{int(SF):03d}")
                SF = 0
        # Gear.FORWARD + Steering.RIGHT
        if node.prevAction == (Gear.FORWARD, Steering.RIGHT):
            RF += 1
        else:
            if RF >= 1:
                RF *= (L / (2 * np.pi * Radius)) * 360
                command.append(f"RF{int(RF):03d}")
                RF = 0
        # Gear.REVERSE + Steering.LEFT
        if node.prevAction == (Gear.REVERSE, Steering.LEFT):
            LR += 1
        else:
            if LR >= 1:
                LR *= (L / (2 * np.pi * Radius)) * 360
                command.append(f"LR{int(LR):03d}")
                LR = 0
        # Gear.REVERSE + Steering.STRAIGHT
        if node.prevAction == (Gear.REVERSE, Steering.STRAIGHT):
            SB += 1
        else:
            if SB >= 1:
                SB *= L
                command.append(f"SB{int(SB):03d}")
                SB = 0
        # Gear.REVERSE + Steering.RIGHT
        if node.prevAction == (Gear.REVERSE, Steering.RIGHT):
            RB += 1
        else:
            if RB >= 1:
                RB *= (L / (2 * np.pi * Radius)) * 360
                command.append(f"RB{int(RB):03d}")
                RB = 0

    return command, droid


def construct_json(command):
    json_file = {
        "type": "NAVIGATION",
        "data": command
        # "path": path
    }
    return json_file


def call_algo(message, L=25*np.pi/4/5, minR=25):
    obstacles = []
    full_commands = []
    data_obstacles = message["data"]["obstacles"]
    for obstacle in data_obstacles:
        obstacles.append(Obstacle(obstacle["x"] * 2, obstacle["y"] * 2, obstacle["dir"]))
    # Run algo
    map = om.OccupancyMap(obstacles)
    tsp = Hamiltonian(obstacles, 15, 15, np.pi/2, -np.pi/2, 'euclidean', minR)
    current_pos = tsp.start
    checkpoints = tsp.find_brute_force_path()
    for idx, checkpoint in enumerate(checkpoints):
        algo = HybridAStar(map, current_pos[0], current_pos[1], current_pos[2], checkpoint[0], checkpoint[1], checkpoint[2], 10, 10, L, minR, 'euclidean', False, 24)
        path, pathHistory = algo.find_path()
        print_path(path)
        current_pos = (path[-1].x, path[-1].y, path[-1].theta)
        commands = construct_path(path, L, minR)
        full_commands.extend(commands)
    # Convert to json
    json_file = construct_json(full_commands)
    return json_file


if __name__ == "__main__":
    message = {"type": "START_TASK", "data": {"task": "EXPLORATION", "robot": {"id": "R", "x": 1, "y": 1, "dir": 'N'},
                                               "obstacles": [{"id": "00", "x": 8, "y": 5, "dir": 'S'},
                                                             {"id": "01", "x": 10, "y": 17, "dir": 'W'}]}}
    print(call_algo(message))

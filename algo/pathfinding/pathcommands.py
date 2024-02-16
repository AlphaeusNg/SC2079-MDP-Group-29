import numpy as np
from enumerations import Gear, Steering
from objects.Obstacle import Obstacle
import algo.objects.OccupancyMap as om
import algo.simulation.simulator as sim


def print_path(path):
    for node in path:
        print(
            f"Current Node (x:{node.x:.2f}, y: {node.y:.2f}, " + f"theta: {node.theta * 180 / np.pi:.2f}), Action: {node.prevAction}")


def construct_path(path, L, Radius):
    LF, SF, RF, LR, SB, RB = 0, 0, 0, 0, 0, 0
    command = []
    for node in path:
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

    return command


def construct_json(command):
    json_file = {
        "type": "NAVIGATION",
        "data": command
        # "path": path
    }
    return json_file


def call_algo(message):
    obstacles = []
    data_obstacles = message["data"]["obstacles"]
    for obstacle in data_obstacles:
        obstacles.append(Obstacle(obstacle["x"] * 2, obstacle["y"] * 2, obstacle["dir"]))
    # Run simulator
    map = om.OccupancyMap(obstacles)
    hamiltonian_args = {'obstacles': map, 'x_start': 15, 'y_start': 15, 'theta_start': np.pi / 2,
                        'theta_offset': -np.pi / 2, 'metric': 'euclidean', 'minR': 25}
    astar_args = {'steeringChangeCost': 10, 'gearChangeCost': 10, 'L': 25 * np.pi / 4 / 5, 'minR': 25,
                  'heuristic': 'euclidean', 'simulate': False, 'thetaBins': 24}
    simulator = sim.Simulator(obstacles, hamiltonian_args, astar_args).start_simulation()
    # Convert to json
    json_file = construct_json(simulator)
    return json_file

import constants as c
import sys
import json
import algo.pathfinding.hamiltonian as h
import algo.pathfinding.hybrid_astar as astar
import algo.objects.OccupancyMap as om
import algo.simulation.simulator as sim
import numpy as np

from connect.rpi_client import PCClient
from objects.Obstacle import Obstacle


class Main:
    def __init__(self):
        self.client = None
        self.commands = None
        self.count = 0

    def connect(self):
        if self.client is None:
            print(f"Connecting to RPi @ {c.RPI_HOST}")
            self.client = PCClient()
            while True:
                try:
                    self.client.connect()
                    break
                except OSError:
                    pass
                except KeyboardInterrupt:
                    self.client.disconnect()
                    sys.exit(1)

    def test(self):
        PC1_sample = {
            "type": "NAVIGATION",
            "data": {"commands": ["RF015", "SF040", "LF005", "SF015", "LF010"]}}
        PC1_json = json.dumps(PC1_sample)
        self.client.send_message(PC1_json)
        self.client.recieve_message()

    def run_task1(self):
        if self.client.connected is True:
            print("Listening...")
            while True:
                # data = {"type": "START_TASK","data": {"task": "EXPLORATION","robot": {"id": "R", "x": 1, "y": 1, "dir": 'N'},"obstacles": [{"id": "00", "x": 8, "y": 5, "dir": 'S'},{"id": "01", "x": 10, "y": 17, "dir": 'W'}]}}
                data = self.client.get_message()
                if data is None:
                    continue
                if data["type"] == "START_TASK":
                    obstacles = []
                    data_obstacles = data["data"]["obstacles"]
                    for obstacle in data_obstacles:
                        obstacles.append(Obstacle(obstacle["x"]*2, obstacle["y"]*2, obstacle["dir"]))
                    # Run simulator
                    map = om.OccupancyMap(obstacles)
                    hamiltonian_args = {'obstacles': map, 'x_start': 15, 'y_start': 15, 'theta_start': np.pi / 2, 'theta_offset': -np.pi / 2, 'metric': 'euclidean', 'minR': 25}
                    astar_args = {'steeringChangeCost': 10, 'gearChangeCost': 10, 'L': 25 * np.pi / 4 / 5, 'minR': 25, 'heuristic': 'euclidean', 'simulate': False, 'thetaBins': 24}
                    sim.Simulator(obstacles, hamiltonian_args, astar_args).start_simulation()
                elif data["type"] == "IMAGE_TAKEN":
                    continue


if __name__ == "__main__":
    # Create an instance of Main
    main_instance = Main()

    # Test connection with RPI
    main_instance.connect()
    main_instance.run_task1()

import constants as c
import sys
import json
import algo.pathfinding.hamiltonian as h
import algo.pathfinding.hybrid_astar as astar
import algo.pathfinding.pathcommands as pc
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
        message = {"type": "START_TASK", "data": {"task": "EXPLORATION", "robot": {"id": "R", "x": 1, "y": 1, "dir": 'N'},
                                               "obstacles": [{"id": "00", "x": 8, "y": 5, "dir": 'S'},
                                                             {"id": "01", "x": 10, "y": 17, "dir": 'W'}]}}

        data = pc.call_algo(message)
        jdata = json.dumps(data)
        print(jdata)
        # self.client.send_message(PC1_json)
        # self.client.receive_message()

    def run_task1(self):
        if self.client.connected is True:
            print("Listening...")
            while True:
                data = self.client.get_message()
                if data is None:
                    continue
                if data["type"] == "START_TASK":
                    json_file = pc.call_algo(data)
                    # Send data to rpi
                    json_data = json.dumps(json_file)
                    self.client.send_message(json_data)
                elif data["type"] == "IMAGE_TAKEN":
                    continue


if __name__ == "__main__":
    # Create an instance of Main
    main_instance = Main()

    # Test connection with RPI
    # main_instance.connect()
    main_instance.test()

import numpy as np
import pygame
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__ + '\..')))

from enumerations import Gear, Steering
from typing import List
import utils

class Node():
    def __init__(self, x_g: int, y_g: int, facing: str, g_n=0) -> None:
        self.x_g = x_g
        self.y_g = y_g
        self.facing = facing
        self.g_n = g_n

class HybridAStar():
    def __init__(self, walls: List[pygame.sprite.Sprite], x_0: float=15, y_0: float=15, theta_0: float=np.pi/2, 
                 x_f: float=15, y_f: float=180, theta_f: float=np.pi/2, 
                 additional_costs: List[float] = [0.05, 0, 0.05, 0.2, 0.1, 0.2], dt: float=0.1):
        
        assert -np.pi < theta_0, theta_f <= np.pi
        assert 0 <= x_0, y_0 <= 200
        assert 0 <= x_f, y_f <= 200

        self.x_0 = x_0
        self.y_0 = y_0
        self.theta_0 = theta_0
        self.x_f = x_f
        self.y_f = y_f
        self.theta_f = theta_f
        self.dt = dt

        gear_choices = [Gear.FORWARD, Gear.REVERSE]
        steering_choices = [Steering.LEFT, Steering.STRAIGHT, Steering.RIGHT]
        self.choices = [(gear, steering) for gear in gear_choices for steering in steering_choices]

        
if __name__ == '__main__':
    algo = HybridAStar()
    print(algo.choices)
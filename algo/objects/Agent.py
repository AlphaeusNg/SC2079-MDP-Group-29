from algo.objects.Map import Map
from algo.enumerations import AgentState
from algo import utils
import numpy as np

class Agent:
    def __init__(self, map: Map, x: float=20., y: float=20., theta: float=np.pi/2, algo: str='astar'):
        """Agent constructor

        Args:
            map (Map): Map object of current environment
            x (float, optional): x coordinate of agent, defaults to 20.
            y (float, optional): y coordinate of agent, defaults to 20.
            theta (float, optional): angle of agent in radians, defaults to np.pi/2
            algo (str): pathfinding algorithm used, defaults to astar

        Parameters:
            facing (str): {'N', 'S', 'E', 'W'} direction of agent
            x_t (float): velocity in x direction
            y_t (float): velocity in y direction
            theta_t (float): angular velocity in rad/s
            dt (float): smallest time step, to be changed
            self.state (AgentState): current state of agent, default to PARK
            self.nextCheckpoint (Checkpoint): next checkpoint of robot, defaults to None, chosen by algorithm
        """

        self.map = map
        self.x = x
        self.y = y
        self.theta = theta
        self.algo = algo

        self.facing = utils.rad_to_facing(theta)
        self.x_t = 0.
        self.y_t = 0.
        self.theta_t = 0.

        self.dt = 0.1
        
        self.state = AgentState.START
        self.nextCheckpoint = None

    def update_position(self):
        pass #todo

    def update_state(self):
        pass #todo

    def start(self):
        pass #todo

    def end(self):
        pass #todo

    def drive(self):
        pass #todo

    def imagerec(self):
        pass #todo

    def selfdrive(self):
        pass #todo

    def task1(self):
        pass #todo

    def task2(self):
        pass #todo

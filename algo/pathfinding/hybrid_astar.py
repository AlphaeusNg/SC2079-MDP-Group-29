import numpy as np
import math
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__ + '\..')))

from enumerations import Gear, Steering
from objects.OccupancyMap import OccupancyMap
from objects.Obstacle import Obstacle
from typing import List
import utils
import constants as c
from queue import PriorityQueue

import matplotlib.pyplot as plt #to remove

class Node():
    def __init__(self, x: float, y: float, theta: float, 
                 prevAction, parent=None) -> None:
        self.x = x
        self.y = y
        self.theta = theta
        self.x_g, self.y_g, self.theta_g = self.discretize_position(self.x, self.y, self.theta)
        self.parent = parent
        self.prevAction = prevAction
        self.g = 0
        self.h = 0
        self.f = 0

    def discretize_position(self, x, y, theta, gridSize=40, thetaBins=18):
        x_g = x // (200/c.GRID_SIZE)
        y_g = y // (200/c.GRID_SIZE)
        theta_g = (theta * 180 / np.pi + 180 / thetaBins) // thetaBins

        return x_g, y_g, theta_g

    def __eq__(self, other):
        return self.x_g == other.x_g and self.y_g == other.y_g and self.theta_g == other.theta_g
    
    def __lt__(self, other):
        return self.f < other.f

class HybridAStar():
    def __init__(self, map: OccupancyMap, x_0: float=15, y_0: float=15, theta_0: float=np.pi/2, 
                 x_f: float=15, y_f: float=180, theta_f: float=np.pi/2, steeringChangeCost=10, gearChangeCost=20,
                    L: float=5, minR: float=25, heuristic: str='euclidean'):
        """HybridAStar constructor

        Args:
            map (2D numpy array): binary occupancy map
            x_0 (float, optional): starting x coordinate of rear axle. Defaults to 15.
            y_0 (float, optional): starting y coordinate of rear axle. Defaults to 15.
            theta_0 (float, optional): starting direction. Defaults to np.pi/2.
            x_f (float, optional): ending x coordinate of rear axle. Defaults to 15.
            y_f (float, optional): ending y coordinate of rear axle. Defaults to 180.
            theta_f (float, optional): ending direction. Defaults to np.pi/2.
            steeringChangeCost (int, optional): extra cost for changing steering input. Defaults to 10.
            gearChangeCost (int, optional): extra cost for changing gear input. Defaults to 20.
            L (float, optional): distance travel each step in cm. Defaults to 5.
            minR (float, optional): minimum turning radius in cm. Defaults to 25.
        """
        
        assert -np.pi < theta_0, theta_f <= np.pi
        assert 0 <= x_0, y_0 <= 200
        assert 0 <= x_f, y_f <= 200

        self.map = map
        assert not map.collide_with_point(x_f, y_f)

        self.x = x_0
        self.y = y_0
        self.theta = theta_0
        self.x_f = x_f
        self.y_f = y_f
        self.theta_f = theta_f
        self.steeringChangeCost = steeringChangeCost
        self.gearChangeCost = gearChangeCost
        self.L = L
        self.minR = minR
        self.heuristic = heuristic

    def find_path(self):
        gearChoices = [Gear.FORWARD, Gear.REVERSE]
        steeringChoices = [Steering.LEFT, Steering.STRAIGHT, Steering.RIGHT]
        choices = [(gear, steering) for gear in gearChoices for steering in steeringChoices]

        startNode = Node(self.x, self.y, self.theta, (Gear.FORWARD, Steering.STRAIGHT))
        endNode = Node(self.x_f, self.y_f, self.theta_f, (Gear.FORWARD, Steering.STRAIGHT))

        open = PriorityQueue()
        close = PriorityQueue()

        open.put((startNode.f, startNode))

        printing = False
        pathFound = False

        while not open.empty() and not pathFound:
            currentNode = open.get()[1]

            if printing:
                print(f"Currently exploring (x:{currentNode.x:.2f}, y: {currentNode.y:.2f}, " +
                    f"theta: {currentNode.theta*180/np.pi:.2f}), Action {currentNode.prevAction} from (" +
                    f"x: {currentNode.parent.x:.2f}, y: {currentNode.parent.y:.2f}, " +
                    f"theta: {currentNode.parent.theta*180/np.pi:.2f}), f = {currentNode.f:.2f}, " + 
                    f"g = {currentNode.g:.2f}, h = {currentNode.h:.2f}")
            
            printing = False

            for choice in choices:
                x_child, y_child, theta_child = self.calculate_next_node(currentNode, choice)

                if self.map.collide_with_point(x_child, y_child):
                    continue #skip if next node is occupied

                childNode = Node(x_child, y_child, theta_child, prevAction=choice, parent=currentNode)

                if childNode == endNode:
                    pathFound = True
                    currentNode = childNode
                
                else:
                    childNode.g = currentNode.g + self.L
                    if self.heuristic == 'euclidean':
                        childNode.h = utils.l2(childNode.x, childNode.y, endNode.x, endNode.y)
                    elif self.heuristic == 'manhattan':
                        childNode.h = utils.l1(childNode.x, childNode.y, endNode.x, endNode.y)
                    elif self.heuristic == 'reeds-shepp':
                        print('Reeds-Shepp not implemented yet')

                    extraCost = 0
                    if currentNode.prevAction[0] != choice[0]:
                        extraCost += self.gearChangeCost
                    
                    if currentNode.prevAction[1] != choice[1]:
                        extraCost += self.steeringChangeCost
                    
                    childNode.f = childNode.g + childNode.h + extraCost

                betterPathExists = False

                for f, node in open.queue:
                    if f > childNode.f:
                        break
                    if node == childNode:
                        betterPathExists = True # better path to current node already exist, to be optimised
                        break 
                
                for f, node in close.queue:
                    if f > childNode.f:
                        break
                    if node == childNode:
                        betterPathExists = True # better path to current node already exist, to be optimised
                        break
                
                if not betterPathExists:
                    open.put((childNode.f, childNode))
            
            close.put((currentNode.f, currentNode))

        path = []
        while currentNode != startNode:
            path.append(currentNode)
            currentNode = currentNode.parent

        path.reverse()

        return path


    def calculate_next_node(self, currentNode, choice):
        gear = choice[0]
        steering = choice[1]

        if steering == Steering.STRAIGHT:
            x_b = currentNode.x + gear * self.L * math.cos(currentNode.theta)
            y_b = currentNode.y + gear * self.L * math.sin(currentNode.theta)
            theta_b = currentNode.theta

        else:
            x_c = currentNode.x + steering*self.minR*math.sin(currentNode.theta)
            y_c = currentNode.y - steering*self.minR*math.cos(currentNode.theta)

            theta_t = -steering*self.L/self.minR
            theta_b = utils.normalise_theta(currentNode.theta + gear*theta_t)

            x_ca = currentNode.x - x_c
            y_ca = currentNode.y - y_c

            x_b = x_c + (x_ca * math.cos(gear*theta_t) - y_ca * math.sin(gear*theta_t))
            y_b = y_c + (x_ca * math.sin(gear*theta_t) + y_ca * math.cos(gear*theta_t))

        return x_b, y_b, theta_b
        
if __name__ == '__main__':
    obstacles = [Obstacle(10, 10, 'N'), Obstacle(20, 10, 'S'), Obstacle(10, 20, 'E'), Obstacle(20, 20, 'W'), 
                 Obstacle(38, 38, 'N')]
    map = OccupancyMap(obstacles)

    algo = HybridAStar(map, x_f=150, y_f=150, theta_f=0)
    path = algo.find_path()
    for node in path:
        print(f"Current Node (x:{node.x:.2f}, y: {node.y:.2f}, " +
                f"theta: {node.theta*180/np.pi:.2f}), Action: {node.prevAction}")


    '''
    theta_grid = np.linspace(-np.pi, np.pi, 3600)
    theta_g = (theta_grid * 180 / np.pi + (180 / 18)) // 18
    
    plt.plot(theta_grid, theta_g)
    plt.show()
    '''

    '''
    node = Node(5, 10, -np.pi/4, '')
    x_b, y_b, theta_b = algo.calculate_next_node(node, (Gear.FORWARD, Steering.RIGHT))

    print(x_b, y_b, theta_b*180/np.pi)
    '''


    
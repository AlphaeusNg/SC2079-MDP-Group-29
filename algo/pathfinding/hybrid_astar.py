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
import time
import pathfinding.reeds_shepp as rs

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

    def discretize_position(self, x, y, theta, thetaBins=24):
        x_g = int(x // (200/c.GRID_SIZE))
        y_g = int(y // (200/c.GRID_SIZE))
        theta_g = int(((theta * 180 / np.pi + 180)//(360/thetaBins)))

        return x_g, y_g, theta_g

    def __eq__(self, other):

        return abs(self.x - other.x) <= 3.5 and abs(self.y - other.y) <= 3.5 and \
        (abs(self.theta - other.theta) <= np.pi/24 or abs(abs(self.theta - other.theta) - 2*np.pi) <= np.pi/24)
    
    def __lt__(self, other):
        return self.f < other.f

class HybridAStar():
    def __init__(self, map: OccupancyMap, x_0: float=15, y_0: float=10, theta_0: float=np.pi/2, 
                 x_f: float=15, y_f: float=180, theta_f: float=np.pi/2, theta_offset: float=0, steeringChangeCost=10, gearChangeCost=20,
                    L: float=5, minR: float=25, heuristic: str='hybriddiag', simulate: bool=False, thetaBins=24):
        """HybridAStar constructor

        Args:
            map (2D numpy array): binary occupancy map
            x_0 (float, optional): starting x coordinate of rear axle. Defaults to 15.
            y_0 (float, optional): starting y coordinate of rear axle. Defaults to 10.
            theta_0 (float, optional): starting direction. Defaults to np.pi/2.
            x_f (float, optional): ending x coordinate of rear axle. Defaults to 15.
            y_f (float, optional): ending y coordinate of rear axle. Defaults to 180.
            theta_f (float, optional): ending direction. Defaults to np.pi/2.
            theta_offset (float, optional): offset for camera direction. Defaults to 0.
            steeringChangeCost (int, optional): extra cost for changing steering input. Defaults to 10.
            gearChangeCost (int, optional): extra cost for changing gear input. Defaults to 20.
            L (float, optional): distance travel each step in cm. Defaults to 5.
            minR (float, optional): minimum turning radius in cm. Defaults to 25.
        """
        
        assert -np.pi <= theta_0, theta_f <= np.pi
        assert -10 <= x_0, y_0 <= 210 # we changed this on 22/2/24
        assert -10 <= x_f, y_f <= 210

        self.map = map
        # assert not map.collide_with_point(x_f, y_f) # we changed this on 22/2/24

        self.x = x_0
        self.y = y_0
        self.theta = theta_0
        self.x_f = x_f
        self.y_f = y_f
        self.theta_f = theta_f
        self.theta_offset = theta_offset
        self.steeringChangeCost = steeringChangeCost
        self.gearChangeCost = gearChangeCost
        self.L = L
        self.minR = minR
        self.heuristic = heuristic
        self.simulate = simulate
        self.thetaBins = thetaBins

    def find_path(self):
        start = time.process_time()
        pathHistory = []
        gearChoices = [Gear.FORWARD, Gear.REVERSE]
        steeringChoices = [Steering.LEFT, Steering.STRAIGHT, Steering.RIGHT]
        choices = [(gear, steering) for gear in gearChoices for steering in steeringChoices]

        startNode = Node(self.x, self.y, self.theta, (Gear.FORWARD, Steering.STRAIGHT))
        endNode = Node(self.x_f, self.y_f, self.theta_f, (Gear.FORWARD, Steering.STRAIGHT))

        open = PriorityQueue()
        close = PriorityQueue()
        openList = 999999*np.ones((c.GRID_SIZE, c.GRID_SIZE, self.thetaBins + 1))
        closedList = 999999*np.ones((c.GRID_SIZE, c.GRID_SIZE, self.thetaBins + 1))

        open.put((startNode.f, startNode))

        printing = False
        pathFound = False
        nodesExpanded = 0

        while not open.empty() and not pathFound:
            currentNode = open.get()[1]
            openList[currentNode.x_g, currentNode.y_g, currentNode.theta_g] = 999999
            nodesExpanded += 1

            if self.simulate:
                pathHistory.append(currentNode)

            if printing:
                print(f"Currently exploring (x:{currentNode.x:.2f}, y: {currentNode.y:.2f}, " +
                    f"theta: {currentNode.theta*180/np.pi:.2f}), Action {currentNode.prevAction} from (" +
                    f"x: {currentNode.parent.x:.2f}, y: {currentNode.parent.y:.2f}, " +
                    f"theta: {currentNode.parent.theta*180/np.pi:.2f}), f = {currentNode.f:.2f}, " + 
                    f"g = {currentNode.g:.2f}, h = {currentNode.h:.2f}")
            
            printing = False

            for choice in choices:
                if choice[0] == -currentNode.prevAction[0] and choice[1] == -currentNode.prevAction[1]:
                    continue 

                x_child, y_child, theta_child = self.calculate_next_node(currentNode, choice)
                

                if self.map.collide_with_point(x_child + c.REAR_AXLE_TO_CENTER*np.cos(theta_child), y_child + c.REAR_AXLE_TO_CENTER*np.sin(theta_child)):
                    continue #skip if next node is occupied

                childNode = Node(x_child, y_child, theta_child, prevAction=choice, parent=currentNode)

                if self.checkPathFound(childNode):
                    print("Path Found!")
                    pathFound = True
                    currentNode = childNode
                    break
                
                else:
                    childNode.g = currentNode.g + self.L
                    if self.heuristic == 'euclidean':
                        childNode.h = utils.l2(childNode.x, childNode.y, endNode.x, endNode.y)
                    elif self.heuristic == 'manhattan':
                        childNode.h = utils.l1(childNode.x, childNode.y, endNode.x, endNode.y)
                    elif self.heuristic == 'diag':
                        childNode.h = utils.diag_dist(childNode.x, childNode.y, endNode.x, endNode.y)
                    elif self.heuristic == 'reeds-shepp':
                        childNode.h = rs.get_optimal_path_length((childNode.x, childNode.y, childNode.theta), 
                                                    (endNode.x, endNode.y, endNode.theta), self.minR)
                    elif self.heuristic == 'hybridl2':
                        childNode.h = max(utils.l2(childNode.x, childNode.y, endNode.x, endNode.y), 
                                          rs.get_optimal_path_length((childNode.x, childNode.y, childNode.theta), 
                                                    (endNode.x, endNode.y, endNode.theta), self.minR))
                    elif self.heuristic == 'hybridl1':
                        childNode.h = min(utils.l1(childNode.x, childNode.y, endNode.x, endNode.y), 
                                          rs.get_optimal_path_length((childNode.x, childNode.y, childNode.theta), 
                                                    (endNode.x, endNode.y, endNode.theta), self.minR))
                    elif self.heuristic == 'hybriddiag':
                        childNode.h = min(utils.diag_dist(childNode.x, childNode.y, endNode.x, endNode.y), 
                                          rs.get_optimal_path_length((childNode.x, childNode.y, childNode.theta), 
                                                    (endNode.x, endNode.y, endNode.theta), self.minR))
                    elif self.heuristic == 'greedy':
                        childNode.h = 0

                    extraCost = 0
                    extraCost += self.gearChangeCost*abs(currentNode.prevAction[0] - choice[0])
                    extraCost += self.steeringChangeCost*abs(currentNode.prevAction[1] - choice[1])
                    
                    childNode.f = childNode.g + childNode.h + extraCost

                if openList[childNode.x_g, childNode.y_g, childNode.theta_g] < childNode.f:
                    continue

                if closedList[childNode.x_g, childNode.y_g, childNode.theta_g] < childNode.f:
                    continue
                
                open.put((childNode.f, childNode))
                openList[childNode.x_g, childNode.y_g, childNode.theta_g] = childNode.f
            
            close.put((currentNode.f, currentNode))
            closedList[currentNode.x_g, currentNode.y_g, currentNode.theta_g] = currentNode.f

        path = []
        while currentNode != startNode:
            path.append(currentNode)
            currentNode = currentNode.parent

        path.reverse()

        end = time.process_time()
        print(f"Nodes Expanded = {nodesExpanded}, Time taken = {(end - start):.2f}")

        if self.simulate:
            return path, pathHistory
        
        else:
            return path, None

    def checkPathFound(self, curNode, thetaMargin:float=np.pi/12, targetDistance:float=25, distanceMargin: float=7.5, maxPerpDistance:float=1):
        if abs(curNode.theta - self.theta_f) > thetaMargin:
            return False
        
        target_x = self.x_f + c.REAR_AXLE_TO_CENTER*np.cos(self.theta_f)
        target_y = self.y_f + c.REAR_AXLE_TO_CENTER*np.sin(self.theta_f)
        target_x += targetDistance*np.cos(self.theta_f - self.theta_offset)
        target_y += targetDistance*np.sin(self.theta_f - self.theta_offset)

        cur_x = curNode.x + c.REAR_AXLE_TO_CENTER*np.cos(curNode.theta)
        cur_y = curNode.y + c.REAR_AXLE_TO_CENTER*np.sin(curNode.theta)
        
        dist = utils.l2(target_x, target_y, cur_x, cur_y)

        if dist > targetDistance + distanceMargin:
            return False
        if dist < targetDistance - distanceMargin:
            return False
        
        projection_x = cur_x + dist*np.cos(curNode.theta - self.theta_offset)
        projection_y = cur_y + dist*np.sin(curNode.theta - self.theta_offset)
        perpDistance = utils.l2(projection_x, projection_y, target_x, target_y)
        
        if perpDistance > maxPerpDistance:
            return False
        
        return True

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

    algo = HybridAStar(map, x_f=150, y_f=150, theta_f=np.pi, gearChangeCost=10, steeringChangeCost=10, 
                           L=5, heuristic='greedy')
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


    
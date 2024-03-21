import random
import itertools
import numpy as np
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__ + '\..')))

import utils
from objects.Obstacle import Obstacle
import pathfinding.reeds_shepp as rs
import constants as c
import copy

class Hamiltonian():
    def __init__(self, map, obstacles, x_start, y_start, theta_start, theta_offset=0, 
                          metric='euclidean', minR=25) -> None:
        assert -np.pi < theta_start, theta_offset <= np.pi
        self.map = map
        self.obstacles = obstacles
        self.checkpoints = []
        self.start = (x_start, y_start, theta_start)
        self.theta_offset = theta_offset
        self.metric = metric
        self.minR = minR

    def find_brute_force_path(self):
        obstacle_permutations = itertools.permutations(self.obstacles)
        shortest_distance = float('inf')
        for obstacle_path in obstacle_permutations:
            current_pos = self.start
            total_distance = 0
            for obstacle in obstacle_path:
                checkpoint = obstacle_to_checkpoint(self.map, obstacle, self.theta_offset)
                if self.metric == 'euclidean':
                    distance = utils.l2(current_pos[0], current_pos[1], checkpoint[0], checkpoint[1])
                elif self.metric == 'reeds-shepp':
                    distance = rs.get_optimal_path_length(current_pos, checkpoint, self.minR)

                total_distance += distance
                current_pos = checkpoint
            if total_distance < shortest_distance:
                shortest_distance = total_distance
                shortest_path = obstacle_path[:]
        return shortest_path

    def find_nearest_neighbor_path(self):
        current_pos = self.start
        path = []

        obstacles = self.obstacles.copy()
        while obstacles:
            nearest_neighbor = None
            minDist = float('inf')
            for obstacle in obstacles:
                checkpoint = obstacle_to_checkpoint(self.map, obstacle, self.theta_offset)
                if self.metric == 'euclidean':
                    dist = utils.l2(current_pos[0], current_pos[1], checkpoint[0], checkpoint[1])
                elif self.metric == 'reeds-shepp':
                    dist = rs.get_optimal_path_length(current_pos, checkpoint, self.minR)
                
                if dist < minDist:
                    minDist = dist
                    nearest_neighbor = obstacle
                
            
            path.append(nearest_neighbor)
            obstacles.remove(nearest_neighbor)
            current_pos = obstacle_to_checkpoint(self.map, nearest_neighbor, self.theta_offset)
        
        return path

def obstacle_to_checkpoint(map, obstacle: Obstacle, theta_offset):
    starting_x, starting_y = utils.grid_to_coords(obstacle.x_g, obstacle.y_g)
    starting_x += offset_x(obstacle.facing)
    starting_y += offset_y(obstacle.facing)
    starting_image_to_pos_theta = offset_theta(obstacle.facing, np.pi)

    theta_scan_list = [0, np.pi/36, -np.pi/36, np.pi/18, -np.pi/18, np.pi/12, -np.pi/12, 
                       np.pi/9, -np.pi/9, np.pi/7.2, -np.pi/7.2, np.pi/6, -np.pi/6, 
                       np.pi*180/35, -np.pi*180/35, np.pi/4.5, -np.pi/4.5, np.pi/4, -np.pi/4]
    r_scan_list = [20, 19, 21, 18, 22, 17, 23, 16, 24, 15, 25, 26, 27, 28, 29, 30]

    
    for r_scan in r_scan_list:
        for theta_scan in theta_scan_list:
            cur_image_to_pos_theta = utils.M(starting_image_to_pos_theta + theta_scan)
            cur_x = starting_x + r_scan*np.cos(cur_image_to_pos_theta)
            cur_y = starting_y + r_scan*np.sin(cur_image_to_pos_theta)
            theta = utils.M(cur_image_to_pos_theta - theta_offset)

            if not map.collide_with_point(cur_x, cur_y) and not \
                map.collide_with_point(cur_x + 0.5*c.REAR_AXLE_TO_CENTER*np.cos(theta), cur_y + 0.5*c.REAR_AXLE_TO_CENTER*np.sin(theta)) and not \
                map.collide_with_point(cur_x - 0.5*c.REAR_AXLE_TO_CENTER*np.cos(theta), cur_y - 0.5*c.REAR_AXLE_TO_CENTER*np.sin(theta)):
                
                cur_x -= c.REAR_AXLE_TO_CENTER*np.cos(theta)
                cur_y -= c.REAR_AXLE_TO_CENTER*np.sin(theta)
                return (cur_x, cur_y, theta, obstacle.id)

    return None

def obstacle_to_checkpoint_all(map, obstacle: Obstacle, theta_offset):
    starting_x, starting_y = utils.grid_to_coords(obstacle.x_g, obstacle.y_g)
    starting_x += offset_x(obstacle.facing)
    starting_y += offset_y(obstacle.facing)
    starting_image_to_pos_theta = offset_theta(obstacle.facing, np.pi)

    valid_checkpoints = []

    theta_scan_list = [0, np.pi/36, -np.pi/36, np.pi/18, -np.pi/18, np.pi/12, -np.pi/12, np.pi/9, -np.pi/9, np.pi/7.2, -np.pi/7.2, np.pi/6, -np.pi/6]
    r_scan_list = [20, 19, 21, 18, 22, 17, 23, 16, 24, 15, 25, 26, 27, 28, 29, 30]
    
    
    for r_scan in r_scan_list:
        for theta_scan in theta_scan_list:
            cur_image_to_pos_theta = utils.M(starting_image_to_pos_theta + theta_scan)
            cur_x = starting_x + r_scan*np.cos(cur_image_to_pos_theta)
            cur_y = starting_y + r_scan*np.sin(cur_image_to_pos_theta)
            theta = utils.M(cur_image_to_pos_theta - theta_offset)

            if not map.collide_with_point(cur_x, cur_y) and not \
                map.collide_with_point(cur_x + 0.5*c.REAR_AXLE_TO_CENTER*np.cos(theta), cur_y + 0.5*c.REAR_AXLE_TO_CENTER*np.sin(theta)) and not \
                map.collide_with_point(cur_x - 0.5*c.REAR_AXLE_TO_CENTER*np.cos(theta), cur_y - 0.5*c.REAR_AXLE_TO_CENTER*np.sin(theta)):
                
                cur_x -= c.REAR_AXLE_TO_CENTER*np.cos(theta)
                cur_y -= c.REAR_AXLE_TO_CENTER*np.sin(theta)
                valid_checkpoints.append((cur_x, cur_y, theta, obstacle.id))

    return valid_checkpoints


def offset_x(facing: str):
    if facing == 'N':
        return 5.
    elif facing == 'S':
        return 5.
    elif facing == 'E':
        return 0.
    elif facing == 'W':
        return 10.


def offset_y(facing: str):
    if facing == 'N':
        return 0.
    elif facing == 'S':
        return 10.
    elif facing == 'E':
        return 5.
    elif facing == 'W':
        return 5.
    
def offset_theta(facing: str, theta_offset: float):
    return utils.M(utils.facing_to_rad(facing) + theta_offset)

def generate_random_obstacles(grid_size, obstacle_count):
    if grid_size < 100:
        offset = 5
    else:
        offset = 50
    obstacles = []
    directions = ['N', 'S', 'E', 'W']

    while len(obstacles) < obstacle_count:
        x = random.randint(offset, grid_size - offset)
        y = random.randint(offset, grid_size - offset)
        direction = random.choice(directions)
        obstacles.append(Obstacle(x, y, direction))

    return obstacles


def print_grid(grid_size, obstacles):
    path = []
    for y in range(grid_size - 1, -1, -1):
        for x in range(grid_size):
            position = (x, y)
            if (0 <= x <= 2) and (0 <= y <= 2):
                print("C", end=" ")  # Starting point
            elif any(obstacle.x_g == x and obstacle.y_g == y for obstacle in obstacles):
                direction = next(
                    (obstacle.facing for obstacle in obstacles if (obstacle.x_g, obstacle.y_g) == position), None)
                print(direction, end=" " if direction else ".")  # Obstacle facing direction
            elif (x, y) in path:
                print("*", end=" ")  # Mark the path with "*"
            else:
                print(".", end=" ")  # Empty space
        print()


if __name__ == "__main__":
    obstacles = [Obstacle(10, 10, 'N'), Obstacle(20, 10, 'S'), Obstacle(10, 20, 'E'), Obstacle(20, 20, 'W'), 
                 Obstacle(38, 38, 'N')]
    
    tsp = Hamiltonian(obstacles, 15, 15, np.pi/2, metric='reeds-shepp')
    path = tsp.find_nearest_neighbor_path()
    print("\nShortest Path:")
    print(path)


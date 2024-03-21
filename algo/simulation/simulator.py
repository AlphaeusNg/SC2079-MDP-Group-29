import pygame
import numpy as np
from sys import exit
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__ + '\..')))

from enumerations import Gear, Steering
from objects.Border import Border, VirtualBorderWall
from objects.Obstacle import Obstacle, VirtualWall
from objects.OccupancyMap import OccupancyMap
from pathfinding.hybrid_astar import HybridAStar
from pathfinding.hamiltonian import Hamiltonian, obstacle_to_checkpoint, obstacle_to_checkpoint_all
from simulation.testing import get_maps
import utils as utils
from typing import List
import constants as c

class Simulator:
    def __init__(self, obstacles:List[Obstacle], hamiltonian_args, astar_args):
        self.hamiltonian_args = hamiltonian_args
        self.astar_args = astar_args

        self.screen = pygame.display.set_mode((c.WIDTH, c.HEIGHT))
        self.screen.fill('white')
        pygame.display.set_caption('Algorithm Simulator')
        self.clock = pygame.time.Clock()

        self.map_surface = pygame.Surface((c.MAP_WIDTH, c.MAP_HEIGHT))
        self.map_surface.fill('azure')
        self.start_surface = pygame.Surface((30*c.MAP_WIDTH/200, 30*c.MAP_HEIGHT/200))
        self.start_surface.fill('aquamarine')

        self.path_surface = pygame.Surface((c.MAP_WIDTH, c.MAP_HEIGHT))
        self.path_surface = self.path_surface.convert_alpha()
        self.path_surface.fill((0,0,0,0))

        left_border = Border(c.BORDER_THICKNESS, c.MAP_HEIGHT + 2*c.BORDER_THICKNESS, 
                            c.MAP_X0 - c.BORDER_THICKNESS, c.MAP_Y0 - c.BORDER_THICKNESS)
        right_border = Border(c.BORDER_THICKNESS, c.MAP_HEIGHT + 2*c.BORDER_THICKNESS, 
                            c.MAP_X0 + c.MAP_WIDTH, c.MAP_Y0 - c.BORDER_THICKNESS)
        top_border = Border(c.MAP_WIDTH + 2*c.BORDER_THICKNESS, c.BORDER_THICKNESS, 
                            c.MAP_X0 - c.BORDER_THICKNESS, c.MAP_Y0 - c.BORDER_THICKNESS)
        bottom_border = Border(c.MAP_WIDTH + 2*c.BORDER_THICKNESS, c.BORDER_THICKNESS, 
                            c.MAP_X0 - c.BORDER_THICKNESS, c.MAP_Y0 + c.MAP_HEIGHT)


        self.borders = pygame.sprite.Group()
        self.borders.add(left_border)
        self.borders.add(right_border)
        self.borders.add(top_border)
        self.borders.add(bottom_border)

        self.obstacles = pygame.sprite.Group()
        self.virtual_walls = pygame.sprite.Group()
        self.virtual_wall_surface = pygame.Surface((c.MAP_WIDTH, c.MAP_HEIGHT), pygame.SRCALPHA)
        self.virtual_wall_surface.fill((0, 0, 0, 0))

        for obstacle in obstacles:
            self.obstacles.add(obstacle)
            vw = VirtualWall(obstacle.x_g, obstacle.y_g)
            self.virtual_walls.add(vw)
            self.virtual_wall_surface.blit(vw.image, (vw.rect.x - c.MAP_X0, vw.rect.y - c.MAP_Y0))
        
        left_border_wall = VirtualBorderWall(10*c.MAP_WIDTH/200, c.MAP_HEIGHT, 0, 0)
        right_border_wall = VirtualBorderWall(10*c.MAP_WIDTH/200, c.MAP_HEIGHT, 
                                               c.MAP_WIDTH - 10*c.MAP_WIDTH/200, 0)
        top_border_wall = VirtualBorderWall(c.MAP_WIDTH, 10*c.MAP_HEIGHT/200, 0, 0)
        bottom_border_wall = VirtualBorderWall(c.MAP_WIDTH, 10*c.MAP_HEIGHT/200, 
                                               0, c.MAP_HEIGHT - 10*c.MAP_HEIGHT/200)
        

        self.virtual_walls.add(left_border_wall)
        self.virtual_walls.add(right_border_wall)
        self.virtual_walls.add(top_border_wall)
        self.virtual_walls.add(bottom_border_wall)

        self.virtual_wall_surface.blit(left_border_wall.image, left_border_wall.rect.topleft)
        self.virtual_wall_surface.blit(right_border_wall.image, right_border_wall.rect.topleft)
        self.virtual_wall_surface.blit(top_border_wall.image, top_border_wall.rect.topleft)
        self.virtual_wall_surface.blit(bottom_border_wall.image, bottom_border_wall.rect.topleft)

        self.virtual_wall_surface.fill((255, 0, 0, 24),special_flags=pygame.BLEND_RGBA_MIN)

    def start_simulation(self):
        map = OccupancyMap(self.obstacles)
        done = False

        tsp = Hamiltonian(obstacles=self.obstacles, map=map, x_start=self.hamiltonian_args['x_start'],
                          y_start=self.hamiltonian_args['y_start'], 
                          theta_start=self.hamiltonian_args['theta_start'],
                          theta_offset=self.hamiltonian_args['theta_offset'], 
                          metric=self.hamiltonian_args['metric'],
                          minR=self.hamiltonian_args['minR'])
        obstacle_path = tsp.find_nearest_neighbor_path()

        print("Starting simulator...")
        print(f"Optimal path found: {obstacle_path}")
        
        current_pos = tsp.start
        allPaths = []
        numNodes = 0
        
        pygame.init()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
            
            self.screen.blit(self.map_surface, (c.MAP_X0, c.MAP_Y0))
            self.screen.blit(self.virtual_wall_surface, (c.MAP_X0, c.MAP_Y0))
            self.screen.blit(self.start_surface, (c.MAP_X0, c.MAP_Y0 + c.MAP_HEIGHT - 30*c.MAP_HEIGHT/200))
            self.borders.draw(self.screen)
            self.obstacles.draw(self.screen)

            colors = [(0, 0, 0, 255), (0, 255, 0, 255), (0, 0, 255, 255), (0, 255, 255, 255)]

            if not done:
                for idx, obstacle in enumerate(obstacle_path):
                    print(f"Calculating path from {current_pos} to {obstacle}")
                    path = None
                    valid_checkpoints = obstacle_to_checkpoint_all(map, obstacle, 
                                                                   theta_offset=self.hamiltonian_args['theta_offset'])

                    while path == None and valid_checkpoints:
                        checkpoint = valid_checkpoints.pop(0)
                        print(f"Routing from x: {current_pos[0]}, y: {current_pos[1]}, theta: {current_pos[2]} " + 
                              f"to x: {checkpoint[0]}, y: {checkpoint[1]} theta: {checkpoint[2]}...")
                        algo = HybridAStar(map, x_0=current_pos[0], y_0=current_pos[1], theta_0=current_pos[2], 
                                        x_f=checkpoint[0], y_f=checkpoint[1], theta_f=checkpoint[2], theta_offset=astar_args['theta_offset'],
                                        steeringChangeCost=self.astar_args['steeringChangeCost'], 
                                        gearChangeCost=self.astar_args['gearChangeCost'], 
                                        L=self.astar_args['L'], minR=self.astar_args['minR'],
                                        heuristic=self.astar_args['heuristic'], simulate=self.astar_args['simulate'],
                                        thetaBins=self.astar_args['thetaBins'])
                        
                        path, pathHistory = algo.find_path()
                        if path == None:
                            print("Path failed to converge, trying another final position...")
                        
                    
                    if path != None:
                        allPaths.append(path)
                        current_pos = (path[-1].x, path[-1].y, path[-1].theta)
                
                idx = 0
                for path in allPaths:    
                    print("Drawing path on simulator...")
                    numNodes += len(path)
                    current_pos = (path[-1].x, path[-1].y, path[-1].theta)
                    x, y = utils.coords_to_pixelcoords(x=path[-1].x + c.REAR_AXLE_TO_CENTER*np.cos(path[-1].theta), 
                                                        y=path[-1].y + c.REAR_AXLE_TO_CENTER*np.sin(path[-1].theta))
                    pygame.draw.lines(self.path_surface, 'black', True, [(x-10,y-10),(x+10,y+10)], 3)
                    pygame.draw.lines(self.path_surface, 'black', True, [(x-10,y+10),(x+10,y-10)], 3)
            
                    for node in path:
                        print(f"Current Node (x:{node.x:.2f}, y: {node.y:.2f}, " +
                            f"theta: {node.theta*180/np.pi:.2f}), Action: {node.prevAction}")
                    
                    color = colors[idx % len(colors)]
                    self.draw_final_path(path, color)
                    self.screen.blit(self.path_surface, (0, 0))
                    pygame.display.update()
                    self.clock.tick(1000)
                    idx += 1
                    
                
                done = True
                print(f"Total path length: {numNodes*self.astar_args['L']}cm")
            
            """
            animateIndex = 0

            node = path[animateIndex]

            animateIndex += 1
            if animateIndex == len(path):
                animateIndex = 0
            """

            #self.draw_path_history(pathHistory)

            #pygame.display.update()
        
    def draw_final_path(self, path, color):
        points = []
        x, y = utils.coords_to_pixelcoords(x=path[0].parent.x, y=path[0].parent.y)
        points.append((x, y))
        for node in path:
            x, y = utils.coords_to_pixelcoords(x=node.x, y=node.y)
            points.append((x, y))
            if node.prevAction[0] == Gear.FORWARD:
                pygame.draw.circle(self.path_surface, (0, 255, 0, 255), (x, y), 4)
            else:
                pygame.draw.circle(self.path_surface, (255, 0, 0, 255), (x, y), 4)

        pygame.draw.lines(self.path_surface, color, False, points, width=3)
    
    def draw_path_history(self, pathHistory):

        for node in pathHistory[1:]:
            x0, y0 = utils.coords_to_pixelcoords(x=node.parent.x, y=node.parent.y)
            x1, y1 = utils.coords_to_pixelcoords(x=node.x, y=node.y)
            pygame.draw.line(self.path_surface, (255, 0, 255, 64), (x0, y0), (x1, y1))

if __name__ == "__main__":
    test_maps = get_maps()
    map = test_maps[7][:8]
    
    hamiltonian_args = {'obstacles': map, 'x_start': 15, 'y_start': 10, 'theta_start': np.pi/2, 
                        'theta_offset': -np.pi/2, 'metric': 'euclidean', 'minR': 26.5}
    astar_args = {'steeringChangeCost': 10, 'gearChangeCost': 10, 'L': 26.5*np.pi/4/5, 'theta_offset': -np.pi/2,
                    'minR': 25, 'heuristic': 'euclidean', 'simulate': False, 'thetaBins': 24}

    sim = Simulator(map, hamiltonian_args, astar_args)
    sim.start_simulation()
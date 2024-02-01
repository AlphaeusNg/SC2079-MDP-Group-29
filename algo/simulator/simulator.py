import pygame
import numpy as np
from sys import exit
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__ + '\..')))

from objects.Border import Border, VirtualBorderWall
from objects.Obstacle import Obstacle, VirtualWall
from objects.OccupancyMap import OccupancyMap
from pathfinding.hybrid_astar import HybridAStar
import utils
from typing import List
import constants as c

class Simulator:
    def __init__(self, obstacles:List[Obstacle]):
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
        
        left_border_wall = VirtualBorderWall(15*c.MAP_WIDTH/200, c.MAP_HEIGHT, 0, 0)
        right_border_wall = VirtualBorderWall(15*c.MAP_WIDTH/200, c.MAP_HEIGHT, 
                                               c.MAP_WIDTH - 15*c.MAP_WIDTH/200, 0)
        top_border_wall = VirtualBorderWall(c.MAP_WIDTH, 15*c.MAP_HEIGHT/200, 0, 0)
        bottom_border_wall = VirtualBorderWall(c.MAP_WIDTH, 15*c.MAP_HEIGHT/200, 
                                               0, c.MAP_HEIGHT - 15*c.MAP_HEIGHT/200)
        

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
        pygame.init()

        map = OccupancyMap(obstacles)
        algo = HybridAStar(map, x_f=120, y_f=160, theta_f=np.pi, gearChangeCost=10, steeringChangeCost=5, 
                           L=39.25/8, simulate=True, heuristic='euclidean')
        path, pathHistory = algo.find_path()

        for node in path:
            print(f"Current Node (x:{node.x:.2f}, y: {node.y:.2f}, " +
                f"theta: {node.theta*180/np.pi:.2f}), Action: {node.prevAction}")

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

            self.draw_path_history(pathHistory)
            self.draw_final_path(path)
            self.screen.blit(self.path_surface, (0, 0))

            pygame.display.update()
            self.clock.tick(1000)
        
    def draw_final_path(self, path):
        points = []
        x, y = utils.coords_to_pixelcoords(x=path[0].parent.x, y=path[0].parent.y)
        points.append((x, y))
        for node in path:
            x, y = utils.coords_to_pixelcoords(x=node.x, y=node.y)
            points.append((x, y))
            pygame.draw.circle(self.path_surface, (255, 0, 0, 255), (x,y), 4)

        pygame.draw.lines(self.path_surface, (0, 0, 0, 255), False, points, width=3)
    
    def draw_path_history(self, pathHistory):

        for node in pathHistory[1:]:
            x0, y0 = utils.coords_to_pixelcoords(x=node.parent.x, y=node.parent.y)
            x1, y1 = utils.coords_to_pixelcoords(x=node.x, y=node.y)
            pygame.draw.line(self.path_surface, (255, 0, 255, 64), (x0, y0), (x1, y1))
        

if __name__ == "__main__":
    obstacles = [Obstacle(10, 10, 'N'), Obstacle(20, 10, 'S'), Obstacle(10, 20, 'E'), Obstacle(20, 20, 'W'), 
                 Obstacle(38, 38, 'N')]

    sim = Simulator(obstacles)
    sim.start_simulation()
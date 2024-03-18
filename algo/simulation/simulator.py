import pygame
import numpy as np
from sys import exit
import os
import sys
import math

sys.path.append(os.path.dirname(os.path.abspath(__file__ + '\..')))

from enumerations import Gear, Steering
from objects.Border import Border, VirtualBorderWall
from objects.Obstacle import Obstacle, VirtualWall
from objects.OccupancyMap import OccupancyMap
from pathfinding.hybrid_astar import HybridAStar
from pathfinding.hamiltonian import Hamiltonian
import pathfinding.pathcommands as pc
from algo.simulation.testing import get_maps
import utils
from typing import List
import constants as c


class Simulator:
    def __init__(self, obstacles: List[Obstacle], hamiltonian_args, astar_args):
        self.hamiltonian_args = hamiltonian_args
        self.astar_args = astar_args
        self.commands = []
        self.car = pygame.image.load(os.path.join("..", "objects", "images", "angle.png"))

        self.screen = pygame.display.set_mode((c.WIDTH, c.HEIGHT))
        self.screen.fill('white')
        pygame.display.set_caption('Algorithm Simulator')
        self.clock = pygame.time.Clock()

        self.map_surface = pygame.Surface((c.MAP_WIDTH, c.MAP_HEIGHT))
        self.map_surface.fill('azure')
        self.start_surface = pygame.Surface((30 * c.MAP_WIDTH / 200, 30 * c.MAP_HEIGHT / 200))
        self.start_surface.fill('aquamarine')

        self.path_surface = pygame.Surface((c.MAP_WIDTH, c.MAP_HEIGHT))
        self.path_surface = self.path_surface.convert_alpha()
        self.path_surface.fill((0, 0, 0, 0))

        left_border = Border(c.BORDER_THICKNESS, c.MAP_HEIGHT + 2 * c.BORDER_THICKNESS,
                             c.MAP_X0 - c.BORDER_THICKNESS, c.MAP_Y0 - c.BORDER_THICKNESS)
        right_border = Border(c.BORDER_THICKNESS, c.MAP_HEIGHT + 2 * c.BORDER_THICKNESS,
                              c.MAP_X0 + c.MAP_WIDTH, c.MAP_Y0 - c.BORDER_THICKNESS)
        top_border = Border(c.MAP_WIDTH + 2 * c.BORDER_THICKNESS, c.BORDER_THICKNESS,
                            c.MAP_X0 - c.BORDER_THICKNESS, c.MAP_Y0 - c.BORDER_THICKNESS)
        bottom_border = Border(c.MAP_WIDTH + 2 * c.BORDER_THICKNESS, c.BORDER_THICKNESS,
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

        left_border_wall = VirtualBorderWall(0 * c.MAP_WIDTH / 200, c.MAP_HEIGHT, 0, 0)
        right_border_wall = VirtualBorderWall(0 * c.MAP_WIDTH / 200, c.MAP_HEIGHT,
                                              c.MAP_WIDTH - 0 * c.MAP_WIDTH / 200, 0)
        top_border_wall = VirtualBorderWall(c.MAP_WIDTH, 0 * c.MAP_HEIGHT / 200, 0, 0)
        bottom_border_wall = VirtualBorderWall(c.MAP_WIDTH, 0 * c.MAP_HEIGHT / 200,
                                               0, c.MAP_HEIGHT - 0 * c.MAP_HEIGHT / 200)

        self.virtual_walls.add(left_border_wall)
        self.virtual_walls.add(right_border_wall)
        self.virtual_walls.add(top_border_wall)
        self.virtual_walls.add(bottom_border_wall)

        self.virtual_wall_surface.blit(left_border_wall.image, left_border_wall.rect.topleft)
        self.virtual_wall_surface.blit(right_border_wall.image, right_border_wall.rect.topleft)
        self.virtual_wall_surface.blit(top_border_wall.image, top_border_wall.rect.topleft)
        self.virtual_wall_surface.blit(bottom_border_wall.image, bottom_border_wall.rect.topleft)

        self.virtual_wall_surface.fill((255, 0, 0, 24), special_flags=pygame.BLEND_RGBA_MIN)

    def start_simulation(self):
        map = OccupancyMap(self.obstacles)
        done = False

        tsp = Hamiltonian(map=map, obstacles=self.obstacles, x_start=self.hamiltonian_args['x_start'],
                          y_start=self.hamiltonian_args['y_start'],
                          theta_start=self.hamiltonian_args['theta_start'],
                          theta_offset=self.hamiltonian_args['theta_offset'],
                          metric=self.hamiltonian_args['metric'],
                          minR=self.hamiltonian_args['minR'])
        checkpoints = tsp.find_nearest_neighbor_path()

        print("Starting simulator...")
        print(f"Optimal path found: {checkpoints}")

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
            self.screen.blit(self.start_surface, (c.MAP_X0, c.MAP_Y0 + c.MAP_HEIGHT - 30 * c.MAP_HEIGHT / 200))
            self.screen.blit(self.car, (c.MAP_X0, c.MAP_Y0 + c.MAP_HEIGHT - 30 * c.MAP_HEIGHT / 200))
            self.borders.draw(self.screen)
            self.obstacles.draw(self.screen)

            colors = [(0, 0, 0, 255), (0, 255, 0, 255), (0, 0, 255, 255), (0, 255, 255, 255)]

            if not done:
                for idx, checkpoint in enumerate(checkpoints):
                    print(f"Calculating path from {current_pos} to {checkpoint}")
                    algo = HybridAStar(map, x_0=current_pos[0], y_0=current_pos[1], theta_0=current_pos[2],
                                       x_f=checkpoint[0], y_f=checkpoint[1], theta_f=checkpoint[2],
                                       steeringChangeCost=self.astar_args['steeringChangeCost'],
                                       gearChangeCost=self.astar_args['gearChangeCost'],
                                       L=self.astar_args['L'], minR=self.astar_args['minR'],
                                       heuristic=self.astar_args['heuristic'], simulate=self.astar_args['simulate'],
                                       thetaBins=self.astar_args['thetaBins'])

                    path, pathHistory = algo.find_path()
                    allPaths.append(path)
                    numNodes += len(path)
                    current_pos = (path[-1].x, path[-1].y, path[-1].theta)

                    pc.print_path(path)
                    commands, droid = pc.construct_path(path, self.astar_args['L'], self.astar_args['minR'])
                    print(f"Commands: {commands}")
                    print(f"APath: {droid}")
                    self.commands.extend(commands)

                    color = colors[idx % len(colors)]
                    # self.draw_final_path(path, color)
                    # self.screen.blit(self.path_surface, (0, 0))
                    for node in path:
                        pygame.display.update()
                        x, y = utils.coords_to_pixelcoords(x=node.x, y=node.y)
                        car_rect = self.car.get_rect(center=(x, y))
                        rotated_car = pygame.transform.rotate(self.car, math.degrees(node.theta))

                        self.screen.fill((255, 255, 255))
                        self.screen.blit(self.map_surface, (c.MAP_X0, c.MAP_Y0))
                        self.screen.blit(self.virtual_wall_surface, (c.MAP_X0, c.MAP_Y0))
                        self.screen.blit(self.start_surface,
                                         (c.MAP_X0, c.MAP_Y0 + c.MAP_HEIGHT - 30 * c.MAP_HEIGHT / 200))
                        self.borders.draw(self.screen)
                        self.obstacles.draw(self.screen)
                        self.draw_final_path(path, color)
                        self.screen.blit(self.path_surface, (0, 0))
                        self.screen.blit(rotated_car, car_rect)

                        pygame.time.delay(30)

                    pygame.display.update()
                    self.clock.tick(1000)

                done = True
                print(f"Total path length: {numNodes * self.astar_args['L']}cm")
                print(self.commands)

            # pygame.display.update()
            # self.draw_path_history(pathHistory)

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
        # Draw X on pygame
        size = 10
        pygame.draw.line(self.path_surface, (255, 0, 0, 255), (x - size, y - size), (x + size, y + size), 5)
        pygame.draw.line(self.path_surface, (255, 0, 0, 255), (x - size, y + size), (x + size, y - size), 5)

    def draw_path_history(self, pathHistory):

        for node in pathHistory[1:]:
            x0, y0 = utils.coords_to_pixelcoords(x=node.parent.x, y=node.parent.y)
            x1, y1 = utils.coords_to_pixelcoords(x=node.x, y=node.y)
            pygame.draw.line(self.path_surface, (255, 0, 255, 64), (x0, y0), (x1, y1))


if __name__ == "__main__":
    test_maps = get_maps()
    map = test_maps[5][:8]

    hamiltonian_args = {'obstacles': map, 'x_start': 5, 'y_start': 15, 'theta_start': 0,
                        'theta_offset': -np.pi / 2, 'metric': 'euclidean', 'minR': 26.5}
    astar_args = {'steeringChangeCost': 10, 'gearChangeCost': 10, 'L': 26.5 * np.pi / 4 / 5,
                  'minR': 26.5, 'heuristic': 'euclidean', 'simulate': False, 'thetaBins': 24}

    sim = Simulator(map, hamiltonian_args, astar_args)
    sim.start_simulation()

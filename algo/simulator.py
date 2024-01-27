import pygame
from sys import exit
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__ + '\..')))

from objects.Border import Border, VirtualBorderWall
from Obstacle import Obstacle, VirtualWall
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

            pygame.display.update()
            self.clock.tick(30)

if __name__ == "__main__":
    obstacles = [Obstacle(10, 10, 'N'), Obstacle(20, 10, 'S'), Obstacle(10, 20, 'E'), Obstacle(20, 20, 'W'), 
                 Obstacle(38, 38, 'N')]
    sim = Simulator(obstacles)
    sim.start_simulation()
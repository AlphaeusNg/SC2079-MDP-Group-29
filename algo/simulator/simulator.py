import pygame
from sys import exit
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__ + '\..')))

from objects.Border import Border
from objects.Obstacle import Obstacle

# simulation parameters
WIDTH = 1200
HEIGHT = 900

MAP_WIDTH = 800
MAP_HEIGHT = 800
MAP_X0 = 50
MAP_Y0 = 50

BORDER_THICKNESS = 5

class Simulator:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.screen.fill('white')
        pygame.display.set_caption('Algorithm Simulator')
        self.clock = pygame.time.Clock()



        self.map_surface = pygame.Surface((MAP_WIDTH, MAP_HEIGHT))
        self.map_surface.fill('azure')
        self.start_surface = pygame.Surface((30*MAP_WIDTH/200, 30*MAP_HEIGHT/200))
        self.start_surface.fill('aquamarine')

        self.left_border = Border(BORDER_THICKNESS, MAP_HEIGHT + 2*BORDER_THICKNESS, 
                            MAP_X0 - BORDER_THICKNESS, MAP_Y0 - BORDER_THICKNESS)
        self.right_border = Border(BORDER_THICKNESS, MAP_HEIGHT + 2*BORDER_THICKNESS, 
                            MAP_X0 + MAP_WIDTH, MAP_Y0 - BORDER_THICKNESS)
        self.top_border = Border(MAP_WIDTH + 2*BORDER_THICKNESS, BORDER_THICKNESS, 
                            MAP_X0 - BORDER_THICKNESS, MAP_Y0 - BORDER_THICKNESS)
        self.bottom_border = Border(MAP_WIDTH + 2*BORDER_THICKNESS, BORDER_THICKNESS, 
                            MAP_X0 - BORDER_THICKNESS, MAP_Y0 + MAP_HEIGHT)


        self.borders = pygame.sprite.Group()
        self.borders.add(self.left_border)
        self.borders.add(self.right_border)
        self.borders.add(self.top_border)
        self.borders.add(self.bottom_border)

        self.obstacles = pygame.sprite.Group()
        self.obstacles.add(Obstacle(10, 10, 'N'))
        self.obstacles.add(Obstacle(20, 10, 'S'))
        self.obstacles.add(Obstacle(10, 20, 'E'))
        self.obstacles.add(Obstacle(20, 20, 'W'))

    def start_simulation(self):
        pygame.init()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
            
            self.screen.blit(self.map_surface, (MAP_X0, MAP_Y0))
            self.screen.blit(self.start_surface, (MAP_X0, MAP_Y0 + MAP_HEIGHT - 30*MAP_HEIGHT/200))
            self.borders.draw(self.screen)
            self.obstacles.draw(self.screen)

            pygame.display.update()
            self.clock.tick(30)

if __name__ == "__main__":
    sim = Simulator()
    sim.start_simulation()
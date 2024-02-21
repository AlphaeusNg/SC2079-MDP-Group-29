import numpy as np
import utils
import pygame
import constants as c

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x_g: int, y_g: int, facing: str) -> None:
        """Obstacle constructor

        Args:
            x_g (int): x coordinate of obstacle (bottom left grid)
            y_g (int): y coordinate of obstacle (bottom left grid)
            facing (str): {'N', 'S', 'E', 'W'} direction of image i.e. which direction agent needs to face to see image

        Parameters:
            theta (float): direction of image in radians
        """
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('algo/objects/images/obstacle.png')
        self.rect = self.image.get_rect()
        self.rect.bottomleft = utils.coords_to_pixelcoords(x_g, y_g)

        self.x_g = x_g
        self.y_g = y_g
        self.facing = facing
        self.theta = utils.facing_to_rad(facing)

        if facing == 'E':
            self.image = pygame.transform.rotate(self.image, 270)
        elif facing == 'S':
            self.image = pygame.transform.rotate(self.image, 180)
        elif facing == 'W':
            self.image = pygame.transform.rotate(self.image, 90)

class VirtualWall(pygame.sprite.Sprite):
    def __init__(self, x_g: int, y_g: int) -> None:
        pygame.sprite.Sprite.__init__(self)
        self.x_g = x_g - 3
        self.y_g = y_g - 3
        self.width = (min(self.x_g + 8, c.GRID_SIZE) - self.x_g)*200/c.GRID_SIZE*c.MAP_WIDTH/200
        self.height = (min(self.y_g + 8, c.GRID_SIZE) - self.y_g)*200/c.GRID_SIZE*c.MAP_HEIGHT/200
        
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill((255, 0, 0, 24))
        self.rect = self.image.get_rect()
        self.rect.bottomleft = utils.coords_to_pixelcoords(self.x_g, self.y_g)

        
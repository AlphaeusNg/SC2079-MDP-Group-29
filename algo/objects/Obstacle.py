import numpy as np
import utils
import pygame

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
            self.image = pygame.transform.rotate(self.image, 90)
        elif facing == 'S':
            self.image = pygame.transform.rotate(self.image, 180)
        elif facing == 'W':
            self.image = pygame.transform.rotate(self.image, 270)


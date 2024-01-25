import pygame

class Border(pygame.sprite.Sprite): 
    def __init__(self, width, height, x, y): 
        super().__init__() 
  
        self.image = pygame.Surface([width, height]) 
        self.image.fill('black')
  
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
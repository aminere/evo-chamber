
import pygame

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__() 
        self.surf = pygame.Surface((20, 20))
        self.surf.fill((128,255,40))
        self.rect = self.surf.get_rect(center = (10, 440))

    

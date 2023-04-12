

import pygame
import map

class Character:
    def __init__(self, name, yOffset):        
        self.sprites = {
            'topLeft': pygame.image.load(f'{name}-top-left.png'),
            'topRight': pygame.image.load(f'{name}-top-right.png'),
            'bottomLeft': pygame.image.load(f'{name}-bottom-left.png'),
            'bottomRight': pygame.image.load(f'{name}-bottom-right.png')
        }

        self.yOffset = yOffset

    def draw(self, worldPos, map):
        print("draw")

    


import pygame as pg
import singletons
from enum import Enum

class Button:
    def __init__(self, image, position, action):
        self.image = image        
        self.position = position
        self.action = action
        self.pressed = False
        self.hovered = False
        self.selected = False
        self.rect = pg.Rect(position, image.get_size())

    def draw(self, screen):

        yOffset = 0
        alpha = 255
        if (self.pressed):
            yOffset = 3
        elif (self.hovered):
            alpha = 128
        
        self.image.set_alpha(alpha)
        
        screen.blit(self.image, (self.position[0], self.position[1] + yOffset))

        if (self.selected):
            pg.draw.rect(screen, (255, 255, 0), self.rect, 2)

        # text = self.font.render("Hello World", True, (255, 255, 255))
        # screen.blit(text, (0, 0))


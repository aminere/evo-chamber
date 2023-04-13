
import pygame as pg
import singletons
from enum import Enum

class Button:
    def __init__(self, image, position):
        self.image = image        
        self.position = position
        # self.callback = callback
        self.pressed = False
        self.hovered = False
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

        # text = self.font.render("Hello World", True, (255, 255, 255))
        # screen.blit(text, (0, 0))


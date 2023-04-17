
import pygame as pg
import singletons
from enum import Enum

class Button:
    def __init__(self, image, position, action, visible = True):
        self.image = image        
        self.position = position
        self.action = action
        self.pressed = False
        self.hovered = False
        self.selected = False
        self.disabled = False
        self.rect = pg.Rect(position, image.get_size())
        self.visible = visible

    def draw(self, screen):

        if (not self.visible):
            return

        yOffset = 0
        alpha = 255
        if (self.disabled):
            alpha = 128
        if (self.pressed):
            yOffset = 3
            alpha = 128
        elif (self.hovered):
            yOffset = -3
        
        self.image.set_alpha(alpha)
        
        screen.blit(self.image, (self.position[0], self.position[1] + yOffset))

        if (self.selected and not self.disabled):
            padding = 6
            rc = self.rect.left - padding, self.rect.top - padding + yOffset, self.rect.width + padding * 2, self.rect.height + padding * 2            
            pg.draw.rect(screen, (255, 255, 0), rc, 2)

        # text = self.font.render("Hello World", True, (255, 255, 255))
        # screen.blit(text, (0, 0))


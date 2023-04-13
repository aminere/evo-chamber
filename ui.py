
import pygame as pg
import config
import button

class UI:
    def __init__(self):
        self.font = pg.font.SysFont("Arial", 32)

        height = config.bottomUI['height']
        self.rect = pg.Rect(0, config.screenSize[1] - height, config.screenSize[0], height)

        topEdge = config.screenSize[1] - height
        self.buttons = [
            button.Button(pg.image.load('images/ui/build.png'), (0, topEdge))
        ]

    def update(self):
        for button in self.buttons:
            if (button.rect.collidepoint(pg.mouse.get_pos())):
                button.hovered = True
            else:
                button.hovered = False

    def draw(self, screen):
        pg.draw.rect(screen, config.bottomUI['bgColor'], self.rect)

        for button in self.buttons:
            button.draw(screen)

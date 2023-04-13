
import pygame as pg
import config

class UI:
    def __init__(self):
        self.font = pg.font.SysFont("Arial", 32)

        height = config.bottomUI['height']
        self.rect = pg.Rect(0, config.screenSize[1] - height, config.screenSize[0], height)

    def draw(self, screen):
        pg.draw.rect(screen, (0, 0, 0), self.rect)
        # text = self.font.render("Hello World", True, (255, 255, 255))
        # screen.blit(text, (0, 0))

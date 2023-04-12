
import pygame as pg
import singletons
from enum import Enum

class State (Enum):
    NORMAL = 1
    HOVER = 2
    PRESSED = 3

class Button:
    def __init__(self, x, y, image, callback):
        self.x = x
        self.y = y
        self.image = image
        self.callback = callback
        self.state = State.NORMAL

    def draw(self):
        screen = singletons._game.screen
        if (self.state == State.NORMAL):
            pg.draw.rect(screen, (0, 0, 0), (self.x, self.y, 100, 100))


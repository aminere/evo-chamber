

import pygame
import tween
from enum import Enum

import singletons
import utils
import config

class State (Enum):
    IDLE = 1
    MOVING = 2    

class Character:
    def __init__(self, name, position, yOffset):        
        # self.sprites = {
        #     'topLeft': pygame.image.load(f'images/{name}-top-left.png'),
        #     'topRight': pygame.image.load(f'images/{name}-top-right.png'),
        #     'bottomLeft': pygame.image.load(f'images/{name}-bottom-left.png'),
        #     'bottomRight': pygame.image.load(f'images/{name}-bottom-right.png')
        # }
        self.sprite = pygame.image.load(f'images/{name}.png')
        self.orientation = 'bottomRight'
        self.position = position
        self.yOffset = yOffset
        self.xOffset = (config.tileSize[0] - self.sprite.get_width()) // 2
        self.state = State.IDLE
        self.moveQueue = None

    def update(self, dt):
        if (self.state == State.MOVING):
            self.position = utils.lerp2d_InOutCubic(self.source, self.destination, self.interpolator)
            self.interpolator += dt
            if (self.interpolator >= 1.0):
                self.interpolator = 1.0
                self.position = self.destinationTile
                self.state = State.IDLE
        elif (self.state == State.IDLE):
            if (self.moveQueue != None):
                self.moveTo(self.moveQueue)
                self.position = utils.lerp2d_InOutCubic(self.source, self.destination, self.interpolator)
                self.moveQueue = None
                    

    def draw(self, surface):

        game = singletons._game
        screenPos = None
        if (self.state == State.MOVING):
            screenPos = self.position
        else:
            screenPos = utils.worldToScreen(self.position)        
        
        surface.blit(
            # self.sprites[self.orientation],
            self.sprite,
            (
                screenPos[0] + game.cameraPos[0] + self.xOffset,
                screenPos[1] + game.cameraPos[1] - self.yOffset
            )
        )

    def moveTo(self, position):
        if (self.state == State.MOVING):
            self.moveQueue = position
            return
        
        dx = position[0] - self.position[0]
        dy = position[1] - self.position[1]

        if (abs(dx) > abs(dy)):
            if (dx > 0):
                self.orientation = 'bottomRight'
            else:
                self.orientation = 'topLeft'
        else:
            if (dy > 0):
                self.orientation = 'bottomLeft'
            else:
                self.orientation = 'topRight'                  

        self.source = utils.worldToScreen(self.position)
        self.destination = utils.worldToScreen(position)
        self.destinationTile = position
        self.interpolator = 0.0
        self.state = State.MOVING
        
    

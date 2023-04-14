

import pygame
import tween
from enum import Enum

import singletons
import utils
import config
import linkedlist

class State (Enum):
    IDLE = 1
    GOING_TO_WORK = 2
    WORKING = 3
    GOING_HOME = 4

class Character:
    def __init__(self, name, startingPos, yOffset):        
        # self.sprites = {
        #     'topLeft': pygame.image.load(f'images/{name}-top-left.png'),
        #     'topRight': pygame.image.load(f'images/{name}-top-right.png'),
        #     'bottomLeft': pygame.image.load(f'images/{name}-bottom-left.png'),
        #     'bottomRight': pygame.image.load(f'images/{name}-bottom-right.png')
        # }
        self.sprite = pygame.image.load(f'images/{name}.png')
        self.orientation = 'bottomRight'
        self.startingPos = startingPos
        self.position = startingPos
        self.yOffset = yOffset
        self.xOffset = (config.tileSize[0] - self.sprite.get_width()) // 2
        self.state = State.IDLE
        self.actionQueue = linkedlist.LinkedList()
        self.moveQueue = None

    def update(self, dt):
        if (self.state == State.GOING_TO_WORK):
            self.position = utils.lerp2d_InOutCubic(self.source, self.destination, self.interpolator)
            self.interpolator += dt
            if (self.interpolator >= 1.0):
                self.interpolator = 1.0
                self.position = self.destinationTile
                self.state = State.IDLE
        elif self.state == State.WORKING:
            pass
        elif self.state == State.GOING_HOME:
            pass
        elif (self.state == State.IDLE):
            if (self.moveQueue != None):
                self.moveTo(self.moveQueue)
                self.position = utils.lerp2d_InOutCubic(self.source, self.destination, self.interpolator)
                self.moveQueue = None

        # plough finished
        # self.tiles[index] = (ploughedTile, 0, None)
        #                         self.updateCoins(-config.ploughCost)
        #                         self.redrawTiles(index)
        #                         self.lastChangedTile = index

    def draw(self, surface):

        game = singletons._game
        screenPos = None
        if (self.state != State.IDLE):
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

    def queueAction(self, action, tileIndex):
        self.actionQueue.append((action, tileIndex))
        pass

    def updateMove(self, dt):
        self.position = utils.lerp2d_InOutCubic(self.source, self.destination, self.interpolator)
        self.interpolator += dt
        if (self.interpolator >= 1.0):
            self.interpolator = 1.0
            self.position = self.destinationTile
            self.state = State.IDLE


    

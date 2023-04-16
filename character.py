

import pygame
# import tween
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
    def __init__(self, name, startingPos, yOffset, area):        
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
        self.area = area
        self.motionPosition = None
        self.yOffset = yOffset
        self.xOffset = (config.tileSize[0] - self.sprite.get_width()) // 2
        self.state = State.IDLE
        self.actionTile = None
        self.action = None
        self.actionQueue = linkedlist.LinkedList()
        # self.moveQueue = None

    def update(self, dt):
        game = singletons._game
        area = self.area
        if (self.state == State.GOING_TO_WORK):
            arrived = self.updateMotion(dt)
            if (arrived):
                self.state = State.WORKING
                area.wipTiles.delete(self.actionTile)
        elif self.state == State.WORKING:            
            tile = area.tiles[self.actionTile]
            if (self.action == 'plough'):
                tile.state = config.ploughedTile
                area.redrawTiles(self.actionTile)                
            elif (self.action == 'plant'):
                tile.state = config.plantedTile
                area.redrawTiles(self.actionTile)             
                area.plantedTiles.append(self.actionTile)
            elif (self.action == 'water'):
                if tile.state == config.fireTile:
                    tile.state = config.stoneTile
                    area.redrawTiles(self.actionTile)
                    area.fireTiles.delete(self.actionTile)
                    area.plantedTiles.delete(self.actionTile)
                else:
                    tile.time = config.growDuration
            elif (self.action == 'harvest'):
                tile.state = config.stoneTile
                game.updateCoins(config.harvestGain)
                area.redrawTiles(self.actionTile)
                area.plantedTiles.delete(self.actionTile)
                area.fireTiles.delete(self.actionTile)
            elif (self.action == 'pick'):
                tile.state = config.rawTile
                area.redrawTiles(self.actionTile)

            tile.action = None

            if (self.actionQueue.head != None):
                self.state = State.IDLE
            else:
                self.moveTo(utils.localToIndex(self.startingPos))
                self.state = State.GOING_HOME            

        elif self.state == State.GOING_HOME:
            arrived = self.updateMotion(dt)
            if (arrived):
                self.state = State.IDLE
        elif (self.state == State.IDLE):
            if (self.actionQueue.head != None):
                action, tileIndex = self.actionQueue.head.data
                self.moveTo(tileIndex)
                self.action = action
                self.actionTile = tileIndex
                self.actionQueue.deleteHead()
                self.state = State.GOING_TO_WORK       

    def draw(self, surface, areaPos):

        ax, ay = areaPos
        game = singletons._game
        if (self.motionPosition != None):
            screenPos = (self.motionPosition[0] + ax, self.motionPosition[1] + ay)
        else:
            sx, sy = utils.worldToScreen(self.position)
            screenPos = (sx + ax, sy + ay)
        
        surface.blit(
            # self.sprites[self.orientation],
            self.sprite,
            (
                screenPos[0] - game.cameraPos[0] + self.xOffset,
                screenPos[1] - game.cameraPos[1] - self.yOffset
            )
        )

    def moveTo(self, tileIndex):
        # if (self.state == State.MOVING):
        #     self.moveQueue = position
        #     return
        x, y = utils.indexToLocal(tileIndex)
        # dx = x - self.position[0]
        # dy = y - self.position[1]
        # if (abs(dx) > abs(dy)):
        #     if (dx > 0):
        #         self.orientation = 'bottomRight'
        #     else:
        #         self.orientation = 'topLeft'
        # else:
        #     if (dy > 0):
        #         self.orientation = 'bottomLeft'
        #     else:
        #         self.orientation = 'topRight'
        self.source = utils.worldToScreen(self.position)
        self.destination = utils.worldToScreen((x, y))
        self.destinationTile = (x, y)
        self.interpolator = 0.0
        self.motionPosition = self.source

    def queueAction(self, action, tileIndex):
        self.actionQueue.append((action, tileIndex))

    def updateMotion(self, dt):
        self.motionPosition = utils.lerp2d_InOutCubic(self.source, self.destination, self.interpolator)
        self.interpolator += dt * config.workerSpeed
        if (self.interpolator >= 1.0):
            self.interpolator = 1.0            
            self.position = self.destinationTile
            self.motionPosition = None
            return True
        return False


    

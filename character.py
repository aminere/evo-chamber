

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
        self.motionPosition = None
        self.yOffset = yOffset
        self.xOffset = (config.tileSize[0] - self.sprite.get_width()) // 2
        self.state = State.IDLE
        self.actionTile = None
        self.action = None
        self.actionQueue = linkedlist.LinkedList()
        # self.moveQueue = None

    def update(self, dt):
        if (self.state == State.GOING_TO_WORK):
            arrived = self.updateMotion(dt)
            if (arrived):
                self.state = State.WORKING
        elif self.state == State.WORKING:
            game = singletons._game
            if (self.action == 'plough'):
                game.tiles[self.actionTile] = (config.ploughedTile, 0, None)
                game.updateCoins(-config.ploughCost)
                game.redrawTiles(self.actionTile)
                game.lastChangedTile = self.actionTile
            elif (self.action == 'plant'):
                game.tiles[self.actionTile] = (config.plantedTile, 0, None)
                game.updateCoins(-config.plantCost)
                game.redrawTiles(self.actionTile)             
                game.plantedTiles.append(self.actionTile)
                game.lastChangedTile = self.actionTile
            elif (self.action == 'water'):
                tileState, _, _ = game.tiles[self.actionTile]
                game.tiles[self.actionTile] = tileState, config.growDuration, None
                game.updateCoins(-config.waterCost)
                game.lastChangedTile = self.actionTile
            elif (self.action == 'harvest'):
                game.tiles[self.actionTile] = (config.stoneTile, 0, None)
                game.updateCoins(config.harvestGain)
                game.redrawTiles(self.actionTile)             
                game.plantedTiles.delete(self.actionTile)
                game.lastChangedTile = self.actionTile
            elif (self.action == 'pick'):
                game.tiles[self.actionTile] = (config.rawTile, 0, None)
                game.updateCoins(-config.pickCost)
                game.redrawTiles(self.actionTile)
                game.lastChangedTile = self.actionTile                
                        
            if (self.actionQueue.head != None):
                self.state = State.IDLE
            else:
                self.moveTo(utils.worldToIndex(self.startingPos))
                self.state = State.GOING_HOME            

        elif self.state == State.GOING_HOME:
            arrived = self.updateMotion(dt)
            if (arrived):
                self.state = State.IDLE
        elif (self.state == State.IDLE):
            if (self.actionQueue.head != None):
                action, tileIndex = self.actionQueue.head.data
                print(f'Action: {action}, tileIndex: {tileIndex}')
                self.moveTo(tileIndex)
                self.action = action
                self.actionTile = tileIndex
                self.actionQueue.deleteHead()
                self.state = State.GOING_TO_WORK       

    def draw(self, surface):

        game = singletons._game
        if (self.motionPosition != None):
            screenPos = self.motionPosition
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

    def moveTo(self, tileIndex):
        # if (self.state == State.MOVING):
        #     self.moveQueue = position
        #     return
        x, y = utils.indexToWorld(tileIndex)
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
        pass

    def updateMotion(self, dt):
        self.motionPosition = utils.lerp2d_InOutCubic(self.source, self.destination, self.interpolator)
        self.interpolator += dt * config.workerSpeed
        if (self.interpolator >= 1.0):
            self.interpolator = 1.0            
            self.position = self.destinationTile
            self.motionPosition = None
            return True
        return False


    

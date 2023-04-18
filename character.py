

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
        self.workingTime = 0
        # self.moveQueue = None

        self.salaryAnimTime = 0
        self.salaryAnimActive = False

    def update(self, dt):
        game = singletons._game
        area = self.area
        if (self.state == State.GOING_TO_WORK):
            arrived = self.updateMotion(dt)
            if (arrived):
                self.state = State.WORKING
                self.workingTime = 0
                # size = area.wipTiles.size
                area.wipTiles.delete(self.actionTile)
                # if (area.wipTiles.size != size - 1):
                #     print("invalid wip tile size")
        elif self.state == State.WORKING: 
            if self.workingTime >= config.workDuration:
                tile = area.tiles[self.actionTile]
                if (self.action == 'plough'):
                    tile.state = config.ploughedTile
                    area.redrawTiles(self.actionTile)     
                    game.workCompleted.play()           
                elif (self.action == 'plant'):
                    tile.state = config.plantedTile
                    area.redrawTiles(self.actionTile)
                    area.plantedTiles.append(self.actionTile)
                    game.workCompleted.play()
                elif (self.action == 'water'):
                    if tile.state == config.fireTile:
                        tile.state = config.stoneTile
                        area.redrawTiles(self.actionTile)
                        area.fireTiles.delete(self.actionTile)
                        area.plantedTiles.delete(self.actionTile)
                    else:
                        tile.time = config.growDuration
                    game.workCompleted.play()
                elif (self.action == 'harvest'):
                    tile.state = config.stoneTile
                    if not tile.costAnimActive:
                        tile.startCostAnim(config.harvestGain)
                        area.animatedTiles.append(self.actionTile)
                    game.updateCoins(config.harvestGain)
                    area.redrawTiles(self.actionTile)
                    area.plantedTiles.delete(self.actionTile)
                    game.updateAffordability(tile)                    
                    game.positiveSound.play()
                    game.totalHarvests += 1
                elif (self.action == 'pick'):
                    tile.state = config.rawTile
                    area.redrawTiles(self.actionTile)
                    game.workCompleted.play()
                else:
                    print(f"invalid action: {self.action}")

                tile.action = None
                # if (self.actionQueue.head != None):
                if len(self.actionQueue.arr) > 0:
                    self.state = State.IDLE
                else:
                    self.moveTo(utils.localToIndex(self.startingPos))
                    self.state = State.GOING_HOME
            else:
                self.workingTime += dt
        elif self.state == State.GOING_HOME:
            arrived = self.updateMotion(dt)
            if (arrived):
                self.state = State.IDLE
        elif (self.state == State.IDLE):
            if len(self.actionQueue.arr) > 0:
            # if (self.actionQueue.head != None):
                action, tileIndex = self.actionQueue.arr[0]#.head.data
                self.moveTo(tileIndex)
                self.action = action
                self.actionTile = tileIndex
                self.actionQueue.deleteHead()
                self.state = State.GOING_TO_WORK

        # salary anim
        if (self.salaryAnimActive):
            self.salaryAnimTime += dt
            if (self.salaryAnimTime > config.costAnimDuration):                
                self.salaryAnimActive = False

    def draw(self, surface, areaPos):

        ax, ay = areaPos
        game = singletons._game
        if (self.motionPosition != None):
            screenPos = (self.motionPosition[0] + ax, self.motionPosition[1] + ay)
        else:
            sx, sy = utils.worldToScreen(self.position)
            screenPos = (sx + ax, sy + ay)
        
        characterPos = (screenPos[0] - game.cameraPos[0] + self.xOffset, screenPos[1] - game.cameraPos[1] - self.yOffset)
        surface.blit(
            # self.sprites[self.orientation],
            self.sprite,
            characterPos
        )

        # show salary indicator
        if (self.salaryAnimActive):
            factor = self.salaryAnimTime / config.costAnimDuration
            positionY = utils.lerp_InOutCubic(0, -config.costAnimYLength, factor)
            alpha = utils.lerp_InOutCubic(255, 0, factor)
            rc = game.ui.salaryText.get_rect(center=(characterPos[0] + self.sprite.get_width() / 2, characterPos[1] - config.costOffsetY + positionY))        
            game.ui.salaryText.set_alpha(int(alpha))
            surface.blit(game.ui.salaryText, rc)

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

    def startSalaryAnim(self):
        self.salaryAnimActive = True
        self.salaryAnimTime = 0

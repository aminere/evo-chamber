
import pygame as pg
import itertools

import config
import utils
import character
import ui
import linkedlist
import math

rawTile = 0
ploughedTile = rawTile + 1
plantedTile = ploughedTile + 1
readyTile = plantedTile + 2
stoneTile = readyTile + 1
tileSprites = [
    pg.image.load('images/tile-grass.png'), # raw
    pg.image.load('images/tile-ground.png'), # ploughed
    pg.image.load('images/tile-ground2.png'), # planted
    pg.image.load('images/tile-ground3.png'), # planted
    pg.image.load('images/tile-ground4.png'), # ready
    pg.image.load('images/tile-stone.png'), # stone
]

class Game:
    def __init__(self):
        self.screen = pg.display.set_mode(size=config.screenSize)
        self.clock = pg.time.Clock()
        self.dt = 0.0
        self.cameraPos = 0.0, 0.0
        self.selected = -1, -1

        self.tileMask = pg.image.load('images/tile-mask.png')
        self.tileSelected = pg.image.load('images/tile-selected.png')
        self.workerTile = pg.image.load('images/tile-worker.png')
        self.tileSelectedRed = pg.image.load('images/tile-selected-red.png')
        self.tileWip = pg.image.load('images/tile-wip.png')
        # self.tileSelectedRed.set_alpha(128)
        # self.harvestIndicator = pg.image.load('images/ui/harvest-indicator.png')        

        self.tilesSurface = pg.Surface(config.mapSize)

        tileCount = config.worldSize[0] * config.worldSize[1]
        self.tiles = list(itertools.repeat((rawTile, 0, None), tileCount))

        self.origin = (config.worldSize[0] - 1) * config.tileSize[0] // 2, 0

        # start with one worker        
        self.workers = []
        self.addWorker(config.firstWorkerPos)
        # self.addWorker((5, 5))     

        self.ui = ui.UI()
        self.action = None
        self.coins = config.coins
        self.plantedTiles = linkedlist.LinkedList()
        # self.readyToHarvestTiles = linkedlist.LinkedList()
        self.lastChangedTile = None
        self.updateCoins(0)

        # generate map
        self.tilesSurface.fill(config.bgColor)
        for y in range(config.worldSize[1]):
            for x in range(config.worldSize[0]):
                sx, sy = utils.worldToScreen((x, y))
                tile = self.tiles[utils.getTileIndex((x, y))]
                (_, _, worker) = tile
                if (worker != None):
                    self.tilesSurface.blit(self.workerTile, (sx, sy))
                else:
                    self.tilesSurface.blit(tileSprites[0], (sx, sy))

    def update(self):

        for worker in self.workers:
            worker.update(self.dt)        

        # camera
        margin = 80
        mouseX, mouseY = pg.mouse.get_pos()
        bottomEdge = config.screenSize[1] - 50
        if (self.ui.hoveredButton == None):
            if (mouseX > config.screenSize[0] - config.scrollMargin):
                self.cameraPos = (self.cameraPos[0] - config.scrollSpeed * self.dt, self.cameraPos[1])
                self.cameraPos = (max(self.cameraPos[0], config.screenSize[0] - self.tilesSurface.get_width() - margin), self.cameraPos[1])
            elif (mouseX < config.scrollMargin):
                self.cameraPos = (self.cameraPos[0] + config.scrollSpeed * self.dt, self.cameraPos[1])
                self.cameraPos = (min(self.cameraPos[0], margin), self.cameraPos[1])            
            if (mouseY > bottomEdge):            
                self.cameraPos = (self.cameraPos[0], self.cameraPos[1] - config.scrollSpeed * self.dt)
                self.cameraPos = (self.cameraPos[0], max(self.cameraPos[1], bottomEdge - self.tilesSurface.get_height() - margin))
            elif (mouseY < config.scrollMargin):
                self.cameraPos = (self.cameraPos[0], self.cameraPos[1] + config.scrollSpeed * self.dt)    
                self.cameraPos = (self.cameraPos[0], min(self.cameraPos[1], margin))

        self.dt = self.clock.tick(config.fps) / 1000
        pg.display.set_caption(f"FPS: {self.clock.get_fps():.2f}")

        self.ui.update()

        # update tiles
        tile = self.plantedTiles.head
        while tile is not None:
            index = tile.data
            (state, time, _) = self.tiles[index]
            if (state == readyTile):
                tile = tile.next
                continue
            time += self.dt
            self.tiles[index] = (state, time, None)
            if (time >= config.growDuration):
                newState = state + 1
                self.tiles[index] = (newState, 0, None)
                self.redrawTiles(index)
                # if (newState == readyTile):
                    # self.readyToHarvestTiles.append(index)
            tile = tile.next

    def draw(self):        
        self.screen.fill(config.bgColor)
        self.screen.blit(self.tilesSurface, self.cameraPos)

        if (self.action != None and self.ui.hoveredButton == None):            
            x, y = self.selected
            if (x >= 0 and y >= 0 and x < config.worldSize[0] and y < config.worldSize[1]):
                sx, sy = utils.worldToScreen(self.selected)
                index = y * config.worldSize[0] + x
                if (index != self.lastChangedTile):
                    allowed = False

                    state, _, worker = self.tiles[index]
                    if (worker != None):
                        allowed = False
                    if (self.action == "harvest"):
                        allowed = state == readyTile
                    elif (self.action == "plough"):
                        allowed = state == rawTile
                    elif (self.action == "plant"):
                        allowed = state == ploughedTile
                    elif (self.action == "water"):
                        allowed = state >= plantedTile and state < readyTile
                    elif (self.action == "pick"):
                        allowed = state == stoneTile
                        
                    tilePos = (sx + self.cameraPos[0], sy + self.cameraPos[1])
                    if (allowed):
                        self.screen.blit(self.tileSelected, tilePos)
                    else:
                        self.screen.blit(self.tileSelectedRed, tilePos)

        # draw harvest indicators
        # tile = self.readyToHarvestTiles.head
        # while tile is not None:
        #     index = tile.data
        #     y = math.floor(index / config.worldSize[0])
        #     x = index - y * config.worldSize[0]
        #     sx, sy = utils.worldToScreen((x, y))
        #     sx += (config.tileSize[0] - self.harvestIndicator.get_width()) // 2
        #     sy -= self.harvestIndicator.get_height()
        #     self.screen.blit(self.harvestIndicator, (sx + self.cameraPos[0], sy + self.cameraPos[1]))
        #     tile = tile.next

        for worker in self.workers:
            worker.draw(self.screen)

        self.ui.draw(self.screen)

    def onMouseMoved(self, x, y):

        # tile selection
        selected, tx, ty = utils.screenToWorld((x, y), self.cameraPos)
        maskColor = self.tileMask.get_at((tx, ty))
        if (maskColor == (255, 0, 0, 255)):
             selected = selected[0] - 1, selected[1]
        elif (maskColor == (0, 255, 0, 255)):
            selected = selected[0], selected[1] - 1
        elif (maskColor == (0, 0, 255, 255)):
            selected = selected[0], selected[1] + 1
        elif (maskColor == (255, 255, 0, 255)):
            selected = selected[0] + 1, selected[1]

        if (selected != self.selected):
            self.selected = selected
            self.lastChangedTile = None

    def onMouseUp(self, button, mousePos):
        if (button == pg.BUTTON_LEFT):

            if (self.ui.pressedButton != None):
                if (self.action == self.ui.pressedButton.action):
                    self.action = None
                else: 
                    self.action = self.ui.pressedButton.action
                self.ui.pressedButton = None
                for button in self.ui.buttons:
                    button.selected = button.action == self.action
                return
            
            if (self.ui.hoveredButton != None):
                return

            if (self.action != None):
                x, y = self.selected
                if (x >= 0 and y >= 0 and x < config.worldSize[0] and y < config.worldSize[1]):
                    index = y * config.worldSize[0] + x                    
                    state, _, worker = self.tiles[index]
                    if (worker != None):
                        pass
                    else:
                        # get closest worker
                        closestWorker = self.getClosestWorker(self.selected)    
                        
                        if self.action == 'harvest':
                            if state == readyTile:
                                # self.queueAction(closestWorker, 'harvest', index)
                                self.tiles[index] = (stoneTile, 0, None)
                                self.updateCoins(config.harvestGain)
                                self.redrawTiles(index)
                                self.plantedTiles.delete(index)
                                # self.readyToHarvestTiles.delete(index)
                                self.lastChangedTile = index
                        elif (self.action == 'plough'):
                            if (state == rawTile):
                                # closestWorker.queueAction('plough', index)
                                self.tiles[index] = (ploughedTile, 0, None)
                                self.updateCoins(-config.ploughCost)
                                self.redrawTiles(index)
                                self.lastChangedTile = index
                      
                        elif (self.action == 'plant'):
                            if (state == ploughedTile):
                                self.tiles[index] = (plantedTile, 0, None)
                                self.updateCoins(-config.plantCost)
                                self.redrawTiles(index)                            
                                self.plantedTiles.append(index)
                                self.lastChangedTile = index
                        elif (self.action == 'water'):
                            if (state >= plantedTile and state < stoneTile):
                                self.tiles[index] = (state, config.growDuration, None)
                                self.updateCoins(-config.waterCost)
                                self.lastChangedTile = index
                        elif (self.action == 'pick'):
                            if (state == stoneTile):
                                self.tiles[index] = (rawTile, 0, None)
                                self.updateCoins(-config.pickCost)
                                self.redrawTiles(index)
                                self.lastChangedTile = index

    def tryUpdateButton(self, button, action, cost):
        updated = False
        if (button.action == action):
            updated = True
            button.disabled = self.coins < cost
            if (button.disabled and self.action == action):
                self.action = None
        return updated

    def updateCoins(self, amount):
        self.coins += amount
        for button in self.ui.buttons:
            if not self.tryUpdateButton(button, 'plough', config.ploughCost):
                if not self.tryUpdateButton(button, 'plant', config.plantCost):
                    self.tryUpdateButton(button, 'water', config.waterCost)
                    
    def redrawTiles(self, index):
        y = math.floor(index / config.worldSize[0])
        startY = max(0, y - 1)
        for _y in range(config.worldSize[1] - startY):
            for _x in range(config.worldSize[0]):
                yCoord = startY + _y
                index = yCoord * config.worldSize[0] + _x
                state, _, worker = self.tiles[index]
                if (worker != None):
                    sprite = self.workerTile
                else:
                    sprite = tileSprites[state]                        
                sx, sy = utils.worldToScreen((_x, yCoord))
                self.tilesSurface.blit(sprite, (sx, sy))

    def addWorker(self, pos):
        worker = character.Character("farmer", pos, 33)
        self.workers.append(worker)
        self.tiles[utils.getTileIndex(pos)] = (rawTile, 0, worker)

    def getClosestWorker(self, pos):
        closestWorker = None
        distToClosestWorker = 999999
        for worker in self.workers:
            dist = utils.distSquared(worker.startingPos, pos)
            if (dist < distToClosestWorker):
                distToClosestWorker = dist
                closestWorker = worker
        return closestWorker   
    


import pygame as pg
import itertools
import math

import config
import utils
import character
import ui
import linkedlist
import tile as Tile

tileSprites = [
    pg.image.load('images/tile-grass.png'), # raw
    pg.image.load('images/tile-ground.png'), # ploughed
    pg.image.load('images/tile-ground2.png'), # planted
    pg.image.load('images/tile-ground3.png'), # planted
    pg.image.load('images/tile-ground4.png'), # ready
    pg.image.load('images/tile-ground4.png'), # on fire
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
        self.fire1 = pg.image.load('images/fire1.png')
        self.tileNoCoins = pg.image.load('images/tile-no-coins.png')
        # self.tileSelectedRed.set_alpha(128)
        # self.harvestIndicator = pg.image.load('images/ui/harvest-indicator.png')        

        self.tilesSurface = pg.Surface(config.mapSize)

        tileCount = config.worldSize[0] * config.worldSize[1]
        self.tiles = []
        for _ in range(tileCount):
            self.tiles.append(Tile.Tile())
        self.origin = (config.worldSize[0] - 1) * config.tileSize[0] // 2, 0

        # start with one worker        
        self.workers = []
        self.addWorker(config.firstWorkerPos)
        # self.addWorker((5, 5))

        self.ui = ui.UI()
        self.action = "plough"
        self.ui.buttons[0].selected = True
        self.actionAllowed = False
        self.selectorInRange = False
        self.coins = config.coins
        self.plantedTiles = linkedlist.LinkedList()
        self.wipTiles = linkedlist.LinkedList()
        self.fireTiles = linkedlist.LinkedList()
        self.lastChangedTile = None
        self.cantAfford = False
        # self.readyToHarvestTiles = linkedlist.LinkedList()
        self.updateCoins(0)

        # generate map
        self.tilesSurface.fill(config.bgColor)
        for y in range(config.worldSize[1]):
            for x in range(config.worldSize[0]):
                sx, sy = utils.worldToScreen((x, y))
                tile = self.tiles[utils.worldToIndex((x, y))]
                if (tile.worker != None):
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
        plantedTile = self.plantedTiles.head
        while plantedTile is not None:
            index = plantedTile.data
            tile = self.tiles[index]            
            if (tile.state == config.readyTile):
                tile.time += self.dt
                if (tile.time >= config.growDuration):
                    tile.time = 0
                    tile.state = config.fireTile
                    self.fireTiles.append(index)
            elif tile.state < config.readyTile:
                tile.time += self.dt
                if (tile.time >= config.growDuration):
                    tile.time = 0
                    newState = tile.state + 1
                    tile.state = newState                    
                    self.redrawTiles(index)                    
            plantedTile = plantedTile.next

    def draw(self):        
        self.screen.fill(config.bgColor)
        self.screen.blit(self.tilesSurface, self.cameraPos)

        # draw wip tiles
        wipTile = self.wipTiles.head
        while wipTile is not None:
            index = wipTile.data
            pos = utils.indexToWorld(index)
            sx, sy = utils.worldToScreen(pos)
            self.screen.blit(self.tileWip, (sx + self.cameraPos[0], sy + self.cameraPos[1]))
            wipTile = wipTile.next

        # draw fire tiles
        fireTile = self.fireTiles.head
        while fireTile is not None:
            index = fireTile.data
            pos = utils.indexToWorld(index)
            sx, sy = utils.worldToScreen(pos)
            self.screen.blit(self.fire1, (sx + self.cameraPos[0], sy + self.cameraPos[1]))
            fireTile = fireTile.next

        if (self.action != None and self.selectorInRange and self.ui.hoveredButton == None):
            sx, sy = utils.worldToScreen(self.selected)
            index = utils.worldToIndex(self.selected)
            if (index != self.lastChangedTile):
                tile = self.tiles[index]
                if (tile.worker == None and tile.action == None):
                    tilePos = (sx + self.cameraPos[0], sy + self.cameraPos[1])
                    if (self.cantAfford):
                        self.screen.blit(self.tileNoCoins, tilePos)
                    elif (self.actionAllowed):
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
            x, y = self.selected
            if (x >= 0 and y >= 0 and x < config.worldSize[0] and y < config.worldSize[1]):                
                index = y * config.worldSize[0] + x
                tile = self.tiles[index]
                self.lastChangedTile = None
                self.actionAllowed = True
                self.cantAfford = False
                if (tile.worker != None or tile.action != None):
                    pass
                elif (self.action == "plough"):
                    self.actionAllowed = tile.state == config.rawTile
                elif (self.action == "plant"):
                    self.actionAllowed = tile.state == config.ploughedTile
                elif (self.action == "water"):
                    self.actionAllowed = (tile.state >= config.plantedTile and tile.state < config.readyTile) or tile.state == config.fireTile
                elif (self.action == "harvest"):
                    self.actionAllowed = tile.state == config.readyTile
                elif (self.action == "pick"):
                    self.actionAllowed = tile.state == config.stoneTile
                self.selectorInRange = True
            else:
                self.selectorInRange = False

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

            if (self.action != None and self.actionAllowed):
                index = utils.worldToIndex(self.selected)
                tile = self.tiles[index]                                
                if (tile.action == None and tile.worker == None):
                    if self.canAfford(self.action):
                        closestWorker = self.getClosestWorker(self.selected)
                        closestWorker.queueAction(self.action, index)
                        tile.action = self.action
                        self.actionAllowed = False
                        self.lastChangedTile = index
                        self.wipTiles.append(index)
                        if (self.action == 'plough'): self.updateCoins(-config.ploughCost)            
                        elif (self.action == 'plant'): self.updateCoins(-config.plantCost)
                        elif (self.action == 'water'): self.updateCoins(-config.waterCost)
                        elif (self.action == 'pick'): self.updateCoins(-config.pickCost)
                    else:
                        self.cantAfford = True

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
                    if not self.tryUpdateButton(button, 'water', config.waterCost):
                        self.tryUpdateButton(button, 'pick', config.pickCost)
                    
    def redrawTiles(self, index):
        y = math.floor(index / config.worldSize[0])
        startY = max(0, y - 1)
        for _y in range(config.worldSize[1] - startY):
            for _x in range(config.worldSize[0]):
                yCoord = startY + _y
                index = yCoord * config.worldSize[0] + _x
                tile = self.tiles[index]
                if (tile.worker != None):
                    sprite = self.workerTile
                else:
                    sprite = tileSprites[tile.state]                        
                sx, sy = utils.worldToScreen((_x, yCoord))
                self.tilesSurface.blit(sprite, (sx, sy))

    def addWorker(self, pos):
        worker = character.Character("farmer", pos, 33)
        self.workers.append(worker)
        self.tiles[utils.worldToIndex(pos)].worker = worker

    def getClosestWorker(self, pos):
        closestWorker = None
        distToClosestWorker = 999999
        for worker in self.workers:
            dist = utils.distSquared(worker.startingPos, pos)
            if (dist < distToClosestWorker):
                distToClosestWorker = dist
                closestWorker = worker
        return closestWorker
    
    def canAfford(self, action):
        if (action == 'plough' and self.coins >= config.ploughCost):
            return True
        elif (action == 'plant' and self.coins >= config.plantCost):
            return True
        elif (action == 'water' and self.coins >= config.waterCost):
            return True
        elif (action == 'pick' and self.coins >= config.pickCost):
            return True
        return True


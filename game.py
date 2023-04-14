
import pygame as pg
import itertools

import config
import utils
import character
import ui
import linkedlist
import math

rawTile = 0
ploughedTile = 1
plantedTile = 2
readyTile = 3
tileSprites = [
    pg.image.load('images/tile-grass.png'), # raw
    pg.image.load('images/tile-ground.png'), # ploughed
    pg.image.load('images/tile-ground2.png'), # planted
    pg.image.load('images/tile-ground3.png') # ready
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
        self.tileSelectedRed = pg.image.load('images/tile-selected-red.png')
        self.tileSelectedRed.set_alpha(128)
        self.harvestIndicator = pg.image.load('images/ui/harvest-indicator.png')

        self.tilesSurface = pg.Surface(config.mapSize)
        self.tiles = list(itertools.repeat(0, config.worldSize[0] * config.worldSize[1]))

        self.origin = (config.worldSize[0] - 1) * config.tileSize[0] // 2, 0
        # self.farmer = character.Character('farmer', (3, 3), 130)

        self.ui = ui.UI()
        self.action = None
        self.coins = config.coins
        self.plantedTiles = linkedlist.LinkedList()
        self.readyToHarvestTiles = linkedlist.LinkedList()
        self.updateCoins(0)

        # generate map
        self.tilesSurface.fill(config.bgColor)
        for y in range(config.worldSize[1]):
            for x in range(config.worldSize[0]):
                sx, sy = utils.worldToScreen((x, y))
                self.tilesSurface.blit(tileSprites[0], (sx, sy))    

    def update(self):

        # self.farmer.update(self.dt)

        # camera
        margin = 80
        mouseX, mouseY = pg.mouse.get_pos()
        if (self.ui.hoveredButton == None):
            if (mouseX > config.screenSize[0] - config.scrollMargin):
                self.cameraPos = (self.cameraPos[0] - config.scrollSpeed * self.dt, self.cameraPos[1])
                self.cameraPos = (max(self.cameraPos[0], config.screenSize[0] - self.tilesSurface.get_width() - margin), self.cameraPos[1])
            elif (mouseX < config.scrollMargin):
                self.cameraPos = (self.cameraPos[0] + config.scrollSpeed * self.dt, self.cameraPos[1])
                self.cameraPos = (min(self.cameraPos[0], margin), self.cameraPos[1])
            bottomEdge = config.screenSize[1]
            if (mouseY > bottomEdge - config.scrollMargin):            
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
            index, state, time = tile.data
            time += self.dt
            tile.data = index, state, time
            if (time >= 1):
                if state < len(tileSprites) - 1:
                    newState = state + 1
                    self.tiles[index] = newState
                    self.redrawTiles(index)
                    tile.data = index, state + 1, 0
                    if newState == readyTile:
                        self.readyToHarvestTiles.append(index)                    

            tile = tile.next

    def draw(self):        
        self.screen.fill(config.bgColor)
        self.screen.blit(self.tilesSurface, self.cameraPos)

        if (self.ui.hoveredButton == None):
            if (self.action != None):
                x, y = self.selected
                if (x >= 0 and y >= 0 and x < config.worldSize[0] and y < config.worldSize[1]):
                    sx, sy = utils.worldToScreen(self.selected)
                    index = y * config.worldSize[0] + x
                    allowed = False

                    if (self.tiles[index] == readyTile):
                        allowed = True                        

                    elif (self.action == "plough"):
                        allowed = self.tiles[index] == rawTile                        
                    elif (self.action == "plant"):
                        allowed = self.tiles[index] == ploughedTile
                        
                    tilePos = (sx + self.cameraPos[0], sy + self.cameraPos[1])
                    if (allowed):
                        self.screen.blit(self.tileSelected, tilePos)
                    else:
                        self.screen.blit(self.tileSelectedRed, tilePos)

        tile = self.readyToHarvestTiles.head
        while tile is not None:
            index = tile.data
            y = math.floor(index / config.worldSize[0])
            x = index - y * config.worldSize[0]
            sx, sy = utils.worldToScreen((x, y))
            sx += (config.tileSize[0] - self.harvestIndicator.get_width()) // 2
            sy -= self.harvestIndicator.get_height()
            self.screen.blit(self.harvestIndicator, (sx + self.cameraPos[0], sy + self.cameraPos[1]))
            tile = tile.next

        # self.farmer.draw(self.screen)
        self.ui.draw(self.screen)

    def onMouseMoved(self, x, y):

        # tile selection
        self.selected, tx, ty = utils.screenToWorld((x, y), self.cameraPos)        
        maskColor = self.tileMask.get_at((tx, ty))
        if (maskColor == (255, 0, 0, 255)):
             self.selected = self.selected[0] - 1, self.selected[1]
        elif (maskColor == (0, 255, 0, 255)):
            self.selected = self.selected[0], self.selected[1] - 1
        elif (maskColor == (0, 0, 255, 255)):
            self.selected = self.selected[0], self.selected[1] + 1
        elif (maskColor == (255, 255, 0, 255)):
            self.selected = self.selected[0] + 1, self.selected[1]

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
                    if self.tiles[index] == readyTile:
                        self.tiles[index] = rawTile
                        self.updateCoins(config.harvestGain)
                        self.redrawTiles(index)
                        self.plantedTiles.delete(lambda data: data[0] == index)
                        self.readyToHarvestTiles.delete(lambda data: data == index)
                    elif (self.action == 'plough'):
                        if (self.tiles[index] == rawTile):
                            self.tiles[index] = ploughedTile
                            self.updateCoins(-config.ploughCost)
                            self.redrawTiles(index)
                    elif (self.action == 'plant'):
                        if (self.tiles[index] == ploughedTile):
                            self.tiles[index] = plantedTile
                            self.updateCoins(-config.plantCost)
                            self.redrawTiles(index)                            
                            self.plantedTiles.append((index, plantedTile, 0.0))


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
                sprite = tileSprites[self.tiles[index]]                        
                sx, sy = utils.worldToScreen((_x, yCoord))
                self.tilesSurface.blit(sprite, (sx, sy))


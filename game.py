
import pygame as pg
import itertools
import math

import config
import utils
import character
import ui
import linkedlist
import tile as Tile
import area as Area

class Game:
    def __init__(self):
        self.screen = pg.display.set_mode(size=config.screenSize)
        self.clock = pg.time.Clock()
        self.dt = 0.0        
        self.selected = -1, -1

        self.tileMask = pg.image.load('images/tile-mask.png')
        self.tileSelected = pg.image.load('images/tile-selected.png')
        
        self.tileSelectedRed = pg.image.load('images/tile-selected-red.png')
        self.tileNoCoins = pg.image.load('images/tile-no-coins.png')
        # self.tileSelectedRed.set_alpha(128)
        # self.harvestIndicator = pg.image.load('images/ui/harvest-indicator.png')

        self.ui = ui.UI()
        self.action = "plough"
        self.ui.buttons[0].selected = True
        self.actionAllowed = False
        self.selectorInRange = False
        self.coins = config.coins
        self.lastChangedTile = None
        self.cantAfford = False
        # self.readyToHarvestTiles = linkedlist.LinkedList()
        self.updateCoins(0)

        # initialize areas
        maxAreasPerRow = config.maxAreasPerRow
        self.startingAreaPos = (math.floor(maxAreasPerRow / 2), math.floor(maxAreasPerRow / 2))
        self.areas = [[]]
        for i in range(maxAreasPerRow):
            row = self.areas[i]
            for _ in range(maxAreasPerRow):
                row.append(None)
            self.areas.append([])
        self.activeAreas = []
        
        # first area
        areaPos = utils.areaToScreen(self.startingAreaPos)
        self.areaBounds = ((areaPos[0], areaPos[0] + config.mapSizePixels[0]), (areaPos[1], areaPos[1] + config.mapSizePixels[1]))
        firstArea = self.addArea(self.startingAreaPos)
        # first worker
        firstArea.addWorker(config.firstWorkerPos)
        workerIndex = utils.localToIndex(config.firstWorkerPos)
        firstArea.redrawTiles(workerIndex)

        # center area in view
        self.cameraPos = (areaPos[0] - (config.screenSize[0] - config.mapSizePixels[0]) // 2, areaPos[1] - (config.screenSize[1] - config.mapSizePixels[1]) // 2)

    def addArea(self, pos):
        area = Area.Area(pos)
        self.areas[pos[1]][pos[0]] = area
        self.activeAreas.append(area)

        # first worker
        # area.addWorker(config.firstWorkerPos)
        # workerIndex = utils.localToIndex(config.firstWorkerPos)
        # area.redrawTiles(workerIndex)

        # update bounds
        xBounds, yBounds = self.areaBounds
        minX, maxX = xBounds
        minY, maxY = yBounds
        x, y = utils.areaToScreen(pos)        
        if (x < minX):
            minX = x
        elif (x + config.mapSizePixels[0] > maxX):
            maxX = x + config.mapSizePixels[0]
        if (y < minY):
            minY = y
        elif (y + config.mapSizePixels[1] > maxY):
            maxY = y + config.mapSizePixels[1]
        self.areaBounds = ((minX, maxX), (minY, maxY))
        return area

    def update(self):

        for area in self.activeAreas:
            area.update(self.dt)

        # camera scroll
        mouseX, mouseY = pg.mouse.get_pos()
        bottomEdge = config.screenSize[1] - 50
        if (self.ui.hoveredButton == None):
            xBounds, yBounds = self.areaBounds
            minX, maxX = xBounds
            minY, maxY = yBounds
            xMargin = (config.screenSize[0] - config.mapSizePixels[0]) // 2
            yMargin = (config.screenSize[1] - config.mapSizePixels[1]) // 2
            if (mouseX > config.screenSize[0] - config.scrollMargin):
                self.cameraPos = (self.cameraPos[0] + config.scrollSpeed * self.dt, self.cameraPos[1])                
                self.cameraPos = (min(self.cameraPos[0], maxX - config.mapSizePixels[0] - xMargin), self.cameraPos[1])
            elif (mouseX < config.scrollMargin):
                self.cameraPos = (self.cameraPos[0] - config.scrollSpeed * self.dt, self.cameraPos[1])
                self.cameraPos = (max(self.cameraPos[0], minX - xMargin), self.cameraPos[1])
            if (mouseY > bottomEdge):                
                self.cameraPos = (self.cameraPos[0], self.cameraPos[1] + config.scrollSpeed * self.dt)
                self.cameraPos = (self.cameraPos[0], min(self.cameraPos[1], maxY - config.mapSizePixels[1] - yMargin))
            elif (mouseY < config.scrollMargin):                
                self.cameraPos = (self.cameraPos[0], self.cameraPos[1] - config.scrollSpeed * self.dt)    
                self.cameraPos = (self.cameraPos[0], max(self.cameraPos[1], minY - yMargin))

        self.ui.update()        
        self.dt = self.clock.tick(config.fps) / 1000
        pg.display.set_caption(f"FPS: {self.clock.get_fps():.2f}")        

    def draw(self):        
        self.screen.fill(config.bgColor)

        # for area in self.activeAreas:
        #     area.draw(self.screen, self.cameraPos)
        for y in range(config.maxAreasPerRow):
            for x in range(config.maxAreasPerRow):
                area = self.areas[y][x]
                if (area != None):
                    area.draw(self.screen, self.cameraPos)        

        if (self.selectorInRange and self.ui.hoveredButton == None):
            sx, sy = utils.worldToScreen(self.selected)
            areaX, areaY = utils.worldToArea(self.selected)
            localPos = utils.worldToLocal((areaX, areaY), self.selected)
            index = utils.localToIndex(localPos)
            area = self.areas[areaY][areaX]
            tile = area.tiles[index]
            tilePos = (sx - self.cameraPos[0], sy - self.cameraPos[1])
            if (tile.state == config.readyTile):
                self.screen.blit(self.tileSelected, tilePos)
            elif (self.action != None and index != self.lastChangedTile):
                if (tile.worker == None and tile.action == None):
                    if (self.cantAfford):
                        self.screen.blit(self.tileNoCoins, tilePos)
                    elif (self.actionAllowed):
                        self.screen.blit(self.tileSelected, tilePos)
                    else:
                        self.screen.blit(self.tileSelectedRed, tilePos)
        # else:
        #     sx, sy = utils.worldToScreen(self.selected)
        #     tilePos = (sx - self.cameraPos[0], sy - self.cameraPos[1])
        #     self.screen.blit(self.tileSelected, tilePos)        

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
            areaX, areaY = utils.worldToArea(self.selected)
            # print(f"worldX: {worldX}, worldY: {worldY}")
            if (areaX < 0 or areaY < 0 or areaX >= config.maxAreasPerRow or areaY >= config.maxAreasPerRow):
                self.selectorInRange = False
            else:
                area = self.areas[areaY][areaX]
                if (area == None):
                    self.selectorInRange = False
                else:
                    self.selectorInRange = True
                    localX, localY = utils.worldToLocal((areaX, areaY), self.selected)
                    # print(f"localX: {localX}, localY: {localY}")                    
                    index = utils.localToIndex((localX, localY))
                    tile = area.tiles[index]
                    self.lastChangedTile = None
                    self.actionAllowed = True
                    self.cantAfford = False
                    if (tile.worker != None or tile.action != None):
                        pass
                    elif tile.state == config.readyTile:
                        pass
                    elif (self.action == "plough"):
                        self.actionAllowed = tile.state == config.rawTile
                    elif (self.action == "plant"):
                        self.actionAllowed = tile.state == config.ploughedTile
                    elif (self.action == "water"):
                        self.actionAllowed = (tile.state >= config.plantedTile and tile.state < config.readyTile) or tile.state == config.fireTile
                    # elif (self.action == "harvest"):
                        # self.actionAllowed = tile.state == config.readyTile
                    elif (self.action == "pick"):
                        self.actionAllowed = tile.state == config.stoneTile
                    elif (self.action == "worker"):
                        self.actionAllowed = tile.state == config.rawTile                    
           
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
            
            if not self.selectorInRange:
                # todo remove, test code
                areaX, areaY = utils.worldToArea(self.selected)
                if (areaX < 0 or areaY < 0 or areaX >= config.maxAreasPerRow or areaY >= config.maxAreasPerRow):
                    pass
                else:
                    area = self.areas[areaY][areaX]
                    if (area == None):
                        self.addArea((areaX, areaY))                        
                return

            areaX, areaY = utils.worldToArea(self.selected)
            area = self.areas[areaY][areaX]
            local = localX, localY = utils.worldToLocal((areaX, areaY), self.selected)
            index = utils.localToIndex((localX, localY))
            tile = area.tiles[index]
            readyToHarvest = tile.state == config.readyTile
            if (self.action != None and self.actionAllowed) or readyToHarvest:
                if (tile.action == None and tile.worker == None):
                    if readyToHarvest:
                        closestWorker = area.getClosestWorker(local)
                        closestWorker.queueAction("harvest", index)
                        tile.action = "harvest"
                        self.actionAllowed = False
                        self.lastChangedTile = index
                        area.wipTiles.append(index)
                    elif self.canAfford(self.action):
                        if (self.action == "worker"):
                            area.addWorker(local)
                            area.redrawTiles(index)
                        else:
                            closestWorker = area.getClosestWorker(local)
                            closestWorker.queueAction(self.action, index)
                            tile.action = self.action
                            self.actionAllowed = False
                            self.lastChangedTile = index
                            area.wipTiles.append(index)
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
                        if not self.tryUpdateButton(button, 'pick', config.pickCost):
                            self.tryUpdateButton(button, 'worker', config.workerCost)
    
    def canAfford(self, action):
        if (action == 'plough'):
            return self.coins >= config.ploughCost
        elif (action == 'plant'):
            return self.coins >= config.plantCost
        elif (action == 'water'):
            return self.coins >= config.waterCost
        elif (action == 'pick'):
            return self.coins >= config.pickCost
        elif action == "worker":
            return self.coins >= config.workerCost
        return True


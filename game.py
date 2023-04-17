
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
import button

class Game:
    def __init__(self):
        self.screen = pg.display.set_mode(size=config.screenSize)
        self.clock = pg.time.Clock()
        self.dt = 0.0        
        self.selected = -1, -1
        self.ui = ui.UI()
        self.tileMask = pg.image.load('images/tile-mask.png')
        self.tileSelected = pg.image.load('images/tile-selected.png')
        self.areaSelector = pg.image.load('images/area-selector.png')
        # self.areaSelectorRed = pg.image.load('images/area-selector-red.png')
        # self.tileSelectedRed = pg.image.load('images/tile-selected-red.png')
        self.tileNoCoins = pg.image.load('images/tile-no-coins.png')

        # gameover screen
        self.gameoverVisible = False
        self.gameover = pg.image.load('images/ui/gameover.png')
        self.backdrop = pg.surface.Surface(config.screenSize)
        self.backdrop.set_alpha(128)
        self.backdrop.fill((0, 0, 0))
        self.replay = pg.image.load('images/ui/replay.png')
        gameOverY = (config.screenSize[1] - self.gameover.get_height()) / 2
        replayPos = ((config.screenSize[0] - self.replay.get_width()) / 2, gameOverY + self.gameover.get_height() + config.uiGap)
        replayButton = button.Button(self.replay, replayPos, "replay", False)
        self.ui.buttons.append(replayButton)
        self.ui.replayButton = replayButton
        
        self.action = None
        self.coins = config.coins
        self.reset()

    def reset(self):
        self.action = None
        self.selectorInRange = False
        self.lastChangedTile = None
        self.canAfford = True
        
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

        self.rawTiles = 0
        self.ploughedTiles = 0
        self.plantedTiles = 0
        self.readyTiles = 0
        self.stoneTiles = 0
        self.fireTiles = 0

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
        self.rawTiles += config.tileCount
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

        for y in range(config.maxAreasPerRow):
            for x in range(config.maxAreasPerRow):
                area = self.areas[y][x]
                if (area != None):
                    area.draw(self.screen, self.cameraPos)

        if (self.gameoverVisible):
            self.screen.blit(self.backdrop, (0, 0))
            gx, gy = (config.screenSize[0] - self.gameover.get_width()) / 2, (config.screenSize[1] - self.gameover.get_height()) / 2
            self.screen.blit(self.gameover , (gx, gy))    
        else:
            sx, sy = utils.worldToScreen(self.selected)
            areaPos = areaX, areaY = utils.worldToArea(self.selected)
            if (self.selectorInRange):
                localPos = utils.worldToLocal((areaX, areaY), self.selected)
                index = utils.localToIndex(localPos)
                area = self.areas[areaY][areaX]
                tile = area.tiles[index]
                tilePos = (sx - self.cameraPos[0], sy - self.cameraPos[1])
                if (tile.state == config.readyTile):
                    self.screen.blit(self.tileSelected, tilePos)
                elif (index != self.lastChangedTile):
                    if (tile.worker == None and tile.action == None):
                        if (self.canAfford):                    
                            self.screen.blit(self.tileSelected, tilePos)
                        else:
                            self.screen.blit(self.tileNoCoins, tilePos)
                        # else:
                            # self.screen.blit(self.tileSelectedRed, tilePos)
            else:
                if (self.action == "expand"):
                    sx, sy = utils.areaToScreen(areaPos)
                    self.screen.blit(self.areaSelector, (sx - self.cameraPos[0], sy - self.cameraPos[1]))

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
                    if self.action == "expand":
                        self.canAfford = self.coins >= config.expandCost
                else:
                    self.selectorInRange = True
                    localX, localY = utils.worldToLocal((areaX, areaY), self.selected)
                    # print(f"localX: {localX}, localY: {localY}")                    
                    index = utils.localToIndex((localX, localY))
                    tile = area.tiles[index]
                    self.lastChangedTile = None
                    # self.actionAllowed = True
                    if (tile.worker != None or tile.action != None):
                        pass
                    if self.action == "expand":
                        self.canAfford = False # must click outside to expand
                    else:
                        self.updateAffordability(tile)
                    # elif (self.action == "plough"):
                    #     self.actionAllowed = tile.state == config.rawTile
                    # elif (self.action == "plant"):
                    #     self.actionAllowed = tile.state == config.ploughedTile
                    # elif (self.action == "water"):
                    #     self.actionAllowed = (tile.state >= config.plantedTile and tile.state < config.readyTile) or tile.state == config.fireTile
                    # # elif (self.action == "harvest"):
                    #     # self.actionAllowed = tile.state == config.readyTile
                    # elif (self.action == "pick"):
                    #     self.actionAllowed = tile.state == config.stoneTile
                    # elif (self.action == "worker"):
                    #     self.actionAllowed = tile.state == config.rawTile                    
           
    def onMouseUp(self, button, mousePos):
        if (button == pg.BUTTON_LEFT):

            if (self.ui.pressedButton != None):
                if (self.ui.pressedButton.action == "replay"):
                    self.showGameover(False)                    
                    self.updateCoins(config.coins - self.coins)
                    self.reset()                    
                    for _button in self.ui.buttons:
                        _button.selected = False
                else:
                    if (self.action == self.ui.pressedButton.action):
                        self.action = None
                    else: 
                        self.action = self.ui.pressedButton.action                    
                    for _button in self.ui.buttons:
                        _button.selected = _button.action == self.action
                self.ui.pressedButton = None
                return
            
            if (self.gameoverVisible):
                return

            if (self.ui.hoveredButton != None):
                return
            
            if not self.selectorInRange:
                if self.action == "expand" and self.canAfford:
                    areaX, areaY = utils.worldToArea(self.selected)
                    if (areaX < 0 or areaY < 0 or areaX >= config.maxAreasPerRow or areaY >= config.maxAreasPerRow):
                        pass
                    else:
                        area = self.areas[areaY][areaX]
                        if (area == None):
                            self.addArea((areaX, areaY))
                            self.updateCoins(-config.expandCost)  
                            self.action = None
                            self.ui.expandButton.selected = False                          
                return

            areaX, areaY = utils.worldToArea(self.selected)
            area = self.areas[areaY][areaX]
            local = localX, localY = utils.worldToLocal((areaX, areaY), self.selected)
            index = utils.localToIndex((localX, localY))
            tile = area.tiles[index]
            if self.canAfford and tile.action == None:
                if (self.action == "worker"): 
                    area.addWorker(local)
                    area.redrawTiles(index)
                    self.updateCoins(-config.workerCost)
                    self.updateAffordability(tile)                    
                    self.action = None
                    self.ui.workerButton.selected = False
                elif tile.state == config.rawTile:
                    self.rawTiles -= 1
                    self.ploughedTiles += 1
                    self.queueAction(area, local, tile, index, "plough", config.ploughCost)                    
                elif tile.state == config.ploughedTile:
                    self.ploughedTiles -= 1
                    self.plantedTiles += 1
                    self.queueAction(area, local, tile, index, "plant", config.plantCost)                    
                elif (tile.state >= config.plantedTile and tile.state < config.readyTile) or tile.state == config.fireTile:
                    if tile.state == config.fireTile:
                        self.fireTiles -= 1
                        self.stoneTiles += 1
                    self.queueAction(area, local, tile, index, "water", config.waterCost)                    
                elif tile.state == config.readyTile:
                    self.plantedTiles -= 1
                    self.readyTiles += 1
                    self.queueAction(area, local, tile, index, "harvest", 0)                    
                elif tile.state == config.stoneTile:
                    self.rawTiles += 1
                    self.stoneTiles -= 1
                    self.queueAction(area, local, tile, index, "pick", config.pickCost)                    
                self.printTileCounts()

            # readyToHarvest = tile.state == config.readyTile
            # if (self.action != None and self.actionAllowed) or readyToHarvest:
            #     if (tile.action == None and tile.worker == None):
            #         if readyToHarvest:
            #             closestWorker = area.getClosestWorker(local)
            #             closestWorker.queueAction("harvest", index)
            #             tile.action = "harvest"
            #             self.actionAllowed = False
            #             self.lastChangedTile = index
            #             area.wipTiles.append(index)
            #         elif self.canAfford(self.action):
            #             if (self.action == "worker"):
            #                 area.addWorker(local)
            #                 area.redrawTiles(index)
            #             else:
            #                 closestWorker = area.getClosestWorker(local)
            #                 closestWorker.queueAction(self.action, index)
            #                 tile.action = self.action
            #                 self.actionAllowed = False
            #                 self.lastChangedTile = index
            #                 area.wipTiles.append(index)
            #                 if (self.action == 'plough'): self.updateCoins(-config.ploughCost)            
            #                 elif (self.action == 'plant'): self.updateCoins(-config.plantCost)
            #                 elif (self.action == 'water'): self.updateCoins(-config.waterCost)
            #                 elif (self.action == 'pick'): self.updateCoins(-config.pickCost)
            #         else:
            #             self.canAfford = True

    def queueAction(self, area, localPos, tile, tileIndex, action, cost):
        closestWorker = area.getClosestWorker(localPos)
        closestWorker.queueAction(action, tileIndex)
        tile.action = action
        self.lastChangedTile = tileIndex
        area.wipTiles.append(tileIndex)
        self.updateCoins(-cost)
        self.updateAffordability(tile)

    def printTileCounts(self):
        print("Raw: " + str(self.rawTiles))
        print("Ploughed: " + str(self.ploughedTiles))
        print("Planted: " + str(self.plantedTiles))
        print("Fire: " + str(self.fireTiles))
        print("Stone: " + str(self.stoneTiles))

    def tryUpdateButton(self, button, action, cost):
        updated = False
        if (button.action == action):
            updated = True
            button.disabled = self.coins < cost
            if (button.disabled and self.action == action):
                self.action = None
                button.selected = False
        return updated
    
    def updateAffordability(self, tile):
        if self.action == "worker":
            self.canAfford = tile.state == config.rawTile
        elif tile.state == config.readyTile:
            self.canAfford = True
        elif tile.state == config.rawTile:
            self.canAfford = self.coins >= config.ploughCost
        elif tile.state == config.ploughedTile:
            self.canAfford = self.coins >= config.plantCost
        elif (tile.state >= config.plantedTile and tile.state < config.readyTile) or tile.state == config.fireTile:
            self.canAfford = self.coins >= config.waterCost
        elif tile.state == config.stoneTile:
            self.canAfford = self.coins >= config.pickCost
        else:
            self.canAfford = False
            print("unknown tile state")

    def updateCoins(self, amount):
        self.coins += amount
        for button in self.ui.buttons:
            if not self.tryUpdateButton(button, 'worker', config.workerCost):
                self.tryUpdateButton(button, 'expand', config.expandCost)                            
            # if not self.tryUpdateButton(button, 'plough', config.ploughCost):
            #     if not self.tryUpdateButton(button, 'plant', config.plantCost):
            #         if not self.tryUpdateButton(button, 'water', config.waterCost):
            #             if not self.tryUpdateButton(button, 'pick', config.pickCost):
            #                 self.tryUpdateButton(button, 'worker', config.workerCost)

        # check game over
        isGameover = False
        if (self.coins < config.plantCost):
            isGameover = self.plantedTiles == 0 and self.readyTiles == 0
        else:
            if self.rawTiles == 0:
                isGameover = self.plantedTiles == 0 and self.readyTiles == 0
            else:
                pass
        if (isGameover):
            self.showGameover(True)

    def showGameover(self, show):
        self.gameoverVisible = show
        uiVisible = not show
        self.ui.workerButton.visible = uiVisible
        self.ui.expandButton.visible = uiVisible
        self.ui.replayButton.visible = show
    
    # def canAfford(self, action):
    #     if (action == 'plough'):
    #         return self.coins >= config.ploughCost
    #     elif (action == 'plant'):
    #         return self.coins >= config.plantCost
    #     elif (action == 'water'):
    #         return self.coins >= config.waterCost
    #     elif (action == 'pick'):
    #         return self.coins >= config.pickCost
    #     elif action == "worker":
    #         return self.coins >= config.workerCost
    #     return True


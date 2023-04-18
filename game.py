
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
        self.notEnoughCoins = self.ui.font.render("Not enough coins!", False, (255, 0, 0))
        self.notEnoughWorkers = self.ui.font.render("Not enough workers!", False, (255, 0, 0))

        # gameover screen
        self.gameoverVisible = False
        self.gameover = pg.image.load('images/ui/gameover.png')
        self.backdrop = pg.surface.Surface(config.screenSize)
        self.backdrop.set_alpha(100)
        self.backdrop.fill((0, 0, 0))
        self.replay = pg.image.load('images/ui/replay.png')
        gameOverY = (config.screenSize[1] - self.gameover.get_height()) / 2
        replayY = gameOverY + self.gameover.get_height() + config.uiGap
        replayPos = ((config.screenSize[0] - self.replay.get_width()) / 2, replayY)
        replayButton = button.Button(self.replay, replayPos, "replay", False)
        self.ui.buttons.append(replayButton)
        self.ui.replayButton = replayButton
        self.ranOutOfCoins = self.ui.font.render("You ran out of coins!", False, (255, 255, 255))
        ranOfOfCoinsY = replayY + self.replay.get_height() + config.uiGap * 2
        self.ranOutOfCoinsRect = self.ranOutOfCoins.get_rect(center=(config.screenSize[0] / 2, ranOfOfCoinsY))  
        self.harvestTile = pg.image.load('images/tile-ground4.png')      
        self.totalHarvestsText = None
        
        self.action = None
        self.coins = config.coins
        self.reset()

        # intro
        self.showIntro = True
        self.logo = pg.image.load('images/logo.png')
        self.play = pg.image.load('images/ui/play.png')
        logoY = (config.screenSize[1] - self.logo.get_height()) / 2
        playY = logoY + self.logo.get_height() + config.uiGap
        playPos = ((config.screenSize[0] - self.play.get_width()) / 2, playY)
        playButton = button.Button(self.play, playPos, "play")
        self.ui.buttons.append(playButton)
        self.ui.playButton = playButton 
        for _button in self.ui.buttons:
            _button.visible = False
        playButton.visible = True
        # self.showGameover(True)

        # play music using pygame        
        pg.mixer.music.load('audio/Juhani Junkala Chiptune Adventures 1 Stage 1.ogg')
        pg.mixer.music.play(-1)
        self.playSound = pg.mixer.Sound('audio/GUI_Sound_Effects_by_Lokif/load.wav')
        self.positiveSound = pg.mixer.Sound('audio/GUI_Sound_Effects_by_Lokif/positive.wav')
        self.clickSound = pg.mixer.Sound('audio/GUI_Sound_Effects_by_Lokif/misc_menu.wav')
        self.tileSound = pg.mixer.Sound('audio/GUI_Sound_Effects_by_Lokif/misc_menu_4.wav')
        self.expandSound = pg.mixer.Sound('audio/GUI_Sound_Effects_by_Lokif/save.wav')
        self.fireSound = pg.mixer.Sound('audio/GUI_Sound_Effects_by_Lokif/negative.wav')
        self.progressSound = pg.mixer.Sound('audio/GUI_Sound_Effects_by_Lokif/sharp_echo.wav')
        self.workCompleted = pg.mixer.Sound('audio/fx/Rise01.wav')

    def reset(self):
        self.action = None
        self.updateCoins(0, False)
        self.selectorInRange = False
        # self.lastChangedTile = None
        self.canAfford = True
        self.totalHarvests = 0
        self.salaryTimer = config.salaryFrequency

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

        # todo testing
        # firstArea.addWorker((3, 0))
        # firstArea.addWorker((3, 3))
        # area = self.addArea((self.startingAreaPos[0] + 1, self.startingAreaPos[1]))        
        # area.addWorker((0, 0))
        # area.addWorker((3, 0))
        # area.addWorker((3, 3))

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
        
        self.dt = self.clock.tick(config.fps) / 1000        
        workerCount = 0

        if (not self.gameoverVisible):
            self.salaryTimer -= self.dt

        paySalary = self.salaryTimer < 0
        for area in self.activeAreas:
            area.update(self.dt, paySalary)
            workerCount += len(area.workers)

        if (not self.gameoverVisible):
            if paySalary:
                salaryToPay = workerCount * config.salary
                if (self.coins < salaryToPay):
                    self.showGameover(True)
                else:
                    self.updateCoins(-salaryToPay)
                    self.fireSound.play()
                self.salaryTimer = config.salaryFrequency

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
        pg.display.set_caption(f"FPS: {self.clock.get_fps():.2f}")        

    def draw(self):        
        self.screen.fill(config.bgColor)

        for y in range(config.maxAreasPerRow):
            for x in range(config.maxAreasPerRow):
                area = self.areas[y][x]
                if (area != None):
                    area.draw(self.screen, self.cameraPos)

        if self.showIntro:
            # self.screen.fill((20, 23, 17))
            self.screen.blit(self.backdrop, (0, 0))
            gx, gy = (config.screenSize[0] - self.logo.get_width()) / 2, (config.screenSize[1] - self.logo.get_height()) / 2
            self.screen.blit(self.logo , (gx, gy))
        elif (self.gameoverVisible):
            self.screen.blit(self.backdrop, (0, 0))
            gx, gy = (config.screenSize[0] - self.gameover.get_width()) / 2, (config.screenSize[1] - self.gameover.get_height()) / 2
            self.screen.blit(self.gameover , (gx, gy))
            self.screen.blit(self.ranOutOfCoins, self.ranOutOfCoinsRect)
            harvestTileY = config.uiGap * 4
            self.screen.blit(self.harvestTile, ((config.screenSize[0] - self.harvestTile.get_width()) / 2, harvestTileY))
            totalHarvestY = harvestTileY + self.harvestTile.get_height() + config.uiGap * 2
            if (self.totalHarvestsText == None):
                self.totalHarvestsText = self.ui.font.render(f"Total Harvests: {self.totalHarvests}", False, (255, 255, 255))
            rc = self.totalHarvestsText.get_rect(center=(config.screenSize[0] / 2, totalHarvestY))  
            self.screen.blit(self.totalHarvestsText, rc)
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
                    if (tile.action == None):
                        self.screen.blit(self.tileSelected, tilePos)
                elif tile.worker == None and tile.action == None:
                    if (self.action != None):
                        if (self.action == "worker"):
                            if tile.state == config.rawTile:
                                self.screen.blit(self.tileSelected, tilePos)
                            else:
                                self.screen.blit(self.tileNoCoins, tilePos)
                    else:
                        if (self.canAfford):
                            if len(area.workers) == 0:                            
                                textPos = (tilePos[0] + config.tileSize[0] // 2, tilePos[1] - 30)
                                rect = self.notEnoughWorkers.get_rect(center=textPos)
                                self.screen.blit(self.notEnoughWorkers, rect)
                                self.screen.blit(self.tileNoCoins, tilePos)
                            else:
                                self.screen.blit(self.tileSelected, tilePos)
                        else:
                            self.screen.blit(self.tileNoCoins, tilePos)
                            textPos = (tilePos[0] + config.tileSize[0] // 2, tilePos[1] - 30)
                            rect = self.notEnoughCoins.get_rect(center=textPos)
                            self.screen.blit(self.notEnoughCoins, rect)
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
                    # self.lastChangedTile = None
                    # self.actionAllowed = True
                    if (tile.worker != None or tile.action != None):
                        pass
                    elif self.action != None:
                        pass
                        # self.canAfford = False # must click outside to expand
                    else:
                        self.updateAffordability(tile)
           
    def onMouseUp(self, button, mousePos):
        if (button == pg.BUTTON_LEFT):

            if (self.ui.pressedButton != None):                
                if self.ui.pressedButton.action == "play":
                    self.showIntro = False
                    for _button in self.ui.buttons:
                        _button.visible = True
                    self.ui.playButton.visible = False
                    self.ui.replayButton.visible = False
                    self.ui.showCoins = True
                    self.playSound.play()
                    self.playInGameMusic()
                elif (self.ui.pressedButton.action == "replay"):
                    self.showGameover(False)                    
                    self.updateCoins(config.coins - self.coins)
                    self.reset()
                    for _button in self.ui.buttons:
                        _button.selected = False
                    self.playSound.play()
                    self.playInGameMusic()
                else:
                    if (self.action == self.ui.pressedButton.action):
                        self.action = None
                    else: 
                        self.action = self.ui.pressedButton.action                    
                    for _button in self.ui.buttons:
                        _button.selected = _button.action == self.action
                    self.clickSound.play()
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
                            newArea = self.addArea((areaX, areaY))
                            self.updateCoins(-config.expandCost)  
                            self.action = None
                            self.ui.expandButton.selected = False
                            self.expandSound.play()
                            newArea.startCostAnim()
                return

            areaX, areaY = utils.worldToArea(self.selected)
            area = self.areas[areaY][areaX]
            local = localX, localY = utils.worldToLocal((areaX, areaY), self.selected)
            index = utils.localToIndex((localX, localY))
            tile = area.tiles[index]
            if tile.action == None and tile.worker == None:
                if self.action == "worker":
                    if tile.state == config.rawTile:
                        area.addWorker(local)
                        area.redrawTiles(index)
                        self.updateCoins(-config.workerCost)
                        self.updateAffordability(tile)                    
                        self.action = None
                        self.ui.workerButton.selected = False
                        self.tileSound.play()
                        tile.startCostAnim(-config.workerCost)
                        area.animatedTiles.append(index)                            
                        
                elif self.canAfford and len(area.workers) > 0:
                    if tile.state == config.rawTile:
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
                        self.readyTiles -= 1
                        self.stoneTiles += 1
                        tile.action = "harvest"
                        area.wipTiles.append(index)                        
                        closestWorker = area.getClosestWorker(local)
                        closestWorker.queueAction("harvest", index)
                        self.updateAffordability(tile)
                        self.tileSound.play()
                    elif tile.state == config.stoneTile:
                        self.rawTiles += 1
                        self.stoneTiles -= 1
                        self.queueAction(area, local, tile, index, "pick", config.pickCost)                                           
                    else:
                        print(f"ERROR: unknown tile state {tile.state}")
                    self.printTileCounts()
                else:
                    print("breakpoint")

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
        tile.action = action        
        if not tile.costAnimActive:
            tile.startCostAnim(-cost)
            area.animatedTiles.append(tileIndex)
        # size = area.wipTiles.size
        area.wipTiles.append(tileIndex)
        # if (area.wipTiles.size != size + 1):
        #     print("invalid wip tile size")
        closestWorker = area.getClosestWorker(localPos)
        closestWorker.queueAction(action, tileIndex)        
        # self.lastChangedTile = tileIndex        
        self.updateCoins(-cost)
        self.updateAffordability(tile)
        self.tileSound.play()

    def printTileCounts(self):
        pass
        # print("Raw: " + str(self.rawTiles))
        # print("Ploughed: " + str(self.ploughedTiles))
        # print("Planted: " + str(self.plantedTiles))
        # print("Fire: " + str(self.fireTiles))
        # print("Stone: " + str(self.stoneTiles))

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
        if tile.state == config.readyTile:
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
            # self.canAfford = False
            print("unknown tile state")

    def updateCoins(self, amount, checkGameOver = True):
        self.coins += amount
        for button in self.ui.buttons:
            if not self.tryUpdateButton(button, 'worker', config.workerCost):
                self.tryUpdateButton(button, 'expand', config.expandCost)                            
            # if not self.tryUpdateButton(button, 'plough', config.ploughCost):
            #     if not self.tryUpdateButton(button, 'plant', config.plantCost):
            #         if not self.tryUpdateButton(button, 'water', config.waterCost):
            #             if not self.tryUpdateButton(button, 'pick', config.pickCost):
            #                 self.tryUpdateButton(button, 'worker', config.workerCost)

        if not checkGameOver:
            return

        self.doGameoverCheck()

    def doGameoverCheck(self):
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
        if (show):
            self.playGameoverMusic()
        else:
            self.totalHarvestsText = None

    def goBackToIntro(self):
        self.playSound.play()
        if (self.gameoverVisible):
            self.showGameover(False)        
        self.updateCoins(config.coins - self.coins)
        self.reset()
        for _button in self.ui.buttons:
           _button.selected = False
           _button.visible = False
        self.showIntro = True
        self.ui.playButton.visible = True
        self.ui.showCoins = False

    def playInGameMusic(self):
        pg.mixer.music.load('audio/Caketown 1.ogg')
        pg.mixer.music.play(-1)

    def playGameoverMusic(self):
        pg.mixer.music.load('audio/25 - Finale.ogg')
        pg.mixer.music.play(-1)


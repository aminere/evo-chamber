
import pygame as pg
import itertools

import config
import utils
import character
import ui

tileSprites = [
    pg.image.load('images/tile-ground.png'),
    pg.image.load('images/tile-grass.png'),
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

        self.tilesSurface = pg.Surface(config.mapSize)
        self.tiles = list(itertools.repeat(0, config.worldSize[0] * config.worldSize[1]))

        self.origin = (config.worldSize[0] - 1) * config.tileSize[0] // 2, 0
        self.farmer = character.Character('farmer', (3, 3), 130)

        self.ui = ui.UI()

        # generate map
        self.tilesSurface.fill((35, 35, 35))
        for y in range(config.worldSize[1]):
            for x in range(config.worldSize[0]):
                sx, sy = utils.worldToScreen((x, y))
                self.tilesSurface.blit(tileSprites[0], (sx, sy))    

    def update(self):

        self.farmer.update(self.dt)

        # camera
        mousePos = mouseX, mouseY = pg.mouse.get_pos()
        if (not self.ui.rect.collidepoint(mousePos)):
            if (mouseX > config.screenSize[0] - config.scrollMargin):
                self.cameraPos = (self.cameraPos[0] - config.scrollSpeed * self.dt, self.cameraPos[1])
                self.cameraPos = (max(self.cameraPos[0], config.screenSize[0] - self.tilesSurface.get_width()), self.cameraPos[1])
            elif (mouseX < config.scrollMargin):
                self.cameraPos = (self.cameraPos[0] + config.scrollSpeed * self.dt, self.cameraPos[1])
                self.cameraPos = (min(self.cameraPos[0], 0), self.cameraPos[1])
            bottomEdge = config.screenSize[1] - config.bottomUI['height']
            if (mouseY > bottomEdge - config.scrollMargin):            
                self.cameraPos = (self.cameraPos[0], self.cameraPos[1] - config.scrollSpeed * self.dt)
                self.cameraPos = (self.cameraPos[0], max(self.cameraPos[1], bottomEdge - self.tilesSurface.get_height()))
            elif (mouseY < config.scrollMargin):
                self.cameraPos = (self.cameraPos[0], self.cameraPos[1] + config.scrollSpeed * self.dt)    
                self.cameraPos = (self.cameraPos[0], min(self.cameraPos[1], 0))

        self.dt = self.clock.tick(config.fps) / 1000
        pg.display.set_caption(f"FPS: {self.clock.get_fps():.2f}")

    def draw(self):        
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.tilesSurface, self.cameraPos)       

        x, y = self.selected
        if (x >= 0 and y >= 0 and x < config.worldSize[0] and y < config.worldSize[1]):
            sx, sy = utils.worldToScreen(self.selected)
            self.screen.blit(self.tileSelected, (sx + self.cameraPos[0], sy + self.cameraPos[1]))

        self.farmer.draw(self.screen)
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

    def onMouseUp(self, button):
        if (button == pg.BUTTON_LEFT):

            # toggle tiles
            x, y = self.selected
            if (x >= 0 and y >= 0 and x < config.worldSize[0] and y < config.worldSize[1]):
                self.farmer.moveTo(self.selected)
                # index = y * config.worldSize[0] + x
                # self.tiles[index] = (self.tiles[index] + 1) % len(tileSprites)
                # startY = max(0, y - 1)
                # for _y in range(config.worldSize[1] - startY):
                #     for _x in range(config.worldSize[0]):
                #         yCoord = startY + _y
                #         index = yCoord * config.worldSize[0] + _x
                #         sprite = tileSprites[self.tiles[index]]                        
                #         sx, sy = Game.worldToScreen((_x, yCoord))
                #         self.tilesSurface.blit(sprite, (sx, sy))


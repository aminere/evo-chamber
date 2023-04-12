
import pygame as pg
import config

class Game:
    def __init__(self):
        self.screen = pg.display.set_mode(size=config.screenSize)
        self.clock = pg.time.Clock()
        self.dt = 0.0
        self.cameraPos = 0.0, 0.0
        self.selected = -1, -1

        self.tile = pg.image.load('images/tile-ground.png')
        self.tileMask = pg.image.load('images/tile-mask.png')
        self.tiles = pg.Surface(config.mapSize)
        self.origin = (config.worldSize[0] - 1) * config.tileSize[0] // 2, 0

        # generate map
        self.tiles.fill((35, 35, 35))
        for y in range(config.worldSize[1]):
            for x in range(config.worldSize[0]):
                sx, sy = Game.worldToScreen(x, y)
                self.tiles.blit(self.tile, (sx, sy))

    @staticmethod
    def worldToScreen(x, y):
        return (config.tileSize[0] // 2 * (x - y)) + config.origin[0], (config.tileSize[1] // 2 * (x + y)) + config.origin[1]

    def update(self):

        # camera
        mouseX, mouseY = pg.mouse.get_pos()
        if (mouseX > config.screenSize[0] - config.scrollMargin):
            self.cameraPos = (self.cameraPos[0] - config.scrollSpeed * self.dt, self.cameraPos[1])
            self.cameraPos = (max(self.cameraPos[0], config.screenSize[0] - self.tiles.get_width()), self.cameraPos[1])
        elif (mouseX < config.scrollMargin):
            self.cameraPos = (self.cameraPos[0] + config.scrollSpeed * self.dt, self.cameraPos[1])
            self.cameraPos = (min(self.cameraPos[0], 0), self.cameraPos[1])
        if (mouseY > config.screenSize[1] - config.scrollMargin):
            self.cameraPos = (self.cameraPos[0], self.cameraPos[1] - config.scrollSpeed * self.dt)
            self.cameraPos = (self.cameraPos[0], max(self.cameraPos[1], config.screenSize[1] - self.tiles.get_height()))
        elif (mouseY < config.scrollMargin):
            self.cameraPos = (self.cameraPos[0], self.cameraPos[1] + config.scrollSpeed * self.dt)    
            self.cameraPos = (self.cameraPos[0], min(self.cameraPos[1], 0))

        self.dt = self.clock.tick(config.fps) / 1000
        pg.display.set_caption(f"FPS: {self.clock.get_fps():.2f}")

    def draw(self):        
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.tiles, self.cameraPos)

    def onMouseMoved(self, x, y):        

        # tile selection
        lx, ly = x - config.origin[0] - int(self.cameraPos[0]), y - config.origin[1] - int(self.cameraPos[1])
        cx, cy = lx // config.tileSize[0], ly // config.tileSize[1]
        tx, ty = lx % config.tileSize[0], ly % config.tileSize[1]
        maskColor = self.tileMask.get_at((tx, ty))
        self.selected = cx + cy, cy - cx
        if (maskColor == (255, 0, 0, 255)):
             self.selected = self.selected[0] - 1, self.selected[1]
        elif (maskColor == (0, 255, 0, 255)):
            self.selected = self.selected[0], self.selected[1] - 1
        elif (maskColor == (0, 0, 255, 255)):
            self.selected = self.selected[0], self.selected[1] + 1
        elif (maskColor == (255, 255, 0, 255)):
            self.selected = self.selected[0] + 1, self.selected[1]


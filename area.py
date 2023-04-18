
import pygame as pg
import config
import tile as Tile
import utils
import character
import linkedlist
import math
import singletons

tileSprites = [
    pg.image.load('images/tile-grass.png'), # raw
    pg.image.load('images/tile-ground.png'), # ploughed
    pg.image.load('images/tile-ground2.png'), # planted
    pg.image.load('images/tile-ground3.png'), # planted
    pg.image.load('images/tile-ground4.png'), # ready
    pg.image.load('images/tile-ground4.png'), # on fire
    pg.image.load('images/tile-stone.png'), # stone
]

workerTile = pg.image.load('images/tile-worker.png')
tileWip = pg.image.load('images/tile-wip.png')
fire1 = pg.image.load('images/fire1.png')

class Area:
    def __init__(self, position):
        self.position = position
        self.surface = pg.Surface(config.surfaceSize, pg.SRCALPHA)
        self.tiles = []
        for _ in range(config.tileCount):
            self.tiles.append(Tile.Tile())
        for y in range(config.mapSize[1]):
            for x in range(config.mapSize[0]):
                sx, sy = utils.worldToScreen((x, y))
                tile = self.tiles[utils.localToIndex((x, y))]
                if (tile.worker != None):
                    self.surface.blit(workerTile, (sx, sy))
                else:
                    self.surface.blit(tileSprites[0], (sx, sy))

        self.workers = []
        self.plantedTiles = linkedlist.LinkedList()
        self.fireTiles = linkedlist.LinkedList()
        self.wipTiles = linkedlist.LinkedList()
        self.animatedTiles = []

        self.costAnim = False
        self.costAnimTime = 0
        self.costAnimText = None

    def startCostAnim(self):
        self.costAnim = True
        self.costAnimTime = 0

    def update(self, dt, paySalary):
        game = singletons._game
        for worker in self.workers:
            worker.update(dt)
            if paySalary:
                worker.startSalaryAnim()

        # update tiles
        for plantedTile in self.plantedTiles.arr:
        # plantedTile = self.plantedTiles.head
        # while plantedTile is not None:
            index = plantedTile#.data
            tile = self.tiles[index]          
            if tile.action == None:
                if (tile.state == config.readyTile):
                    tile.time += dt
                    if (tile.time >= config.growDuration):
                        tile.time = 0
                        tile.state = config.fireTile
                        self.fireTiles.append(index)
                        game.fireTiles += 1
                        game.readyTiles -= 1
                        game.fireSound.play()
                        game.doGameoverCheck()
                elif tile.state < config.readyTile:
                    tile.time += dt
                    if (tile.time >= config.growDuration):
                        tile.time = 0
                        newState = tile.state + 1
                        tile.state = newState                    
                        self.redrawTiles(index)
                        game.progressSound.play()
                        if (newState == config.readyTile):
                            game.plantedTiles -= 1
                            game.readyTiles += 1
            # plantedTile = plantedTile.next

        tilesToRemove = []
        for index in self.animatedTiles:
            tile = self.tiles[index]
            if (tile.costAnimActive):
                tile.costAnimTime += game.dt
                if (tile.costAnimTime > config.costAnimDuration):                
                    tile.costAnimActive = False
                    tilesToRemove.append(index)
        for index in tilesToRemove:
            self.animatedTiles.remove(index)

        # cost anim
        if (self.costAnim):
            self.costAnimTime += game.dt
            if (self.costAnimTime > config.costAnimDuration):                
                self.costAnim = False

    def draw(self, screen, cameraPos):
        sx, sy = utils.areaToScreen(self.position)
        screen.blit(self.surface, (sx - cameraPos[0], sy - cameraPos[1]))

        ax, ay = utils.areaToScreen(self.position)
        # draw wip tiles
        for wipTile in self.wipTiles.arr:
        # wipTile = self.wipTiles.head
        # while wipTile is not None:
            index = wipTile#.data
            pos = utils.indexToLocal(index)            
            sx, sy = utils.worldToScreen(pos)
            tilePos = (sx + ax - cameraPos[0], sy + ay - cameraPos[1])
            screen.blit(tileWip, tilePos)
            # wipTile = wipTile.next 

        # todo draw selector if any

        # draw fire tiles
        for fireTile in self.fireTiles.arr:
        # fireTile = self.fireTiles.head
        # while fireTile is not None:
            index = fireTile#.data
            pos = utils.indexToLocal(index)
            sx, sy = utils.worldToScreen(pos)
            ox = config.tileSize[0] // 2 - fire1.get_width() // 2
            oy = -76
            screen.blit(fire1, (sx + ax - cameraPos[0] + ox, sy + ay - cameraPos[1] + oy))
            # fireTile = fireTile.next

        for worker in self.workers:
            worker.draw(screen, (ax, ay))

        for index in self.animatedTiles:
            tile = self.tiles[index]
            if (tile.costAnimActive):
                factor = tile.costAnimTime / config.costAnimDuration
                positionY = utils.lerp_InOutCubic(0, -config.costAnimYLength, factor)
                alpha = utils.lerp_InOutCubic(255, 0, factor)
                pos = utils.indexToLocal(index)            
                tx, ty = utils.worldToScreen(pos)
                tilePos = (tx + ax - cameraPos[0], ty + ay - cameraPos[1])
                rc = tile.costText.get_rect(center=(tilePos[0] + config.tileSize[0] / 2, tilePos[1] - config.costOffsetY + positionY))
                tile.costText.set_alpha(int(alpha))
                screen.blit(tile.costText, rc)

        # expand cost anim
        game = singletons._game
        if (self.costAnim):
            if (self.costAnimText == None):
                self.costAnimText = game.ui.font.render(f"{-config.expandCost}", False, (255, 0, 0))
            factor = self.costAnimTime / config.costAnimDuration
            positionY = utils.lerp_InOutCubic(0, -config.costAnimYLength, factor)
            alpha = utils.lerp_InOutCubic(255, 0, factor)            
            animPos = (sx + config.mapSizePixels[0] / 2 - cameraPos[0], sy + config.mapSizePixels[1] / 2 - cameraPos[1])
            rc = self.costAnimText.get_rect(center=(animPos[0], animPos[1] + positionY))
            self.costAnimText.set_alpha(int(alpha))
            screen.blit(self.costAnimText, rc)

    def redrawTiles(self, index):
        y = math.floor(index / config.mapSize[0])
        startY = max(0, y - 1)
        for _y in range(config.mapSize[1] - startY):
            for _x in range(config.mapSize[0]):
                yCoord = startY + _y
                index = yCoord * config.mapSize[0] + _x
                tile = self.tiles[index]
                if (tile.worker != None):
                    sprite = workerTile
                else:
                    sprite = tileSprites[tile.state]                        
                sx, sy = utils.worldToScreen((_x, yCoord))
                self.surface.blit(sprite, (sx, sy))
            
    def addWorker(self, pos):
        worker = character.Character("farmer", pos, 33, self)
        self.workers.append(worker)
        self.tiles[utils.localToIndex(pos)].worker = worker

    def getClosestWorker(self, pos):
        closestWorker = None
        distToClosestWorker = 999999
        for worker in self.workers:
            dist = utils.distSquared(worker.startingPos, pos)
            if (dist < distToClosestWorker):
                distToClosestWorker = dist
                closestWorker = worker
        return closestWorker
    

import sys
import pygame as pg
import tweener as tw
import numpy as np
import math

WIN_SIZE = WIDTH, HEIGHT = 1024, 768
FPS = 60

WORLD_WIDTH, WORLD_HEIGHT = 12, 12
SCROLL_SPEED = 800
SCROLL_MARGIN = 100

pg.init()
screen = pg.display.set_mode(size=WIN_SIZE)
clock = pg.time.Clock()

font = pg.font.SysFont("Arial", 32)
tile = pg.image.load('tile-ground.png')
tileMask = pg.image.load('tile-mask.png')
tileSelected = pg.image.load('tile-selected.png')

farmer = {
    'topLeft': pg.image.load('farmer-top-left.png'),
    'topRight': pg.image.load('farmer-top-right.png'),
    'bottomLeft': pg.image.load('farmer-bottom-left.png'),
    'bottomRight': pg.image.load('farmer-bottom-right.png')
}

# tileW, tileH = tile.get_size()
dt = 0.0
selected = -1, -1

tileSize = (128, 64)
# tileOffset = (66, 34)

cameraPos = (0.0, 0.0)

worldSize = (WORLD_WIDTH) * tileSize[0], (WORLD_HEIGHT) * tileSize[1]
tiles = pg.Surface(worldSize)

ORIGIN_X, ORIGIN_Y = (WORLD_WIDTH - 1) * tileSize[0] // 2, 0
# ORIGIN_X, ORIGIN_Y = 0, 0

def worldToScreen(x, y):
    return (tileSize[0] // 2 * (x - y)) + ORIGIN_X, (tileSize[1] // 2 * (x + y)) + ORIGIN_Y

# generate map
tiles.fill((35, 35, 35))
for y in range(WORLD_HEIGHT):
        for x in range(WORLD_WIDTH):
            # sx, sy = tileW / 2 * (x - y), tileH / 2 * (x + y)
            # sx, sy = np.dot(worldToScreen, (x, y))
            sx, sy = worldToScreen(x, y)
            tiles.blit(tile, (sx, sy))

def update():
    global dt
    dt = clock.tick(FPS) / 1000
    pg.display.set_caption(f"FPS: {clock.get_fps():.2f}")

def draw():
    screen.fill((0, 0, 0))

    screen.blit(tiles, cameraPos)

    x, y = selected    
    if (x >= 0 and y >= 0 and x < WORLD_WIDTH and y < WORLD_HEIGHT):
        # sx, sy = tileW / 2 * (x - y), tileH / 2 * (x + y)
        sx, sy = worldToScreen(x, y)
        screen.blit(tileSelected, (sx + cameraPos[0], sy + cameraPos[1]))

    farmerPos = worldToScreen(3, 3)
    farmerOffsetY = 130
    screen.blit(farmer['topLeft'], (farmerPos[0] + cameraPos[0], farmerPos[1] + cameraPos[1] - farmerOffsetY))

    # rc = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    # text = font.render("{x} {y}".format(x = x, y = y), False, (255, 0, 0))
    # screen.blit(text, (0, 0))
    # pg.draw.rect(screen, (255, 0, 0), (cx * tileW, cy * tileH / 2, tileW, tileH / 2), 1)    

while True:

    # keys = pg.key.get_pressed()
    # if (keys[pg.K_LEFT]):
    #     ORIGIN_X -= 1
    # elif (keys[pg.K_RIGHT]):
    #     ORIGIN_X += 1
    # elif (keys[pg.K_UP]):
    #     ORIGIN_Y -= 1
    # elif (keys[pg.K_DOWN]):
    #     ORIGIN_Y += 1

    mouseX, mouseY = pg.mouse.get_pos()
    if (mouseX > WIDTH - SCROLL_MARGIN):
        cameraPos = (cameraPos[0] - SCROLL_SPEED * dt, cameraPos[1])
        cameraPos = (max(cameraPos[0], WIDTH - tiles.get_width()), cameraPos[1])
    elif (mouseX < SCROLL_MARGIN):
        cameraPos = (cameraPos[0] + SCROLL_SPEED * dt, cameraPos[1])
        cameraPos = (min(cameraPos[0], 0), cameraPos[1])
    if (mouseY > HEIGHT - SCROLL_MARGIN):
        cameraPos = (cameraPos[0], cameraPos[1] - SCROLL_SPEED * dt)
        cameraPos = (cameraPos[0], max(cameraPos[1], HEIGHT - tiles.get_height()))
    elif (mouseY < SCROLL_MARGIN):
        cameraPos = (cameraPos[0], cameraPos[1] + SCROLL_SPEED * dt)    
        cameraPos = (cameraPos[0], min(cameraPos[1], 0))    

    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                pg.quit()
                sys.exit()
        elif event.type == pg.MOUSEMOTION:
            x, y = event.pos
            lx, ly = x - ORIGIN_X - int(cameraPos[0]), y - ORIGIN_Y - int(cameraPos[1])
            cx, cy = lx // tileSize[0], ly // tileSize[1]
            tx, ty = lx % tileSize[0], ly % tileSize[1]
            maskColor = tileMask.get_at((tx, ty))
            selected = cx + cy, cy - cx
            if (maskColor == (255, 0, 0, 255)):
                 selected = selected[0] - 1, selected[1]
            elif (maskColor == (0, 255, 0, 255)):
                selected = selected[0], selected[1] - 1
            elif (maskColor == (0, 0, 255, 255)):
                selected = selected[0], selected[1] + 1
            elif (maskColor == (255, 255, 0, 255)):
                selected = selected[0] + 1, selected[1]
           
    update()
    draw()
    pg.display.flip()

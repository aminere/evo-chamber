import sys
import pygame as pg
import tweener as tw

WIN_SIZE = WIDTH, HEIGHT = 1024, 768
FPS = 60

ORIGIN_X, ORIGIN_Y = 3, 0
WORLD_WIDTH, WORLD_HEIGHT = 8, 8

pg.init()
screen = pg.display.set_mode(size=WIN_SIZE)
clock = pg.time.Clock()

font = pg.font.SysFont("Arial", 32)
tile = pg.image.load('tile.png')
tileMask = pg.image.load('tile-mask.png')
tileSelected = pg.image.load('tile-selected.png')
tileW, tileH = tile.get_size()
dt = 0
cx, cy = 0, 0
selected = -1, -1
tx, ty = 0, 0

def update():
    dt = clock.tick(FPS)
    pg.display.set_caption(f"FPS: {clock.get_fps():.2f}")

def draw():
    screen.fill((0, 0, 0))

    for y in range(WORLD_HEIGHT):
        for x in range(WORLD_WIDTH):            
            wx, wy = tileW / 2 * (x - y), tileH / 2 * (x + y)
            if x == selected[0] and y == selected[1]:
                screen.blit(tileSelected, (wx + ORIGIN_X * tileW, wy + ORIGIN_Y * tileH))
            else:
                screen.blit(tile, (wx + ORIGIN_X * tileW, wy + ORIGIN_Y * tileH))    

    # rc = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    text = font.render("{x} {y}".format(x = tx, y = ty), False, (255, 255, 255))
    screen.blit(text, (0, 0))
    # screen.blit(tileSelected, (cx * tileW, cy * tileH))
    # pg.draw.rect(screen, (255, 0, 0), (cx * tileW, cy * tileH, tileW, tileH), 1)    

while True:
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
            cx, cy = x // tileW, y // tileH
            tx, ty = x % tileW, y % tileH
            maskColor = tileMask.get_at((tx, ty))
            selected = (cx - ORIGIN_X) + (cy - ORIGIN_Y), (cy - ORIGIN_Y) - (cx - ORIGIN_X)
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

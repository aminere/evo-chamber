import sys
import pygame as pg
import singletons

pg.init()
singletons.init()

while True:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                pg.quit()
                sys.exit()
        elif event.type == pg.MOUSEBUTTONUP:
            print("mouse button up")
        elif event.type == pg.MOUSEMOTION:            
            x, y = event.pos
            singletons._game.onMouseMoved(x, y)

    singletons._game.update()
    singletons._game.draw()
    pg.display.flip()
    
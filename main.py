import sys
import pygame as pg
import singletons

pg.init()
singletons.init()

while True:
    game = singletons._game
    
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                if (game.showIntro):
                    pg.quit()
                    sys.exit()
                else:
                    game.goBackToIntro()
        elif event.type == pg.MOUSEBUTTONUP:
            game.onMouseUp(event.button, event.pos)
        elif event.type == pg.MOUSEMOTION:            
            x, y = event.pos
            game.onMouseMoved(x, y)
    
    game.update()
    game.draw()
    pg.display.flip()

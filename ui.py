
import pygame as pg
import config
import button

class UI:
    def __init__(self):
        self.font = pg.font.SysFont("Arial", 32)

        height = config.bottomUI['height']
        self.rect = pg.Rect(0, config.screenSize[1] - height, config.screenSize[0], height)

        topEdge = config.screenSize[1] - height
        padding = 10
        gap = 10

        buildIcon = pg.image.load('images/ui/build.png')
        self.buttons = [
            button.Button(
                buildIcon,
                (padding, topEdge + padding),
                lambda: print('onClick build')
            ),
            button.Button(
                pg.image.load('images/ui/worker.png'),
                (padding + buildIcon.get_width() + gap, topEdge + padding),
                lambda: print('onClick worker')
            )
        ]

        self.pressedButton = None

    def update(self):
        (leftPressed, _, _) = pg.mouse.get_pressed()
        for button in self.buttons:
            if (button.rect.collidepoint(pg.mouse.get_pos())):                
                button.hovered = True
                button.pressed = leftPressed
                if (leftPressed):
                    self.pressedButton = button
            else:   
                button.hovered = False
                button.pressed = False

    def draw(self, screen):
        pg.draw.rect(screen, config.bottomUI['bgColor'], self.rect)

        for button in self.buttons:
            button.draw(screen)

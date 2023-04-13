
import pygame as pg
import config
import button

class UI:
    def __init__(self):

        height = config.bottomUI['height']
        self.surface = pg.Surface((config.screenSize[0], height))
        self.font = pg.font.SysFont("Arial", 32)
        
        self.rect = pg.Rect(0, config.screenSize[1] - height, self.surface.get_width(), height)
        self.pressedButton = None
        
        padding = 10
        gap = 10

        actions = [
            "plough",
            "plant",
            "water"
        ]
        self.buttons = []

        xPos = padding
        for action in actions:
            image = pg.image.load('images/ui/icon-' + action + '.png')
            self.buttons.append(button.Button(image, (xPos, padding), action))
            xPos += image.get_width() + gap                

    def update(self):
        (leftPressed, _, _) = pg.mouse.get_pressed()
        mousPos = pg.mouse.get_pos()
        localPos = mousPos[0], mousPos[1] - self.rect.y
        for button in self.buttons:
            if (button.rect.collidepoint(localPos)):
                button.hovered = True
                button.pressed = leftPressed
                if (leftPressed):
                    self.pressedButton = button
            else:   
                button.hovered = False
                button.pressed = False

    def draw(self, screen):        
        self.surface.fill(config.bottomUI['bgColor'])
        for button in self.buttons:
            button.draw(self.surface)

        screen.blit(self.surface, (0, config.screenSize[1] - self.surface.get_height()))

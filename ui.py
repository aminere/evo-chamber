
import pygame as pg
import config
import button
import singletons

class UI:
    def __init__(self):

        # height = config.uiHeight
        # self.surface = pg.Surface((config.screenSize[0], height))
        self.font = pg.font.Font("fixedsys.ttf", 48)
        self.coin = pg.image.load('images/ui/coin.png')
        
        # self.rect = pg.Rect(0, config.screenSize[1] - height, self.surface.get_width(), height)
        self.pressedButton = None
        self.hoveredButton = None    
        self.showCoins = False 

        actions = [
            # "plough",
            # "plant",
            # "water",
            # "pick",
            "worker",
            "expand"
            # "harvest"
        ]
        self.buttons = []

        iconSize = 100
        # width = iconSize * len(actions) + config.uiGap * (len(actions) - 1)
        yPos = config.screenSize[1] - iconSize - config.uiPadding
        xPos = config.uiPadding #(config.screenSize[0] - width) // 2
        for action in actions:
            image = pg.image.load('images/ui/icon-' + action + '.png')
            self.buttons.append(button.Button(image, (xPos, yPos), action))
            xPos += image.get_width() + config.uiGap 

        self.workerButton = self.buttons[0]
        self.expandButton = self.buttons[1]
        self.replayButton = None
        self.playButton = None        

    def update(self):
        (leftPressed, _, _) = pg.mouse.get_pressed()
        mousPos = pg.mouse.get_pos()
        hoveredButton = None
        for button in self.buttons:
            if (not button.visible):
                pass
            elif (button.disabled):
                button.hovered = False
                button.pressed = False
            elif (button.rect.collidepoint(mousPos)):
                button.hovered = True
                hoveredButton = button
                button.pressed = leftPressed
                if (leftPressed and not button.disabled):
                    self.pressedButton = button
            else:   
                button.hovered = False
                button.pressed = False
                
        self.hoveredButton = hoveredButton

    def draw(self, screen):        
        # self.surface.fill(config.uiBgColor)
        for button in self.buttons:
            button.draw(screen)

        if (self.showCoins):
            screen.blit(self.coin, (config.uiPadding, config.uiPadding))
            game = singletons._game
            text = self.font.render(f"{game.coins}", False, (255, 255, 255))
            screen.blit(text, (config.uiGap * 2 + self.coin.get_width(), config.uiGap))

    
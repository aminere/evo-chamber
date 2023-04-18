
import config
import singletons

class Tile:
    def __init__(self):
        self.state = config.rawTile
        self.worker = None
        self.time = 0
        self.action = None
        self.costAnimActive = False
        self.costAnimTime = 0
        self.costText = None

    def startCostAnim(self, cost):
        game = singletons._game
        self.costAnimActive = True
        self.costAnimTime = 0
        if (cost > 0):
            self.costText = game.ui.font.render(f"+{cost}", False, (0, 255, 0))
        else:
            self.costText = game.ui.font.render(f"{cost}", False, (255, 0, 0))

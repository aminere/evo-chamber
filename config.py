
bgColor = (17, 17, 17)
screenSize = (1024, 768)
fps = 60

worldSize = (12, 12)
tileSize = (128, 64)
origin = (worldSize[0] - 1) * tileSize[0] // 2, 0
mapSize = worldSize[0] * tileSize[0], worldSize[1] * tileSize[1]

scrollSpeed = 800
scrollMargin = 100

uiBgColor = (17, 17, 17)
uiPadding = 20
uiGap = 20

rawTile = 0
ploughedTile = rawTile + 1
plantedTile = ploughedTile + 1
readyTile = plantedTile + 2
fireTile = readyTile + 1
stoneTile = fireTile + 1

coins = 30
ploughCost = 1
plantCost = 2
waterCost = 5
pickCost = 2
harvestGain = 20
growDuration = 5
harvestDuration = 2
workerSpeed = 0.7

firstWorkerPos = (0, worldSize[1] // 2 - 1)


bgColor = (17, 17, 17)
screenSize = (1024, 768)
fps = 60

mapSize = (5, 5)
tileSize = (128, 64)
tileCount = mapSize[0] * mapSize[1]
origin = (mapSize[0] - 1) * tileSize[0] // 2, 0
mapSizePixels = mapSize[0] * tileSize[0], mapSize[1] * tileSize[1]
surfaceSize = mapSizePixels[0], mapSizePixels[1] + 10
maxAreasPerRow = 9

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

coins = 300
ploughCost = 1
plantCost = 2
waterCost = 5
pickCost = 2
workerCost = 10
expandCost = 20
harvestGain = 20
growDuration = 5
harvestDuration = 2
workerSpeed = 0.7
workDuration = 2

firstWorkerPos = (0, mapSize[1] // 2 - 1)

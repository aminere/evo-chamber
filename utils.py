
import config
import math

def worldToScreen(position):
    #x, y = map(lambda i: int(i), position)
    # x, y = int(position[0]), int(position[1])
    x, y = position
    return (config.tileSize[0] // 2 * (x - y)) + config.origin[0], (config.tileSize[1] // 2 * (x + y)) + config.origin[1]

def screenToWorld(position, cameraPos):
    x, y = position
    lx, ly = x - config.origin[0] + cameraPos[0], y - config.origin[1] + cameraPos[1]
    cx, cy = lx // config.tileSize[0], ly // config.tileSize[1]
    tx, ty = int(lx % config.tileSize[0]), int(ly % config.tileSize[1])
    return (cx + cy, cy - cx), tx, ty

def localToIndex(position):
    x, y = position
    return int(x + y * config.mapSize[0])

def worldToArea(position):
    x, y = position
    return int(x // config.mapSize[0]), int(y // config.mapSize[1])

def worldToLocal(area, worldPos):
    x, y = worldPos
    return x - area[0] * config.mapSize[0], y - area[1] * config.mapSize[1]

def indexToLocal(index):
    y = math.floor(index / config.mapSize[0])
    x = index - y * config.mapSize[0]
    return x, y

def lerp(a, b, t):
    return a + (b - a) * t

def lerp2d_InOutCubic(a, b, t):
    # return a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
    _t = t
    if (t < 0.5):
        _t = 4 * t * t * t
    else:
        _t = 1 - ((-2 * t + 2)**3) / 2
    return a[0] + (b[0] - a[0]) * _t, a[1] + (b[1] - a[1]) * _t
    
def distSquared(a, b):
    return ((a[0] - b[0])**2 + (a[1] - b[1])**2)

def areaToScreen(area):
    x, y = area
    return (config.mapSizePixels[0] // 2 * (x - y)), (config.mapSizePixels[1] // 2 * (x + y))

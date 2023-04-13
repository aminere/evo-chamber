
import config

def worldToScreen(position):
    x, y = map(lambda i: int(i), position)
    return (config.tileSize[0] // 2 * (x - y)) + config.origin[0], (config.tileSize[1] // 2 * (x + y)) + config.origin[1]

def screenToWorld(position, cameraPos):
    x, y = position
    lx, ly = x - config.origin[0] - int(cameraPos[0]), y - config.origin[1] - int(cameraPos[1])
    cx, cy = lx // config.tileSize[0], ly // config.tileSize[1]
    tx, ty = lx % config.tileSize[0], ly % config.tileSize[1]    
    return (cx + cy, cy - cx), tx, ty

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
    

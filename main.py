import sys
import pygame
from pygame.locals import *
import player
from tweener import *

pygame.init()
vec = pygame.math.Vector2  # 2 for two dimensional

WIDTH = 1024
HEIGHT = 768
ACC = 0.5
FRIC = -0.12
FPS = 60

FramePerSec = pygame.time.Clock()

displaysurface = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Evo Chamber")
 
class platform(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.surf = pygame.Surface((WIDTH, 20))
        self.surf.fill((255,0,0))
        self.rect = self.surf.get_rect(center = (WIDTH/2, HEIGHT - 10)) 

PT1 = platform()
P1 = player.Player()

image = pygame.image.load('test.png')
font = pygame.font.Font('Roboto-Medium.ttf', 30)
text = font.render('Hello world', True, (0, 255, 0), (0, 0, 128))

rect = pygame.Surface((100, 100))
rc = rect.get_rect()
rc.topleft = (100, 100)
rect.fill((255, 255, 255))

textRect = text.get_rect()
textRect.bottomright = (WIDTH, HEIGHT)
# textRect.topleft = (WIDTH - textRect.width, HEIGHT - textRect.height)

all_sprites = pygame.sprite.Group()
all_sprites.add(PT1)
all_sprites.add(P1)

alpha = {"alpha": 0}

# hero_tween = tween.to(rc, "x", 400, 5, "easeInOutQuad")
# hero_tween.on_complete.add(lambda: print("Tween complete!"))

anim = Tween(begin=100, end=400, duration=1000, easing=Easing.BOUNCE,
               easing_mode=EasingMode.OUT,
               boomerang=True, 
               loop=True)
anim.start()
# fadeout = tween.to(alpha, "alpha", 255, 1, "easeInOutQuad")

transition = pygame.Surface((WIDTH, HEIGHT))

angle = 0
while True:
    pos = pygame.mouse.get_pos()
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:            
            if rc.collidepoint(pos):
                if event.button == 1:
                    print("Left MOUSEBUTTONDOWN at ({0}, {1})".format(pos[0], pos[1]))
                if event.button == 3:
                    print("Right MOUSEBUTTONDOWN at ({0}, {1})".format(pos[0], pos[1]))
        elif event.type == pygame.MOUSEBUTTONUP:
            if rc.collidepoint(pos):
                if event.button == 1:
                    print("Left MOUSEBUTTONUP at ({0}, {1})".format(pos[0], pos[1]))
                if event.button == 3:
                    print("Right MOUSEBUTTONUP at ({0}, {1})".format(pos[0], pos[1]))

    displaysurface.fill((0,0,0))
 
    for entity in all_sprites:
        displaysurface.blit(entity.surf, entity.rect)

    scaled_image = pygame.transform.scale(image, (100, 100))
    rotated_image = pygame.transform.rotate(scaled_image, angle)    
    angle += 1
    displaysurface.blit(rotated_image, ((WIDTH - rotated_image.get_width()) / 2, (HEIGHT - rotated_image.get_height()) / 2))
    displaysurface.blit(text, textRect)    
    
    anim.update()
    rc.x = anim.value
    displaysurface.blit(rect, rc) 
    
    pygame.draw.line(displaysurface, (255, 255, 255), (0, 0), (WIDTH, HEIGHT), 1)

    # pygame.draw.rect(transition, (255, 0, 0), (0, 0, WIDTH, HEIGHT))
    # transition.set_alpha(alpha.get("alpha"))
    # displaysurface.blit(transition, (0, 0))

    pygame.display.update()
    dt = FramePerSec.tick(FPS) / 1000

    # tween.update(dt)        

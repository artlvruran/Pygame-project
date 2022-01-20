import sys
import os

import pygame
import pytmx

FPS = 60
SCREEN_SIZE = WIDTH, HEIGHT = 1300, 700
TILE_WIDTH, TILE_HEIGHT = 64, 32
FIELD_WIDTH, FIELD_HEIGHT = 20, 20
MAPS_DIR = 'maps'

pygame.init()
screen = pygame.display.set_mode(SCREEN_SIZE)
clock = pygame.time.Clock()

all_sprites = pygame.sprite.Group()
enemies_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
box_group = pygame.sprite.Group()
layers = [pygame.sprite.Group() for i in range(3)]
tiles = [[[0] * (FIELD_WIDTH + 1) for __ in range(FIELD_HEIGHT + 1)] for _ in range(3)]


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def terminate():
    pygame.quit()
    sys.exit()


def start_screen(screen, clock):
    fon = pygame.transform.scale(load_image('fon.jpg'), SCREEN_SIZE)
    screen.blit(fon, (0, 0))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                return
            pygame.display.flip()
            clock.tick(FPS)


class Field:
    def __init__(self, filename):
        self.map = pytmx.load_pygame(f'{MAPS_DIR}/{filename}')
        self.height = self.map.height
        self.width = self.map.width
        self.tile_height = self.map.tileheight
        self.tile_width = self.map.tilewidth

    def create(self, screen):
        for y in range(self.height - 1, -1, -1):
            xx = y * TILE_WIDTH // 2
            yy = 320 - y * TILE_HEIGHT // 2
            for x in range(0, self.width):
                image = self.map.get_tile_image(x, self.height - y - 1, layer)
                if image:
                    tile = Tile(image, xx + x * TILE_WIDTH // 2, yy + x * TILE_HEIGHT // 2 - TILE_HEIGHT * layer)
                    layers[layer].add(tile)
                    tiles[layer][y][x] = 1
                print(x, y)

    def get_tile_id(self, position):
        return self.map.tiledgidmap[self.map.get_tile_gid(*position, 0)]


class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, group, frames, x, y):
        super().__init__(all_sprites, group)
        self.frames = [load_image(frame) for frame in frames]
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(x, y)

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]


class Hero(AnimatedSprite):

    def __init__(self, pos_x, pos_y):
        self.pos_x = pos_x
        self.pos_y = pos_y






class Enemy:
    pass


class Tile(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        super().__init__(all_sprites)
        self.image = image
        self.rect = self.image.get_rect().move(x, y)



"""class Camera:
    def __init__(self):
        self.dx = 0
        self.dy = 0

    def apply(self, obj):
        obj.rect.x = (obj.rect.x + self.dx) % (len(load_level(level_name)[0]) * tile_width)
        obj.rect.y = (obj.rect.y + self.dy) % (len(load_level(level_name)) * tile_height)

    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - WIDTH // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - HEIGHT // 2)
"""


def main():

    # camera = Camera()

    start_screen(screen, clock)
    screen.fill((0, 0, 0))
    running = True
    field = Field('map1.tmx')
    field.create(screen)

    hero = Hero(0, 0)
    player_group.add(hero)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if pygame.key.get_pressed()[pygame.K_UP]:
                hero.move(TILE_WIDTH // 2, -TILE_HEIGHT // 2, 'rightup', 0, 1)
            if pygame.key.get_pressed()[pygame.K_DOWN]:
                hero.move(-TILE_WIDTH // 2, TILE_HEIGHT // 2, 'leftdown', 0, -1)
            if pygame.key.get_pressed()[pygame.K_LEFT]:
                hero.move(-TILE_WIDTH // 2, -TILE_HEIGHT // 2, 'leftup', -1, 0)
            if pygame.key.get_pressed()[pygame.K_RIGHT]:
                hero.move(TILE_WIDTH // 2, TILE_HEIGHT // 2, 'rightdown', 1, 0)
        screen.fill((0, 0, 0))
        all_sprites.update()
        layers[0].draw(screen)
        screen.blit(hero.image, hero.rect)
        for layer in layers[1:]:
            layer.draw(screen)
        pygame.display.flip()
    pygame.quit()
main()
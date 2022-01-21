import sys
import os
import math

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


"""class Field:
    def __init__(self, filename):
        self.map = pytmx.load_pygame(f'{MAPS_DIR}/{filename}')
        self.height = self.map.height
        self.width = self.map.width
        self.tile_height = self.map.tileheight
        self.tile_width = self.map.tilewidth

    def create(self, screen):
        for y in range(self.height - 1, -1, -1):
            for x in range(0, self.width):
                image = self.map.get_tile_image(x, self.height - y - 1, 0)

    def get_tile_id(self, position):
        return self.map.tiledgidmap[self.map.get_tile_gid(*position, 0)]"""


class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y):
        super().__init__(all_sprites)
        self.frames = []
        self.cut_sheet(sheet, columns, rows, 0, 0)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)

    def cut_sheet(self, sheet, columns, rows, x, y):
        self.rect = pygame.Rect(x, y, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]

    def update_sheet(self, sheet, columns, rows):
        self.frames = []
        self.cut_sheet(sheet, columns, rows, self.rect.x, self.rect.y)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]


class Hero(AnimatedSprite):
    idle = load_image('idle.png')
    run = load_image('run.png')

    def __init__(self, pos_x, pos_y):
        self.pos_x = pos_x
        self.pos_y = pos_y
        super().__init__(Hero.idle, 4, 1, pos_x, pos_y)
        self.mode = 'idle'
        self.key = 'right'

    def change_mode(self, mode):
        if mode == 'run':
            self.mode = 'run'
            self.update_sheet(Hero.run, 8, 1)
        if mode == 'idle':
            self.mode = 'idle'
            self.update_sheet(Hero.idle, 4, 1)

class Enemy:
    pass


"""class Tile(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        super().__init__(all_sprites)
        self.image = image
        self.rect = self.image.get_rect().move(x, y)"""


def main():
    start_screen(screen, clock)
    screen.fill((0, 0, 0))
    running = True
    """field = Field('map1.tmx')
    field.create(screen)"""

    hero = Hero(100, 100)
    player_group.add(hero)
    moving = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and \
                    (hero.rect.x != pygame.mouse.get_pos()[0] or hero.rect.y != pygame.mouse.get_pos()[1]):
                moving = True
            if event.type == pygame.MOUSEBUTTONUP:
                moving = False
        if moving:
            if hero.mode != 'run':
                hero.change_mode('run')
            sx = pygame.mouse.get_pos()[0] - hero.rect.x
            sy = pygame.mouse.get_pos()[1] - hero.rect.y
            cos = sx / (sx ** 2 + sy ** 2) ** 0.5
            sin = sy / (sx ** 2 + sy ** 2) ** 0.5
            hero.pos_x += cos
            hero.pos_y += sin
            hero.rect.x = hero.pos_x
            hero.rect.y = hero.pos_y
        else:
            hero.change_mode('idle')
        clock.tick(30)
        screen.fill((6, 59, 36))
        all_sprites.update()
        all_sprites.draw(screen)
        pygame.display.flip()
    pygame.quit()


main()
import sys
import os
import math
import random

import pygame
import pytmx


SCREEN_SIZE = WIDTH, HEIGHT = 720, 480
TILE_WIDTH, TILE_HEIGHT = 64, 32
FIELD_WIDTH, FIELD_HEIGHT = 20, 20
MAPS_DIR = 'maps'

def load_map(map_id):
    map_img = pygame.image.load('data/maps/' + map_id + '.png')
    map_data = []
    enemy_count = 0
    for y in range(map_img.get_height()):
        for x in range(map_img.get_width()):
            c = map_img.get_at((x, y))
            if c[1] == 100:
                map_data.append({'type': 'grass', 'pos': [x, y], 'h_pos': 400, 'enemy': False})
            if c[1] == 255:
                map_data.append({'type': 'bush', 'pos': [x, y], 'h_pos': 400, 'enemy': False})
            if c[2] == 100:
                map_data.append({'type': 'rock', 'pos': [x, y], 'h_pos': 400, 'enemy': False})
            if c[2] == 255:
                map_data.append({'type': 'box', 'pos': [x, y], 'h_pos': 400, 'enemy': False})
            if c[0] == 255:
                spawn = [x, y]
            if c[0] == 100:
                map_data[-1]['enemy'] = True
                enemy_count += 1
    return map_data, spawn, enemy_count

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

FPS = 60
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


class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, list_of_frames, x, y):
        super().__init__(all_sprites)
        self.frames = list_of_frames
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = pygame.Rect(x, y, self.frames[self.cur_frame].get_width(),
                                self.frames[self.cur_frame].get_height())
        self.rect = self.rect.move(x, y)

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]

    def change_frame(self, list_of_frames):
        self.frames = list_of_frames
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]


class Hero(AnimatedSprite):
    im_1 = pygame.transform.scale(load_image('character_1.png'), (64, 96))
    im_2 = pygame.transform.scale(load_image('character_2.png'), (64, 96))
    sword_im = load_image('sword.png')

    def __init__(self, pos_x, pos_y):
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.update_ = False
        self.right = True
        self.cos_angle, sin_angle = 0, 1
        self.sword = pygame.sprite.Sprite(all_sprites)
        super().__init__([Hero.im_1, Hero.im_2], pos_x, pos_y)

    def advance(self):
        sx = pygame.mouse.get_pos()[0] - self.rect.x
        sy = pygame.mouse.get_pos()[1] - self.rect.y
        if sx != 0:
            cos = sx / (sx ** 2 + sy ** 2) ** 0.5
        else:
            cos = 0
        if sy != 0:
            sin = sy / (sx ** 2 + sy ** 2) ** 0.5
        else:
            sin = 0
        if sin == 0 and cos == 0:
            self.update_ = False
        else:
            self.update_ = True
        if (cos > 0) != self.right:
            self.right = cos > 0
            self.frames = [pygame.transform.flip(self.frames[0], True, False),
                           pygame.transform.flip(self.frames[1], True, False)]
        self.pos_x += cos
        self.pos_y += sin
        self.rect.x = self.pos_x
        self.rect.y = self.pos_y
        self.sin_angle, self.cos_angle = sin, cos

    def update(self):
        super().update()
        rect = pygame.transform.rotate(Hero.sword_im, math.acos(self.cos_angle)).get_rect()
        rect.x, rect.y = self.rect.x, self.rect.y
        self.sword.rect = rect
        self.sword.image = Hero.sword_im


def main():
    start_screen(screen, clock)
    screen.fill((0, 0, 0))
    running = True
    speed = 4

    hero = Hero(100, 100)
    player_group.add(hero)

    while running:
        mx, my = pygame.mouse.get_pos()

        # Buttons
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                pass

        # Moving
        hero.advance()

        # Rendering


        # Background

        clock.tick(60)
        screen.fill((0, 0, 0))
        all_sprites.update()
        all_sprites.draw(screen)
        screen.blit(hero.sword.image, hero.sword.rect)
        pygame.display.flip()
    pygame.quit()


main()

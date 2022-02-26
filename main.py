import sys
import os
import math
import random

import pygame
import pytmx
from scripts import *
pygame.init()
screen = pygame.display.set_mode(SCREEN_SIZE)
from entities import *


FIELD_WIDTH, FIELD_HEIGHT = 20, 20
MAPS_DIR = './data/maps'


clock = pygame.time.Clock()
THIRD_WIDTH = WIDTH // 3
THIRD_HEIGHT = HEIGHT // 3
RADIUS = int(math.sqrt(THIRD_HEIGHT ** 2 + THIRD_WIDTH ** 2))
all_sprites = pygame.sprite.Group()
enemies_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
wall_group = pygame.sprite.Group()
projectiles_group = pygame.sprite.Group()
tiles = [[[0] * (FIELD_WIDTH + 1) for __ in range(FIELD_HEIGHT + 1)] for _ in range(3)]
sword_animation = [pygame.transform.scale(load_image(f'SP301_0{i}.png'), (120, 120)) for i in range(1, 6)]

spawn = {
    1: (30, 4)
}


class Field:
    def __init__(self, filename, spawn_pos):
        self.map = pytmx.load_pygame(f'{MAPS_DIR}/{filename}')
        self.height = self.map.height
        self.width = self.map.width
        self.tile_size = self.map.tilewidth
        self.offset = spawn_pos
        self.free_tiles = [9]
        self.finish_tiles = []

    def render(self, screen):
        for y in range(self.height):
            for x in range(self.width):
                image = self.map.get_tile_image(x, y, 0)
                screen.blit(image, (x * self.tile_size - self.offset[0] * self.tile_size,
                                    y * self.tile_size - self.offset[1] * self.tile_size))

    def get_tile_id(self, position):
        return self.map.tiledgidmap[self.map.get_tile_gid(*position, 0)]

    def is_free(self, position):
        return self.get_tile_id(position) in self.free_tiles


sword_im = pygame.transform.scale(load_image('saber.png'), (116, 16))


class Particles(pygame.sprite.Sprite):
    img = pygame.transform.scale(load_image('projectile.png'), (15, 15))

    def __init__(self, pos, dx, dy, all_sprites):
        super().__init__(all_sprites, projectiles_group)
        self.image = Particles.img
        self.rect = self.image.get_rect()

        self.velocity = [dx, dy]

        self.rect.x, self.rect.y = pos

    def update(self):
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        if pygame.sprite.spritecollideany(self, player_group):
            player = player_group.sprites()[0]
            if self.rect.x + self.image.get_width() >= player.rect.x >= self.rect.x and self.velocity[0] > 0:
                self.velocity[0] = -self.velocity[0]
            elif player.rect.x + player.image.get_width() >= self.rect.x >= player.rect.x and self.velocity[0] < 0:
                self.velocity[0] = -self.velocity[0]
            if self.rect.y + self.image.get_height() >= player.rect.y >= self.rect.y and self.velocity[1] > 0:
                self.velocity[1] = -self.velocity[1]
            elif player.rect.y + player.image.get_height() >= self.rect.y >= player.rect.y and self.velocity[1] < 0:
                self.velocity[1] = -self.velocity[1]

        if not self.rect.colliderect(screen_rect):
            self.kill()


class Enemy(AnimatedSprite):
    img = [load_image('enemy.png')]
    speed = 10

    def __init__(self, x, y, all_sprites, number):
        super().__init__(Enemy.img, x, y, all_sprites)
        self.image = Enemy.img[0]
        self.x, self.y = x, y
        self.rect = pygame.Rect(x, y, self.image.get_width(), self.image.get_height())
        self.particles = []
        self.number = number

    def let_out(self, all_sprites):
        for i in range(self.number):
            dx = math.cos(math.radians(i * (360 / self.number))) * Enemy.speed
            dy = math.sin(math.radians(i * (360 / self.number))) * Enemy.speed
            self.particles.append(Particles((self.rect.x + self.image.get_width() // 2,
                                             self.rect.y), dx, dy, all_sprites))



class Angle:
    def __init__(self):
        self.degrees = 0
        self.sin = 0
        self.cos = 1
        self.hyp = 0

    def change(self, mx, my, pos):
        self.hyp = math.sqrt((mx - pos[0]) ** 2 + (my - pos[1]) ** 2)
        if self.hyp:
            self.cos = (mx - pos[0]) / self.hyp
            self.sin = (-my + pos[1]) / self.hyp
            self.degrees = math.degrees(math.atan2(self.sin, self.cos))
        else:
            self.sin = 0
            self.cos = 1


mainAngle = Angle()


class Hero(AnimatedSprite):
    im_1 = pygame.transform.scale(load_image('explorer_run1.png'), (40, 60))
    im_2 = pygame.transform.scale(load_image('explorer_run2.png'), (40, 60))
    idle = pygame.transform.scale(load_image('explorer_idle.png'), (40, 60))

    def __init__(self, pos_x, pos_y):
        self.idle_frame = [Hero.idle]
        self.move_frames = [Hero.im_1, Hero.im_2]
        self.flip = False
        self.progress = 0
        self.speed = 0
        self.mode = 'idle'
        self.dx = 0
        self.dy = 0
        super().__init__([Hero.im_1, Hero.im_2], pos_x, pos_y, all_sprites)

    def advance(self):
        cos, sin = mainAngle.cos, mainAngle.sin
        if cos < 0 and not self.flip or cos > 0 and self.flip:
            self.flip = not self.flip
            self.move_frames = [pygame.transform.flip(self.move_frames[0], True, False),
                                pygame.transform.flip(self.move_frames[1], True, False)]
            self.idle_frame = [pygame.transform.flip(Hero.idle, True, False)]
            self.frames = self.move_frames
        if cos != 0:
            self.dx = max(1, abs(cos * self.speed)) * (1 if cos > 0 else -1)
        if sin != 0:
            self.dy = max(1, abs(sin * self.speed)) * (1 if sin < 0 else -1)

    def update(self):
        if self.mode == 'move':
            super().update()
            if len(self.frames) == 1:
                self.change_frame(self.move_frames)
        else:
            self.change_frame(self.idle_frame)
        if pygame.sprite.spritecollideany(self, projectiles_group):
            self.dx = -self.dx
            self.dy = -self.dy

    def increase_progress(self, amount):
        self.progress += amount
        self.cur_frame = int(self.progress) % len(self.frames)


class Cursor(pygame.sprite.Sprite):
    image = pygame.transform.scale(load_image('cursor.png'), (32, 32))

    def __init__(self, abcissa, ordinate, *group):
        super().__init__(*group)
        self.image = Cursor.image
        self.rect = self.image.get_rect()
        self.rect.x = abcissa
        self.rect.y = ordinate
        self.hide = False

    def update(self, abcissa, ordinate):
        self.rect.x = abcissa
        self.rect.y = ordinate


class Camera:
    def __init__(self):
        self.dx = 0
        self.dy = 0
        self.hyp = 0
        self.sin = 0
        self.cos = 1


def main():
    field = Field('level1.tmx', spawn[1])

    level = 1

    tile_width = field.tile_size

    cursor_sprite = Cursor(0, 0)

    frame_offset = 0

    pygame.mouse.set_visible(False)

    camera = Camera()

    start_screen(screen, clock)

    screen.fill((0, 0, 0))

    running = True

    hero = Hero(screen.get_width() // 4, screen.get_height() // 4)
    player_group.add(hero)

    sword_anim_idx = None

    background_offset = 0

    enemies = []
    enemy1 = Enemy(16 * field.tile_size - spawn[level][0], 11 * field.tile_size - spawn[level][1], all_sprites, 8)
    enemies += [enemy1]
    enemy_progress = 0
    for enemy in enemies:
        enemies_group.add(enemy)

    while running:
        mx, my = pygame.mouse.get_pos()
        mainAngle.change(mx, my, (hero.rect.x, hero.rect.y))

        hero.speed = min(1, max(0, mainAngle.hyp - 100) / 150)
        hero.speed = hero.speed ** 2
        hero.speed *= 10
        hero.speed /= 2

        if int(mainAngle.hyp) > 1:
            hero.mode = 'move'
            hero.advance()
        else:
            hero.mode = 'idle'
            hero.dx = 0
            hero.dy = 0
        hero.rect.x += hero.dx
        hero.rect.y += hero.dy
        if hero.rect.x > 2 * THIRD_WIDTH:
            hero.rect.x = 2 * THIRD_WIDTH
        elif hero.rect.x < THIRD_WIDTH:
            hero.rect.x = THIRD_WIDTH
        if hero.rect.y > 2 * THIRD_HEIGHT:
            hero.rect.y = 2 * THIRD_HEIGHT
        elif hero.rect.y < THIRD_HEIGHT:
            hero.rect.y = THIRD_HEIGHT

        hero.increase_progress(0.2)

        camera.dx += hero.dx
        camera.dy += hero.dy

        for enemy in enemies:
            enemy.rect.x = enemy.x - camera.dx
            enemy.rect.y = enemy.y - camera.dy
            enemy_progress += 0.5

            if enemy_progress == 50:
                enemy_progress = 0
                enemy.let_out(all_sprites)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEMOTION:
                cursor_sprite.update(*event.pos)
            # Buttons
            if event.type == pygame.MOUSEBUTTONDOWN:
                sword_anim_idx = 0

        # Rendering

        clock.tick(60)
        screen.fill((0, 0, 0))
        background_offset = (background_offset + 0.25) % 30
        for i in range(9):
            pygame.draw.line(screen, (5, 18, 24), (-10, int(i * 30 + background_offset - 20)),
                             (screen.get_width() + 10, int(i * 30 - 110 + background_offset)), 15)

        field.offset = (camera.dx / 32, camera.dy / 32)
        field.render(screen)
        all_sprites.update()
        all_sprites.draw(screen)
        screen.blit(cursor_sprite.image, cursor_sprite.rect)

        if sword_anim_idx is not None:
            frame = sword_animation[sword_anim_idx]
            if hero.flip:
                frame = pygame.transform.flip(frame, True, False)
            if mainAngle.sin > 0:
                frame = pygame.transform.flip(frame, False, True)
            screen.blit(frame, pygame.Rect(hero.rect.x + (hero.image.get_width() - frame.get_width()) // 2,
                                           hero.rect.y + (hero.image.get_height() - frame.get_height()) // 2,
                                           frame.get_width(), frame.get_height()))
            sword_anim_idx += 1
            if sword_anim_idx == len(sword_animation):
                sword_anim_idx = None
        else:
            rotated_sword_im = pygame.transform.rotate(sword_im, math.degrees(math.atan2(mainAngle.sin, mainAngle.cos)))
            pos = (hero.rect.x + hero.image.get_width() // 2, int(hero.rect.y + hero.image.get_height() * 2 / 3))
            screen.blit(rotated_sword_im, rotated_sword_im.get_rect(center=pos))

        if hero.speed >= 8:
            frame_offset += (15 - frame_offset) / 20
        else:
            frame_offset += (-frame_offset) / 50

        pygame.draw.rect(screen, (5, 18, 24),
                         pygame.Rect(0, screen.get_height() - frame_offset, screen.get_width(), 15))
        pygame.draw.rect(screen, (5, 18, 24), pygame.Rect(0, -15 + frame_offset, screen.get_width(), 15))
        pygame.display.flip()
    pygame.quit()


main()

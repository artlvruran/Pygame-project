import pygame
import math
from scripts import *
screen_rect = pygame.Rect(0, 0, WIDTH, HEIGHT)


class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, list_of_frames, x, y, all_sprites):
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


class Particles(pygame.sprite.Sprite):
    img = load_image('projectile.png')

    def __init__(self, pos, dx, dy, all_sprites):
        super().__init__(all_sprites)
        self.image = Particles.img
        self.rect = self.image.get_rect()

        self.velocity = [dx, dy]

        self.rect.x, self.rect.y = pos

    def update(self):
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
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
        for i in range(number):
            dx = math.cos(math.radians(i * (360 / number))) * Enemy.speed
            dy = math.sin(math.radians(i * (360 / number))) * Enemy.speed
            self.particles.append(Particles((x, y), dx, dy, all_sprites))
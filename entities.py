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

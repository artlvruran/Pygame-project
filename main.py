import sys
import os

import pygame
import pytmx

FPS = 60
SCREEN_SIZE = WIDTH, HEIGHT = 1300, 700
TILE_WIDTH, TILE_HEIGHT = 64, 32
MAPS_DIR = 'maps'

pygame.init()
screen = pygame.display.set_mode(SCREEN_SIZE)
clock = pygame.time.Clock()

all_sprites = pygame.sprite.Group()
enemies_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
box_group = pygame.sprite.Group()


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

    def render(self, screen):
        for layer in range(3):
            for y in range(self.height - 1, 0, -1):
                xx = y * TILE_WIDTH // 2
                yy = 320 - y * TILE_HEIGHT // 2
                for x in range(self.width):
                    image = self.map.get_tile_image(x, y, layer)
                    if image:
                        screen.blit(image, (xx + x * TILE_WIDTH // 2, yy + x * TILE_HEIGHT // 2))

    def get_tile_id(self, position):
        return self.map.tiledgidmap[self.map.get_tile_gid(*position, 0)]


class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, group, frames, x, y):
        super().__init__(all_sprites, group)
        self.names = frames
        self.frames = [load_image(frame) for frame in self.names]
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(x, y)

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]


class Hero(AnimatedSprite):
    #player_image = load_image('knights_sprites .png')
    images_walking_rightup = [f'crusader_walk_300{str(i).ljust(2, "0")}.png' for i in range(15)]
    images_walking_leftup = [f'crusader_walk_500{str(i).ljust(2, "0")}.png' for i in range(15)]
    images_walking_rightdown = [f'crusader_walk_100{str(i).ljust(2, "0")}.png' for i in range(15)]
    images_walking_leftdown = [f'crusader_walk_200{str(i).ljust(2, "0")}.png' for i in range(15)]
    images_idle = ['crusader_idle.png']

    def __init__(self, pos_x, pos_y):
        self.pos_x = pos_x
        self.pos_y = pos_y
        xx = pos_y * TILE_WIDTH // 2 + TILE_WIDTH // 2
        yy = 320 - pos_y * TILE_HEIGHT // 2 - 1.5 * TILE_HEIGHT
        super().__init__(player_group, Hero.images_idle, xx + pos_x * TILE_WIDTH // 2,
                         yy + pos_x * TILE_HEIGHT // 2)
        self.mode = 'idle'

        """if pygame.sprite.spritecollideany(self, layers_sprites[1]):
            self.rect.x -= kx * (TILE_WIDTH // 2)
            self.rect.y -= ky * (TILE_HEIGHT // 2)"""
    def update(self):
        super().update()
        if self.mode == 'idle':
            self.names = Hero.images_idle
        if self.mode == 'walking_leftup':
            self.names = Hero.images_walking_leftup
        if self.mode == 'walking_rightup':
            self.names = Hero.images_walking_rightup
        if self.mode == 'walking_leftdown':
            self.names = Hero.images_walking_leftdown
        if self.mode == 'walking_rightdown':
            self.names = Hero.images_walking_rightdown


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

    hero = Hero(0, 0)
    player_group.add(hero)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if pygame.key.get_pressed()[pygame.K_UP]:
                hero.rect.x += TILE_WIDTH // 2
                hero.rect.y -= TILE_HEIGHT // 2
                hero.mode = 'rightup'
            if pygame.key.get_pressed()[pygame.K_DOWN]:
                hero.rect.x -= TILE_WIDTH // 2
                hero.rect.y += TILE_HEIGHT // 2
                hero.mode = 'leftdown'
            if pygame.key.get_pressed()[pygame.K_LEFT]:
                hero.rect.x -= TILE_WIDTH // 2
                hero.rect.y -= TILE_HEIGHT // 2
                hero.mode = 'leftup'
            if pygame.key.get_pressed()[pygame.K_RIGHT]:
                hero.rect.x += TILE_WIDTH // 2
                hero.rect.y += TILE_HEIGHT // 2
                hero.mode = 'right_down'
        screen.fill((0, 0, 0))
        field.render(screen)
        all_sprites.update()
        all_sprites.draw(screen)
        pygame.display.flip()
    pygame.quit()
main()
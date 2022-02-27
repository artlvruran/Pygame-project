import os
import sys
import pygame


SCREEN_SIZE = WIDTH, HEIGHT = 920, 680
FPS = 60


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


def game_over_text_screen(last_frame, screen_text, screen, clock):
    timer = 0
    going = True
    while going:
        screen.blit(last_frame, (0, 0))
        timer += 1
        timer %= 20
        black_surf = pygame.Surface((WIDTH, HEIGHT))
        black_surf.set_alpha(int(timer * 12.75))
        screen.blit(black_surf, (0, 0))
        font = pygame.font.SysFont('bauhaus 93', 50)
        text = font.render("", True, (100, 255, 100))
        text = font.render(screen_text, True, (100, 255, 100))
        text_x = WIDTH // 2 - text.get_width() // 2
        text_y = HEIGHT // 2 - text.get_height() // 2
        screen.blit(text, (text_x, text_y))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    going = False

        screen.blit(pygame.transform.scale(screen, (WIDTH, HEIGHT)), (0, 0))
        pygame.display.update()
        clock.tick(60)
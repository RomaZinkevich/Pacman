import pygame
import time
import sys
BEGIN = True
walls = pygame.sprite.Group()
player = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()
saves_hor = pygame.sprite.Group()
ghosts = pygame.sprite.Group()

SCORE = '0'


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(all_sprites)
        self.image = pygame.transform.scale(tile_images[tile_type], (50, 50))
        self.images = self.image
        self.type = tile_type
        if tile_type == "wall" or tile_type == "gate":
            self.add(walls)
        if tile_type == "save_hor":
            self.add(saves_hor)
        self.rect = self.image.get_rect().move(
            tile_width * pos_x - 50, tile_height * pos_y)
        self.flag = False

    def update(self, a):
        global SCORE
        if self.type == 'empty' and pygame.sprite.spritecollideany(self, player)\
                and self.image == self.images:
            if int(SCORE) >= 0:
                pygame.mixer.music.play()
            self.image = pygame.transform.scale(
                pygame.image.load('black.bmp'), (50, 50))
            SCORE = int(SCORE)
            SCORE += 10
            SCORE = str(SCORE)


class Pacman(pygame.sprite.Sprite):
    def __init__(self, group, x, y):
        super().__init__(group)
        self.add(player)
        self.ball = pygame.transform.scale(
            pygame.image.load('ball.png'), (50, 50))
        self.image_right = pygame.transform.scale(player_image, (50, 50))
        self.image_left = pygame.transform.flip(self.image_right, True, False)
        self.image_up = pygame.transform.rotate(self.image_right, 90)
        self.image_down = pygame.transform.rotate(self.image_right, 270)
        self.image_right_open = pygame.transform.scale(
            player_image_open, (50, 50))
        self.image_left_open = pygame.transform.flip(
            self.image_right_open, True, False)
        self.image_up_open = pygame.transform.rotate(self.image_right_open, 90)
        self.image_down_open = pygame.transform.rotate(
            self.image_right_open, 270)
        self.image = self.ball
        self.rect = self.image.get_rect().move(
            tile_width * x - 50, tile_height * y)
        self.flag_left, self.flag_right, self.flag_up, self.flag_down, \
            = True, True, True, True
        self.direction = None
        self.direction2 = None
        self.frames = [self.image_right, self.image_right_open]
        self.frame = 1
        self.time = 0
        self.update(self.direction)

    def update(self, direction):
        self.time += 1
        if self.time == 20:
            self.frame = abs(self.frame - 1)
            self.image = self.frames[self.frame]
            self.time = 0
        if direction and self.rect.x % 50 == 0 and self.rect.y % 50 == 0:
            self.direction = direction
        elif direction:
            self.direction2 = direction
        if self.direction2 and self.rect.x % 50 == 0 and self.rect.y % 50 == 0:
            checks = self.check_level(
                (self.rect.x + 50) // 50, self.rect.y // 50)
            if self.direction2 == "right" and checks[0]:
                self.direction = self.direction2
                self.direction2 = None
            if self.direction2 == "up" and checks[1]:
                self.direction = self.direction2
                self.direction2 = None
            if self.direction2 == "left" and checks[2]:
                self.direction = self.direction2
                self.direction2 = None
            if self.direction2 == "down" and checks[3]:
                self.direction = self.direction2
                self.direction2 = None
            self.image = self.frames[self.frame]
        x, y = self.rect.x, self.rect.y
        if self.direction == "up":
            self.up(self.flag_up)
            if self.flag_up:
                self.frames[0] = self.image_up
                self.frames[1] = self.image_up_open
            else:
                self.frames[1] = self.image_up
        if self.direction == "down":
            self.down(self.flag_down)
            if self.flag_down:
                self.frames[0] = self.image_down
                self.frames[1] = self.image_down_open
            else:
                self.frames[1] = self.image_down
        if self.direction == "left":
            self.left(self.flag_left)
            if self.flag_left:
                self.frames[0] = self.image_left
                self.frames[1] = self.image_left_open
            else:
                self.frames[1] = self.image_left
        if self.direction == "right":
            self.right(self.flag_right)
            if self.flag_right:
                self.frames[0] = self.image_right
                self.frames[1] = self.image_right_open
            else:
                self.frames[1] = self.image_right
        if pygame.sprite.spritecollideany(self, walls):
            if self.rect.x - x > 0:
                self.flag_right = False
                self.frames = [self.image_right, self.image_right]
            if self.rect.x - x < 0:
                self.flag_left = False
                self.frames = [self.image_left, self.image_left]
            if self.rect.y - y < 0:
                self.flag_up = False
                self.frames = [self.image_up, self.image_up]
            if self.rect.y - y > 0:
                self.flag_down = False
                self.frames = [self.image_down, self.image_down]
            self.rect.x, self.rect.y = x, y
        if pygame.sprite.spritecollideany(self, saves_hor):
            if self.rect.x - x > 0:
                self.rect.x -= 16 * 50
            else:
                self.rect.x += 16 * 50

    def check_level(self, x, y):
        return (level_map[y][x + 1] != "#" and level_map[y][x + 1] != "-", level_map[y - 1][x] != "#" and level_map[y - 1][x] != "-",
                level_map[y][x - 1] != "#" and level_map[y][x - 1] != "-", level_map[y + 1][x] != "#" and level_map[y + 1][x] != "-")

    def right(self, flag):
        if flag:
            self.rect.x += 1
            self.flag_left, self.flag_right, self.flag_up, self.flag_down, \
                = True, True, True, True

    def left(self, flag):
        if flag:
            self.rect.x -= 1
            self.flag_left, self.flag_right, self.flag_up, self.flag_down, \
                = True, True, True, True

    def up(self, flag):
        if flag:
            self.rect.y -= 1
            self.flag_left, self.flag_right, self.flag_up, self.flag_down, \
                = True, True, True, True

    def down(self, flag):
        if flag:
            self.rect.y += 1
            self.flag_left, self.flag_right, self.flag_up, self.flag_down, \
                = True, True, True, True


class Blinky(pygame.sprite.Sprite):
    def __init__(self, group, x, y):
        super().__init__(group)
        self.add(ghosts)
        self.image_right = blinky_right
        self.image_left = blinky_left
        self.image_up = blinky_up
        self.image_down = blinky_down
        self.image = self.image_left
        self.rect = self.image.get_rect().move(
            tile_width * x - 50, tile_height * y)
        self.flag_left, self.flag_right, self.flag_up, self.flag_down, \
            = True, True, True, True
        self.direction = None
        self.time = 0
        # self.update(self.direction)

    def update(self, direction):
        pass


class Pinky(pygame.sprite.Sprite):
    def __init__(self, group, x, y):
        super().__init__(group)
        self.add(ghosts)
        self.image_right = pinky_right
        self.image_left = pinky_left
        self.image_up = pinky_up
        self.image_down = pinky_down
        self.image = self.image_down
        self.rect = self.image.get_rect().move(
            tile_width * x - 50, tile_height * y)
        self.flag_left, self.flag_right, self.flag_up, self.flag_down, \
            = True, True, True, True
        self.direction = None
        self.time = 0
        # self.update(self.direction)

    def update(self, direction):
        pass


class Inky(pygame.sprite.Sprite):
    def __init__(self, group, x, y):
        super().__init__(group)
        self.add(ghosts)
        self.image_right = inky_right
        self.image_left = inky_left
        self.image_up = inky_up
        self.image_down = inky_down
        self.image = self.image_up
        self.rect = self.image.get_rect().move(
            tile_width * x - 50, tile_height * y)
        self.flag_left, self.flag_right, self.flag_up, self.flag_down, \
            = True, True, True, True
        self.direction = None
        self.time = 0
        # self.update(self.direction)

    def update(self, direction):
        pass


class Clyde(pygame.sprite.Sprite):
    def __init__(self, group, x, y):
        super().__init__(group)
        self.add(ghosts)
        self.image_right = clyde_right
        self.image_left = clyde_left
        self.image_up = clyde_up
        self.image_down = clyde_down
        self.image = self.image_up
        self.rect = self.image.get_rect().move(
            tile_width * x - 50, tile_height * y)
        self.flag_left, self.flag_right, self.flag_up, self.flag_down, \
            = True, True, True, True
        self.direction = None
        self.time = 0
        # self.update(self.direction)

    def update(self, direction):
        pass


def move(hero, direction):
    hero.update(direction)


def load_level(filename):
    filename = filename
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))

    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '@':
                Tile('emptyg', x, y)
                new_player = Pacman(all_sprites, x, y)
            elif level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == '!':
                Tile('save_hor', x, y)
            elif level[y][x] == "-":
                Tile('gate', x, y)
            elif level[y][x] == "B":
                Tile('empty', x, y)
                blinky = Blinky(all_sprites, x, y)
            elif level[y][x] == "P":
                Tile('emptyg', x, y)
                pinky = Pinky(all_sprites, x, y)
            elif level[y][x] == "I":
                Tile('emptyg', x, y)
                inky = Inky(all_sprites, x, y)
            elif level[y][x] == "C":
                Tile('emptyg', x, y)
                clyde = Clyde(all_sprites, x, y)
    return new_player


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    intro_text = "PACMAN"
    fon = pygame.transform.scale(pygame.image.load('fon.jpg'), (width, height))
    title = pygame.transform.scale(pygame.image.load(
        'title.png'), (int(650 * 1.2), int(650 * 1.2 / (1280 / 720))))
    settings = pygame.transform.scale(pygame.image.load(
        'settings.png'), (113, 100))
    screen.blit(fon, (0, 0))
    screen.blit(title, (35, -50))
    screen.blit(settings, (-10, 705))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN and \
                    -10 < event.pos[0] < 103 and 805 > event.pos[1] > 705:
                settings_screen()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                start()   # начинаем игру
        pygame.display.flip()
        clock.tick(100)


def set_draw(volume=0.5):
    if volume == 0.7999999999999999:
        volume = 0.8
    elif volume == 0.19999999999999998:
        volume = 0.2
    vol = int(volume * 10)
    volume2 = set_images[0]
    volume1 = set_images[1]
    plus = set_images[3]
    minus = set_images[4]
    fon = set_images[2]
    arrow = set_images[5]
    screen.blit(fon, (0, 0))
    text = "Громкость:"
    string_rendered = font.render(text, 1, pygame.Color('yellow'))
    screen.blit(string_rendered, (320, 250))
    screen.blit(minus, (120, 300))
    screen.blit(plus, (670, 300))
    screen.blit(arrow, (0, 750))
    if vol:
        for i in range(vol):
            screen.blit(volume2, (i * 50 + 170, 300))
    else:
        i = -1
    for j in range(i + 1, 11 - vol + i):
        screen.blit(volume1, (j * 50 + 170, 300))


def settings_screen():
    pygame.mixer.music.set_volume(0.5)
    start_sound.set_volume(0.5)
    set_draw(volume=0.5)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN and \
                    170 < event.pos[0] < 670 and 350 > event.pos[1] > 300:
                x = event.pos[0]
                x = x - 170
                volume = ((x // 50) + 1) / 10
                pygame.mixer.music.set_volume(((x // 50) + 1) / 10)
                start_sound.set_volume(((x // 50) + 1) / 10)
                set_draw(volume)
            elif event.type == pygame.MOUSEBUTTONDOWN and \
                    120 < event.pos[0] < 170 and 350 > event.pos[1] > 300:
                volume = get_volume(pygame.mixer.music.get_volume()) - 0.1
                if volume < 0:
                    volume = 0
                set_draw(volume)
                pygame.mixer.music.set_volume(volume)
                start_sound.set_volume(volume)
            elif event.type == pygame.MOUSEBUTTONDOWN and \
                    670 < event.pos[0] < 720 and 350 > event.pos[1] > 300:
                volume = get_volume(pygame.mixer.music.get_volume()) + 0.1
                if volume > 1:
                    volume = 1
                set_draw(volume)
                pygame.mixer.music.set_volume(volume)
                start_sound.set_volume(volume)
            elif event.type == pygame.MOUSEBUTTONDOWN and \
                    0 <= event.pos[0] <= 50 and 800 >= event.pos[1] >= 750:
                print(1)
                start_screen()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                start_screen()  # начинаем игру
        pygame.display.flip()
        clock.tick(100)


def get_volume(volume):
    volume += 0.0146875
    if 0 <= volume <= 1:
        return int(volume * 10) / 10
    elif volume > 1:
        return 1
    else:
        return 0


size = width, height = 850, 800
set_images = [
    pygame.transform.scale(pygame.image.load('volume2.png'), (50, 50)),
    pygame.transform.scale(pygame.image.load('volume1.png'), (50, 50)),
    pygame.transform.scale(pygame.image.load('fon.jpg'), (width, height)),
    pygame.transform.scale(pygame.image.load('plus.png'), (50, 50)),
    pygame.transform.scale(pygame.image.load('minus.png'), (50, 50)),
    pygame.transform.scale(pygame.image.load('arrow.png'), (50, 50))
]

pygame.init()
pygame.font.init()
font = pygame.font.Font(None, 50)

screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()
pygame.display.set_caption("Pacman")


tile_width = tile_height = 50

tile_images = {
    'wall': pygame.image.load('wall.bmp'),
    'empty': pygame.image.load('point.bmp'),
    'save_hor': pygame.image.load('point.bmp'),
    'gate': pygame.image.load('gate.bmp'),
    'emptyg': pygame.image.load('black.bmp')
}
player_image = pygame.image.load('pacman.png')
player_image_open = pygame.image.load('pacman_open.png')
blinky_right = pygame.image.load('blinky_right.png')
blinky_up = pygame.image.load('blinky_up.png')
blinky_down = pygame.image.load('blinky_down.png')
blinky_left = pygame.image.load('blinky_left.png')
pinky_right = pygame.image.load('pinky_right.png')
pinky_up = pygame.image.load('pinky_up.png')
pinky_down = pygame.image.load('pinky_down.png')
pinky_left = pygame.image.load('pinky_left.png')
inky_right = pygame.image.load('inky_right.png')
inky_up = pygame.image.load('inky_up.png')
inky_down = pygame.image.load('inky_down.png')
inky_left = pygame.image.load('inky_left.png')
clyde_right = pygame.image.load('clyde_right.png')
clyde_up = pygame.image.load('clyde_up.png')
clyde_down = pygame.image.load('clyde_down.png')
clyde_left = pygame.image.load('clyde_left.png')
pygame.mixer.music.load('pac.mp3')
pygame.mixer.music.set_volume(0.5)
start_sound = pygame.mixer.Sound('start.mp3')
start_sound.set_volume(0.5)

level_map = load_level('map1.txt')
hero = generate_level(level_map)


def start():
    global BEGIN, SIGNAL
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    move(hero, "up")
                elif event.key == pygame.K_DOWN:
                    move(hero, "down")
                elif event.key == pygame.K_LEFT:
                    move(hero, "left")
                elif event.key == pygame.K_RIGHT:
                    move(hero, "right")
        screen.fill('black')
        all_sprites.draw(screen)
        all_sprites.update(None)
        text = font.render("SCORE: " + SCORE, 1, 'yellow')
        screen.blit(text, (0, 750))
        player.draw(screen)
        player.update(None)
        ghosts.draw(screen)
        ghosts.update(None)
        pygame.display.flip()
        clock.tick(100)
        if BEGIN:
            start_sound.play()
            time.sleep(4)
            BEGIN = False


start_screen()

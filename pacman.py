import pygame
import time

walls = pygame.sprite.Group()
player = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()
saves_hor = pygame.sprite.Group()

SCORE = '-10'


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(all_sprites)
        self.image = pygame.transform.scale(tile_images[tile_type], (50, 50))
        self.images = self.image
        self.type = tile_type
        if tile_type == "wall":
            self.add(walls)
        if tile_type == "save_hor":
            self.add(saves_hor)
        self.rect = self.image.get_rect().move(
            tile_width * pos_x - 50, tile_height * pos_y)

    def update(self, a):
        global SCORE
        if self.type == 'empty' and pygame.sprite.spritecollideany(self, player)\
                and self.image == self.images:
            self.image = pygame.transform.scale(
                pygame.image.load('black.bmp'), (50, 50))
            SCORE = int(SCORE)
            SCORE += 10
            SCORE = str(SCORE)


class Pacman(pygame.sprite.Sprite):
    def __init__(self, group, x, y):
        super().__init__(group)
        self.add(player)
        self.image_right = pygame.transform.scale(player_image, (50, 50))
        self.image_left = pygame.transform.flip(self.image_right, True, False)
        self.image_up = pygame.transform.rotate(self.image_right, 90)
        self.image_down = pygame.transform.rotate(self.image_right, 270)
        self.image = self.image_right
        self.rect = self.image.get_rect().move(
            tile_width * x - 50, tile_height * y)
        self.flag_left, self.flag_right, self.flag_up, self.flag_down, \
            = True, True, True, True
        self.direction = None
        self.direction2 = None
        self.update(self.direction)

    def update(self, direction):
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
                print(self.rect.x, self.rect.y)
                print((self.rect.x // 50), self.rect.y // 50)
                self.direction = self.direction2
                self.direction2 = None
        x, y = self.rect.x, self.rect.y
        if self.direction == "up":
            self.up(self.flag_up)
        if self.direction == "down":
            self.down(self.flag_down)
        if self.direction == "left":
            self.left(self.flag_left)
        if self.direction == "right":
            self.right(self.flag_right)
        if pygame.sprite.spritecollideany(self, walls):
            if self.rect.x - x > 0:
                self.flag_right = False
            if self.rect.x - x < 0:
                self.flag_left = False
            if self.rect.y - y > 0:
                self.flag_up = False
            if self.rect.y - y > 0:
                self.flag_down = False
            self.rect.x, self.rect.y = x, y
        if pygame.sprite.spritecollideany(self, saves_hor):
            if self.rect.x - x > 0:
                self.rect.x -= 16 * 50
            else:
                self.rect.x += 16 * 50

    def check_level(self, x, y):
        return (level_map[y][x + 1] == ".", level_map[y - 1][x] == ".", level_map[y][x - 1] == ".", level_map[y + 1][x] == ".")

    def right(self, flag):
        if flag:
            self.rect.x += 1
            self.flag_left, self.flag_right, self.flag_up, self.flag_down, \
                = True, True, True, True
            self.image = self.image_right

    def left(self, flag):
        if flag:
            self.rect.x -= 1
            self.flag_left, self.flag_right, self.flag_up, self.flag_down, \
                = True, True, True, True
            self.image = self.image_left

    def up(self, flag):
        if flag:
            self.rect.y -= 1
            self.flag_left, self.flag_right, self.flag_up, self.flag_down, \
                = True, True, True, True
            self.image = self.image_up

    def down(self, flag):
        if flag:
            self.rect.y += 1
            self.flag_left, self.flag_right, self.flag_up, self.flag_down, \
                = True, True, True, True
            self.image = self.image_down


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
                Tile('empty', x, y)
                new_player = Pacman(all_sprites, x, y)
            elif level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == '!':
                Tile('save_hor', x, y)

    return new_player


tile_width = tile_height = 50

tile_images = {
    'wall': pygame.image.load('wall.bmp'),
    'empty': pygame.image.load('point.bmp'),
    'save_hor': pygame.image.load('point.bmp')
}
player_image = pygame.image.load('pacman.png')

pygame.init()
pygame.font.init()
size = width, height = 850, 800
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()
pygame.display.set_caption("Pacman")

level_map = load_level('map1.txt')
hero = generate_level(level_map)

font = pygame.font.Font(None, 50)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
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
    pygame.display.flip()
    clock.tick(100)

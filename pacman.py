import pygame
import sys
from time import sleep, time
from functools import wraps

BEGIN = True
END=False
AB=[False]

walls = pygame.sprite.Group()
player = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()
saves_hor = pygame.sprite.Group()
ghosts = pygame.sprite.Group()
only_walls=pygame.sprite.Group()
food=pygame.sprite.Group()
GHOSTS_AT_HOME=[False,False,False,False,False]
SCORE = '0'


def mult_threading(func):
    #Декоратор для запуска функции в отдельном потоке
    @wraps(func)
    def wrapper(*args_, **kwargs_):
        import threading
        func_thread = threading.Thread(target=func,
                                       args=tuple(args_),
                                       kwargs=kwargs_)
        func_thread.start()
        return func_thread
    return wrapper


@mult_threading
def some_func(a):
    global AB
    AB=[False]
    while True:
        if not AB[-1]:
            if a=='food':
                sleep(7)
                some_func([7, 20, 7, 20, 5, 20, 5, 'end'])
                from_food()
                break
            if a=='wait':
                sleep(5)
                return True
            b = a.pop(0)
            if b != "end":
                if b != 20:
                    change_mode("Scatter")
                else:
                    change_mode("Chase")
                sleep(b)  # Тут мы чего-то доолго ждем / вычисляем / etc
            else:
                change_mode("Chase")
                break
        else:
            break
        


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(all_sprites)
        self.image = pygame.transform.scale(tile_images[tile_type], (50, 50))
        self.images = self.image
        self.type = tile_type
        if tile_type == "wall" or tile_type == "gate":
            self.add(walls)
        if tile_type=="wall":
            self.add(only_walls)
        if tile_type == "save_hor":
            self.add(saves_hor)
        self.rect = self.image.get_rect().move(
            tile_width * pos_x - 50, tile_height * pos_y)
        self.flag = False

    def update(self, a):
        global SCORE
        if self.type == 'empty' and pygame.sprite.spritecollideany(self, player)\
                and self.image == self.images:
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
        self.frames_death=[]
        self.hearts=3
        self.mode='standart'
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
        self.cur_frame=0
        self.death_flag=False
        self.time = 0
        self.update(self.direction)

    def update(self, direction):
        global AB
        if self.mode=='dead':
            self.direction=None
        self.time += 1
        if self.death_flag and self.time==30:
            go_home()
            self.image=self.frames_death[self.cur_frame]
            self.cur_frame+=1
            if self.cur_frame==10:
                self.death_flag=False
                if self.hearts==0:
                    AB.append(True)
                    restart()
                else:
                    self.rect.x=400
                    self.rect.y=550
                    self.image=self.ball
                    at_home(pacmanh=True)
            self.time = 0
        elif self.time == 30:
            self.frame = abs(self.frame - 1)
            self.image = self.frames[self.frame]
            self.time = 0
        if pygame.sprite.spritecollideany(self, ghosts) and self.mode=="standart":
            self.hearts-=1
            change_mode('Scatter')
            end_sound.play()
            self.death()
            self.mode='dead'
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
        self.change_map(x, y, self.direction)

    def change_map(self, x1, y1, direct):
        x1, y1 = x1 // 50 + 1, y1 // 50
        lvl = load_level("map1cp.txt")
        with open('map1cp.txt', "w", encoding='u8') as f:
            for y in range(len(lvl)):
                for x in range(len(lvl[y])):
                    if x == x1 and y == y1:
                        lvl[y] = lvl[y][:x] + "@" + lvl[y][x + 1:]
                    if lvl[y][x] == "@" and (x1 != x or y1 != y):
                        if level_map[y][x] != "B":
                            if level_map[y][x] != "@":
                                lvl[y] = lvl[y][:x] + \
                                    level_map[y][x] + lvl[y][x + 1:]
                            else:
                                lvl[y] = lvl[y][:x] + '.' + lvl[y][x + 1:]
                        else:
                            lvl[y] = lvl[y][:x] + '$' + lvl[y][x + 1:]
                    if level_map[y][x]=="B":
                        lvl[y]= lvl[y][:x] + '$' + lvl[y][x + 1:]
            for y in range(len(lvl)):
                for x in range(len(lvl[y])):
                    f.write(lvl[y][x])
                f.write("\n")

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
    def death(self):
        sheet=pygame.transform.scale(pygame.image.load('pacman_dying.png'),(550,50))
        columns=11
        rows=1
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames_death.append(pygame.transform.scale(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)),(50,50)))
        self.cur_frame=0
        self.death_flag=True


class Blinky(pygame.sprite.Sprite):
    def __init__(self, group, x, y):
        super().__init__(group)
        self.add(ghosts)
        self.mode = None
        self.speed=1
        self.aim = [14, 0]
        self.image_right = blinky_right
        self.image_left = blinky_left
        self.image_up = blinky_up
        self.image_down = blinky_down
        self.image = self.image_right
        self.rect = self.image.get_rect().move(
            tile_width * x - 50, tile_height * y)
        self.flag_left, self.flag_right, self.flag_up, self.flag_down, \
            = True, True, True, True
        self.direction = 'right'
        self.direction2 = None
        self.home=False
        self.time = 0

    def update(self, direction):
        doll_checks = self.check_dollar(
            (self.rect.x+50) // 50, self.rect.y // 50)
        if self.home:
            self.aim=[8,5]
        if self.aim==[5,5]:
            self.aim=self.find_pac()
        if self.aim==[8,5] and(self.rect.x%2==1 or self.rect.y%2==1):
            if self.rect.x%2==1:
                self.rect.x-=1
            if self.rect.y%2==1:
                self.rect.y-=1
        if self.aim==[8,5] and self.rect.x==400 and self.rect.y==250 and self.home:
            self.speed=1
            self.home=False
            self.direction = None
            self.direction2 = None
            self.aim=[14,0]
            at_home(blinkyh=True)
        if self.mode == "Scatter" and not self.home:
            self.aim = [14, 0]
        if self.direction == 'right':
            if doll_checks[0]:
                if self.mode=="Chase":
                    self.aim=self.find_pac()
                a = self.check_level((self.rect.x + 100)
                                     // 50, self.rect.y // 50)
                b = list(a)
                b[2] = False
                coords_bool = {"right": b[0],
                               "up": b[1], "left": b[2], "down": b[3]}
                self.direction2 = self.get_coords((self.rect.x + 100)
                                                  // 50, self.rect.y // 50, coords_bool)
        elif self.direction == 'left':
            if doll_checks[2]:
                
                if self.mode=="Chase":
                    self.aim=self.find_pac()
                a = self.check_level((self.rect.x)
                                     // 50, self.rect.y // 50)
                b = list(a)
                b[0] = False
                coords_bool = {"right": b[0],
                               "up": b[1], "left": b[2], "down": b[3]}
                self.direction2 = self.get_coords((self.rect.x)
                                                  // 50, self.rect.y // 50, coords_bool)
        elif self.direction == 'up':
            if doll_checks[1]:
                if self.mode=="Chase":
                    self.aim=self.find_pac()
                a = self.check_level((self.rect.x + 50)
                                     // 50, (self.rect.y-50) // 50)
                b = list(a)
                b[3] = False
                coords_bool = {"right": b[0],
                               "up": b[1], "left": b[2], "down": b[3]}
                self.direction2 = self.get_coords((self.rect.x + 50)
                                     // 50, (self.rect.y-50) // 50, coords_bool)
        elif self.direction == 'down':
            if doll_checks[3]:
                if self.mode=="Chase":
                    self.aim=self.find_pac()
                a = self.check_level((self.rect.x + 50)
                                     // 50, (self.rect.y+50) // 50)
                b = list(a)
                b[1] = False
                coords_bool = {"right": b[0],
                               "up": b[1], "left": b[2], "down": b[3]}
                self.direction2 = self.get_coords((self.rect.x + 50)
                                     // 50, (self.rect.y+50) // 50, coords_bool)
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
            elif self.direction2 == "up" and checks[1]:
                self.direction = self.direction2
                self.direction2 = None
            elif self.direction2 == "left" and checks[2]:
                self.direction = self.direction2
                self.direction2 = None
            elif self.direction2 == "down" and checks[3]:
                self.direction = self.direction2
                self.direction2 = None
        x, y = self.rect.x, self.rect.y
        if self.direction == "up":
            self.up(self.flag_up)
            self.image = self.image_up
        elif self.direction == "down":
            self.down(self.flag_down)
            self.image = self.image_down
        elif self.direction == "left":
            self.left(self.flag_left)
            self.image = self.image_left
        elif self.direction == "right":
            self.right(self.flag_right)
            self.image = self.image_right
        if pygame.sprite.spritecollideany(self, walls):
            if self.rect.x - x > 0:
                self.flag_right = False
            if self.rect.x - x < 0:
                self.flag_left = False
            if self.rect.y - y < 0:
                self.flag_up = False
            if self.rect.y - y > 0:
                self.flag_down = False
            self.rect.x, self.rect.y = x, y
        if pygame.sprite.spritecollideany(self, saves_hor):
            if self.rect.x - x > 0:
                self.rect.x -= 16 * 50
            else:
                self.rect.x += 16 * 50
    def find_pac(self):
        a=None
        lvl = load_level("map1cp.txt")
        with open('map1cp.txt', "r", encoding='u8') as f:
            for y in range(len(lvl)):
                for x in range(len(lvl[y])):
                    if lvl[y][x]=="@":
                        return [x,y]
        return [5,5]
    def check_level(self, x, y):
        return (level_map[y][x + 1] != "#" and level_map[y][x + 1] != "-", level_map[y - 1][x] != "#" and level_map[y - 1][x] != "-",
                level_map[y][x - 1] != "#" and level_map[y][x - 1] != "-", level_map[y + 1][x] != "#" and level_map[y + 1][x] != "-")

    def get_coords(self, x, y, coords_bool):
        coords = []
        a = {1: 'right', 2: "up", 3: "left", 4: "down"}
        for i in coords_bool:
            if coords_bool[i]:
                if i == "right":
                    coords.append((x + 1, y))
                if i == "left":
                    coords.append((x - 1, y))
                if i == "up":
                    coords.append((x, y - 1))
                if i == "down":
                    coords.append((x, y + 1))
            else:
                coords.append((-1000000, -10000000))
        leng = []
        for i in coords:
            x1, y1 = i
            x2, y2 = self.aim
            delx = abs(x2 - x1)
            dely = abs(y1 - y2)
            leng.append((delx**2 + dely**2)**0.5)
        minleng = min(leng)
        c = 0
        for i in leng:
            c += 1
            if i == minleng:
                return a[c]

    def change_mode(self, mode):
        self.mode = mode

    def right(self, flag):
        if flag:
            self.rect.x += self.speed
            self.flag_left, self.flag_right, self.flag_up, self.flag_down, \
                = True, True, True, True

    def left(self, flag):
        if flag:
            self.rect.x -= self.speed
            self.flag_left, self.flag_right, self.flag_up, self.flag_down, \
                = True, True, True, True

    def up(self, flag):
        if flag:
            self.rect.y -= self.speed
            self.flag_left, self.flag_right, self.flag_up, self.flag_down, \
                = True, True, True, True

    def down(self, flag):
        if flag:
            self.rect.y += self.speed
            self.flag_left, self.flag_right, self.flag_up, self.flag_down, \
                = True, True, True, True

    def check_dollar(self, x, y):
        level_map=load_level("map1points.txt")
        return (level_map[y][x + 1] == "$", level_map[y - 1][x] == "$",
                level_map[y][x - 1] == "$", level_map[y + 1][x] == "$")
    def go_home(self):
        self.aim=[8,5]
        self.speed=2
        self.home=True
        

class Pinky(pygame.sprite.Sprite):
    def __init__(self, group, x, y):
        super().__init__(group)
        self.add(ghosts)
        self.speed=1
        self.mode = None
        self.aim = [2, 0]
        self.image_right = pinky_right
        self.image_left = pinky_left
        self.image_up = pinky_up
        self.image_down = pinky_down
        self.image = self.image_up
        self.rect = self.image.get_rect().move(
            tile_width * x - 50, tile_height * y)
        self.flag_left, self.flag_right, self.flag_up, self.flag_down, \
            = True, True, True, True
        self.direction = 'up'
        self.direction2 = None
        self.c=0
        self.time = 0
        self.home=False

    def update(self, direction):
        global SCORE
        doll_checks = self.check_dollar(
            (self.rect.x + 50) // 50, self.rect.y // 50)
        if self.home:
            self.aim=[8,7]
        if self.aim==[5,5]:
            self.aim=self.find_pac()
        if self.aim==[8,7] and(self.rect.x%2==1 or self.rect.y%2==1):
            if self.rect.x%2==1:
                self.rect.x-=1
            if self.rect.y%2==1:
                self.rect.y-=1
        if self.aim==[8,7] and self.rect.x==400 and self.rect.y==350 and self.home:
            self.speed=1
            self.home=False
            self.direction = None
            self.direction2 = None
            at_home(pinkyh=True)
        if self.mode == "Scatter" and not self.home:
            self.aim = [2, 0]
        if not self.flag_up and not self.c:
            self.c=1
            self.direction='right'
        if self.direction == 'right':
            if doll_checks[0]:
                if self.mode=="Chase":
                    self.aim=self.find_pac()
                a = self.check_level((self.rect.x + 100)
                                     // 50, self.rect.y // 50)
                b = list(a)
                b[2] = False
                coords_bool = {"right": b[0],
                               "up": b[1], "left": b[2], "down": b[3]}
                self.direction2 = self.get_coords((self.rect.x + 100)
                                                  // 50, self.rect.y // 50, coords_bool)
        elif self.direction == 'left':
            if doll_checks[2]:
                if self.mode=="Chase":
                    self.aim=self.find_pac()
                a = self.check_level((self.rect.x)
                                     // 50, self.rect.y // 50)
                b = list(a)
                b[0] = False
                coords_bool = {"right": b[0],
                               "up": b[1], "left": b[2], "down": b[3]}
                self.direction2 = self.get_coords((self.rect.x)
                                                  // 50, self.rect.y // 50, coords_bool)
        elif self.direction == 'up':
            if doll_checks[1]:
                if self.mode=="Chase":
                    self.aim=self.find_pac()
                a = self.check_level((self.rect.x + 50)
                                     // 50, (self.rect.y-50) // 50)
                b = list(a)
                b[3] = False
                coords_bool = {"right": b[0],
                               "up": b[1], "left": b[2], "down": b[3]}
                self.direction2 = self.get_coords((self.rect.x + 50)
                                     // 50, (self.rect.y-50) // 50, coords_bool)
        elif self.direction == 'down':
            if doll_checks[3]:
                if self.mode=="Chase":
                    self.aim=self.find_pac()
                a = self.check_level((self.rect.x + 50)
                                     // 50, (self.rect.y+50) // 50)
                b = list(a)
                b[1] = False
                coords_bool = {"right": b[0],
                               "up": b[1], "left": b[2], "down": b[3]}
                self.direction2 = self.get_coords((self.rect.x + 50)
                                     // 50, (self.rect.y+50) // 50, coords_bool)
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
            elif self.direction2 == "up" and checks[1]:
                self.direction = self.direction2
                self.direction2 = None
            elif self.direction2 == "left" and checks[2]:
                self.direction = self.direction2
                self.direction2 = None
            elif self.direction2 == "down" and checks[3]:
                self.direction = self.direction2
                self.direction2 = None
        x, y = self.rect.x, self.rect.y
        if self.direction == "up":
            self.up(self.flag_up)
            self.image = self.image_up
        elif self.direction == "down":
            self.down(self.flag_down)
            self.image = self.image_down
        elif self.direction == "left":
            self.left(self.flag_left)
            self.image = self.image_left
        elif self.direction == "right":
            self.right(self.flag_right)
            self.image = self.image_right
        if pygame.sprite.spritecollideany(self, only_walls):
            if self.rect.x - x > 0:
                self.flag_right = False
            if self.rect.x - x < 0:
                self.flag_left = False
            if self.rect.y - y < 0:
                self.flag_up = False
            if self.rect.y - y > 0:
                self.flag_down = False
            self.rect.x, self.rect.y = x, y
        if pygame.sprite.spritecollideany(self, saves_hor):
            if self.rect.x - x > 0:
                self.rect.x -= 16 * 50
            else:
                self.rect.x += 16 * 50
    def find_pac(self):
        a=None
        lvl = load_level("map1cp.txt")
        with open('map1cp.txt', "r", encoding='u8') as f:
            for y in range(len(lvl)):
                for x in range(len(lvl[y])):
                    if lvl[y][x]=="@":
                        if hero.direction=="up":
                            x-=2
                            y-=2
                        elif hero.direction=="down":
                            y+=2
                        elif hero.direction=="right":
                            x+=2
                        elif hero.direction=="left":
                            x-=2
                        else:
                            x,y=x,y
                        return[x,y]
        return [5,5]
    def check_level(self, x, y):
        return (level_map[y][x + 1] != "#", level_map[y - 1][x] != "#",
                level_map[y][x - 1] != "#", level_map[y + 1][x] != "#")

    def get_coords(self, x, y, coords_bool):
        coords = []
        a = {1: 'right', 2: "up", 3: "left", 4: "down"}
        for i in coords_bool:
            if coords_bool[i]:
                if i == "right":
                    coords.append((x + 1, y))
                if i == "left":
                    coords.append((x - 1, y))
                if i == "up":
                    coords.append((x, y - 1))
                if i == "down":
                    coords.append((x, y + 1))
            else:
                coords.append((-1000000, -10000000))
        leng = []
        for i in coords:
            x1, y1 = i
            x2, y2 = self.aim
            delx = abs(x2 - x1)
            dely = abs(y1 - y2)
            leng.append((delx**2 + dely**2)**0.5)
        minleng = min(leng)
        c = 0
        for i in leng:
            c += 1
            if i == minleng:
                return a[c]

    def change_mode(self, mode):
        self.mode = mode

    def right(self, flag):
        if flag:
            self.rect.x += self.speed
            self.flag_left, self.flag_right, self.flag_up, self.flag_down, \
                = True, True, True, True

    def left(self, flag):
        if flag:
            self.rect.x -= self.speed
            self.flag_left, self.flag_right, self.flag_up, self.flag_down, \
                = True, True, True, True

    def up(self, flag):
        if flag:
            self.rect.y -= self.speed
            self.flag_left, self.flag_right, self.flag_up, self.flag_down, \
                = True, True, True, True

    def down(self, flag):
        if flag:
            self.rect.y += self.speed
            self.flag_left, self.flag_right, self.flag_up, self.flag_down, \
                = True, True, True, True

    def check_dollar(self, x, y):
        level_map = load_level("map1points.txt")
        return (level_map[y][x + 1] == "$", level_map[y - 1][x] == "$",
                level_map[y][x - 1] == "$", level_map[y + 1][x] == "$")
    def go_home(self):
        self.aim=[8,7]
        self.speed=2
        self.home=True
        

class Inky(pygame.sprite.Sprite):
    def __init__(self, group, x, y):
        super().__init__(group)
        self.add(ghosts)
        self.mode = None
        self.speed=1
        self.aim = [0, 14]
        self.image_right = inky_right
        self.image_left = inky_left
        self.image_up = inky_up
        self.image_down = inky_down
        self.image = self.image_right
        self.rect = self.image.get_rect().move(
            tile_width * x - 50, tile_height * y)
        self.flag_left, self.flag_right, self.flag_up, self.flag_down, \
            = True, True, True, True
        self.direction = 'right'
        self.direction2 = 'up'
        self.home=False
        self.time = 0
        self.c=0

    def update(self, direction):
        global SCORE
        doll_checks = self.check_dollar(
            (self.rect.x + 50) // 50, self.rect.y // 50)
        if self.home:
            self.aim=[7,7]
        if self.aim==[5,5]:
            self.aim=self.find_pac()
        if self.aim==[7,7] and(self.rect.x%2==1 or self.rect.y%2==1):
            if self.rect.x%2==1:
                self.rect.x-=1
            if self.rect.y%2==1:
                self.rect.y-=1
        if self.aim==[7,7] and self.rect.x==350 and self.rect.y==350 and self.home:
            self.speed=1
            self.home=False
            self.direction = None
            self.direction2 = None
            at_home(inkyh=True)
        if self.mode == "Scatter" and not self.home:
            self.aim = [0, 14]
        if not self.flag_up and not self.c:
            self.c=1
            self.direction='right'
        if self.direction == 'right':
            if doll_checks[0]:
                if self.mode=="Chase" and not self.home:
                    self.aim=self.find_pac()
                a = self.check_level((self.rect.x + 100)
                                     // 50, self.rect.y // 50)
                b = list(a)
                b[2] = False
                coords_bool = {"right": b[0],
                               "up": b[1], "left": b[2], "down": b[3]}
                self.direction2 = self.get_coords((self.rect.x + 100)
                                                  // 50, self.rect.y // 50, coords_bool)
        elif self.direction == 'left':
            if doll_checks[2]:
                if self.mode=="Chase" and not self.home:
                    self.aim=self.find_pac()
                a = self.check_level((self.rect.x)
                                     // 50, self.rect.y // 50)
                b = list(a)
                b[0] = False
                coords_bool = {"right": b[0],
                               "up": b[1], "left": b[2], "down": b[3]}
                self.direction2 = self.get_coords((self.rect.x)
                                                  // 50, self.rect.y // 50, coords_bool)
        elif self.direction == 'up':
            if doll_checks[1]:
                if self.mode=="Chase" and not self.home:
                    self.aim=self.find_pac()
                a = self.check_level((self.rect.x + 50)
                                     // 50, (self.rect.y-50) // 50)
                b = list(a)
                b[3] = False
                coords_bool = {"right": b[0],
                               "up": b[1], "left": b[2], "down": b[3]}
                self.direction2 = self.get_coords((self.rect.x + 50)
                                     // 50, (self.rect.y-50) // 50, coords_bool)
        elif self.direction == 'down':
            if doll_checks[3]:
                if self.mode=="Chase" and not self.home:
                    self.aim=self.find_pac()
                a = self.check_level((self.rect.x + 50)
                                     // 50, (self.rect.y+50) // 50)
                b = list(a)
                b[1] = False
                coords_bool = {"right": b[0],
                               "up": b[1], "left": b[2], "down": b[3]}
                self.direction2 = self.get_coords((self.rect.x + 50)
                                     // 50, (self.rect.y+50) // 50, coords_bool)
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
            elif self.direction2 == "up" and checks[1]:
                self.direction = self.direction2
                self.direction2 = None
            elif self.direction2 == "left" and checks[2]:
                self.direction = self.direction2
                self.direction2 = None
            elif self.direction2 == "down" and checks[3]:
                self.direction = self.direction2
                self.direction2 = None
        x, y = self.rect.x, self.rect.y
        if self.direction == "up":
            self.up(self.flag_up)
            self.image = self.image_up
        elif self.direction == "down":
            self.down(self.flag_down)
            self.image = self.image_down
        elif self.direction == "left":
            self.left(self.flag_left)
            self.image = self.image_left
        elif self.direction == "right":
            self.right(self.flag_right)
            self.image = self.image_right
        if pygame.sprite.spritecollideany(self, only_walls):
            if self.rect.x - x > 0:
                self.flag_right = False
            if self.rect.x - x < 0:
                self.flag_left = False
            if self.rect.y - y < 0:
                self.flag_up = False
            if self.rect.y - y > 0:
                self.flag_down = False
            self.rect.x, self.rect.y = x, y
        if pygame.sprite.spritecollideany(self, saves_hor):
            if self.rect.x - x > 0:
                self.rect.x -= 16 * 50
            else:
                self.rect.x += 16 * 50
    def find_pac(self):
        a=None
        lvl = load_level("map1cp.txt")
        with open('map1cp.txt', "r", encoding='u8') as f:
            for y in range(len(lvl)):
                for x in range(len(lvl[y])):
                    if lvl[y][x]=="@":
                        if hero.direction=="up":
                            x-=2
                            y-=2
                        elif hero.direction=="down":
                            y+=2
                        elif hero.direction=="right":
                            x+=2
                        elif hero.direction=="left":
                            x-=2
                        else:
                            x,y=x,y
                        return[x,y]
        return [5,5]
    def check_level(self, x, y):
        return (level_map[y][x + 1] != "#", level_map[y - 1][x] != "#",
                level_map[y][x - 1] != "#", level_map[y + 1][x] != "#")

    def get_coords(self, x, y, coords_bool):
        coords = []
        a = {1: 'right', 2: "up", 3: "left", 4: "down"}
        for i in coords_bool:
            if coords_bool[i]:
                if i == "right":
                    coords.append((x + 1, y))
                if i == "left":
                    coords.append((x - 1, y))
                if i == "up":
                    coords.append((x, y - 1))
                if i == "down":
                    coords.append((x, y + 1))
            else:
                coords.append((-1000000, -10000000))
        leng = []
        for i in coords:
            x1, y1 = i
            x2, y2 = self.aim
            delx = abs(x2 - x1)
            dely = abs(y1 - y2)
            leng.append((delx**2 + dely**2)**0.5)
        minleng = min(leng)
        c = 0
        for i in leng:
            c += 1
            if i == minleng:
                return a[c]

    def change_mode(self, mode):
        self.mode = mode

    def right(self, flag):
        if flag:
            self.rect.x += self.speed
            self.flag_left, self.flag_right, self.flag_up, self.flag_down, \
                = True, True, True, True

    def left(self, flag):
        if flag:
            self.rect.x -= self.speed
            self.flag_left, self.flag_right, self.flag_up, self.flag_down, \
                = True, True, True, True

    def up(self, flag):
        if flag:
            self.rect.y -= self.speed
            self.flag_left, self.flag_right, self.flag_up, self.flag_down, \
                = True, True, True, True

    def down(self, flag):
        if flag:
            self.rect.y += self.speed
            self.flag_left, self.flag_right, self.flag_up, self.flag_down, \
                = True, True, True, True

    def check_dollar(self, x, y):
        level_map = load_level("map1points.txt")
        return (level_map[y][x + 1] == "$", level_map[y - 1][x] == "$",
                level_map[y][x - 1] == "$", level_map[y + 1][x] == "$")
    def go_home(self):
        self.aim=[7,7]
        self.speed=2
        self.home=True

class Clyde(pygame.sprite.Sprite):
    def __init__(self, group, x, y):
        super().__init__(group)
        self.add(ghosts)
        self.speed=1
        self.mode = None
        self.aim = [16, 14]
        self.image_right = clyde_right
        self.image_left = clyde_left
        self.image_up = clyde_up
        self.image_down = clyde_down
        self.image = self.image_up
        self.rect = self.image.get_rect().move(
            tile_width * x - 50, tile_height * y)
        self.flag_left, self.flag_right, self.flag_up, self.flag_down, \
            = True, True, True, True
        self.direction = 'left'
        self.direction2 = None
        self.c=0
        self.time = 0
        self.home=False

    def update(self, direction):
        global SCORE
        doll_checks = self.check_dollar(
            (self.rect.x + 50) // 50, self.rect.y // 50)
        if self.home:
            self.aim=[10,7]
        if self.aim==[5,5]:
            self.aim=self.find_pac()
        if self.aim==[10,7] and(self.rect.x%2==1 or self.rect.y%2==1):
            if self.rect.x%2==1:
                self.rect.x-=1
            if self.rect.y%2==1:
                self.rect.y-=1
        if self.aim==[10,7] and self.rect.x==450 and self.rect.y==350 and self.home:
            self.speed=1
            self.home=False
            self.direction = None
            self.direction2 = None
            at_home(clydeh=True)
        if self.mode == "Scatter" and not self.home:
            self.aim = [16, 14]
        if not self.flag_up and not self.c:
            self.c=1
            self.direction='right'
        if self.direction == 'right':
            if doll_checks[0]:
                if self.mode=="Chase":
                    self.aim=self.find_pac()
                a = self.check_level((self.rect.x + 100)
                                     // 50, self.rect.y // 50)
                b = list(a)
                b[2] = False
                coords_bool = {"right": b[0],
                               "up": b[1], "left": b[2], "down": b[3]}
                self.direction2 = self.get_coords((self.rect.x + 100)
                                                  // 50, self.rect.y // 50, coords_bool)
        elif self.direction == 'left':
            if doll_checks[2]:
                if self.mode=="Chase":
                    self.aim=self.find_pac()
                a = self.check_level((self.rect.x)
                                     // 50, self.rect.y // 50)
                b = list(a)
                b[0] = False
                coords_bool = {"right": b[0],
                               "up": b[1], "left": b[2], "down": b[3]}
                self.direction2 = self.get_coords((self.rect.x)
                                                  // 50, self.rect.y // 50, coords_bool)
        elif self.direction == 'up':
            if doll_checks[1]:
                if self.mode=="Chase":
                    self.aim=self.find_pac()
                a = self.check_level((self.rect.x + 50)
                                     // 50, (self.rect.y-50) // 50)
                b = list(a)
                b[3] = False
                coords_bool = {"right": b[0],
                               "up": b[1], "left": b[2], "down": b[3]}
                self.direction2 = self.get_coords((self.rect.x + 50)
                                     // 50, (self.rect.y-50) // 50, coords_bool)
        elif self.direction == 'down':
            if doll_checks[3]:
                if self.mode=="Chase":
                    self.aim=self.find_pac()
                a = self.check_level((self.rect.x + 50)
                                     // 50, (self.rect.y+50) // 50)
                b = list(a)
                b[1] = False
                coords_bool = {"right": b[0],
                               "up": b[1], "left": b[2], "down": b[3]}
                self.direction2 = self.get_coords((self.rect.x + 50)
                                     // 50, (self.rect.y+50) // 50, coords_bool)
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
            elif self.direction2 == "up" and checks[1]:
                self.direction = self.direction2
                self.direction2 = None
            elif self.direction2 == "left" and checks[2]:
                self.direction = self.direction2
                self.direction2 = None
            elif self.direction2 == "down" and checks[3]:
                self.direction = self.direction2
                self.direction2 = None
        x, y = self.rect.x, self.rect.y
        if self.direction == "up":
            self.up(self.flag_up)
            self.image = self.image_up
        elif self.direction == "down":
            self.down(self.flag_down)
            self.image = self.image_down
        elif self.direction == "left":
            self.left(self.flag_left)
            self.image = self.image_left
        elif self.direction == "right":
            self.right(self.flag_right)
            self.image = self.image_right
        if pygame.sprite.spritecollideany(self, only_walls):
            if self.rect.x - x > 0:
                self.flag_right = False
            if self.rect.x - x < 0:
                self.flag_left = False
            if self.rect.y - y < 0:
                self.flag_up = False
            if self.rect.y - y > 0:
                self.flag_down = False
            self.rect.x, self.rect.y = x, y
        if pygame.sprite.spritecollideany(self, saves_hor):
            if self.rect.x - x > 0:
                self.rect.x -= 16 * 50
            else:
                self.rect.x += 16 * 50
    def find_pac(self):
        a=None
        lvl = load_level("map1cp.txt")
        with open('map1cp.txt', "r", encoding='u8') as f:
            for y in range(len(lvl)):
                for x in range(len(lvl[y])):
                    if lvl[y][x]=="@":
                        if hero.direction=="up":
                            x-=2
                            y-=2
                        elif hero.direction=="down":
                            y+=2
                        elif hero.direction=="right":
                            x+=2
                        elif hero.direction=="left":
                            x-=2
                        else:
                            x,y=x,y
                        return[x,y]
        return [5,5]
    def check_level(self, x, y):
        return (level_map[y][x + 1] != "#", level_map[y - 1][x] != "#",
                level_map[y][x - 1] != "#", level_map[y + 1][x] != "#")

    def get_coords(self, x, y, coords_bool):
        coords = []
        a = {1: 'right', 2: "up", 3: "left", 4: "down"}
        for i in coords_bool:
            if coords_bool[i]:
                if i == "right":
                    coords.append((x + 1, y))
                if i == "left":
                    coords.append((x - 1, y))
                if i == "up":
                    coords.append((x, y - 1))
                if i == "down":
                    coords.append((x, y + 1))
            else:
                coords.append((-1000000, -10000000))
        leng = []
        for i in coords:
            x1, y1 = i
            x2, y2 = self.aim
            delx = abs(x2 - x1)
            dely = abs(y1 - y2)
            leng.append((delx**2 + dely**2)**0.5)
        minleng = min(leng)
        c = 0
        for i in leng:
            c += 1
            if i == minleng:
                return a[c]

    def change_mode(self, mode):
        self.mode = mode

    def right(self, flag):
        if flag:
            self.rect.x += self.speed
            self.flag_left, self.flag_right, self.flag_up, self.flag_down, \
                = True, True, True, True

    def left(self, flag):
        if flag:
            self.rect.x -= self.speed
            self.flag_left, self.flag_right, self.flag_up, self.flag_down, \
                = True, True, True, True

    def up(self, flag):
        if flag:
            self.rect.y -= self.speed
            self.flag_left, self.flag_right, self.flag_up, self.flag_down, \
                = True, True, True, True

    def down(self, flag):
        if flag:
            self.rect.y += self.speed
            self.flag_left, self.flag_right, self.flag_up, self.flag_down, \
                = True, True, True, True

    def check_dollar(self, x, y):
        level_map = load_level("map1points.txt")
        return (level_map[y][x + 1] == "$", level_map[y - 1][x] == "$",
                level_map[y][x - 1] == "$", level_map[y + 1][x] == "$")
    def go_home(self):
        self.aim=[7,7]
        self.speed=2
        self.home=True
def restart():
    global SCORE,GHOSTS_AT_HOME,BEGIN,END,level_map,hero,blinky,pinky,inky,clydewalls,player,all_sprites,saves_hor,ghosts,only_walls,AB  
    SCORE='0'
    walls = pygame.sprite.Group()
    player = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group()
    saves_hor = pygame.sprite.Group()
    ghosts = pygame.sprite.Group()
    only_walls=pygame.sprite.Group()
    GHOSTS_AT_HOME=[False,False,False,False,False]
    BEGIN=True
    END=True
    level_map = load_level('map1.txt')
    hero, blinky, pinky,inky,clyde = generate_level(level_map)
    start_screen() 

def at_home(pacmanh=False,blinkyh=False,pinkyh=False,inkyh=False,clydeh=False):
    global BEGIN,GHOSTS_AT_HOME,AB
    if pacmanh:
        GHOSTS_AT_HOME[0]=True
    if blinkyh:
        GHOSTS_AT_HOME[1]=True
    if pinkyh:
        GHOSTS_AT_HOME[2]=True
    if inkyh:
        GHOSTS_AT_HOME[3]=True
    if clydeh:
        GHOSTS_AT_HOME[4]=True
    if GHOSTS_AT_HOME==[True,True,True,True,True]:
        hero.mode="standart"
        BEGIN=True
        GHOSTS_AT_HOME=[False,False,False,False,False]
        pacmanh,blinkyh,pinkyh,inkyh,clydeh=False,False,False,False,False
        blinky.direction="right"
        blinky.aim=[14,0]
        pinky.direction="up"
        pinky.c=0
        pinky.aim=[2,0]
        inky.direction='right'
        inky.aim=[2,0]
        inky.c=0
        clyde.direction='left'
        clyde.aim=[14,0]
        clyde.c=0
        AB.append(True)
        start()
def go_home():
    blinky.go_home()
    pinky.go_home()
    inky.go_home()
    clyde.go_home()

def change_mode(mode):
    blinky.change_mode(mode)
    pinky.change_mode(mode)
    inky.change_mode(mode)
    clyde.change_mode(mode)


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
            elif level[y][x]=='$':
                Tile('empty',x,y)
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
            elif level[y][x]=="F":
                Tile('food',x,y)
    return new_player, blinky, pinky,inky,clyde


def terminate():
    lvl = load_level("map1cp.txt")
    with open('map1cp.txt', "w", encoding='u8') as f:
        for y in range(len(lvl)):
            lvl[y] = level_map[y]
        for y in range(len(lvl)):
            for x in range(len(lvl[y])):
                f.write(lvl[y][x])
            f.write("\n")
    pygame.quit()
    sys.exit()


def start_screen():
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
    end_sound.set_volume(0.5)
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
                end_sound.set_volume(((x // 50) + 1) / 10)
                set_draw(volume)
            elif event.type == pygame.MOUSEBUTTONDOWN and \
                    120 < event.pos[0] < 170 and 350 > event.pos[1] > 300:
                volume = get_volume(pygame.mixer.music.get_volume()) - 0.1
                if volume < 0:
                    volume = 0
                set_draw(volume)
                pygame.mixer.music.set_volume(volume)
                start_sound.set_volume(volume)
                end_sound.set_volume(volume)
            elif event.type == pygame.MOUSEBUTTONDOWN and \
                    670 < event.pos[0] < 720 and 350 > event.pos[1] > 300:
                volume = get_volume(pygame.mixer.music.get_volume()) + 0.1
                if volume > 1:
                    volume = 1
                set_draw(volume)
                pygame.mixer.music.set_volume(volume)
                start_sound.set_volume(volume)
                end_sound.set_volume(volume)
            elif event.type == pygame.MOUSEBUTTONDOWN and \
                    0 <= event.pos[0] <= 50 and 800 >= event.pos[1] >= 750:
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

def pac_lifes():
    image=pygame.image.load('pacman.png')
    image=pygame.transform.scale(image, (50, 50))
    image=pygame.transform.flip(image, True, False)
    for i in range(hero.hearts):
        screen.blit(image, (300+(50*(i-1)), 750))

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
end_sound= pygame.mixer.Sound('end.mp3')
end_sound.set_volume(0.5)

level_map = load_level('map1.txt')
hero, blinky, pinky,inky,clyde = generate_level(level_map)


def start():
    global BEGIN,END
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
        pac_lifes()
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
            sleep(4)
            some_func([7, 20, 7, 20, 5, 20, 5, 'end'])
            BEGIN = False
        if END:
            END=False
            break


start_screen()

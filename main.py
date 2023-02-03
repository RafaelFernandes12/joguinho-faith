from dataclasses import dataclass
import pygame
from pygame.locals import *
from sys import exit
import random
from itertools import repeat
from abc import ABC, abstractmethod
pygame.font.get_init()
pygame.init()

superficie = (800, 600)

TEXT_FONT = pygame.font.Font('assets/font.otf', 32)

WHITE = (255, 255, 255)

HORIZONTAL = 1
UP = 2
DOWN = 0 

ANIMATION_FRAME_RATE = 10
FRAME_RATE = 60

cam_x = 250
cam_y = 250

objects = []
enemies = []

CLOCK = pygame.time.Clock()

is_game_over = False 

tela = pygame.display.set_mode(superficie)
pygame.display.set_caption('Joguinho f')


# funçoes
def load_tileset(filename, width, height):
    image = pygame.image.load(filename).convert_alpha()
    image_width, image_height = image.get_size()
    tileset = []
    for tile_x in range(0, image_width // width):
        line = []
        tileset.append(line)
        for tile_y in range(0, image_height // height):
            rect = (tile_x * width, tile_y * height, width, height)
            line.append(image.subsurface(rect))
    return tileset

def reiniciar_jogo():
    global x_protagonista, y_protagonista, x_monstro, y_monstro, morreu
    x_protagonista = int(superficie[0] / 2)
    y_protagonista = int(superficie[1] /2)
    x_monstro = random.randint(50,750)
    y_monstro = random.randint(50,550)
    morreu = False
   
player_input = {"left": False, "right": False, "up": False, "down": False}

def check_input(key, value):
    if key == pygame.K_LEFT or key == pygame.K_a:
        player_input["left"] = value
    elif key == pygame.K_RIGHT or key == pygame.K_d:
        player_input["right"] = value
    elif key == pygame.K_UP or key == pygame.K_w:
        player_input["up"] = value
    elif key == pygame.K_DOWN or key == pygame.K_s:
        player_input["down"] = value

def update_screen():
    CLOCK.tick(FRAME_RATE)
    pygame.display.update()

def check_collisions(obj1, obj2):
    x1, y1 = obj1.get_center()
    x2, y2 = obj2.get_center()
    w1, h1 = obj1.collider[0] / 2, obj1.collider[1] / 2
    w2, h2 = obj2.collider[0] / 2, obj2.collider[1] / 2
    if x1 + w1 > x2 - w2 and x1 - w1 < x2 + w2:
        return y1 + h1 > y2 - h2 and y1 - h1 < y2 + h2
    return False

def game_over():
    if is_game_over:
            game_over_text = TEXT_FONT.render("Game over!", True, WHITE)
            tela.blit(game_over_text, (superficie[0] / 2 - game_over_text.get_width() / 2,
                                        superficie[1] / 2 - game_over_text.get_height() / 2))

# estabelecendo os parametros dos nossos objetos
class Object():
    def __init__(self, x, y, width, height, image):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.image = image
        self.velocity = [0, 0]
        self.collider = [width, height]
        objects.append(self)



    def draw(self):
        tela.blit(pygame.transform.scale(self.image, (self.width, self.height)), (self.x, self.y))


    def update(self):
        self.x += self.velocity[0]
        self.y += self.velocity[1]
        self.draw()
    
    def get_center(self):
        return self.x + self.width / 2, self.y + self.height / 2

class Entity(Object):
    def __init__(self, x, y, width, height, tileset, speed):
        super().__init__(x, y, width, height, None)
        self.speed = speed

        self.tileset = load_tileset(tileset,32, 32)
        self.direction = 0
        self.flipX = False
        self.frame = 0
        self.frames = [0, 1, 0, 2]
        self.frame_timer = 0

    def change_direction(self):
        if self.velocity[0] < 0:
            self.direction = HORIZONTAL
            self.flipX = True
        elif self.velocity[0] > 0:
            self.direction = HORIZONTAL
            self.flipX = False
        elif self.velocity[1] > 0:
            self.direction = DOWN
        elif self.velocity[1] < 0:
            self.direction = UP

    def draw(self):
        image = pygame.transform.scale(self.tileset[self.frames[self.frame]][self.direction], (self.width, self.height))

        self.change_direction()

        image = pygame.transform.flip(image, self.flipX, False)
        tela.blit(image, (self.x, self.y))

        if self.velocity[0] == 0 and self.velocity[1] == 0:
            self.frame = 0
            return

        self.frame_timer += 1

        if self.frame_timer < ANIMATION_FRAME_RATE:
            return

        self.frame += 1
        if self.frame >= len(self.frames):
            self.frame = 0

        self.frame_timer = 0

    def update(self):
        self.x += self.velocity[0] * self.speed
        self.y += self.velocity[1] * self.speed
        self.draw()


class Player(Entity):
    def __init__(self, x, y, width, height, tileset, speed):
        super().__init__(x, y, width, height, tileset, speed)
        self.health = self.max_health = 3
        self.collider = [width, height]
    def update(self):
        super().update()

class Enemy(Entity):
    def __init__(self, x, y, width, height, tileset, speed):
        super().__init__(x, y, width, height, tileset, speed)

        self.health = 3
        self.collider = [width / 2.5, height / 1.5]
        enemies.append(self)

    def update(self):
        player_center = player.get_center()
        enemy_center = self.get_center()

        self.velocity = [player_center[0] - enemy_center[0], player_center[1] - enemy_center[1]]

        magnitude = (self.velocity[0] ** 2 + self.velocity[1] ** 2) ** 0.5
        self.velocity = [self.velocity[0] / magnitude * self.speed, self.velocity[1] / magnitude * self.speed]

        super().update()

    def change_direction(self):
        super().change_direction()

        if self.velocity[1] > self.velocity[0] > 0:
            self.direction = DOWN
        elif self.velocity[1] < self.velocity[0] < 0:
            self.direction = UP

class School(Entity):
    def __init__(self, x, y, width, height, tileset, speed):
        super().__init__(x, y, width, height, tileset, speed)

@dataclass
class Position:
    x = 0
    y = 0
scroll = Position()


#Objects
player = Player(400 - scroll.x, 400 - scroll.y, 70, 70, "assets/monstro5.png", 5)
enemy = Enemy(200, 200, 200, 200, "assets/monstro5.png", 2)
school = School(100,100, 75, 75, "assets/protagonista.png", 1)

while True :
    
    tela.fill((0,0,0))
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            exit()
        elif event.type == pygame.KEYDOWN:
            check_input(event.key, True)
        elif event.type == pygame.KEYUP:
            check_input(event.key, False)

    player.velocity[0] = player_input["right"] - player_input["left"]
    player.velocity[1] = player_input["down"] - player_input["up"]

    game_over()

    if is_game_over:
         update_screen()
         continue

    if player.health <= 0:
        if not is_game_over:
            is_game_over = True
    
    if check_collisions(player, school):
        game_over_text = TEXT_FONT.render("Congratulations, You Won!", True, WHITE)
        tela.blit(game_over_text, (superficie[0] / 2 - game_over_text.get_width() / 2,
                                        superficie[1] / 2 - game_over_text.get_height() / 2))
        update_screen()
        continue

            
    for e in enemies:
        if check_collisions(player, e):
            player.health -= 1

    for obj in objects:
            obj.update()
    
    if player.x - scroll.x != tela.get_width() / 2:
            scroll.x += player.x - (scroll.x + tela.get_width() / 2)
    if player.y - scroll.y != tela.get_height() / 2:
            scroll.y += player.y - (scroll.y + tela.get_height() / 2)


    update_screen()

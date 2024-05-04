import os
import random
import math
import pygame
from os import listdir
from os.path import isfile, join
pygame.init()

pygame.display.set_caption("Platformer")


WIDTH, HEIGHT = 1000, 800

FPS = 60
PLAYER_VEL = 5

window = pygame.display.set_mode((WIDTH, HEIGHT))

jump_sfx = pygame.mixer.Sound("assets/Sound/jump.mp3")
finish_sfx = pygame.mixer.Sound("assets/Sound/finish.mp3")
hit_sfx = pygame.mixer.Sound("assets/Sound/hit.mp3")
hit_sfx.set_volume(0.2)

def flip(sprites):
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]

def load_sprite_sheets(dir1, dir2, width, height, direction=False):
    path = join("assets", dir1, dir2)
    images = [f for f in listdir(path) if isfile(join(path, f))]

    all_sprites = {}

    for image in images:
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()

        sprites = []
        for i in range(sprite_sheet.get_width() // width):
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
            rect = pygame.Rect((i * width, 0, width, height))
            surface.blit(sprite_sheet, (0, 0), rect)
            sprites.append(pygame.transform.scale2x(surface))

        if direction:
            all_sprites[image.replace(".png", "") + "_right"] = sprites
            all_sprites[image.replace(".png", "") + "_left"] = flip(sprites)
        else:
            all_sprites[image.replace(".png", "")] = sprites

    return all_sprites

def get_block(size):
    path = join("assets", "Terrain", "Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(96,0,size,size)
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale2x(surface)

def get_brick(size):
    path = join("assets", "Terrain", "brick.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(0, 0, size, size)
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale2x(surface)

def get_end(size):
    path = join("assets", "Items", "Checkpoints", "End", "End.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(0, 0, size, size)
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale2x(surface)

class Player(pygame.sprite.Sprite):
    
    
    GRAVITY = 1
    SPRITES = load_sprite_sheets("MainCharacters", "NinjaFrog", 32, 32, True)
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0
        self.hit = False
        self.hit_count = 0
        self.die = False

    def jump(self):
        self.y_vel = -self.GRAVITY*8
        self.animation_count = 0
        self.jump_count += 1
        if self.jump_count == 1:
            self.fall_count = 0

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def make_hit(self):
        self.hit = True
        

    def move_left(self, vel):
        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0
    def move_right(self, vel):
        self.x_vel = vel 
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0

    def loop(self, fps):
        self.y_vel += min(1, self.fall_count / fps) * self.GRAVITY
        self.move(self.x_vel, self.y_vel)

        if self.hit:
            self.hit_count += 1
            hit_sfx.play()
        if self.hit_count > 15:
            self.hit = False
            self.hit_count = 0
            self.die = True
            
        self.fall_count += 1
        self.update_sprite()

    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0

    def hit_head(self):
        self.count = 0
        self.y_vel *= -1

    def update_sprite(self):
        sprite_sheet = "idle"
        if self.hit:
            sprite_sheet = "hit"
        elif self.y_vel < 0:
            if self.jump_count == 1:
                sprite_sheet = "jump"
            elif self.jump_count == 2:
                sprite_sheet = "double_jump"
        elif self.y_vel > self.GRAVITY * 2:
            sprite_sheet = "fall"
        elif self.x_vel != 0:
            sprite_sheet = "run"

        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()

    def respawn(self):
        self.rect.x = 96
        self.rect.y = HEIGHT - 96
        self.x_vel = 0
        self.y_vel = 0
        self.jump_count = 0
        self.fall_count = 0
        self.hit = False
        self.hit_count = 0
        self.animation_count = 0
        self.update()


    def update(self):
        self.rect = self.sprite.get_rect(topleft = (self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)

    def draw(self, window, offset_x):
        
        window.blit(self.sprite, (self.rect.x - offset_x , self.rect.y))


class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name

    def draw(self, window, offset_x):
        window.blit(self.image, (self.rect.x - offset_x, self.rect.y))

class Block(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = get_block(size)
        self.image.blit(block,(0,0))
        self.mask = pygame.mask.from_surface(self.image)

class Brick(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        brick = get_brick(size)
        self.image.blit(brick, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)

class End(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size, "end")
        brick = get_end(size)
        self.image.blit(brick, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)

class Mushroom(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "mushroom")
        self.mushroom = load_sprite_sheets("Enemy", "Mushroom", width, height, True)
        self.image = self.mushroom["run_right"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "run"
        self.x_vel = 2
        self.move_counter = 0
        self.direction = "left"
    def loop(self):
        sprite_sheet_name = "run_" + self.direction
        sprites = self.mushroom[sprite_sheet_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1
        self.rect = self.image.get_rect(topleft = (self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY == len(sprites):
            self.animation_count = 0

        self.rect.x += self.x_vel
        self.move_counter += 1
        if abs(self.move_counter) > 70:
            self.direction = "right" if self.direction == "left" else "left"
            self.x_vel *= -1
            self.move_counter *= -1

class Fire(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "fire")
        self.fire = load_sprite_sheets("Traps", "Fire", width, height)
        self.image = self.fire["off"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "on"

    def loop(self):
        sprites = self.fire[self.animation_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1
        self.rect = self.image.get_rect(topleft = (self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY == len(sprites):
            self.animation_count = 0

def get_background(name):
    image = pygame.image.load(join("assets", "Background", name))
    _, _, width, height = image.get_rect()
    tiles = []
    for i in range(WIDTH // width + 1):
        for j in range(HEIGHT // height + 1):
            pos = (i * width, j * height)
            tiles.append((pos))

    return tiles, image

def draw(window, background, bg_image, player, objects, offset_x):
    for tile in background:
        window.blit(bg_image, tile)

    for obj in objects:
        obj.draw(window, offset_x)

    player.draw(window, offset_x)

    pygame.display.update()

def handle_vertical_collision(player, objects, dy):
    collided_objects = []
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            if dy > 0:
                player.rect.bottom = obj.rect.top
                player.landed()
            if dy < 0:
                player.rect.top = obj.rect.bottom
                player.hit_head()

            collided_objects.append(obj)

    return collided_objects

def collide(player, objects, dx):
    player.move(dx, 0)
    player.update()
    collided_object = None
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            collided_object = obj
            break

    player.move(-dx, 0)
    player.update()
    return collided_object
def handle_move(player, objects):
    keys = pygame.key.get_pressed()

    player.x_vel = 0
    collide_left = collide(player, objects, -PLAYER_VEL * 2)
    collide_right = collide(player, objects, PLAYER_VEL * 2)
    if keys[pygame.K_a] and not collide_left:
        player.move_left(PLAYER_VEL)

    if keys[pygame.K_d] and not collide_right:
        player.move_right(PLAYER_VEL)
        
    vertical_collide = handle_vertical_collision(player, objects, player.y_vel)
    to_check = [collide_left, collide_right] + vertical_collide
   
    for obj in to_check:
        if obj and obj.name == "fire":
            player.make_hit()
        if obj and obj.name == "mushroom":
            player.make_hit()
    for obj in to_check:
        if obj and obj.name == "end":
            finish_sfx.play()
            pygame.time.wait(1000)
            player.respawn()
def main(window):
    clock = pygame.time.Clock()
    background, bg_image = get_background("Yellow.png")
    
    block_size = 96
    offset_x = 0
    player = Player(96, HEIGHT-96, 50, 50)
    mushroom = Mushroom(10*block_size + 16, HEIGHT-block_size*5 + 32, 32, 32)
    mushroom1 = Mushroom(19*block_size + 16, HEIGHT-block_size*6 + 32, 32, 32)
    end = End(28*block_size, HEIGHT - block_size*6 - 32, block_size * 2)
    
    fires = [Fire(4*block_size+32,HEIGHT - block_size - 64, 16, 32 ), Fire(5*block_size+32,HEIGHT - block_size - 64, 16, 32 ), Fire(7*block_size+32,HEIGHT - block_size - 64, 16, 32 ),
             Fire(8*block_size+32,HEIGHT - block_size - 64, 16, 32 ),Fire(22*block_size+32,HEIGHT - block_size*6 - 64, 16, 32 )]
    floor = [Block(i * block_size, HEIGHT - block_size, block_size) for i in range(1, (WIDTH * 3) // block_size)]
    wall = [Brick(0, i * block_size, block_size) for i in range(HEIGHT // block_size)]
    end_wall = [Brick(block_size * 31, i * block_size, block_size) for i in range(HEIGHT // block_size)]
    blocks = [  Block(3*block_size, HEIGHT - block_size*2 , block_size), Block(6*block_size, HEIGHT - block_size*4, block_size) , Block(9*block_size, HEIGHT - block_size*4, block_size) ,
                Block(10*block_size, HEIGHT - block_size*4, block_size), Block(11*block_size, HEIGHT - block_size*4, block_size), Block(13*block_size, HEIGHT - block_size*6, block_size),
                Block(16*block_size, HEIGHT - block_size*7, block_size), Block(18*block_size, HEIGHT - block_size*5, block_size), Block(19*block_size, HEIGHT - block_size*5, block_size), 
                Block(20*block_size, HEIGHT - block_size*5, block_size), Block(22*block_size, HEIGHT - block_size*6, block_size), Block(22*block_size, HEIGHT - block_size*9, block_size), 
                Block(24*block_size, HEIGHT - block_size*6, block_size), Block(27*block_size, HEIGHT - block_size*5, block_size), Block(28*block_size, HEIGHT - block_size*5, block_size)]
    objects = [*floor,*wall, *blocks, *fires, end, *end_wall, mushroom, mushroom1 ]

    
    scroll_area_width = 200
    run = True
    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and player.jump_count < 2:
                    player.jump()
                    jump_sfx.play()
        player.loop(FPS)
        mushroom.loop()
        mushroom1.loop()
        for fire in fires:
            fire.loop()
        handle_move(player, objects)
        draw(window, background, bg_image, player, objects, offset_x)

        if  (player.rect.right - offset_x >= WIDTH - scroll_area_width and player.x_vel > 0) or (player.rect.left - offset_x <= scroll_area_width and player.x_vel < 0):
            offset_x += player.x_vel
        if player.die:
            player.die = False
            offset_x = 0
            player.respawn()
    pygame.quit()
    quit()

if __name__ == "__main__":
    main(window)
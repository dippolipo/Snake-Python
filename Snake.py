import pygame
from pygame import Vector2

import random

def init():
    pygame.init()
    if not pygame.display.get_init():
        print("display non-initiated")
        input()
        pygame.quit()


init()

# ENGINE
running = True
clock = pygame.time.Clock()
pygame.display.set_icon(pygame.image.load(r"data/IconSmall.png"))
pygame.display.set_caption("Snake")
screen = pygame.display.set_mode((384, 216), pygame.SCALED) # SCALED called to allow fullscreen
tileset = pygame.image.load(r"data/Tiles.png").convert_alpha()
TILESIZE = 16
max_fps = 30
render_delta = 0
pygame.display.toggle_fullscreen()


def load_tiles(tileset_image, grid, background_color = pygame.Color(255, 255, 255, 0)):
    grid_size = (len(grid[0]), len(grid))
    final_canvas = pygame.Surface((grid_size[0] * TILESIZE, grid_size[1] * TILESIZE)).convert_alpha()
    final_canvas.fill(background_color)

    # loading tiles
    tileset_size = (int(tileset_image.get_width() / TILESIZE), int(tileset_image.get_height() / TILESIZE))
    single_tiles = [pygame.Surface((TILESIZE, TILESIZE)).convert_alpha()]
    single_tiles[0].fill(pygame.Color(255, 255, 255, 0))
    for i in range(tileset_size[1]):
        for j in range(tileset_size[0]):
            single_tiles.append(tileset_image.subsurface(pygame.Rect(j * TILESIZE, i * TILESIZE, TILESIZE, TILESIZE)))

    # draw tiles
    for i, row in enumerate(grid):
        for j, tile_id in enumerate(row):
            final_canvas.blit(single_tiles[tile_id], (j*TILESIZE, i*TILESIZE))
    return final_canvas


def load_map(tileset_image, file_path, background_color = pygame.Color(255, 255, 255, 0)): # file_path needs to be raw

    # file transcription
    with open(file_path) as file:
        content = file.readlines()

    # file processing
    grid =  []
    for i, line in enumerate(content[1:]):
        line = line.strip()
        if line[-1] == ",":
            line = line[:-1]
        line = [int(n) for n in line.split(",")]
        grid.append(line)

    return load_tiles(tileset_image, grid, background_color)





# GAME
# keys
up, down, left, right = pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d
# constants
APPLE = 255
# map
map_width = 18
map_height = 12
initial_snake_length = 3
game_map= [[0 for i in range(map_width)] for j in range(map_height)]
game_map_render = [row.copy() for row in game_map]
for x in range(initial_snake_length):
    game_map[5][x + 1] = x+1
game_map[5][14] = APPLE
# snake
snake_max_speed = 90/max_fps
snake_speed = 0
snake_pos = Vector2((initial_snake_length), 5)
snake_dir = Vector2(1, 0)
snake_last_dir = Vector2(1, 0)
snake_spritesheet = pygame.image.load(r"./data/Snake.png").convert_alpha()
current_score = 0
snake_head_sprite = [snake_spritesheet.subsurface(pygame.Rect(0, 0, TILESIZE, TILESIZE))]
for n in range(3):
    snake_head_sprite.append(pygame.transform.rotate(snake_head_sprite[n], 90))
snake_tail_sprite = [snake_spritesheet.subsurface(pygame.Rect(TILESIZE, 0, TILESIZE, TILESIZE))]
for n in range(3):
    snake_tail_sprite.append(pygame.transform.rotate(snake_tail_sprite[n], 90))
# init
background = load_map(tileset, r"./data/Map.txt")


def render_frame():
    screen.blit(background, [0, -4])
    for y, row in enumerate(game_map_render):
        for x, cell in enumerate(row):

            if game_map[y][x] == APPLE:
                game_map_render[y][x] = 9
            elif cell != 0 and game_map[y][x] == 0:
                game_map_render[y][x] = 0
            elif game_map[y][x] <= map_width*map_height and game_map[y][x] != 0:
                game_map_render[y][x] = 10

    snake_body = load_tiles(tileset, game_map_render)

    # draw head
    """if snake_dir == Vector2(0, -1):
        snake_body.blit(snake_head_sprite[0], snake_pos)
    elif snake_dir == Vector2(-1, 0):
        snake_body.blit(snake_head_sprite[1], snake_pos)
    elif snake_dir == Vector2(0, 1):
        snake_body.blit(snake_head_sprite[2], snake_pos)
    elif snake_dir == Vector2(1, 0):
        snake_body.blit(snake_head_sprite[3], snake_pos)"""

    screen.blit(snake_body, (48, 12))

    pygame.display.flip()

def random_cell_replace(grid, starting_value, final_value):
    positions = []
    for y, row in enumerate(grid):
        for x, cell in enumerate(row):
            if cell == starting_value:
                positions.append([x, y])
    final_xy = random.choice(positions)
    grid[final_xy[1]][final_xy[0]] = final_value
    return grid


delta = 0
while running:
    # poll for events
    for event in pygame.event.get():
        match event.type:
            case pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                if snake_speed == 0 and (event.key == up or event.key == down or event.key == right):
                    snake_speed = snake_max_speed

                if event.key == up and not snake_last_dir == Vector2(0, 1):
                    snake_dir = Vector2(0, -1)
                elif event.key == down and not snake_last_dir == Vector2(0, -1):
                    snake_dir = Vector2(0, 1)
                elif event.key == left and not snake_last_dir == Vector2(1, 0):
                    snake_dir = Vector2(-1, 0)
                elif event.key == right and not snake_last_dir == Vector2(-1, 0):
                    snake_dir = Vector2(1, 0)
            case pygame.QUIT:
                running = False

    # movement
    if delta == TILESIZE / 16:
        delta = 0
        snake_pos += snake_dir
        snake_posx = int(snake_pos.x)
        snake_posy = int(snake_pos.y)
        if snake_posx < 0 or snake_posx >= map_width or snake_posy < 0 or snake_posy >= map_height or (game_map[snake_posy][snake_posx] != 0 and game_map[snake_posy][snake_posx] < map_width * map_height):
            print("STOP") # change room
            snake_speed = 0
        else:
            if game_map[snake_posy][snake_posx] == APPLE:
                current_score += 1
                game_map = random_cell_replace(game_map, 0, APPLE)
            else:
                for y in range(len(game_map)):
                    for x in range(len(game_map[0])):
                        if game_map[y][x] != 0 and game_map[y][x] < map_width * map_height:
                            game_map[y][x] -= 1
            game_map[snake_posy][snake_posx] = current_score + initial_snake_length
        snake_last_dir = snake_dir
    elif snake_speed != 0:
        delta += 1

    render_frame()
    clock.tick(max_fps)

pygame.quit()
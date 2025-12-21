import pygame as pg
from pygame import Vector2

import random

def init():
    pg.init()
    if not pg.display.get_init():
        print("display non-initiated")
        input()
        pg.quit()


init()

# ENGINE
def load_tileset(tileset_image, tile_size):

    tileset_size = (int(tileset_image.get_width() / tile_size), int(tileset_image.get_height() / tile_size))
    single_tiles = [pg.Surface((tile_size, tile_size)).convert_alpha()]
    single_tiles[0].fill(pg.Color(255, 255, 255, 0))

    for i in range(tileset_size[1]):
        for j in range(tileset_size[0]):
            single_tiles.append(tileset_image.subsurface(pg.Rect(j * tile_size, i * tile_size, tile_size, tile_size)))

    return single_tiles


def draw_tilemap(single_tiles, grid, background_color=pg.Color(255, 255, 255, 0)):

    tile_size = single_tiles[0].get_width()
    grid_size = (len(grid[0]), len(grid))
    final_canvas = pg.Surface((grid_size[0] * tile_size, grid_size[1] * tile_size)).convert_alpha()
    final_canvas.fill(background_color)

    for i, row in enumerate(grid):
        for j, tile_id in enumerate(row):
            final_canvas.blit(single_tiles[tile_id], (j * tile_size, i * tile_size))

    return final_canvas


def load_tilemap(file_path):  # file_path needs to be raw

    # file transcription
    with open(file_path) as file:
        content = file.readlines()

    # file processing
    grid = []
    for i, line in enumerate(content[1:]):
        line = line.strip()
        if line[-1] == ",":
            line = line[:-1]
        line = [int(n) for n in line.split(",")]
        grid.append(line)

    return grid


running = True
clock = pg.time.Clock()
pg.display.set_icon(pg.image.load(r"data/IconSmall.png"))
pg.display.set_caption("Snake")
screen = pg.display.set_mode((384, 216), pg.SCALED) # SCALED called to allow fullscreen
TILESIZE = 16
tileset = load_tileset(pg.image.load(r"data/Tiles.png").convert_alpha(), TILESIZE)
max_fps = 30
pg.display.toggle_fullscreen()

# GAME
# keys
UP, DOWN, LEFT, RIGHT = pg.K_w, pg.K_s, pg.K_a, pg.K_d
# constants
APPLE = 255
MAPWIDTH = 18
MAPHEIGHT = 12
# map
initial_snake_length = 3
game_map= [[0 for i in range(MAPWIDTH)] for j in range(MAPHEIGHT)]
game_map_render = [row.copy() for row in game_map]
for x in range(initial_snake_length):
    game_map[5][x + 1] = x+1
game_map[5][14] = APPLE
# snake
snake_max_speed = 90/max_fps
snake_speed = 0
snake_pos = Vector2((initial_snake_length), 5)
snake_dir = [Vector2(1, 0), Vector2(1, 0)] # 0 = last, 1 = current, ... FIFO
snake_spritesheet = pg.image.load(r"./data/Snake.png").convert_alpha()
current_score = 0
snake_head_sprite = [snake_spritesheet.subsurface(pg.Rect(0, 0, TILESIZE, TILESIZE))]
for n in range(3):
    snake_head_sprite.append(pg.transform.rotate(snake_head_sprite[n], 90))
snake_tail_sprite = [snake_spritesheet.subsurface(pg.Rect(TILESIZE, 0, TILESIZE, TILESIZE))]
for n in range(3):
    snake_tail_sprite.append(pg.transform.rotate(snake_tail_sprite[n], 90))
# init
background = draw_tilemap(tileset, load_tilemap(r"./data/Map.txt"))


def render_frame():
    screen.blit(background, [0, -4])
    for y, row in enumerate(game_map_render):
        for x, cell in enumerate(row):

            if game_map[y][x] == APPLE:
                game_map_render[y][x] = 9
            elif cell != 0 and game_map[y][x] == 0:
                game_map_render[y][x] = 0
            elif game_map[y][x] <= MAPWIDTH*MAPHEIGHT and game_map[y][x] != 0:
                game_map_render[y][x] = 10

    snake_body = draw_tilemap(tileset, game_map_render)

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

    pg.display.flip()


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
    for event in pg.event.get():
        match event.type:
            case pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    pause = True

                if event.key == pg.K_ESCAPE:
                    pause = True

                if snake_speed == 0 and (event.key == UP or event.key == DOWN or event.key == RIGHT):
                    snake_speed = snake_max_speed

                if event.key == UP and not snake_dir[-1] == Vector2(0, 1):
                    snake_dir.append(Vector2(0, -1))
                elif event.key == DOWN and not snake_dir[-1] == Vector2(0, -1):
                    snake_dir.append(Vector2(0, 1))
                elif event.key == LEFT and not snake_dir[-1] == Vector2(1, 0):
                    snake_dir.append(Vector2(-1, 0))
                elif event.key == RIGHT and not snake_dir[-1] == Vector2(-1, 0):
                    snake_dir.append(Vector2(1, 0))
            case pg.QUIT:
                running = False

    # movement
    if delta == TILESIZE / 16:
        delta = 0
        if len(snake_dir) == 1:
            snake_dir.append(snake_dir[0])
        snake_pos += snake_dir[1]
        snake_posx = int(snake_pos.x)
        snake_posy = int(snake_pos.y)
        if snake_posx < 0 or snake_posx >= MAPWIDTH or snake_posy < 0 or snake_posy >= MAPHEIGHT or (game_map[snake_posy][snake_posx] != 0 and game_map[snake_posy][snake_posx] < MAPWIDTH * MAPHEIGHT):
            print("STOP") # change room
            snake_speed = 0
        else:
            if game_map[snake_posy][snake_posx] == APPLE:
                current_score += 1
                game_map = random_cell_replace(game_map, 0, APPLE)
            else:
                for y in range(len(game_map)):
                    for x in range(len(game_map[0])):
                        if game_map[y][x] != 0 and game_map[y][x] < MAPWIDTH * MAPHEIGHT:
                            game_map[y][x] -= 1
            game_map[snake_posy][snake_posx] = current_score + initial_snake_length
        snake_dir.pop(0)
    elif snake_speed != 0:
        delta += 1

    render_frame()
    clock.tick(max_fps)

pg.quit()

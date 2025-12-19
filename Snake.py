import pygame
import os


def init():
    pygame.init()
    if not pygame.display.get_init():
        print("display non-initiated")
        input()
        pygame.quit()


init()

# engine
running = True
clock = pygame.time.Clock()
screen = pygame.display.set_mode((384, 216), pygame.SCALED) # SCALED called to allow fullscreen
tileset = pygame.image.load(os.path.join(r"./data/Tiles.png")).convert_alpha()
TILESIZE = 16
max_fps = 30
render_delta = 0
pygame.display.toggle_fullscreen()
pygame.display.set_icon(pygame.image.load(os.path.join("./data", "icon.png")))

# keys
up, down, left, right = pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d

# game
map_width = 18
map_height = 12
game_map= [[0 for i in range(map_width)] for i in range(map_height)]
snake_speed = 60/max_fps
snake_pos = pygame.Vector2(0, 0)
snake_direction = pygame.Vector2(0, 0)
snake_spritesheet = pygame.image.load(r"./data/Snake.png")
snake_head_sprite = snake_spritesheet.subsurface(pygame.Rect(TILESIZE, TILESIZE, TILESIZE, TILESIZE))


def load_tiles(tileset_image, grid, background_color = pygame.Color(0, 0, 0, 0,)):
    grid_size = (len(grid[0]), len(grid))
    final_canvas = pygame.Surface((grid_size[0] * TILESIZE, grid_size[1] * TILESIZE))

    # loading tiles
    tileset_size = (int(tileset_image.get_width() / TILESIZE), int(tileset_image.get_height() / TILESIZE))
    single_tiles = [None] * (tileset_size[0] * tileset_size[1] + 1)  # +1 to add "blank tile"
    single_tiles[0] = (pygame.Surface((TILESIZE, TILESIZE)))
    single_tiles[0].fill(pygame.Color(0, 0, 0, 0))
    for i in range(1, tileset_size[1] + 1):
        for j in range(tileset_size[0]):
            single_tiles[i * j + 1] = tileset_image.subsurface(pygame.Rect(j * TILESIZE, (i - 1) * TILESIZE, TILESIZE, TILESIZE))

    for i, row in enumerate(grid):
        for j, tile_id in enumerate(row):
            print(tile_id, end=", ")
            final_canvas.blit(single_tiles[tile_id], (j*TILESIZE, i*TILESIZE))
        print()

    return final_canvas


def load_map(tileset_image, file_path, background_color = pygame.Color(0, 0, 0, 0,)): # file_path needs to be raw

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


background = load_map(tileset, r"./data/Map.txt")

while running:
    # poll for events
    for event in pygame.event.get():
        match event.type:
            case pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                if event.key == up:
                    snake_direction = pygame.Vector2(0, -1)
                elif event.key == down:
                    snake_direction = pygame.Vector2(0, 1)
                elif event.key == left:
                    snake_direction = pygame.Vector2(-1, 0)
                elif event.key == right:
                    snake_direction = pygame.Vector2(1, 0)

            case pygame.QUIT:
                running = False

    snake_pos += snake_direction * snake_speed

    screen.blit(background, [0, -4])
    screen.blit(snake_head_sprite, snake_pos)
    pygame.display.flip()

    clock.tick(max_fps)

pygame.quit()
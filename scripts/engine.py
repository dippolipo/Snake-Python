from operator import truediv

import pygame as pg
import random

clock = pg.time.Clock()
screen = None
running = True

class Scene:
    stack = []
    def init(self):
        pass

    def __init__(self, scene_stack_index):
        self.scene_stack_index = scene_stack_index
        self.init()

    def key_events(self, event):
        print("events not done")
        pg.quit()


    def get_events(self):
        global running

        for event in pg.event.get():
            match event.type:
                case pg.KEYDOWN:
                    self.key_events(event)
                case pg.QUIT:
                    running = False


    def tick(self):
        print("tick not done")
        pg.quit()


    def draw(self):
        print("render_frame not done")
        pg.quit()

    # stack manager
    def permit_scene_stack(self):
        if self.scene_stack_index == 0 or self.scene_stack_index == len(Scene.stack) - 1:
            return True
        else:
            return False

    def draw_stack(self, index):
        if self.permit_scene_stack():
            Scene.stack[index].draw()

    def tick_stack(self, index):
        if self.permit_scene_stack():
            Scene.stack[index].tick()

    @staticmethod
    def replace_stack(new_scene):
        Scene.stack = list(new_scene)

    @staticmethod
    def remove_stack(index):
        for i in range(index, len(Scene.stack)):
            Scene.stack[i + index].scene_stack_index -= 1
        Scene.stack.remove(index)

    @staticmethod
    def append_stack(new_scene):
        Scene.stack.append(new_scene(len(Scene.stack)))


class Game:

    def __init__(self, max_fps):
        self.max_fps = max_fps
        self.clock = pg.time.Clock()
    def loop(self):

        while running:
            Scene.stack[-1].tick()
            Scene.stack[-1].draw()
            pg.display.flip()
            self.clock.tick(self.max_fps)


def pygame_init(name, icon, screen_size): # TODO
    global screen
    pg.init()
    pg.display.set_icon(pg.image.load(icon))
    pg.display.set_caption(name)
    screen = pg.display.set_mode((384, 216), pg.SCALED)


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


def random_cell_replace(grid, starting_value, final_value):
    positions = []
    for y, row in enumerate(grid):
        for x, cell in enumerate(row):
            if cell == starting_value:
                positions.append([x, y])
    final_xy = random.choice(positions)
    grid[final_xy[1]][final_xy[0]] = final_value
    return grid
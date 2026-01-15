from operator import truediv

import pygame
import pygame as pg
import random
import copy

from pygame.display import toggle_fullscreen

clock = pg.time.Clock()
screen = None
running = True

class Scene:
    stack_update = False
    stack_append = []
    stack_insert = []
    stack_reset = None
    stack_delete = None
    stack_replace = []

    def __init__(self):
        self.visible = True
        self.active = True


    def set_visible(self, value):
        self.visible = value

    def set_active(self, value):
        self.active = value

    def key_down_events(self, key):
        pass


    def key_up_events(self, key):
        pass


    def non_key_event(self, event):
        pass


    def get_events(self):
        global running

        for event in pg.event.get():
            match event.type:
                case pg.KEYDOWN:
                    if event.key == pg.K_F11:
                        pg.display.toggle_fullscreen()
                    self.key_down_events(event.key)
                case pg.KEYUP:
                    self.key_up_events(event.key)
                case pg.QUIT:
                    running = False
                case _:
                    self.non_key_event(event)


    def tick(self):
        if self.active:
            return True
        else:
            return False


    def draw(self):
        if self.visible:
            return True
        else:
            return False



class SceneManager:
    scene_dict = dict()
    main_scene = None

    @staticmethod
    def draw(scene = None):

        if scene is None:
            scene = SceneManager.main_scene
        SceneManager.scene_dict[scene].draw()

    @staticmethod
    def tick(scene = None):
        if scene is None:
            scene = SceneManager.main_scene
        SceneManager.scene_dict[scene].tick()

    @staticmethod
    def pop(scene):
        SceneManager.scene_dict.pop(scene)
        if scene == SceneManager.main_scene:
            global running
            running = False

    @staticmethod
    def add(new_scene):
        SceneManager.scene_dict.update({new_scene: new_scene()})

    @staticmethod
    def replace(old_scene, new_scene):
        if SceneManager.main_scene == old_scene:
            SceneManager.main_scene = new_scene
        SceneManager.pop(old_scene)
        SceneManager.add(new_scene)

    @staticmethod
    def reset(new_scene):
        SceneManager.scene_dict.update({new_scene: new_scene()})
        SceneManager.main_scene = new_scene

    @staticmethod
    def get(scene):
        return SceneManager.scene_dict[scene]

    @staticmethod
    def set_main(scene):
        SceneManager.main_scene = scene


class Game:

    def __init__(self, max_fps, fullscreen):
        pg.mouse.set_visible(False)
        self.max_fps = max_fps
        self.clock = pg.time.Clock()
        if fullscreen:
            pg.display.toggle_fullscreen()
    def loop(self):

        while running:
            SceneManager.tick()
            SceneManager.draw()
            pg.display.flip()
            self.clock.tick(self.max_fps)


class FontPNG:
    def __init__(self, file_path): # no file extension
        self.dict = {}
        self.char_images = []
        self.line_spacing = 1
        self.char_size = []
        self.char_spacing = 1
        self.load(file_path)


    def load(self, file_path):
        txt_path = file_path + ".txt"
        png_path = file_path + ".png"
        image = pygame.image.load(png_path).convert_alpha()

        with open(txt_path) as file:
            content = file.readlines()

        self.char_size = [int(n) for n in content[0].split("x")]
        self.line_spacing = int(content[2])
        self.char_spacing = int(content[3])
        self.dict[" "] = pg.Surface((int(content[1]) - self.char_spacing * 2, self.char_size[1]), pg.SRCALPHA)
        self.dict[" "].fill(pg.Color(255, 255, 255, 0))
        chars_horizontal = int((image.get_width() - 1) / (self.char_size[0] + 1)) # 1 pixel space between each letter
        chars_vertical = int((image.get_height() - 1) / (self.char_size[1] + 1))  # 1 pixel space between each letter
        char_i = 0
        charset_length = len(content[4])
        for y in range(chars_vertical):
            for x in range(chars_horizontal):
                if char_i < charset_length:
                    self.dict[content[4][char_i]] =  image.subsurface(pg.Rect(1 + x * (self.char_size[0] + 1), 1 + y * (self.char_size[1] + 1), self.char_size[0], self.char_size[1]))
                    char_i += 1
                else:
                    break


    def draw(self, text = "404", background_color=pg.Color(255, 255, 255, 0)):
        text = str(text)
        text_size = [0, 1]
        line_width = 0
        for char in text:
            if char == "\n":
                text_size[1] += 1
                if text_size[0] < line_width:
                    text_size[0] = line_width
                line_width = 0
            else:
                line_width += 1

        if text_size[0] < line_width:
            text_size[0] = line_width

        textblock = pg.Surface(((self.char_size[0] + self.char_spacing) * text_size[0], (self.char_size[1] + self.line_spacing) * text_size[1]), pg.SRCALPHA)
        textblock.fill(background_color)

        x, y = 0, 0
        for char in text:
            if char == "\n":
                y += self.char_size[1] + self.line_spacing
                x = 0
            else:
                textblock.blit(self.dict[char], (x, y))
                x += self.char_size[0] + self.char_spacing

        return textblock


class ButtonArray:
    def __init__(self, image_path, buttons_names, font, v_space = 0, text_offset = None): # image must be horizontal
        image = pg.image.load(image_path).convert_alpha()
        self.names = buttons_names
        self.button_image = []
        self.font = font
        self.v_space = v_space
        self.size = (image.get_width()/3, image.get_height())
        for i in range(3):
            self.button_image.append(image.subsurface(pg.Rect(i * self.size[0], 0, self.size[0], self.size[1])))
        self.text_offset = text_offset
        self.selected = 0
        self.pressed = False
        if self.text_offset == None:
            self.text_offset = (1, self.size[1]/2-self.font.char_size[1]/2)

    def cursor_move(self, movement): # movement is 1 or -1
        self.selected += movement
        self.pressed = False

        if self.selected >= len(self.names):
            self.selected -= len(self.names)
        elif self.selected < 0:
            self.selected += len(self.names)

    def print_vertically(self):
        canvas = pg.Surface((self.size[0], self.size[1]*len(self.names) + self.v_space * (len(self.names) - 1)), pg.SRCALPHA)
        for i in range(len(self.names)):
            dest = (0, (self.size[1] + self.v_space) * i)
            if self.selected == i:
                if self.pressed:
                    canvas.blit(self.button_image[2], dest)
                else:
                    canvas.blit(self.button_image[1], dest)
            else:
                canvas.blit(self.button_image[0], dest)
            text = self.font.draw(self.names[i])
            canvas.blit(text, (dest[0] + self.size[0]/2 - text.get_width() / 2 + self.text_offset[0], dest[1] + self.text_offset[1]))
        return canvas


class Grid:
    def __init__(self, grid):
        self.grid = grid

    def get(self, dest):
        if type(dest) == pg.Vector2:
            return self.grid[int(dest.y)][int(dest.x)]
        else:
            return self.grid[dest[1]][dest[0]]

    def set_at(self, dest, value):
        if type(dest) == pg.Vector2:
            self.grid[int(dest.y)][int(dest.x)] = value
        else:
            self.grid[dest[1]][dest[0]] = value

    def add_at(self, dest, value):
        if type(dest) == pg.Vector2:
            self.grid[int(dest.y)][int(dest.x)] += value
        else:
            self.grid[dest[1]][dest[0]] += value

    def get_width(self):
        return len(self.grid[0])

    def get_height(self):
        return len(self.grid)

    def inside_boundaries(self, dest):
        if dest.x >= 0 and dest.x < self.get_width() and dest.y >= 0 and dest.y < self.get_height():
            return True
        else:
            return False

    def random_cell_replace(self, starting_value, final_value):
        positions = []
        for y, row in enumerate(self.grid):
            for x, cell in enumerate(row):
                if cell == starting_value:
                    positions.append([x, y])

        if not positions:
            return False
        final_xy = random.choice(positions)
        self.grid[final_xy[1]][final_xy[0]] = final_value
        return True

    def copy(self):
        return Grid([row[:] for row in self.grid])

    def cells(self):
        for y, row in enumerate(self.grid):
            for x, cell in enumerate(row):
                yield x, y, cell


class Tilemap:
    def __init__(self):
        self.grid = []
        self.tiles_array = []

    def load_grid(self, file_path):  # file_path needs to be raw
        # file transcription
        with open(file_path) as file:
            content = file.readlines()

        # file processing
        self.grid = []
        for i, line in enumerate(content[1:]):
            line = line.strip()
            if line[-1] == ",":
                line = line[:-1]
            line = [int(n) for n in line.split(",")]
            self.grid.append(line)

    def set_grid(self, grid):
        if isinstance(grid, Grid):
            grid = grid.grid
        self.grid = grid

    def set_tileset(self, tileset):
        self.tiles_array = tileset

    def print(self, background_color=pg.Color(255, 255, 255, 0)):
        tile_size = self.tiles_array[0].get_width()
        grid_size = (len(self.grid[0]), len(self.grid))
        final_canvas = pg.Surface((grid_size[0] * tile_size, grid_size[1] * tile_size)).convert_alpha()
        final_canvas.fill(background_color)

        for i, row in enumerate(self.grid):
            for j, tile_id in enumerate(row):
                final_canvas.blit(self.tiles_array[tile_id], (j * tile_size, i * tile_size))

        return final_canvas

def pygame_init(name, icon, screen_size): # TODO
    global screen
    pg.init()
    pg.display.set_icon(pg.image.load(icon))
    pg.display.set_caption(name)
    screen = pg.display.set_mode(screen_size, pg.SCALED)


def load_tileset(tileset_image, tile_size):

    tileset_size = (int(tileset_image.get_width() / tile_size), int(tileset_image.get_height() / tile_size))
    single_tiles = [pg.Surface((tile_size, tile_size)).convert_alpha()]
    single_tiles[0].fill(pg.Color(255, 255, 255, 0))

    for i in range(tileset_size[1]):
        for j in range(tileset_size[0]):
            single_tiles.append(tileset_image.subsurface(pg.Rect(j * tile_size, i * tile_size, tile_size, tile_size)))

    return single_tiles
from operator import truediv

import pygame
import pygame as pg
import random

from pygame.display import toggle_fullscreen

clock = pg.time.Clock()
screen = None
running = True

class Scene:
    stack = []
    stack_update = False
    stack_append = []
    stack_insert = []
    stack_reset = None
    stack_delete = None
    stack_replace = []

    def init(self):
        pass

    def __init__(self, scene_stack_index):
        self.scene_stack_index = scene_stack_index
        self.init()

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
    def stack_management():
        if Scene.stack_update:
            if Scene.stack_append:
                Scene.stack.append(Scene.stack_append[0](len(Scene.stack)))
                del Scene.stack_append[0]
            if Scene.stack_delete != None:
                for i in range(Scene.stack_delete, len(Scene.stack)):
                    Scene.stack[i].scene_stack_index -= 1
                del Scene.stack[Scene.stack_delete]
                Scene.stack_delete = None
            if Scene.stack_insert:
                Scene.stack.insert(Scene.stack_insert[0][0], Scene.stack_insert[0][1])
                del Scene.stack_insert[0]
            if Scene.stack_replace:
                Scene.stack[Scene.stack_replace[0][0]] = Scene.stack_replace[0][1](len(Scene.stack) - 1)
                del Scene.stack_replace[0]
            if Scene.stack_reset != None:
                Scene.stack = []
                Scene.stack.append(Scene.stack_reset(0))
                Scene.stack_reset = None

            if not (Scene.stack_append or Scene.stack_delete != None or Scene.stack_insert or Scene.stack_reset != None or Scene.stack_replace):
                Scene.stack_update = False

    @staticmethod
    def reset_stack(new_scene):
        Scene.stack_reset = new_scene
        Scene.stack_update = True

    @staticmethod
    def del_stack(index):
        Scene.stack_delete = (index)
        Scene.stack_update = True

    @staticmethod
    def append_stack(new_scene):
        Scene.stack_append.append(new_scene)
        Scene.stack_update = True

    @staticmethod
    def insert_stack(index, new_scene):
        Scene.stack_insert.append((index, new_scene))
        Scene.stack_update = True

    @staticmethod
    def replace_stack(index, new_scene):
        Scene.stack_replace.append((index, new_scene))
        Scene.stack_update = True

class Game:

    def __init__(self, max_fps):
        self.max_fps = max_fps
        self.clock = pg.time.Clock()
    def loop(self):

        while running:
            Scene.stack_management()
            Scene.stack[-1].tick()
            Scene.stack[-1].draw()
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
        self.dict[" "] = pg.Surface((int(content[1]) - self.char_spacing * 2, self.char_size[1]), pg.SRCALPHA).fill(pg.Color(255, 255, 255, 0))
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
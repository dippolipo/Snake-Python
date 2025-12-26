from scripts import engine, globs, entities
import pygame as pg
from pygame import Vector2

from scripts.engine import draw_tilemap


class Level(engine.Scene):


    def init(self):
        # constants
        self.MAP_WIDTH = 18
        self.MAP_HEIGHT = 12
        self.APPLE = 255
        # logic
        self.snake = entities.Snake((3, 5), 3, (1, 0))
        self.delta = 0
        self.game_map = [[0 for i in range(self.MAP_WIDTH)] for j in range(self.MAP_HEIGHT)]
        self.score = 0
        for x in range(self.snake.length):
            self.game_map[5][x + 1] = x + 1
        self.game_map[5][14] = self.APPLE
        self.delta = 0
        # rendering
        self.game_map_render = [row.copy() for row in self.game_map]
        self.background = engine.draw_tilemap(globs.tileset, engine.load_tilemap(r"./data/Map.txt"))
        self.append_stack(LevelGUI)


    def key_down_events(self, key):
        if key == pg.K_ESCAPE:
            self.append_stack(PauseLevel)

        if self.snake.speed == 0 and (key == globs.UP or key == globs.DOWN or key == globs.RIGHT):
            self.snake.speed = self.snake.max_speed

        if key == globs.UP and not self.snake.dir[-1] == Vector2(0, 1):
            self.snake.dir.append(Vector2(0, -1))
        elif key == globs.DOWN and not self.snake.dir[-1] == Vector2(0, -1):
            self.snake.dir.append(Vector2(0, 1))
        elif key == globs.LEFT and not self.snake.dir[-1] == Vector2(1, 0):
            self.snake.dir.append(Vector2(-1, 0))
        elif key == globs.RIGHT and not self.snake.dir[-1] == Vector2(-1, 0):
            self.snake.dir.append(Vector2(1, 0))


    def tick(self):

        self.get_events()

        # movement TODO: implement different speeds
        if len(self.snake.dir) == 1:
            self.snake.dir.append(self.snake.dir[0])

        if self.delta == 1:
            self.snake.pos += self.snake.dir[1]
            int_pos_x = int(self.snake.pos.x)
            int_pos_y = int(self.snake.pos.y)

            if int_pos_x < 0 or int_pos_x >= self.MAP_WIDTH or int_pos_y < 0 or int_pos_y >= self.MAP_HEIGHT or (
                    self.game_map[int_pos_y][int_pos_x] != 0 and self.game_map[int_pos_y][int_pos_x] < self.MAP_WIDTH * self.MAP_HEIGHT):
                print("STOP")  # TODO: change room
                self.snake.speed = 0
            else:
                if self.game_map[int_pos_y][int_pos_x] == self.APPLE:
                    self.score += 1
                    self.snake.length += 1
                    self.game_map = engine.random_cell_replace(self.game_map, 0, self.APPLE)
                else:
                    for y in range(len(self.game_map)):
                        for x in range(len(self.game_map[0])):
                            if self.game_map[y][x] != 0 and self.game_map[y][x] < self.MAP_WIDTH * self.MAP_HEIGHT:
                                self.game_map[y][x] -= 1
                self.game_map[int_pos_y][int_pos_x] = self.snake.length
            self.snake.dir.pop(0)
            self.delta = 0
        elif self.snake.speed != 0:
            self.delta += 1


    def draw(self):
        engine.screen.blit(self.background, [0, 0])

        for y, row in enumerate(self.game_map_render):
            for x, cell in enumerate(row):

                if self.game_map[y][x] == self.APPLE:
                    self.game_map_render[y][x] = 1
                elif cell != 0 and self.game_map[y][x] == 0:
                    self.game_map_render[y][x] = 0
                elif self.game_map[y][x] <= self.MAP_WIDTH * self.MAP_HEIGHT and self.game_map[y][x] != 0:
                    self.game_map_render[y][x] = 24

        snake_body = engine.draw_tilemap(globs.entities_tiles, self.game_map_render)

        engine.screen.blit(snake_body, (48, 16))


class LevelGUI(engine.Scene):
    def init(self):
        self.static_gui = pg.Surface((384, 216), pg.SRCALPHA)
        self.static_gui.fill(pg.Color(255, 255, 255, 0))
        self.static_gui.blit(globs.font.draw(f"TOP:\n{globs.highscore[globs.difficulty]}\n"), (0, 0))
    def tick(self):
        self.tick_stack(0)

    def draw(self):
        self.draw_stack(0)
        textblock = globs.font.draw(self.stack[0].score)
        engine.screen.blit(self.static_gui, (0, 0))
        engine.screen.blit(textblock, (192 - int(textblock.get_width() / 2), 3))


class PauseLevel(engine.Scene):
    def init(self):
        self.buttons = ["RESUME", "RESET", "QUIT"]
        self.selected = 0
        self.pressed = False
        self.stack[0].draw()
        self.background = engine.screen.copy()
        self.button_image = []
        button_tiles = engine.load_tileset(pg.image.load(r"data/Button.png").convert_alpha(), 16)
        for i in range(len(self.buttons)):
            self.button_image.append(draw_tilemap(button_tiles, [[1 + i*3, 2 + i*3, 3 + i*3]]))


    def key_down_events(self, key):
        if key == globs.PAUSE:
            self.resume()

        if key == globs.UP:
            if self.selected == 0:
                self.selected = len(self.buttons) - 1
            else:
                self.selected -= 1
            self.pressed = False
        elif key == globs.DOWN:
            if self.selected == len(self.buttons) - 1:
                self.selected = 0
            else:
                self.selected += 1
            self.pressed = False

        if key == globs.A:
            self.pressed = True

    def key_up_events(self, key):
        if key == globs.A and self.pressed:
            if self.selected == 0:
                self.resume()
            elif self.selected == 1:
                self.replace_stack(type(self.stack[0]))
            elif self.selected == 2:
                engine.running = False

    def resume(self):
        self.del_stack(self.scene_stack_index)
        self.append_stack(ResumeLevel)

    def tick(self):
        self.get_events()


    def draw(self):
        engine.screen.blit(self.background, (0, 0))

        pause_text = globs.font.draw("MENU")
        engine.screen.blit(pause_text, (192 - int(pause_text.get_width() / 2), 3))

        for i in range(len(self.buttons)):
            button_pos = (192-24, 68 + i * 32)
            if self.selected == i:
                if self.pressed:
                    engine.screen.blit(self.button_image[2], button_pos)
                else:
                    engine.screen.blit(self.button_image[1], button_pos)
            else:
                engine.screen.blit(self.button_image[0], button_pos)
            text = globs.font.draw(self.buttons[i])
            engine.screen.blit(text, (button_pos[0] + 25 - int(text.get_width() / 2), button_pos[1] + 3))


class ResumeLevel(engine.Scene):
    def init(self):
        pg.time.set_timer(pg.USEREVENT, 1000)
        self.stack[0].draw()
        self.background = engine.screen.copy()
        self.countdown = 3

    def unusual_event(self, event):
        if event.type == pg.USEREVENT:
            self.countdown -= 1

    def key_down_events(self, key):
        if key == globs.PAUSE:
            self.del_stack(self.scene_stack_index)
            self.append_stack(PauseLevel)
        elif self.countdown <= 1:
            self.stack[0].key_down_events(key)

    def tick(self):
        self.get_events()

        if (self.countdown == 0):
            pg.time.set_timer(pg.USEREVENT, 0)
            self.del_stack(self.scene_stack_index)

    def draw(self):
        engine.screen.blit(self.background, (0, 0))
        pause_text = globs.font.draw(self.countdown)
        engine.screen.blit(pause_text, (192 - int(pause_text.get_width() / 2), 3))


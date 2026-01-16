from pygame.display import toggle_fullscreen

from scripts import engine, globs, entities
from scripts.engine import SceneManager as SM
import pygame as pg
from pygame import Vector2


class Level(engine.Scene):

    def __init__(self):
        super().__init__()
        # constants
        self.MAP_WIDTH = 18
        self.MAP_HEIGHT = 12
        self.APPLE = 255
        # logic
        self.pause = False
        self.snake = entities.Snake((3, 5), 3, (1, 0))
        self.delta = 0
        self.game_map = engine.Grid([[0 for i in range(self.MAP_WIDTH)] for j in range(self.MAP_HEIGHT)])
        self.score = 0
        for x in range(self.snake.length):
            self.game_map.set_at((x + 1, 5), x + 1)

        self.game_map.set_at((14, 5), self.APPLE)
        if globs.apples >= 1:
            self.game_map.set_at((12, 7), self.APPLE)
            self.game_map.set_at((12, 3), self.APPLE)
        if globs.apples == 2:
            self.game_map.set_at((10, 9), self.APPLE)
            self.game_map.set_at((10, 1), self.APPLE)
        self.delta = 0
        self.delta_reset = (3 - globs.difficulty)
        # rendering
        self.game_map_render = self.game_map.copy()
        tilemap = engine.Tilemap()
        tilemap.set_tileset(globs.tileset)
        tilemap.load_grid(r"./data/Map.txt")
        self.background = tilemap.print()
        self.snake_body = engine.Tilemap()
        self.snake_body.set_tileset(globs.entities_tiles)
        SM.add(LevelGUI)


    def key_down_events(self, key):
        if key == pg.K_ESCAPE:
            self.pause = True
            SM.add(PauseLevel)

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
        if self.pause:
            return

        # movement
        if len(self.snake.dir) == 1:
            self.snake.dir.append(self.snake.dir[0])

        if self.delta == self.delta_reset:
            self.snake.pos += self.snake.dir[1]
            pos_x = int(self.snake.pos.x)
            pos_y = int(self.snake.pos.y)

            if pos_x < 0 or pos_x >= self.MAP_WIDTH or pos_y < 0 or pos_y >= self.MAP_HEIGHT or (
                    self.game_map.get((pos_x, pos_y)) != 0 and self.game_map.get((pos_x, pos_y)) < self.MAP_WIDTH * self.MAP_HEIGHT):
                SM.add(EndLevel)
                SM.set_main(EndLevel)
            else:
                if self.game_map.get((pos_x, pos_y)) == self.APPLE:
                    self.score += 1
                    self.snake.length += 1
                    self.game_map.random_cell_replace(0, self.APPLE)
                else:
                    for x, y, cell in self.game_map.cells():
                        if cell != 0 and cell < self.MAP_WIDTH * self.MAP_HEIGHT:
                            self.game_map.add_at((x, y), -1)
                self.game_map.set_at(self.snake.pos, self.snake.length)
            self.snake.dir.pop(0)
            self.delta = 0
        elif self.snake.speed != 0:
            self.delta += 1


    def draw(self):
        engine.screen.blit(self.background, [0, 0])

        for x, y, cell in self.game_map.cells():
            if cell == self.APPLE:
                self.game_map_render.set_at((x, y), 1)
            elif cell != 0 and cell == 0:
                self.game_map_render.set_at((x, y), 0)
            elif cell <= self.MAP_WIDTH * self.MAP_HEIGHT and cell != 0:
                self.game_map_render.set_at((x, y), 24)
            else:
                self.game_map_render.set_at((x, y), 0)

        self.snake_body.set_grid(self.game_map_render)
        engine.screen.blit(self.snake_body.print(), (48, 16))
        SM.draw(LevelGUI)


class LevelGUI(engine.Scene):
    def __init__(self):
        super().__init__()
        self.static_gui = pg.Surface((384, 216), pg.SRCALPHA)
        self.static_gui.fill(pg.Color(255, 255, 255, 0))
        self.static_gui.blit(globs.font.draw(f"TOP:\n{globs.highscore[globs.difficulty][globs.apples]}\n"), (0, 0))

    def draw(self):
        if not super().draw():
            return
        textblock = globs.font.draw(SM.get(Level).score)
        engine.screen.blit(self.static_gui, (0, 0))
        engine.screen.blit(textblock, (192 - int(textblock.get_width() / 2), 3))


class PauseLevel(engine.Scene):
    def __init__(self):
        super().__init__()
        buttons_names = ["RESUME", "RESET", "MENU"]
        self.buttons = engine.ButtonArray(r"data/Button.png", buttons_names, globs.font, 8)
        SM.get(LevelGUI).set_visible(False)
        SM.draw(Level)
        self.background = engine.screen.copy()
        self.pause_text = globs.font.draw("MENU")
        self.pause_text_des = (192 - int(self.pause_text.get_width() / 2), 3)
        SM.set_main(PauseLevel)


    def key_down_events(self, key):
        if key == globs.PAUSE:
            self.resume()

        if key == globs.UP:
            self.buttons.cursor_move(-1)
        elif key == globs.DOWN:
            self.buttons.cursor_move(+1)

        if key == globs.A:
            self.buttons.pressed = True

    def key_up_events(self, key):
        if key == globs.A and self.buttons.pressed:
            if self.buttons.selected == 0:
                self.resume()
            elif self.buttons.selected == 1:
                SM.reset(Level)
            elif self.buttons.selected == 2:
                SM.reset(MainMenu)

    def resume(self):
        SM.get(Level).pause = False
        SM.replace(PauseLevel, ResumeLevel)

    def tick(self):
        self.get_events()


    def draw(self):
        engine.screen.blit(self.background, (0, 0))

        engine.screen.blit(self.pause_text, self.pause_text_des)

        buttons_surface = self.buttons.print_vertically()
        engine.screen.blit(buttons_surface, (384/2-self.buttons.size[0]/2, 216/2 - self.buttons.size[1]/2))


class ResumeLevel(engine.Scene):
    def __init__(self):
        super().__init__()
        pg.time.set_timer(pg.USEREVENT, 1000)
        SM.get(Level).draw()
        self.background = engine.screen.copy()
        self.countdown = 3

    def non_key_event(self, event):
        if event.type == pg.USEREVENT:
            self.countdown -= 1

    def key_down_events(self, key):
        if key == globs.PAUSE:
            SM.replace(ResumeLevel, PauseLevel)
        elif self.countdown <= 1:
            SM.get(Level).key_down_events(key)

    def tick(self):
        self.get_events()

        if self.countdown == 0:
            pg.time.set_timer(pg.USEREVENT, 0)
            SM.get(LevelGUI).set_visible(True)
            SM.set_main(Level)
            SM.pop(ResumeLevel)

    def draw(self):
        engine.screen.blit(self.background, (0, 0))
        pause_text = globs.font.draw(self.countdown)
        engine.screen.blit(pause_text, (192 - int(pause_text.get_width() / 2), 3))


class MainMenu(engine.Scene):
    def __init__(self):
        super().__init__()
        # scene stack
        SM.add(Level)
        SM.add(AutoPlay)
        SM.get(LevelGUI).set_visible(False)
        # logic
        buttons_names = ["START", "SPEED", "APPLES", "QUIT"]
        self.buttons = engine.ButtonArray(r"data/Button.png", buttons_names, globs.font, 8)
        # rendering
        self.background = pg.Surface((384, 216))
        play_text = globs.font.draw("PLAY")
        snake_text = globs.font.draw("SNAKE")
        grid = [[20, 9, 9, 9, 9, 19], [11, 3, 2, 3, 2, 8], [18, 10, 10, 10, 10, 17]]
        self.menu_overlay = pg.Surface((16*6, 16*5), pg.SRCALPHA)
        self.menu_overlay.fill(pg.Color(0, 0, 0, 0))
        self.menu_overlay.blit(play_text, (16*3 - int(play_text.get_width() / 2), 3))
        menu_overlay_tilemap = engine.Tilemap()
        menu_overlay_tilemap.set_grid(grid)
        menu_overlay_tilemap.set_tileset(globs.tileset)
        self.menu_overlay.blit(menu_overlay_tilemap.print(), (0, 16*2))
        self.menu_overlay.blit(snake_text, (16*3 - int(snake_text.get_width() / 2), 51))
        self.level_apples = globs.apples
        globs.apples = 0

    def tick(self):
        self.get_events()
        SM.get(AutoPlay).tick()

    def key_down_events(self, key):
        if key == globs.UP:
            self.buttons.cursor_move(-1)
        elif key == globs.DOWN:
            self.buttons.cursor_move(+1)
        if key == globs.A:
            self.buttons.pressed = True

    def key_up_events(self, key):
        if key == globs.A and self.buttons.pressed:
            if self.buttons.selected == 0:
                globs.apples = self.level_apples
                SM.reset(Level)
            elif self.buttons.selected == 1:
                SM.add(SpeedMenu)
                SM.set_main(SpeedMenu)
            elif self.buttons.selected == 2:
                SM.add(AppleMenu)
                SM.set_main(AppleMenu)
            elif self.buttons.selected == 3:
                engine.running = False

    def draw(self):
        SM.draw(Level)
        buttons_surface = self.buttons.print_vertically()
        engine.screen.blit(buttons_surface, (384 / 2 - self.buttons.size[0] / 2, 216 / 2 - self.buttons.size[1] / 2))
        engine.screen.blit(self.menu_overlay, (16*9, 0))


class SpeedMenu(engine.Scene):
    def __init__(self):
        buttons_names = ["EASY", "MEDIUM", "HARD"]
        self.buttons = engine.ButtonArray(r"data/Button.png", buttons_names, globs.font, 8)
        self.background = pg.Surface((384, 216))
        self.background.fill(pg.Color("aquamarine"))
        super().__init__()

    def tick(self):
        self.get_events()
        SM.get(AutoPlay).tick()

    def key_down_events(self, key):
        if key == globs.UP:
            self.buttons.cursor_move(-1)
        elif key == globs.DOWN:
            self.buttons.cursor_move(+1)

        if key == globs.A:
            self.buttons.pressed = True

    def key_up_events(self, key):
        if key == globs.A and self.buttons.pressed:
            if self.buttons.selected == 0:
                globs.difficulty = 0
            elif self.buttons.selected == 1:
                globs.difficulty = 1
            elif self.buttons.selected == 2:
                globs.difficulty = 2
            SM.set_main(MainMenu)
            SM.pop(SpeedMenu)

    def draw(self):
        SM.get(Level).draw()
        buttons_surface = self.buttons.print_vertically()
        engine.screen.blit(buttons_surface, (384 / 2 - self.buttons.size[0] / 2, 216 / 2 - self.buttons.size[1] / 2))
        engine.screen.blit(SM.get(MainMenu).menu_overlay, (16*9, 0))


class AppleMenu(engine.Scene):
    def __init__(self):
        super().__init__()
        buttons_names = ["ONE", "A FEW", "MANY"]
        self.buttons = engine.ButtonArray(r"data/Button.png", buttons_names, globs.font, 8)
        self.background = pg.Surface((384, 216))
        self.background.fill(pg.Color("aquamarine"))

    def tick(self):
        self.get_events()
        SM.get(AutoPlay).tick()

    def key_down_events(self, key):
        if key == globs.UP:
            self.buttons.cursor_move(-1)
        elif key == globs.DOWN:
            self.buttons.cursor_move(+1)

        if key == globs.A:
            self.buttons.pressed = True

    def key_up_events(self, key):
        if key == globs.A and self.buttons.pressed:
            if self.buttons.selected == 0:
                SM.get(MainMenu).level_apples = 0
            elif self.buttons.selected == 1:
                SM.get(MainMenu).level_apples = 1
            elif self.buttons.selected == 2:
                SM.get(MainMenu).level_apples = 2
            SM.set_main(MainMenu)
            SM.pop(AppleMenu)

    def draw(self):
        SM.get(Level).draw()
        buttons_surface = self.buttons.print_vertically()
        engine.screen.blit(buttons_surface, (384 / 2 - self.buttons.size[0] / 2, 216 / 2 - self.buttons.size[1] / 2))
        engine.screen.blit(SM.get(MainMenu).menu_overlay, (16*9, 0))


class EndLevel(engine.Scene):
    def __init__(self):
        super().__init__()
        buttons_names = ["RETRY", "MENU", "QUIT"]
        self.buttons = engine.ButtonArray(r"data/Button.png", buttons_names, globs.font, 8)
        self.background = engine.screen.copy()

        def print_text_to_background(text):
            grid = [[20, 9, 9, 9, 9, 9, 9, 19], [11, 3, 2, 3, 2, 3, 2, 8], [18, 10, 10, 10, 10, 10, 10, 17]]
            text_background = engine.Tilemap()
            text_background.set_grid(grid)
            text_background.set_tileset(globs.tileset)
            text_to_print = globs.font.draw(text)
            self.background.blit(text_background.print(), (192 - 64, 32))
            self.background.blit(text_to_print, (192 - int(text_to_print.get_width() / 2), 51))

        if SM.get(Level).score > globs.highscore[globs.difficulty][globs.apples]:
            print_text_to_background("NEW HIGHSCORE")
            globs.highscore[globs.difficulty][globs.apples] = SM.get(Level).score
        if SM.get(Level).MAP_WIDTH * SM.get(Level).MAP_HEIGHT - SM.get(Level).snake.length == 0:
            print_text_to_background("CONGRATULATIONS")

    def key_down_events(self, key):
        if key == globs.PAUSE:
            self.resume()

        if key == globs.UP:
            self.buttons.cursor_move(-1)
        elif key == globs.DOWN:
            self.buttons.cursor_move(+1)

        if key == globs.A:
            self.buttons.pressed = True

    def key_up_events(self, key):
        if key == globs.A and self.buttons.pressed:
            if self.buttons.selected == 0:
                SM.reset(Level)
            elif self.buttons.selected == 1:
                SM.reset(MainMenu)
            elif self.buttons.selected == 2:
                engine.running = False

    def tick(self):
        self.get_events()


    def draw(self):
        engine.screen.blit(self.background, (0, 0))

        buttons_surface = self.buttons.print_vertically()
        engine.screen.blit(buttons_surface, (384/2-self.buttons.size[0]/2, 216/2 - self.buttons.size[1]/2))


class AutoPlay(engine.Scene):
    def __init__(self):
        super().__init__()
        for x in range (6):
            for y in range (3):
                SM.get(Level).game_map.set_at((x, y), SM.get(Level).MAP_WIDTH * SM.get(Level).MAP_HEIGHT + 1)
        self.score = 0
        self.commands = [] # ((position)(direction))
        self.lost = False # TODO
        SM.get(Level).key_down_events(pg.K_d)

    def find_path(self, start_pos):
        visited = [start_pos]  # starting
        visited_parent = [-1]
        visited_index = 0
        grid = SM.get(Level).game_map

        def visit_cell(vis_index, mov):
            dest = visited[vis_index] + mov
            if grid.inside_boundaries(dest):
                dest_value = grid.get(dest)
                if (dest_value == 0 or dest_value >= 250) and dest not in visited:
                    visited.append(dest)
                    visited_parent.append(vis_index)
                    if grid.get(dest) == SM.get(Level).APPLE:
                        return True
            return False

        found = False
        while not self.lost and not found:
            if not found:
                found = visit_cell(visited_index, pg.Vector2(0, 1))
            if not found:
                found = visit_cell(visited_index, pg.Vector2(0, -1))
            if not found:
                found = visit_cell(visited_index, pg.Vector2(1, 0))
            if not found:
                found = visit_cell(visited_index, pg.Vector2(-1, 0))

            if visited_index + 1 < len(visited):
                visited_index += 1
            else:
                self.lost = True

        print("----")
        i = len(visited) - 1
        last_dir = visited[i] - visited[visited_parent[i]]
        while visited_parent[i] != 0:
            i = visited_parent[i]
            new_dir = visited[i] - visited[visited_parent[i]]
            print("dir", new_dir)
            print(str(visited[i]) + "-" + str(visited[visited_parent[i]]))
            if new_dir != last_dir:
                print("dir changed")
                self.commands.append((visited[i], last_dir))
                last_dir = new_dir

        self.commands.append((start_pos, last_dir))

        print(self.commands)

    def tick(self):
        if self.lost:
            return

        SM.get(Level).tick()

        if SM.get(Level).score != self.score:
            self.score = SM.get(Level).score
            self.find_path(SM.get(Level).snake.pos)
            print("path found")

        print(self.commands)
        print("pos:", SM.get(Level).snake.pos)
        if self.commands != [] and SM.get(Level).snake.pos == self.commands[-1][0]:
            if self.commands[-1][1] == Vector2(1, 0):
                SM.get(Level).key_down_events(pg.K_d)
                print("D")
            elif self.commands[-1][1] == Vector2(-1, 0):
                SM.get(Level).key_down_events(pg.K_a)
                print("A")
            elif self.commands[-1][1] == Vector2(0, 1):
                SM.get(Level).key_down_events(pg.K_s)
                print("S")
            elif self.commands[-1][1] == Vector2(0, -1):
                SM.get(Level).key_down_events(pg.K_w)
                print("W")
            self.commands.pop()

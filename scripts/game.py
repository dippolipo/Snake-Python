import pygame as pg
import engine
import scenes

pg.init()

running = True
clock = pg.time.Clock()
pg.display.set_icon(pg.image.load(r"data/IconSmall.png"))
pg.display.set_caption("Snake")
screen = pg.display.set_mode((384, 216), pg.SCALED) # SCALED called to allow fullscreen
TILESIZE = 16
tileset = Engine.load_tileset(pg.image.load(r"data/Tiles.png").convert_alpha(), TILESIZE)
max_fps = 30
pg.display.toggle_fullscreen()

UP, DOWN, LEFT, RIGHT, A, B, PAUSE= pg.K_w, pg.K_s, pg.K_a, pg.K_d, pg.K_j, pg.K_i, pg.K_ESCAPE

current_scene = scenes.Level()

while running:
    current_scene.tick()
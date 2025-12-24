from scripts import engine
import pygame as pg

engine.pygame_init("Snake", r"data/IconSmall.png", (384, 216))

TILE_SIZE = 16
tileset = engine.load_tileset(pg.image.load(r"data/Tiles.png").convert_alpha(), TILE_SIZE)
UP, DOWN, LEFT, RIGHT, A, B, PAUSE= pg.K_w, pg.K_s, pg.K_a, pg.K_d, pg.K_j, pg.K_i, pg.K_ESCAPE
difficulty = 2 # from 0 to 2
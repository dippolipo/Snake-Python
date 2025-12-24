import pygame as pg
from scripts import scenes, engine, globs

game = engine.Game(30, scenes.Level())
game.loop()
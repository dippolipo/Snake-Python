import pygame as pg
from scripts import scenes, engine, globs

scenes.Level()
game = engine.Game(30)
game.loop()
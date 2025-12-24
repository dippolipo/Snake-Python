import pygame as pg
from scripts import scenes, engine, globs

engine.Scene.append_stack(scenes.Level)
game = engine.Game(30)
game.loop()
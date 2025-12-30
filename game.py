import pygame as pg
from scripts import scenes, engine, globs

engine.Scene.append_stack(scenes.MainMenu)
game = engine.Game(30, globs.fullscreen)
game.loop()
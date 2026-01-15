import pygame as pg
from scripts import scenes, engine, globs

engine.SceneManager.reset(scenes.MainMenu)
game = engine.Game(30, globs.fullscreen)
game.loop()
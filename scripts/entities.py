from pygame import Vector2
from scripts import globs

class Snake:
    def __init__(self, initial_pos, initial_length, initial_dir):
        self.pos = Vector2(initial_pos)
        self.dir = [Vector2(initial_dir), Vector2(initial_dir)] # 0 = last, 1 = current, 2 = next, ... FIFO
        self.length = initial_length
        self.speed = 0
        speeds = (3, 2, 1) # frames per tiles
        self.max_speed = speeds[globs.difficulty]
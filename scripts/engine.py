import pygame as pg

clock = pg.time.Clock()

class Scene:
    def key_events(self, event):
        print("events not done")
        pg.quit()

    def event_poll(self):
        for event in pg.event.get():
            match event.type:
                case pg.KEYDOWN:
                    self.key_events(event)

    def tick(self):
        print("tick not done")
        pg.quit()

    def render_frame(self):
        print("render_frame not done")
        pg.quit()

def load_tileset(tileset_image, tile_size):

    tileset_size = (int(tileset_image.get_width() / tile_size), int(tileset_image.get_height() / tile_size))
    single_tiles = [pg.Surface((tile_size, tile_size)).convert_alpha()]
    single_tiles[0].fill(pg.Color(255, 255, 255, 0))

    for i in range(tileset_size[1]):
        for j in range(tileset_size[0]):
            single_tiles.append(tileset_image.subsurface(pg.Rect(j * tile_size, i * tile_size, tile_size, tile_size)))

    return single_tiles


def draw_tilemap(single_tiles, grid, background_color=pg.Color(255, 255, 255, 0)):

    tile_size = single_tiles[0].get_width()
    grid_size = (len(grid[0]), len(grid))
    final_canvas = pg.Surface((grid_size[0] * tile_size, grid_size[1] * tile_size)).convert_alpha()
    final_canvas.fill(background_color)

    for i, row in enumerate(grid):
        for j, tile_id in enumerate(row):
            final_canvas.blit(single_tiles[tile_id], (j * tile_size, i * tile_size))

    return final_canvas


def load_tilemap(file_path):  # file_path needs to be raw

    # file transcription
    with open(file_path) as file:
        content = file.readlines()

    # file processing
    grid = []
    for i, line in enumerate(content[1:]):
        line = line.strip()
        if line[-1] == ",":
            line = line[:-1]
        line = [int(n) for n in line.split(",")]
        grid.append(line)
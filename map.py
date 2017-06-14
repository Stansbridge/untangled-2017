import pygame
import pygame.locals
from random import randint


class Map():
    seed = "b1148905734895734895789789347589" #lmao

    def __init__(self, screen, tileset, world_tile_dimen = (16, 16), tileset_tile_dimen = (64, 64)):
        self.screen = screen
        self.tileset = tileset

        self.tileset_width, self.tileset_height = tileset.get_size()
        self.tileset_tile_dimen = tileset_tile_dimen
        self.world_tile_dimen = world_tile_dimen

        self.offset = {
            "x": 0,
            "y": 0
		}

    def init_grid(self, width = 100, height = 100):
        self.grid = [
            [
                self.gen_grid_tile(i, j) for i in range(width)
            ] for j in range(height)
        ]

    # TODO: move generation to a new class. 
    def gen_grid_tile(self, x, y):
        return randint(0, 100);



    def get_grid_tile(self, x, y):
        return self.grid[y][x];

    def tileset_coord_from_tile_id(self, tile_id):
        x = tile_id % (self.tileset_width // self.tileset_tile_dimen[0])
        y = tile_id // (self.tileset_height // self.tileset_tile_dimen[1])

        return (x, y)

    def get_grid_tile_subsurface(self, tile_id):
        clip_coords = self.tileset_coord_from_tile_id(tile_id)

        tw = self.tileset_tile_dimen[0]
        th = self.tileset_tile_dimen[1]

        clip_rect = (
            tw * clip_coords[0],
            th * clip_coords[1],
            tw,
            th,
        )

        sub_surf = self.tileset.subsurface(clip_rect)
        sub_surf = pygame.transform.scale(sub_surf, self.world_tile_dimen)

        return sub_surf

    def render_grid_tile(self, x, y, tile_id):
        tile_clipped_image = self.get_grid_tile_subsurface(tile_id)

        self.screen.blit(tile_clipped_image, (x * self.world_tile_dimen[0], y * self.world_tile_dimen[1]))
        return 0

    def render(self):
        for y in range(len(self.grid)):
            for x in range(len(self.grid[y])):
                tile_id = self.grid[y][x]
                self.render_grid_tile(x, y, tile_id)
        return 0
import pygame
import pygame.locals

from opensimplex import OpenSimplex
from random import randint


class Map():
    seed = 34234234235232343 #lmao keyboard mashing ftw

    def __init__(self, screen, tileset, world_tile_dimen = (16, 16), tileset_tile_dimen = (64, 64)):
        self.screen = screen
        self.tileset = tileset

        self.tileset_width, self.tileset_height = tileset.get_size()
        self.tileset_tile_dimen = tileset_tile_dimen
        self.world_tile_dimen = world_tile_dimen

        self.openSimplex = OpenSimplex(self.seed)

        self.offset = {
            "x": 0,
            "y": 0
		}

        self.preload_tileset_tiles()

    def init_grid(self, width = 20, height = 20):
        self.grid = [
            [
                self.gen_grid_tile(i, j) for i in range(width)
            ] for j in range(height)
        ]

    # TODO: move generation to a new class. 
    def gen_grid_tile(self, x, y):
        return self.openSimplex.noise2d(x / 10, y / 10);

    def get_grid_tile(self, x, y):
        return self.grid[y][x];

    def tileset_coord_from_tile_id(self, tile_id):
        x = tile_id % (self.tileset_width // self.tileset_tile_dimen[0])
        y = tile_id // (self.tileset_height // self.tileset_tile_dimen[1])

        return (x, y)

    def tile_id_from_tileset_coord(self, x, y):
        return y * (self.tileset_width // self.tileset_tile_dimen[0]) + x

    def get_grid_tile_subsurface(self, tile_id):
        sub_surf = 0
        if(tile_id in self.loaded_tileset_subsurfaces):
            sub_surf = self.loaded_tileset_subsurfaces[tile_id]
        else:
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

            self.loaded_tileset_subsurfaces[tile_id] = sub_surf
        return sub_surf

    def preload_tileset_tiles(self):
        w = self.tileset_width // self.tileset_tile_dimen[0]
        h = self.tileset_height // self.tileset_tile_dimen[1]

        self.loaded_tileset_subsurfaces = {}

        for i in range(w):
            for j in range(h):
                tile_id = self.tile_id_from_tileset_coord(i, j);
                self.loaded_tileset_subsurfaces[tile_id] = self.get_grid_tile_subsurface(tile_id)

    def render_grid_tile(self, x, y, tile_id):
        tile_clipped_image = self.get_grid_tile_subsurface(tile_id)

        self.screen.blit(tile_clipped_image, (x * self.world_tile_dimen[0], y * self.world_tile_dimen[1]))
        return 0

    def render(self):
        for y, row in enumerate(self.grid):
            for x, noise_val in enumerate(self.grid[y]):
                if(noise_val < 0):
                    self.render_grid_tile(x, y, 5)
                else:
                    self.render_grid_tile(x, y, 3)
        return 0
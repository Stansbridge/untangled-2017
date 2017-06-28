import pygame
import pygame.locals

from opensimplex import OpenSimplex

from player import *

class Map():
    seed = 34234234235232343 #lmao keyboard mashing ftw

    def __init__(self, screen, tileset, world_tile_dimen = (16, 16), tileset_tile_dimen = (64, 64)):
        self.screen = screen
        self.screen_size = screen.get_size()

        self.tileset = tileset
    
        self.tileset_width, self.tileset_height = tileset.get_size()
        self.tileset_tile_dimen = tileset_tile_dimen
        self.world_tile_dimen = world_tile_dimen

        self.openSimplex = OpenSimplex(self.seed)

        self.offset = {
            'x': 0,
            'y': 0
        }

        self.preload_tileset_tiles()

    def init_grid(self, width = 200, height = 200):
        self.width = width
        self.height = height
        
        self.grid = [
            [
                self.gen_grid_tile(i, j) for i in range(width)
            ] for j in range(height)
        ]

    def set_centre_player(self, player):
        player.is_centre = True
        self.centre_player = player
        
    # TODO: move generation to a new class. 
    def gen_grid_tile(self, x, y):
        noise = self.openSimplex.noise2d(x / 10, y / 10)

        if (noise < 0):
            tile_val = 6
        else:
            tile_val = 2

        return tile_val

    def get_grid_tile(self, x, y):
        return self.grid[y][x]

    def tileset_coord_from_tile_id(self, tile_id):
        x = tile_id % (self.tileset_width // self.tileset_tile_dimen[0])
        y = tile_id // (self.tileset_height // self.tileset_tile_dimen[1])

        return (x, y)

    def tile_id_from_tileset_coord(self, x, y):
        return y * (self.tileset_width // self.tileset_tile_dimen[0]) + x

    def get_grid_tile_subsurface(self, tile_id):
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

    def check_collision(self, x, y):
        adjusted_x = x // self.world_tile_dimen[0]
        adjusted_y = y // self.world_tile_dimen[1]

        return self.get_grid_tile(adjusted_x, adjusted_y)

    def render(self):
        for y, row in enumerate(self.grid):
            for x, tile_val in enumerate(self.grid[y]):
                self.offset['x'] = -self.centre_player.x // self.world_tile_dimen[0] + self.screen_size[0] // self.world_tile_dimen[0] * 0.5 
                self.offset['y'] = -self.centre_player.y // self.world_tile_dimen[1] + self.screen_size[1] // self.world_tile_dimen[1] * 0.5

                self.render_grid_tile(x + self.offset['x'], y + self.offset['y'], tile_val)
        return 0

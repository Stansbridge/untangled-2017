import pygame
import pygame.locals

from opensimplex import OpenSimplex
from enum import Enum

from player import *

'''
Tiles represents the actions which a tile is able to inflict upon a player.

'''
class Tiles(Enum):
    COLLIDE = 1
    SPIKES = 2
    LAVA = 4
    WATER = 8

class Map():
    seed = 34234234235232343 #lmao keyboard mashing ftw

    def __init__(self, screen, tileset, world_tile_dimen, tileset_tile_dimen):
        self.screen = screen
        self.screen_size = screen.get_size()

        self.tileset = tileset

        self.tileset_width, self.tileset_height = tileset.get_size()
        self.tileset_tile_dimen = tileset_tile_dimen
        self.world_tile_dimen = world_tile_dimen

        self.openSimplex = OpenSimplex(self.seed)

        # Tuple holding all tiles which will report as a collision.
        self.tile_attributes = {
            6: Tiles.COLLIDE.value,
        }

        self.offset = {
            'x': 0,
            'y': 0
        }

        self.preload_tileset_tiles()

    def init_grid(self, width = 25, height = 25):
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

        if (noise < -0.5):
            tile_val = 6
        elif noise < -0.2:
            tile_val = 2
        else:
            tile_val = 67

        return tile_val

    def get_centre(self):
        return (self.screen_size[0] * 0.5, self.screen_size[1] * 0.5)

    def get_grid_tile(self, x, y):
        return self.grid[y][x]

    def get_tile_id_attrib(self, tile_id):
        return self.tile_attributes.get(tile_id)

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

            print("tileset cache miss. loading tile: {0}".format(tile_id))
            clip_coords = self.tileset_coord_from_tile_id(tile_id)

            tw = self.tileset_tile_dimen[0]
            th = self.tileset_tile_dimen[1]

            clip_rect = (
                tw * clip_coords[0],
                th * clip_coords[1],
                tw,
                th,
            )

            sub_surf = self.tileset.subsurface(clip_rect).convert_alpha()
            sub_surf = pygame.transform.scale(sub_surf, self.world_tile_dimen)

            self.loaded_tileset_subsurfaces[tile_id] = sub_surf
        return sub_surf

    def preload_tileset_tiles(self):
        w = self.tileset_width // self.tileset_tile_dimen[0]
        h = self.tileset_height // self.tileset_tile_dimen[1]

        self.loaded_tileset_subsurfaces = {}

        for i in range(w):
            for j in range(h):
                tile_id = self.tile_id_from_tileset_coord(i, j)
                self.loaded_tileset_subsurfaces[tile_id] = self.get_grid_tile_subsurface(tile_id)

    def render_grid_tile(self, x, y, tile_id):
        tile_clipped_image = self.get_grid_tile_subsurface(tile_id)

        self.screen.blit(tile_clipped_image, (x * self.world_tile_dimen[0], y * self.world_tile_dimen[1]))
        return 0

    def get_tile_attributes(self, x, y):
        adjusted_x = x // self.world_tile_dimen[0]
        adjusted_y = y // self.world_tile_dimen[1]

        # Lookup for the tile_id at the provided x, y coordinates.
        tile_id = self.get_grid_tile(adjusted_x, adjusted_y)

        # Lookup the collision status for the current tile_id, defaults to 0 (no status).
        collide_status = self.get_tile_id_attrib(tile_id) or 0

        return collide_status

    def render(self):

        screen_tile_width = self.screen_size[0] // self.world_tile_dimen[0]
        screen_tile_height = self.screen_size[1] // self.world_tile_dimen[1]

        player_pos_screen_x = self.centre_player.x // self.world_tile_dimen[0]
        player_pos_screen_y = self.centre_player.y // self.world_tile_dimen[1]

        self.offset['x'] = -player_pos_screen_x + screen_tile_width * 0.5
        self.offset['y'] = -player_pos_screen_y + screen_tile_height * 0.5

        screen_clip_rect = Rect((0, 0), (screen_tile_width, screen_tile_height))

        for y, row in enumerate(self.grid):
            final_y = y + self.offset['y']
            tile_clip_rect = Rect((0, final_y), (1, 1))

            if(not screen_clip_rect.contains(tile_clip_rect)):
                continue

            for x, tile_val in enumerate(self.grid[y]):
                final_x = x + self.offset['x']
                tile_clip_rect = Rect((final_x, final_y), (1, 1))

                if(not screen_clip_rect.contains(tile_clip_rect)):
                    continue

                self.render_grid_tile(final_x, final_y, tile_val)

        return 0

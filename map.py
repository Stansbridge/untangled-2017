import pygame
import pygame.locals

from opensimplex import OpenSimplex
from enum import Enum

from player import *

'''
TileAttributes represents the actions which a tile is able to inflict upon a player.
'''
class TileAttributes(Enum):
    COLLIDE = 1
    SPIKES = 2
    LAVA = 4
    WATER = 8

class Tile():
    def __init__(self, id, attributes, subsurface):
        self.id = id
        self.attributes = attributes
        self.subsurface = subsurface

class Tileset():
    def __init__(self, tileset, tileset_tile_dimen, tile_attributes, world_tile_dimen):
        self.tileset = tileset
        self.tileset_width, self.tileset_height = tileset.get_size()
        self.tileset_tile_dimen = tileset_tile_dimen
        self.tiles = {}
        self.tile_attributes = tile_attributes
        self.world_tile_dimen = world_tile_dimen

        self.load_tiles()

    def get_tile(self, tile_id):
        return self.tiles[tile_id]

    def get_tile_id_attributes(self, tile_id):
        return self.tile_attributes.get(tile_id, 0)

    def tileset_coord_from_tile_id(self, tile_id):
        x = tile_id % (self.tileset_width // self.tileset_tile_dimen[0])
        y = tile_id // (self.tileset_height // self.tileset_tile_dimen[1])
        return (x, y)

    def get_tile_id(self, x, y):
        return y * (self.tileset_width // self.tileset_tile_dimen[0]) + x

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

        sub_surf = self.tileset.subsurface(clip_rect).convert_alpha()
        sub_surf = pygame.transform.scale(sub_surf, self.world_tile_dimen)
        return sub_surf

    def load_tiles(self):
        w = self.tileset_width // self.tileset_tile_dimen[0]
        h = self.tileset_height // self.tileset_tile_dimen[1]

        for i in range(w):
            for j in range(h):
                id = self.get_tile_id(i, j)
                self.tiles[id] = Tile(id, self.get_tile_id_attributes(id), self.get_grid_tile_subsurface(id))

class Level():
    def __init__(self, id, tileset):
        self.id = id 
        self.tileset = tileset

    # get tile identifier
    def get_grid_tile(self, x, y):
        return self.grid[y][x]

    # get tile
    def get_tile(self, x, y):
        return self.tileset.get_tile(self.get_grid_tile(x, y))

    def id(self):
        return self.id

class ProceduralLevel(Level):
    def __init__(self, id, tileset, seed):
        Level.__init__(self, id, tileset)
        self.openSimplex = OpenSimplex(seed)
        self.init_grid()

    def init_grid(self, width = 500, height = 500):
        self.width = width
        self.height = height
        self.grid = [
            [
                self.gen_grid_tile(i, j) for i in range(width)
            ] for j in range(height)
        ]
        
    def gen_grid_tile(self, x, y):
        noise = self.openSimplex.noise2d(x / 10, y / 10)

        if (noise < 0):
            tile_val = 6
        else:
            tile_val = 2

        return tile_val

class Map():
    def __init__(self, screen, level, world_tile_dimen):
        self.screen = screen
        self.level = level
        self.screen_size = screen.get_size()
        self.world_tile_dimen = world_tile_dimen
        self.offset = {
            'x': 0,
            'y': 0
        }

    def set_level(self, level):
        self.level = level

    def set_centre_player(self, player):
        player.is_centre = True
        self.centre_player = player

    def get_centre(self):
        return (self.screen_size[0] * 0.5, self.screen_size[1] * 0.5)

    def render_grid_tile(self, x, y, tile_id):
        tile = self.level.get_tile(x, y)
        self.screen.blit(tile.subsurface, (x * self.world_tile_dimen[0], y * self.world_tile_dimen[1]))
        return 0

    def get_tile_attributes(self, x, y):
        adjusted_x = x // self.world_tile_dimen[0]
        adjusted_y = y // self.world_tile_dimen[1]

        # Lookup for the tile_id at the provided x, y coordinates.
        tile = self.level.get_tile(adjusted_x, adjusted_y)

        return tile.attributes

    def render(self):

        screen_tile_width = self.screen_size[0] // self.world_tile_dimen[0]
        screen_tile_height = self.screen_size[1] // self.world_tile_dimen[1]

        player_pos_screen_x = self.centre_player.x // self.world_tile_dimen[0]
        player_pos_screen_y = self.centre_player.y // self.world_tile_dimen[1]

        self.offset['x'] = -player_pos_screen_x + screen_tile_width * 0.5
        self.offset['y'] = -player_pos_screen_y + screen_tile_height * 0.5

        screen_clip_rect = Rect((0, 0), (screen_tile_width, screen_tile_height))

        for y, row in enumerate(self.level.grid):
            final_y = y + self.offset['y']
            tile_clip_rect = Rect((0, final_y), (1, 1))

            if(not screen_clip_rect.contains(tile_clip_rect)):
                continue

            for x, tile in enumerate(self.level.grid[y]):
                final_x = x + self.offset['x']
                tile_clip_rect = Rect((final_x, final_y), (1, 1))

                if(not screen_clip_rect.contains(tile_clip_rect)):
                    continue

                self.render_grid_tile(final_x, final_y, tile)

        return 0

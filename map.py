import pygame
import pygame.locals
from functools import reduce
from opensimplex import OpenSimplex

from player import *
from constants import TileTypes, TileDefinitions

class Tile():
    def __init__(self, attributes, subsurface):
        self.attributes = attributes
        self.subsurface = subsurface

def gridTileFactory (*tiles):
    def processSurfaces(x, y):
        x = x.copy()
        y = y.copy()
        x.blit(y, (0, 0))
        return x

    tiles = list(tiles)
    subsurface = reduce(processSurfaces, [t.subsurface for t in tiles])
    mask = reduce(lambda x, y: x | y, [t.attributes.mask for t in tiles])
    definitions = reduce(lambda x, y: x + y, [t.attributes.definitions for t in tiles])
    return Tile(TileAttributes(mask, definitions), subsurface)

class TileAttributes():
    def __init__(self, mask, definitions):
        self.mask = mask;
        self.definitions = definitions

class Tileset():
    def __init__(self, tileset, dimension, masks, definitions, world_dimension):
        self.tileset = tileset
        self.width, self.height = tileset.get_size()
        self.dimension = dimension
        self.masks = masks
        self.definitions = definitions
        self.world_dimension = world_dimension
        self.tiles = {}
        self.load_tiles()

    def get_tile_by_id(self, id):
        return self.tiles[id]

    def get_mask(self, id):
        return self.masks.get(id, TileTypes.DEFAULT.value)

    def get_definition(self, id):
        return self.definitions.get(id, [TileDefinitions.DEFAULT.value])

    def find_position(self, id):
        x = id % (self.width // self.dimension[0])
        y = id // (self.height // self.dimension[1])
        return (x, y)

    def find_id(self, x, y):
        return y * (self.width // self.dimension[0]) + x

    def find_subsurface(self, id):
        clip_x, clip_y = self.find_position(id)
        tw, th = self.dimension

        clip_rect = (
            tw * clip_x,
            th * clip_y,
            tw,
            th
        )

        subsurface = self.tileset.subsurface(clip_rect).convert_alpha()
        subsurface = pygame.transform.scale(subsurface, self.world_dimension)
        return subsurface

    def load_tiles(self):
        w = self.width // self.dimension[0]
        h = self.height // self.dimension[1]

        for i in range(w):
            for j in range(h):
                id = self.find_id(i, j)
                self.tiles[id] = Tile(TileAttributes(self.get_mask(id), self.get_definition(id)), self.find_subsurface(id))

class Level():
    def __init__(self, id, tileset):
        self.id = id
        self.tileset = tileset
        self.load_grid()

    def load_grid(self):
        self.grid = [[]]

    def get_grid_tile(self, x, y):
        return self.grid[y][x]

class ProceduralLevel(Level):
    def __init__(self, id, tileset, seed):
        self.openSimplex = OpenSimplex(seed)
        Level.__init__(self, id, tileset)
    
    def load_grid(self, width = 500, height = 500):
        self.width = width
        self.height = height
        self.grid = [
                [
                    self.generate_grid_tile(i, j) for i in range(width)
                    ] for j in range(height)
                ]
        self.grid = self.spawn_example_ladder(self.grid)

    def generate_grid_tile(self, x, y):
        noise = self.openSimplex.noise2d(x / 10, y / 10)
        if (noise < 0):
            id = 6
        else:
            id = 2

        return self.tileset.get_tile_by_id(id)

    def spawn_example_ladder(self, grid):
        spawnable = 1;
        for y, row in enumerate(grid):
            for x, tile in enumerate(grid[y]):
                if spawnable > 0:
                    temp_y = y
                    temp_x = x
                    
                    criteria = True
                    if criteria:
                        existing_tile = grid[y][x]
                        grid[y][x] = gridTileFactory(existing_tile,
                            Tile(TileAttributes(self.tileset.get_mask(83), self.tileset.get_definition(83)), self.tileset.find_subsurface(83)))
                        spawnable -= 1
        return grid

class Map():
    def __init__(self, screen, level, world_dimension = (32, 32)):
        self.screen = screen
        self.level = level
        self.screen_size = screen.get_size()
        self.dimension = world_dimension
        self.offset = {
            'x': 0,
            'y': 0
        }


    def set_centre_player(self, player):
        player.is_centre = True
        self.centre_player = player

    def get_centre(self):
        return (self.screen_size[0] * 0.5, self.screen_size[1] * 0.5)

    def render_grid_tile(self, x, y, tile):
        self.screen.blit(tile.subsurface, (x * self.dimension[0], y * self.dimension[1]))

    def get_tile_attributes(self, x, y):
        adjusted_x = x // self.dimension[0]
        adjusted_y = y // self.dimension[1]

        # Lookup for the tile_id at the provided x, y coordinates.
        tile = self.level.get_grid_tile(adjusted_x, adjusted_y)
        return tile.attributes

    def render(self):

        screen_tile_width = self.screen_size[0] // self.dimension[0]
        screen_tile_height = self.screen_size[1] // self.dimension[1]

        player_pos_screen_x = self.centre_player.x // self.dimension[0]
        player_pos_screen_y = self.centre_player.y // self.dimension[1]

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

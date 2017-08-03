from functools import reduce

import pygame

class Tileset():
    def __init__(self, tileset_path, dimension, attributes, world_dimension):
        self.tileset = pygame.image.load(tileset_path)
        self.width, self.height = self.tileset.get_size()
        self.height = self.height
        self.dimension = dimension
        self.attributes = attributes
        self.world_dimension = world_dimension
        self.tiles = {}
        self.load_tiles()

    def get_tile_by_id(self, id):
        return self.tiles[id]

    def get_attributes(self, id):
        return self.attributes.get(id, 0)

    def find_position(self, id):
        x = id % (self.width // self.dimension[0])
        y = id // (self.height // self.dimension[1])
        return (x, y)

    def find_id(self, x, y):
        return y * (self.width // self.dimension[0]) + x

    # pos: tile precision (x, y) coordinates.
    def find_subsurface(self, i, j):
        tw, th = self.dimension
        clip_rect = (
            tw * i,
            th * j,
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
                self.tiles[id] = Tile(self.get_attributes(id), self.find_subsurface(i, j))


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
    attributes = reduce(lambda x, y: x | y, [t.attributes for t in tiles])
    return Tile(attributes, subsurface)
from enum import Enum

import pygame

import map

'''
TileAttribute represents the actions which a tile is able to inflict upon a player.

'''
class TileAttribute(Enum):
    COLLIDE =   0b0001
    SPIKES =    0b0010
    LAVA =      0b0100
    WATER =     0b1000


class TileType(Enum):
    DIRT = (2, [])
    BRICK = (7, [ TileAttribute.COLLIDE ])

    def __init__(self, tileset_id, attributes):
        self.tileset_id = tileset_id
        self.attributes = 0
        for attribute in attributes:
            self.attributes = self.attributes | attribute.value

    def has_attribute(self, attribute):
        return self.attributes & attribute.value == attribute.value


class Tileset():
    def __init__(self, image, grid_dimensions, render_dimensions=(map.TILE_PIX_WIDTH, map.TILE_PIX_HEIGHT)):
        self.image = image
        self.grid_dimensions = grid_dimensions
        self.render_dimensions = render_dimensions
        self.surfaces = {}

    def get_surface(self, id):
        if id in self.surfaces:
            return self.surfaces[id]

        clip_x, clip_y = self.find_position(id)

        cur_tile_width = (self.image.get_width() / self.grid_dimensions[0])
        cur_tile_height = (self.image.get_height() / self.grid_dimensions[0])

        clip_rect = (
            cur_tile_width * clip_x,
            cur_tile_height * clip_y,
            cur_tile_width,
            cur_tile_height
        )

        subsurface = self.image.subsurface(clip_rect).convert_alpha()
        subsurface = pygame.transform.scale(subsurface, self.render_dimensions)
        self.surfaces[id] = subsurface

        return self.surfaces[id]

    def find_position(self, id):
        x = id % self.grid_dimensions[0]
        y = id // self.grid_dimensions[1]

        return (x, y)

    def find_id(self, x, y):
        return y * (self.width // self.grid_dimensions[0]) + x

import pygame
import pygame.locals
import os.path

from functools import reduce
from opensimplex import OpenSimplex
from enum import Enum
from pyknon.genmidi import Midi
from pyknon.music import NoteSeq

from player import *

'''
TileTypes represents the actions which a tile is able to inflict upon a player.

'''
class TileTypes(Enum):
    COLLIDE = 1
    SPIKES = 2
    LAVA = 4
    WATER = 8

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

class Tileset():
    def __init__(self, tileset, dimension, attributes, world_dimension):
        self.tileset = tileset
        self.width, self.height = tileset.get_size()
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
                if id == 6:
                    self.tiles[id] = gridTileFactory(
                            Tile(self.get_attributes(id), self.find_subsurface(id)),
                            Tile(self.get_attributes(10), self.find_subsurface(10)))
                else:
                    self.tiles[id] = Tile(self.get_attributes(id), self.find_subsurface(id))

class LevelMusic():
    def __init__(self, location):
        self.location = location

    def load_music(self):
        return pygame.mixer.music.load(self.location)

    # Play the music a given number of times.
    # -1 will play on repeat, 0 will play once and so on...
    @staticmethod
    def play_music(count):
        pygame.mixer.music.play(count)

    @staticmethod
    def play_music_repeat():
        pygame.mixer.music.play(-1)

    @staticmethod
    def stop_music():
        pygame.mixer.music.stop()

    # https://github.com/kroger/pyknon
    # e.g. TileMusic.create_music("D4 F#8 A Bb4", 90, 0, "Test")
    # Append given notes to a music file.
    @staticmethod
    def create_music(note_seq, given_tempo, given_track, song_name):
        notes = NoteSeq(note_seq)
        midi = Midi(1, tempo=given_tempo)
        midi.seq_notes(notes, track=given_track)
        file = ("assets\music\/" + song_name + ".mid")

        # Check if file exists
        if os.path.isfile(file):
            midi.write(file)
        else:
            print(song_name + ".mid Does not exist")

class Level():
    def __init__(self, id, tileset, music):
        self.id = id
        self.tileset = tileset
        self.music = music
        self.load_grid()

    def load_grid(self):
        self.grid = [[]]

    def get_grid_tile(self, x, y):
        return self.grid[y][x]

class ProceduralLevel(Level):
    def __init__(self, id, tileset, music, seed):
        self.openSimplex = OpenSimplex(seed)
        Level.__init__(self, id, tileset, music)

    def load_grid(self, width = 500, height = 500):
        self.width = width
        self.height = height
        self.grid = [
                [
                    self.generate_grid_tile(i, j) for i in range(width)
                    ] for j in range(height)
                ]

    def generate_grid_tile(self, x, y):
        noise = self.openSimplex.noise2d(x / 10, y / 10)
        if (noise < 0):
            id = 6
        else:
            id = 2

        return self.tileset.get_tile_by_id(id)

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

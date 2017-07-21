from enum import Enum

'''
TileTypes represents the actions which a tile is able to inflict upon a player.

'''
class TileTypes(Enum):
    DEFAULT = 0
    COLLIDE = 1
    SPIKES = 2
    LAVA = 4
    WATER = 8

'''
GameState
'''
class GameState(Enum):
    MENU = 0
    PLAY = 1
    HELP = 2
    CHARACTER = 3
    QUIT = 4

'''
Colours?
'''
class Colours(Enum):
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)

'''
Tilesheet Enum
'''
class TileDefinitions(Enum):
    DEFAULT = 0
    BLOCK = 1
    MUD = 2
    GRID = 3
    LADDER = 4

class Movement(Enum):
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3

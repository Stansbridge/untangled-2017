from opensimplex import OpenSimplex

from tile import TileAttribute
from tile import TileType

class Level():
    def load_tiles(self):
        self.width = 0
        self.height = 0
        self.grid = [[]]

    def get_tile(self, x, y):
        return self.grid[y][x]

    def can_move_to(self, x, y):
        if x < 0 or x >= self.width:
            return False
        elif y < 0 or y >= self.height:
            return False
        elif self.get_tile(x, y).has_attribute(TileAttribute.COLLIDE):
            # return False
            return True
        return True


class ProceduralLevel(Level):
    def __init__(self, seed):
        self.openSimplex = OpenSimplex(seed)
        self.load_tiles()

    def load_tiles(self, width = 1000, height = 1000):
        self.width = width
        self.height = height
        self.grid = [
            [ self.generate_grid_tile(i, j) for i in range(width) ] for j in range(height)
        ] 

    def generate_grid_tile(self, x, y):
        noise = self.openSimplex.noise2d(x / 10, y / 10)
        if (noise < 0):
            return TileType.BRICK
        else:
            return TileType.DIRT

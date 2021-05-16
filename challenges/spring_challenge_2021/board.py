
from dataclasses import dataclass


@dataclass(frozen=True)
class CubeCoord:
    x: int
    y: int
    z: int

    def __add__(self, other):
        return CubeCoord(self.x + other.x, self.y + other.y, self.z + other.z)

    def __mul__(self, factor):
        return CubeCoord(self.x * factor, self.y * factor, self.z * factor)

    def distance(self, other):
        return (abs(self.x - other.x) + abs(self.y - other.y) + abs(self.z - other.z)) // 2


DIRECTIONS = (CubeCoord(+1, -1, 0), CubeCoord(+1, 0, -1), CubeCoord(0, +1, -1),
              CubeCoord(-1, +1, 0), CubeCoord(-1, 0, +1), CubeCoord(0, -1, +1))


@dataclass(frozen=True)
class Cell:
    index: int
    richness: int

    def __str__(self):
        return f'{self.index}'

    @staticmethod
    def from_string(string):
        cell_index, richness, *neighbors = map(int, string.split())
        return Cell(cell_index, richness)


class Board:

    def __init__(self, size):
        self.coordinates_to_index = {}
        self.index_to_coordinates = {}
        self.cells = []
        self.cells_at_dist = {}

        index = 0
        coord = CubeCoord(0, 0, 0)
        self.coordinates_to_index[coord] = index
        self.index_to_coordinates[index] = coord
        self.cells.append(Cell(index, 3))

        index += 1
        coord += DIRECTIONS[0]
        richness = 3

        for dist in range(1, size + 1):
            for orientation, direction in enumerate(DIRECTIONS):
                for count in range(dist):
                    self.coordinates_to_index[coord] = index
                    self.index_to_coordinates[index] = coord
                    self.cells.append(Cell(index, richness))

                    index += 1
                    coord += DIRECTIONS[(orientation + 2) % 6]

            coord += DIRECTIONS[0]
            richness -= 1
        self.update_cells_at_dist()

    def update_cells_at_dist(self):
        self.cells_at_dist = {(origin, dist): set() for origin in self.index_to_coordinates for dist in range(4)}
        for target in self.cells:
            if target.richness > 0:
                target_coord = self.index_to_coordinates[target.index]
                for origin in self.cells:
                    origin_coord = self.index_to_coordinates[origin.index]
                    dist = origin_coord.distance(target_coord)
                    if dist <= 3:
                        self.cells_at_dist[(origin.index, dist)].add(target.index)

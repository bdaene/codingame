
# https://www.codingame.com/ide/puzzle/doubly-solved-rubiks-cube

from dataclasses import dataclass, astuple
from enum import Enum
from typing import Optional


class Color(Enum):
    UP = 'U'
    LEFT = 'L'
    FRONT = 'F'
    RIGHT = 'R'
    BACK = 'B'
    DOWN = 'D'


@dataclass
class Cube:
    up: Optional[Color] = None
    left: Optional[Color] = None
    front: Optional[Color] = None
    right: Optional[Color] = None
    back: Optional[Color] = None
    down: Optional[Color] = None

    @property
    def colors(self):
        return frozenset(astuple(self))

    @staticmethod
    def get_cube_with_transformation(before, after, origin):
        before_tuple = astuple(before)
        after_tuple = astuple(after)
        origin_tuple = astuple(origin)
        return Cube(*(origin_tuple[before_tuple.index(color)] for color in after_tuple))


@dataclass
class RubikCube:
    # Layers from up to down, lines from back to front, cubes from left to right:
    # 0  1  2
    #  3  4  5
    #   6  7  8
    # 9 10 11
    #  12 13 14
    #   15 16 17
    # 18 19 20
    #  21 22 23
    #   24 25 26
    cubes: tuple[Cube, ...]  

    @staticmethod
    def from_string(string):
        return RubikCube((
            Cube(up=Color(string[4]), left=Color(string[25]), back=Color(string[39])),
            Cube(up=Color(string[5]), back=Color(string[38])),
            Cube(up=Color(string[6]), right=Color(string[35]), back=Color(string[37])),

            Cube(up=Color(string[12]), left=Color(string[26])),
            Cube(up=Color(string[13])),
            Cube(up=Color(string[14]), right=Color(string[34])),

            Cube(up=Color(string[20]), left=Color(string[27]), front=Color(string[29])),
            Cube(up=Color(string[21]), front=Color(string[30])),
            Cube(up=Color(string[22]), right=Color(string[33]), front=Color(string[31])),

            Cube(left=Color(string[41]), back=Color(string[55])),
            Cube(back=Color(string[54])),
            Cube(right=Color(string[51]), back=Color(string[53])),

            Cube(left=Color(string[42])),
            Cube(),
            Cube(right=Color(string[50])),

            Cube(left=Color(string[43]), front=Color(string[45])),
            Cube(front=Color(string[46])),
            Cube(right=Color(string[49]), front=Color(string[47])),

            Cube(down=Color(string[94]), left=Color(string[57]), back=Color(string[71])),
            Cube(down=Color(string[95]), back=Color(string[70])),
            Cube(down=Color(string[96]), right=Color(string[67]), back=Color(string[69])),

            Cube(down=Color(string[86]), left=Color(string[58])),
            Cube(down=Color(string[87])),
            Cube(down=Color(string[88]), right=Color(string[66])),

            Cube(down=Color(string[78]), left=Color(string[59]), front=Color(string[61])),
            Cube(down=Color(string[79]), front=Color(string[62])),
            Cube(down=Color(string[80]), right=Color(string[65]), front=Color(string[63])),
        ))

    def to_string(self):
        string = ''
        string += '    ' + self.cubes[0].up.value + self.cubes[1].up.value + self.cubes[2].up.value + '\n'
        string += '    ' + self.cubes[3].up.value + self.cubes[4].up.value + self.cubes[5].up.value + '\n'
        string += '    ' + self.cubes[6].up.value + self.cubes[7].up.value + self.cubes[8].up.value + '\n'
        string += '\n'
        string += self.cubes[0].left.value + self.cubes[3].left.value + self.cubes[6].left.value + ' '
        string += self.cubes[6].front.value + self.cubes[7].front.value + self.cubes[8].front.value + ' '
        string += self.cubes[8].right.value + self.cubes[5].right.value + self.cubes[2].right.value + ' '
        string += self.cubes[2].back.value + self.cubes[1].back.value + self.cubes[0].back.value + '\n'
        string += self.cubes[9].left.value + self.cubes[12].left.value + self.cubes[15].left.value + ' '
        string += self.cubes[15].front.value + self.cubes[16].front.value + self.cubes[17].front.value + ' '
        string += self.cubes[17].right.value + self.cubes[14].right.value + self.cubes[11].right.value + ' '
        string += self.cubes[11].back.value + self.cubes[10].back.value + self.cubes[9].back.value + '\n'
        string += self.cubes[18].left.value + self.cubes[21].left.value + self.cubes[24].left.value + ' '
        string += self.cubes[24].front.value + self.cubes[25].front.value + self.cubes[26].front.value + ' '
        string += self.cubes[26].right.value + self.cubes[23].right.value + self.cubes[20].right.value + ' '
        string += self.cubes[20].back.value + self.cubes[19].back.value + self.cubes[18].back.value + '\n'
        string += '\n'
        string += '    ' + self.cubes[24].down.value + self.cubes[25].down.value + self.cubes[26].down.value + '\n'
        string += '    ' + self.cubes[21].down.value + self.cubes[22].down.value + self.cubes[23].down.value + '\n'
        string += '    ' + self.cubes[18].down.value + self.cubes[19].down.value + self.cubes[20].down.value

        return string

    @staticmethod
    def get_rubik_cube_with_transformation(before, after, origin):
        new_cubes = []

        for after_cube in after.cubes:
            for before_cube, origin_cube in zip(before.cubes, origin.cubes):
                if before_cube.colors == after_cube.colors:
                    new_cubes.append(Cube.get_cube_with_transformation(before_cube, after_cube, origin_cube))

        return RubikCube(tuple(new_cubes))


SOLVED_CUBE = RubikCube((
    Cube(up=Color.UP, left=Color.LEFT, back=Color.BACK), Cube(up=Color.UP, back=Color.BACK), Cube(up=Color.UP, right=Color.RIGHT, back=Color.BACK),
    Cube(up=Color.UP, left=Color.LEFT), Cube(up=Color.UP), Cube(up=Color.UP, right=Color.RIGHT),
    Cube(up=Color.UP, left=Color.LEFT, front=Color.FRONT), Cube(up=Color.UP, front=Color.FRONT), Cube(up=Color.UP, right=Color.RIGHT, front=Color.FRONT),

    Cube(left=Color.LEFT, back=Color.BACK), Cube(back=Color.BACK), Cube(right=Color.RIGHT, back=Color.BACK),
    Cube(left=Color.LEFT), Cube(), Cube(right=Color.RIGHT),
    Cube(left=Color.LEFT, front=Color.FRONT), Cube(front=Color.FRONT), Cube(right=Color.RIGHT, front=Color.FRONT),

    Cube(down=Color.DOWN, left=Color.LEFT, back=Color.BACK), Cube(down=Color.DOWN, back=Color.BACK), Cube(down=Color.DOWN, right=Color.RIGHT, back=Color.BACK),
    Cube(down=Color.DOWN, left=Color.LEFT), Cube(down=Color.DOWN), Cube(down=Color.DOWN, right=Color.RIGHT),
    Cube(down=Color.DOWN, left=Color.LEFT, front=Color.FRONT), Cube(down=Color.DOWN, front=Color.FRONT), Cube(down=Color.DOWN, right=Color.RIGHT, front=Color.FRONT),
))


def main():
    configuration = RubikCube.from_string('\n'.join(input() for _ in range(11)))
    new_configuration = RubikCube.get_rubik_cube_with_transformation(configuration, SOLVED_CUBE, SOLVED_CUBE)
    print(new_configuration.to_string())


if __name__ == "__main__":
    main()

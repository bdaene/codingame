# See https://www.codingame.com/ide/puzzle/l-triominoes

import numpy


def print_grid(grid):
    w, h = grid.shape
    print('+' + '--+' * w)
    for y in range(h):
        line = '|'
        for x in range(w):
            line += '##' if grid[x][y] == 0 else '  '
            line += ' ' if x + 1 < w and grid[x + 1][y] == grid[x][y] else '|'
        print(line)
        line = '+'
        for x in range(w):
            line += '  +' if y + 1 < h and grid[x][y + 1] == grid[x][y] else '--+'
        print(line)


def solve(grid, n, x, y):
    to_visit = [(n, 0, 0, x, y)]
    count = 0
    while to_visit:
        n, pos_x, pos_y, x, y = to_visit.pop()
        n -= 1
        mid_x, mid_y = pos_x + (1 << n), pos_y + (1 << n)
        count += 1
        for pos_x, pos_y, corner_x, corner_y in [
            (pos_x, pos_y, mid_x - 1, mid_y - 1),
            (mid_x, pos_y, mid_x, mid_y - 1),
            (mid_x, mid_y, mid_x, mid_y),
            (pos_x, mid_y, mid_x - 1, mid_y),

        ]:
            if pos_x <= x < pos_x + (1 << n) and pos_y <= y < pos_y + (1 << n):
                hole_x, hole_y = x, y
            else:
                grid[corner_x][corner_y] = count
                hole_x, hole_y = corner_x, corner_y
            if n > 0:
                to_visit.append((n, pos_x, pos_y, hole_x, hole_y))


def main():
    n = int(input())
    x, y = map(int, input().split())

    grid = numpy.full((1 << n, 1 << n), 0, dtype=numpy.int8)
    solve(grid, n, x, y)
    print_grid(grid)


if __name__ == "__main__":
    main()

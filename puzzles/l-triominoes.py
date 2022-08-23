# See https://www.codingame.com/ide/puzzle/l-triominoes

import numpy


def show_grid(grid):
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


def solve(grid, x, y):
    to_visit = [(0, 0) + grid.shape + (x, y)]
    count = 0
    while to_visit:
        m, n, o, p, x, y = to_visit.pop()
        q, r = (m + o) // 2, (n + p) // 2
        count += 1
        for m_, n_, o_, p_, q_, r_ in [(m, n, q, r, q - 1, r - 1), (q, n, o, r, q, r - 1), (q, r, o, p, q, r),
                                       (m, r, q, p, q - 1, r)]:
            if m_ <= x < o_ and n_ <= y < p_:
                if o_-m_ > 1 and p_-n_ > 1:
                    to_visit.append((m_, n_, o_, p_, x, y))
            else:
                grid[q_][r_] = count
                if o_-m_ > 1 and p_-n_ > 1:
                    to_visit.append((m_, n_, o_, p_, q_, r_))


def main():
    n = int(input())
    x, y = map(int, input().split())

    grid = numpy.full((1 << n, 1 << n), 0, dtype=numpy.int8)
    solve(grid, x, y)
    show_grid(grid)


if __name__ == "__main__":
    main()

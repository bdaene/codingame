# https://www.codingame.com/ide/puzzle/sudoku-solver

import sys


def debug(*msg):
    print(*msg, file=sys.stderr, flush=True)


EMPTY_VALUE = '0'
VALUES = set('123456789')


def solve(sudoku):
    rows_values = [VALUES - set(sudoku[row][j] for j in range(9)) for row in range(9)]
    columns_values = [VALUES - set(sudoku[i][col] for i in range(9)) for col in range(9)]
    squares_values = [VALUES - set(sudoku[row + i][col + j] for i in range(3) for j in range(3)) for row in
                      range(0, 9, 3) for col in range(0, 9, 3)]

    debug(rows_values)
    debug(columns_values)
    debug(squares_values)

    empty_cells = set((row, col) for row in range(9) for col in range(9) if sudoku[row][col] == EMPTY_VALUE)

    debug(empty_cells)

    def fill():
        if not empty_cells:
            yield sudoku
            return

        cell = min(empty_cells, key=lambda c: len(rows_values[c[0]] & columns_values[c[1]] & squares_values[c[0]//3*3+c[1]//3]))
        empty_cells.remove(cell)

        row, col = cell
        square = row//3*3+col//3
        values = rows_values[row] & columns_values[col] & squares_values[square]

        for value in values:
            sudoku[row][col] = value
            rows_values[row].remove(value)
            columns_values[col].remove(value)
            squares_values[square].remove(value)
            yield from fill()
            sudoku[row][col] = EMPTY_VALUE
            rows_values[row].add(value)
            columns_values[col].add(value)
            squares_values[square].add(value)

        empty_cells.add(cell)

    return next(fill())


def main():
    sudoku = [list(input()) for _ in range(9)]
    sudoku = solve(sudoku)
    print('\n'.join(map(''.join, sudoku)))


if __name__ == "__main__":
    main()

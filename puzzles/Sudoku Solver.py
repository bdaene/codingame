
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

    empty_cells = [(row, col) for row in range(9) for col in range(9) if sudoku[row][col] == EMPTY_VALUE]
    empty_cells.sort(key=lambda cell: len(
        rows_values[cell[0]] & columns_values[cell[1]] & squares_values[cell[0] // 3 * 3 + cell[1] // 3]), reverse=True)

    debug(empty_cells)

    index = len(empty_cells) - 1
    cell_values = {}
    while 0 <= index < len(empty_cells):
        cell = empty_cells[index]
        row, col = cell
        square = row // 3 * 3 + col // 3
        if cell not in cell_values:
            cell_values[cell] = rows_values[row] & columns_values[col] & squares_values[square]
        values = cell_values[cell]
        value = sudoku[row][col]
        if value != EMPTY_VALUE:
            rows_values[row].add(value)
            columns_values[col].add(value)
            squares_values[square].add(value)
        if not values:
            sudoku[row][col] = EMPTY_VALUE
            del cell_values[cell]
            index += 1
        else:
            value = values.pop()
            sudoku[row][col] = value
            rows_values[row].remove(value)
            columns_values[col].remove(value)
            squares_values[square].remove(value)
            index -= 1

    if index < 0:
        return sudoku


def main():
    sudoku = [list(input()) for _ in range(9)]
    sudoku = solve(sudoku)
    print('\n'.join(map(''.join, sudoku)))


if __name__ == "__main__":
    main()

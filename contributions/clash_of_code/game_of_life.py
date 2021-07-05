
from random import choices

height, width = map(int, input().split())
board = [input() for _ in range(height)]

# board = [choices('O ', k=width) for _ in range(height)]
print('\n'.join(''.join(row) for row in board))
print()


def next_state(row, col):
    alive_neighbors_count = 0
    for r in range(-1, 2):
        for c in range(-1, 2):
            if (r, c) == (0, 0):
                continue
            if not (0 <= row + r < height) or not (0 <= col + c < width):
                continue
            if board[row+r][col+c] == 'O':
                alive_neighbors_count += 1
    if board[row][col] == '.' and alive_neighbors_count == 3:
        return 'O'
    elif board[row][col] == 'O' and (alive_neighbors_count < 2 or alive_neighbors_count > 3):
        return '.'
    else:
        return board[row][col]


print('\n'.join(''.join(next_state(row, col) for col in range(width)) for row in range(height)))

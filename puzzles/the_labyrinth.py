import sys

nb_rows, nb_cols, alarm_delay = map(int, input().split())

directions = {
    'LEFT': (0, -1),
    'RIGHT': (0, 1),
    'UP': (-1, 0),
    'DOWN': (1, 0),
}


def get_shortest_path(start_pos, target, allowed_tiles, maze):
    visited_cells = {start_pos: (None, None)}
    starts = [start_pos]
    while starts:
        new_starts = []
        for row, col in starts:
            for direction, (dr, dc) in directions:
                if 0 <= row + dr < nb_rows and 0 <= col + dc < nb_cols:
                    if maze[row+dr][col+dc] == target:
                        path = []
                        current = (row, col)
                        while current is not None:
                            path.append(direction)
                            current, direction = visited_cells[current]
                        return path[::-1]

                    if maze[row+dr][col+dc] in allowed_tiles and (row+dr, col+dc) not in visited_cells:
                        visited_cells[(row+dr, col+dc)] = ((row, col), direction)
                        new_starts.append((row+dr, col+dc))

    return None


# game loop
while True:
    kirk_row, kirk_col = map(int, input().split())
    maze = [input() for row in range(nb_rows)]
    print('\n'.join(maze), file=sys.stderr)

    # Write an action using print
    # To debug: print("Debug messages...", file=sys.stderr, flush=True)

    # Kirk's next move (UP DOWN LEFT or RIGHT).
    print("RIGHT")

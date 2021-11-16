
# https://www.codingame.com/ide/puzzle/codingame-sponsored-contest

import sys

DIRECTIONS = {d: a for d, a in zip('>x^v<', 'ABCDE')}


def debug(*msg):
    print(*msg, file=sys.stderr, flush=True)


def is_far(position, positions):
    x, y = position
    for x_, y_ in positions[:-1]:
        if abs(x - x_) + abs(y - y_) < 2:
            return False
    return True


def get_neighbors(position):
    x, y = position
    return {(x, y - 1): '^', (x + 1, y): '>', (x, y + 1): 'v', (x - 1, y): '<'}


def find_direction(grid, positions):
    seen_positions = {positions[-1]}
    to_check = {position: direction for position, direction in get_neighbors(positions[-1]).items() if
                is_far(position, positions)}
    seen_positions |= to_check.keys()
    best_unknown = None

    while to_check:
        to_check_ = {}
        for position, direction in to_check.items():
            cell = grid.get(position, ' ')
            if cell == '.':
                debug(position, direction)
                return direction
            elif cell == ' ':
                if best_unknown is None:
                    best_unknown = position, direction
                continue

            for position_ in get_neighbors(position):
                if position_ not in seen_positions and grid.get(position_, ' ') != '#' and is_far(position_, positions):
                    to_check_[position_] = direction
                    seen_positions.add(position_)
        to_check = to_check_

    if best_unknown is not None:
        return best_unknown[1]
    return 'x'


def show_grid(height, width, grid, positions):
    lines = []
    for row in range(height):
        current_line = ''
        for col in range(width):
            position = (col, row)
            if position == positions[-1]:
                current_line += 'P'
            elif position in positions[:-1]:
                current_line += 'E'
            else:
                current_line += grid.get(position, ' ')
        lines.append(current_line)
    debug('\n'.join(lines))


def update_grid(grid, borders, positions):
    grid[positions[-1]] = '_'
    for position in positions[:-1]:
        grid.setdefault(position, '.')
    x, y = positions[-1]
    for position, border in zip(((x, y - 1), (x + 1, y), (x, y + 1), (x - 1, y)), borders):
        if border == '#':
            grid[position] = border
        else:
            debug(borders)


def main():
    height, width, players = map(int, (input(), input(), input()))
    debug(height, width, players)

    grid = {}

    while True:
        borders = input(), input(), input(), input()
        positions = [tuple(map(int, input().split())) for _ in range(players)]
        debug(borders, positions)

        update_grid(grid, borders, positions)
        show_grid(height, width, grid, positions)

        print(DIRECTIONS[find_direction(grid, positions)])


if __name__ == "__main__":
    main()

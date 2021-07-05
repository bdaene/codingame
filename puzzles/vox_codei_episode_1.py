import sys
from heapq import heappush, heappop


def get_nodes(grid, row, col):
    height, width = len(grid), len(grid[0])
    if grid[row][col] == '#':
        return set()
    nodes_ = set()
    for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        for d in range(1, 4):
            r = row + dr * d
            c = col + dc * d
            if not (0 <= r < height) or not (0 <= c < width) or grid[r][c] == '#':
                break
            if grid[r][c] == '@':
                nodes_.add((r, c))
    return frozenset(nodes_)


def get_inputs():
    width, height = map(int, input().split())
    grid = tuple(input() for _ in range(height))

    reachable_nodes = {(row, col): get_nodes(grid, row, col) for col in range(width) for row in range(height)}
    reachable_nodes = {pos: value for pos, value in reachable_nodes.items() if len(value) > 0}
    print(reachable_nodes, file=sys.stderr)

    nodes = frozenset((row, col) for col in range(width) for row in range(height) if grid[row][col] == '@')
    print(nodes, file=sys.stderr)

    rounds, nb_bombs = map(int, input().split())
    actions = list(solve(reachable_nodes, nodes, nb_bombs))[::-1]
    print(actions, file=sys.stderr)

    return reachable_nodes, nodes, actions


def solve(reachable_nodes, nodes, nb_bombs):
    heap = [(0, len(nodes), (), nodes)]
    seen_states = set()

    while heap:
        _, _, bombs, nodes = heappop(heap)
        for bomb in sorted(reachable_nodes, key=lambda pos: len(reachable_nodes[pos] & nodes), reverse=True):
            if bomb in nodes:
                continue
            if len(reachable_nodes[bomb] & nodes) == 0:
                break
            new_bombs = bombs + (bomb,)
            state = frozenset(new_bombs)
            if state in seen_states:
                continue
            seen_states.add(state)
            new_nodes = nodes - reachable_nodes[bomb]
            if len(new_nodes) == 0:
                return new_bombs
            if len(new_bombs) < nb_bombs:
                heappush(heap, (len(new_nodes), len(new_bombs), new_bombs, new_nodes))

    return []


def play():
    reachable_nodes, nodes, actions = get_inputs()

    bomb_waiting = {}
    while True:
        for bomb in bomb_waiting:
            bomb_waiting[bomb] -= 1
            if bomb_waiting[bomb] == 0:
                nodes -= reachable_nodes[bomb]
        print(bomb_waiting, file=sys.stderr)

        action = next((action for action in actions if action not in nodes), 'WAIT')
        if action == 'WAIT':
            print('WAIT')
        else:
            actions.remove(action)
            row, col = action
            print(col, row)
            bomb_waiting[action] = 4

        input()  # No need for round and bombs


if __name__ == "__main__":
    play()

"""
............
............
..@@@..@@@#.
.@....@...@.
.@....@..@#.
.@....@.....
.@....@.....
.#@@@.#@@@..
............
"""
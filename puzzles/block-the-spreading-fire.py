#  See https://www.codingame.com/ide/puzzle/block-the-spreading-fire
import sys
from heapq import heappush, heappop
from random import randrange
from time import perf_counter
from typing import NamedTuple


def log(*args):
    print(*args, file=sys.stderr)


class Cell(NamedTuple):
    cut_duration: int
    fire_duration: int
    value: int


Position = tuple[int, int]


class Plan(NamedTuple):
    width: int
    height: int
    cells: dict[Position, Cell]


FireProgress = tuple[int, ...]


def get_turns_before_fire(plan: Plan, fire_start: Position):
    turns_before_fire = {}
    heap = [(0, fire_start)]
    while heap:
        time, position = heappop(heap)
        if position in turns_before_fire:
            continue
        turns_before_fire[position] = time
        time += plan.cells[position].fire_duration
        x, y = position
        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            neighbor_position = (x + dx, y + dy)
            if plan.cells.get(neighbor_position) is not None:
                heappush(heap, (time, neighbor_position))

    return turns_before_fire


def get_circle(plan: Plan, center: Position, radius: int):
    circled_cells, border = {center}, {center}
    for _ in range(radius):
        border_ = set()
        for (x, y) in border:
            for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                neighbor_position = (x + dx, y + dy)
                if neighbor_position not in circled_cells and plan.cells.get(neighbor_position) is not None:
                    border_.add(neighbor_position)
        border = border_
        circled_cells |= border
    return border, circled_cells


def is_valid(plan: Plan, border: list[Position], turns_before_fire: dict[Position, int]):
    turn = 0
    for position in border:
        if turns_before_fire[position] <= turn:
            return False
        turn += plan.cells[position].cut_duration
    return True


def show_grid(width, height, grid, spaces=1):
    log('\n'.join(''.join(f"{grid.get((x, y), '#'):>{spaces}}" for x in range(width)) for y in range(height)))


def solve(plan: Plan, fire_start: Position):
    timer_start = perf_counter()

    total_value = sum(cell.value for cell in plan.cells.values() if cell is not None)
    turns_before_fire = get_turns_before_fire(plan, fire_start)
    # show_grid(plan.width, plan.height, turns_before_fire, 3)

    best_cut = []
    best_value = 0
    tested, valid, total = set(), 0, 0
    while perf_counter() < timer_start + 4.9:
        total += 1
        center = randrange(1, plan.width - 1), randrange(1, plan.height - 1)
        if center not in plan.cells:
            continue
        radius = randrange(1, plan.width + plan.height)
        key = (center, radius)
        if key in tested:
            continue
        tested.add(key)

        border, circled_cells = get_circle(plan, center, radius)
        border = sorted(border, key=lambda position: turns_before_fire[position])
        if not is_valid(plan, border, turns_before_fire):
            continue
        valid += 1

        circle_value = sum(plan.cells[position].value for position in circled_cells)
        if fire_start in circled_cells:
            value = total_value - circle_value
        else:
            border_value = sum(plan.cells[position].value for position in border)
            value = circle_value - border_value
        if value > best_value:
            best_value, best_cut = value, border
    log(f"Tests: {valid}/{len(tested)}/{total}")
    log(f"Value: {best_value}/{total_value}")

    return best_cut


def main():
    tree_cell = Cell(*map(int, input().split()))
    house_cell = Cell(*map(int, input().split()))
    log(f"Tree: {tree_cell}")
    log(f"House: {house_cell}")

    cell_types = {
        '.': tree_cell,
        'X': house_cell,
    }

    width, height = map(int, input().split())
    fire_start_x, fire_start_y = map(int, input().split())
    cells = {(x, y): cell
             for y in range(height) for x, cell in enumerate(map(cell_types.get, input()))
             if cell is not None}
    plan = Plan(width, height, cells)

    cuts = solve(plan, (fire_start_x, fire_start_y))[::-1]

    while 1:
        cooldown = int(input())
        fire_progress = {(x, y): progress
                         for y in range(height) for x, progress in enumerate(map(int, input().split()))}
        if cooldown > 0:
            print("WAIT")
        else:
            if cuts:
                x, y = cuts.pop()
                assert fire_progress[(x, y)] == -1
                print(f"{x} {y}")
            else:
                print("WAIT")


if __name__ == "__main__":
    main()

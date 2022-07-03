#  See https://www.codingame.com/ide/puzzle/block-the-spreading-fire
import sys
from heapq import heappush, heappop, heapify
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
TurnsBeforeFire = dict[Position, int]


def get_turns_before_fire(plan: Plan, fire_start: Position) -> TurnsBeforeFire:
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


def get_circle(plan: Plan, center: Position, radius: int) -> tuple[set[Position], set[Position]]:
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


def is_valid(plan: Plan, border_cells: list[Position], turns_before_fire: dict[Position, int]) -> bool:
    turn = 0
    for position in border_cells:
        if turns_before_fire[position] <= turn:
            return False
        turn += plan.cells[position].cut_duration
    return True


def improve_solution(plan: Plan, turns_before_fire: TurnsBeforeFire,
                     border_cells: list[Position], saved_cells: set[Position]) -> tuple[list[Position], set[Position]]:
    unsorted_border = set(border_cells)
    cells_to_visit = [(-plan.cells[cell].value, cell) for cell in border_cells]
    heapify(cells_to_visit)
    while cells_to_visit:
        _, position = heappop(cells_to_visit)
        x, y = position
        neighbors = set()
        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            neighbor_position = (x + dx, y + dy)
            if (plan.cells.get(neighbor_position) is not None
                    and neighbor_position not in saved_cells
                    and neighbor_position not in unsorted_border):
                neighbors.add(neighbor_position)
        new_border = unsorted_border - {position} | neighbors
        if is_valid(plan, sorted(new_border, key=turns_before_fire.__getitem__), turns_before_fire):
            unsorted_border = new_border
            saved_cells.add(position)
            for neighbor in neighbors:
                heappush(cells_to_visit, (-plan.cells[neighbor].value, neighbor))

    border_cells = sorted(unsorted_border, key=turns_before_fire.__getitem__)
    return border_cells, saved_cells


def show_grid(width, height, grid, spaces=1):
    log('\n'.join(''.join(f"{grid.get((x, y), '#'):>{spaces}}" for x in range(width)) for y in range(height)))


def solve(plan: Plan, fire_start: Position) -> list[Position]:
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

        border_cells, circled_cells = get_circle(plan, center, radius)
        border_cells = sorted(border_cells, key=turns_before_fire.__getitem__)
        if not is_valid(plan, border_cells, turns_before_fire):
            continue
        valid += 1
        if fire_start in circled_cells:
            saved_cells = plan.cells.keys() - circled_cells
        else:
            saved_cells = circled_cells - set(border_cells)
        border_cells, saved_cells = improve_solution(plan, turns_before_fire, border_cells, saved_cells)

        value = sum(plan.cells[position].value for position in saved_cells)
        if value > best_value:
            best_value, best_cut = value, border_cells
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

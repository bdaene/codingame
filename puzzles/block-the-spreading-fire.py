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
    fire_start: Position
    turns_before_fire: dict[Position, int] = {}


FireProgress = tuple[int, ...]
TurnsBeforeFire = dict[Position, int]
Cells = set[Position]
SortedCells = list[Position]

# Global and used everywhere
plan: Plan


def update_plan_turns_before_fire():
    turns_before_fire = plan.turns_before_fire
    heap = [(0, plan.fire_start)]
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


def get_circle(center: Position, radius: int) -> tuple[Cells, Cells]:
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


def is_valid(border_cells: Cells) -> bool:
    turn = 0
    for position in sorted(border_cells, key=plan.turns_before_fire.__getitem__):
        if plan.turns_before_fire[position] <= turn:
            return False
        turn += plan.cells[position].cut_duration
    return True


def get_neighbors(cell: Position) -> Cells:
    x, y = cell
    neighbors = set()
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        neighbor_position = (x + dx, y + dy)
        if neighbor_position in plan.cells:
            neighbors.add(neighbor_position)
    return neighbors


def improve_solution(burned_cells: Cells, border_cells: Cells, saved_cells: Cells) -> tuple[Cells, Cells, Cells]:
    cells_to_visit = border_cells.copy()

    while cells_to_visit:
        position = cells_to_visit.pop()
        neighbors = get_neighbors(position)
        new_safe_cells = neighbors & burned_cells
        if not new_safe_cells:
            border_cells.remove(position)
            saved_cells.add(position)
            continue

        new_border = (border_cells - {position}) | new_safe_cells
        if is_valid(new_border):
            border_cells = new_border
            saved_cells.add(position)
            burned_cells -= neighbors
            cells_to_visit |= (neighbors & border_cells)

    return burned_cells, border_cells, saved_cells


def solve(time_limit: float) -> Cells:
    best_border = set()
    best_value = 0
    tested, valid, total = set(), 0, 0
    while perf_counter() < time_limit:
        total += 1
        center = randrange(1, plan.width - 1), randrange(1, plan.height - 1)
        if center not in plan.cells:
            continue
        radius = randrange(1, plan.width + plan.height)
        key = (center, radius)
        if key in tested:
            continue
        tested.add(key)

        border_cells, circled_cells = get_circle(center, radius)
        if not is_valid(border_cells):
            continue
        valid += 1
        inside_cells = circled_cells - border_cells
        outside_cells = plan.cells.keys() - circled_cells
        if plan.fire_start in inside_cells:
            burned_cells, saved_cells = inside_cells, outside_cells
        else:
            burned_cells, saved_cells = outside_cells, inside_cells
        burned_cells, border_cells, saved_cells = improve_solution(burned_cells, border_cells, saved_cells)

        value = sum(plan.cells[position].value for position in saved_cells)
        if value > best_value:
            best_value, best_border = value, border_cells
    log(f"Tests: {valid}/{len(tested)}/{total}")
    log(f"Value: {best_value}")

    return best_border


def show_cells(cells):
    unsafe_cells = plan.cells.keys() - cells
    return '\n'.join(''.join(
        '.' if (x, y) in unsafe_cells else '#'
        for x in range(plan.width))
        for y in range(plan.height)
    )


def main():
    global plan

    time_start = perf_counter()

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
    fire_start = (fire_start_x, fire_start_y)
    cells = {(x, y): cell
             for y in range(height) for x, cell in enumerate(map(cell_types.get, input()))
             if cell is not None}
    plan = Plan(width, height, cells, fire_start)
    update_plan_turns_before_fire()

    cuts = sorted(solve(time_start + 4.9), key=plan.turns_before_fire.__getitem__, reverse=True)

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

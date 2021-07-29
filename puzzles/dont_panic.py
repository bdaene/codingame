
"""
https://www.codingame.com/ide/puzzle/don't-panic-episode-2
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class NodeType(Enum):
    EXIT = '@'
    ELEVATOR = '^'
    MAYBE_ELEVATOR = '?'
    BLOCK = '#'
    USED = 'x'


def get_graph(exit_coord, elevators):
    limit_left = max((pos for pos in elevators[exit_coord[0]] if pos < exit_coord[1]), default=-1)
    limit_right = min((pos for pos in elevators[exit_coord[0]] if pos > exit_coord[1]), default=999999)

    graph = [{exit_coord[1]: NodeType.EXIT}]
    for floor in reversed(range(exit_coord[0])):
        new_floor = {}
        for pos in graph[-1]:
            new_floor[pos] = NodeType.MAYBE_ELEVATOR
        for pos in elevators[floor]:
            if limit_left < pos < limit_right:
                new_floor[pos] = NodeType.ELEVATOR
        graph.append(new_floor)
        limit_left = max((pos for pos in elevators[floor] if pos <= limit_left), default=-1)
        limit_right = min((pos for pos in elevators[floor] if pos >= limit_right), default=999999)

    return graph[::-1]


def show_graph(graph, width):
    for floor in reversed(graph):
        print(''.join(floor[pos].value if pos in floor else '.' for pos in range(width)), file=sys.stderr)


class Direction(Enum):
    LEFT = "LEFT"
    RIGHT = "RIGHT"


@dataclass(frozen=True, order=True)
class Cost:
    nb_turns: int
    players: int
    ladders: int

    def __add__(self, other: Cost):
        return Cost(self.nb_turns + other.nb_turns, self.players + other.players, self.ladders + other.ladders)


@dataclass(frozen=True, order=True)
class Cell:
    cost: Cost
    floor: int
    pos: int
    direction: Direction = field(compare=False)
    origin: Optional[Cell] = field(compare=False, default=None)

    def move(self, cost, pos, direction):
        return Cell(self.cost + cost, self.floor + 1, pos, direction, self)


def get_path(start, graph, ladders, players, nb_turns):

    floor, pos, direction = start
    current_cells = {Cell(Cost(0, 0, 0), floor, pos, direction)}

    for floor in range(len(graph)):
        current_cells_ = set()
        for origin in current_cells:
            node_type = graph[origin.floor].get(origin.pos, None)
            if node_type is NodeType.EXIT:
                return origin

            limit_left = max((pos for pos, node_type in graph[origin.floor].items() if pos <= origin.pos and node_type is NodeType.ELEVATOR), default=-1)
            limit_right = min((pos for pos, node_type in graph[origin.floor].items() if pos >= origin.pos and node_type is NodeType.ELEVATOR), default=999999)
            for pos, node_type in graph[origin.floor].items():
                if limit_left <= pos <= limit_right:
                    cost_player, cost_ladder = 0, 0
                    block = (pos > origin.pos and origin.direction is Direction.LEFT) or (pos < origin.pos and origin.direction is Direction.RIGHT)
                    if block:
                        if origin.cost.players < players - 1:
                            cost_player += 1
                        else:
                            continue
                    if node_type is not NodeType.ELEVATOR:
                        if origin.cost.ladders < ladders:
                            cost_ladder += 1
                            cost_player += 1
                        else:
                            continue

                    cost_nb_turns = 1 + 3*cost_player + abs(pos - origin.pos)
                    if origin.cost.nb_turns + cost_nb_turns >= nb_turns:
                        continue

                    if pos < origin.pos:
                        direction = Direction.LEFT
                    elif pos > origin.pos:
                        direction = Direction.RIGHT
                    else:
                        direction = origin.direction

                    current_cells_.add(origin.move(Cost(cost_nb_turns, cost_player, cost_ladder), pos, direction))
        current_cells = current_cells_


def apply_path(graph, path):
    while path and path.origin:
        graph[path.floor-1][path.pos] = NodeType.ELEVATOR if graph[path.floor-1].get(path.pos) is NodeType.MAYBE_ELEVATOR else NodeType.USED
        if path.direction != path.origin.direction:
            graph[path.origin.floor][path.origin.pos] = NodeType.BLOCK
        path = path.origin


def main():
    nb_floors, width, nb_rounds, exit_floor, exit_pos, nb_total_clones, nb_addtional_elevators, nb_elevators = map(int, input().split())

    elevators = [set() for _ in range(nb_floors)]
    for _ in range(nb_elevators):
        floor, pos = map(int, input().split())
        elevators[floor].add(pos)

    graph = get_graph((exit_floor, exit_pos), elevators)
    show_graph(graph, width)

    path = None
    while True:
        clone_floor, clone_pos, clone_direction = input().split()
        if clone_direction == 'NONE':
            print('WAIT')
            continue
        clone_floor, clone_pos, clone_direction = int(clone_floor), int(clone_pos), Direction(clone_direction)

        if not path:
            path = get_path((clone_floor, clone_pos, clone_direction), graph, nb_addtional_elevators, nb_total_clones, nb_rounds)
            print(path, file=sys.stderr)
            apply_path(graph, path)
            show_graph(graph, width)

        if graph[clone_floor].get(clone_pos) is NodeType.BLOCK:
            print('BLOCK')
        elif graph[clone_floor].get(clone_pos) is NodeType.ELEVATOR:
            print('ELEVATOR')
        else:
            print('WAIT')
        graph[clone_floor][clone_pos] = NodeType.USED


if __name__ == "__main__":
    main()

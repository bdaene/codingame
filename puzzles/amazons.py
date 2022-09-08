# See https://www.codingame.com/ide/puzzle/amazons
import sys
from enum import Enum
from random import choice
from time import perf_counter

from typing import NamedTuple, Iterable, Optional


def debug(*msg):
    print(*msg, file=sys.stderr, flush=True)


class Color(str, Enum):
    WHITE = "w"
    BLACK = "b"

    @property
    def opposite(self):
        return {Color.WHITE: Color.BLACK, Color.BLACK: Color.WHITE}.get(self)


class Position(NamedTuple):
    row: int
    col: int

    def __str__(self):
        return f"{'abcdefgh'[self.col]}{8 - self.row}"

    def __add__(self, other):
        return Position(self.row + other.row, self.col + other.col)

    @classmethod
    def all_directions(cls):
        return (Position(1, 0), Position(1, 1), Position(0, 1), Position(-1, 1),
                Position(-1, 0), Position(-1, -1), Position(0, -1), Position(1, -1))


class Action(NamedTuple):
    start: Position
    end: Position
    wall: Position
    msg: Optional[str] = None

    def __str__(self):
        return f"{self.start} {self.end} {self.wall} msg {self.msg}"


class Board(NamedTuple):
    grid: list[list[str]]

    @classmethod
    def from_strings(cls, lines: Iterable[str]) -> 'Board':
        return Board(list(list(line) for line in lines))

    def __str__(self):
        return '\n'.join(''.join(line) for line in self.grid)

    def get_available_cells(self, position: Position):
        for direction in Position.all_directions():
            current_position = position
            while True:
                current_position += direction
                if (0 <= current_position.row < len(self.grid)
                        and 0 <= current_position.col < len(self.grid[current_position.row])
                        and self.grid[current_position.row][current_position.col] == '.'):
                    yield current_position
                else:
                    break

    def get_move(self, color: Color):
        my_positions = {Position(row, col)
                        for row, line in enumerate(self.grid) for col, cell in enumerate(line)
                        if cell == color}
        opponent_positions = {Position(row, col)
                              for row, line in enumerate(self.grid) for col, cell in enumerate(line)
                              if cell == color.opposite}

        scores = {}
        end_time = perf_counter() + 0.09
        for position in my_positions:
            if perf_counter() > end_time:
                break
            my_positions.remove(position)
            self.grid[position.row][position.col] = '.'
            for new_position in self.get_available_cells(position):
                if perf_counter() > end_time:
                    break
                self.grid[new_position.row][new_position.col] = color.value
                my_positions.add(new_position)
                for wall_position in self.get_available_cells(new_position):
                    if perf_counter() > end_time:
                        break
                    self.grid[wall_position.row][wall_position.col] = '-'
                    score = (sum(len(list(self.get_available_cells(p))) for p in my_positions)
                             - sum(len(list(self.get_available_cells(p))) for p in opponent_positions))
                    scores[Action(position, new_position, wall_position, str(score))] = score
                    self.grid[wall_position.row][wall_position.col] = '.'
                my_positions.remove(new_position)
                self.grid[new_position.row][new_position.col] = '.'
            self.grid[position.row][position.col] = color.value
            my_positions.add(position)

        best_score = max(scores.values())
        best_actions = [action for action, score in scores.items() if score == best_score]
        return choice(best_actions)


def main():
    board_size = int(input())

    while True:
        color = Color(input())
        board = Board.from_strings(input() for _ in range(board_size))
        last_action = input()
        actions_count = int(input())
        debug(last_action, actions_count)

        print(board.get_move(color))


if __name__ == "__main__":
    main()

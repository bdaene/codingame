
import sys
from time import perf_counter_ns

from action import Action
from board import Board, Cell
from game_state import Player, Tree, GameState
from simulation import Simulation


def read_cells(board):
    number_of_cells = int(input())
    for _ in range(number_of_cells):
        cell = Cell.from_string(input())
        board.cells[cell.index] = cell
        board.update_cells_at_dist()


def read_game_state():
    day = int(input())
    nutrients = int(input())
    player = Player.from_string(input())
    opponent = Player.from_string(input())

    number_of_trees = int(input())
    trees = tuple(Tree.from_string(input()) for _ in range(number_of_trees))

    game_state = GameState(day, nutrients, trees, (player, opponent))

    number_of_possible_actions = int(input())
    possible_actions = frozenset(Action.from_string(input()) for _ in range(number_of_possible_actions))
    # print(game_state.get_possible_actions(board), file=sys.stderr)
    # print(possible_actions, file=sys.stderr)
    # assert possible_actions == game_state.get_possible_actions(board)[player]

    return game_state


def main(load_cells=True):
    # Initialize board
    board = Board(3)
    if load_cells:
        read_cells(board)

    simulation = Simulation(board)

    first_turn = True
    prev_day = 0
    timeout_margin = 1E6
    while True:
        game_state = read_game_state()

        allowed_time = (1000E6 if first_turn else 100E6)
        allowed_time = 10**12
        start_time = perf_counter_ns()
        best_action, nb_simulations = simulation.explore(game_state, start_time + allowed_time - timeout_margin)
        print(best_action, flush=True)

        elapsed_time = perf_counter_ns() - start_time
        print(f'Done {nb_simulations} simulations in {elapsed_time / 1E6:.3f} ms.', file=sys.stderr)
        timeout_margin = max(timeout_margin*0.7, (elapsed_time - allowed_time) * (nb_simulations + 2) / nb_simulations)
        print(f"Timeout margin = {timeout_margin/ 1E6:.3f} ms", file=sys.stderr)

        first_turn = False
        if game_state.day != prev_day:
            prev_day = game_state.day
            timeout_margin *= 2


if __name__ == "__main__":
    main()

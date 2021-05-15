import math
import random
import sys
from collections import Counter
from dataclasses import dataclass, field
from enum import IntEnum
from time import perf_counter_ns
import gc

gc.disable()


@dataclass(frozen=True)
class CubeCoord:
    x: int
    y: int
    z: int

    def __add__(self, other):
        return CubeCoord(self.x + other.x, self.y + other.y, self.z + other.z)

    def __mul__(self, factor):
        return CubeCoord(self.x * factor, self.y * factor, self.z * factor)

    def distance(self, other):
        return (abs(self.x - other.x) + abs(self.y - other.y) + abs(self.z - other.z)) // 2


DIRECTIONS = (CubeCoord(+1, -1, 0), CubeCoord(+1, 0, -1), CubeCoord(0, +1, -1),
              CubeCoord(-1, +1, 0), CubeCoord(-1, 0, +1), CubeCoord(0, -1, +1))


@dataclass(frozen=True)
class Cell:
    index: int
    richness: int

    def __str__(self):
        return f'{self.index}'

    @staticmethod
    def from_string(string):
        cell_index, richness, *neighbors = map(int, string.split())
        return Cell(cell_index, richness)


@dataclass
class Board:
    coordinates_to_index: dict = field(default_factory=dict)
    index_to_coordinates: dict = field(default_factory=dict)
    cells: list = field(default_factory=list)
    cells_at_dist: dict = field(default_factory=dict)

    @staticmethod
    def get_board(size):

        board = Board()

        index = 0
        coord = CubeCoord(0, 0, 0)
        board.coordinates_to_index[coord] = index
        board.index_to_coordinates[index] = coord

        index += 1
        coord += DIRECTIONS[0]

        for dist in range(1, size + 1):
            for orientation, direction in enumerate(DIRECTIONS):
                for count in range(dist):
                    board.coordinates_to_index[coord] = index
                    board.index_to_coordinates[index] = coord

                    index += 1
                    coord += DIRECTIONS[(orientation + 2) % 6]

            coord += DIRECTIONS[0]

        board.cells = [None] * (1 + 3 * size * (size + 1))

        return board

    def update_cells_at_dist(self):
        self.cells_at_dist = {(origin, dist): set() for origin in self.index_to_coordinates for dist in range(4)}
        for target in self.cells:
            if target.richness > 0:
                target_coord = self.index_to_coordinates[target.index]
                for origin in self.cells:
                    origin_coord = self.index_to_coordinates[origin.index]
                    dist = origin_coord.distance(target_coord)
                    if dist <= 3:
                        self.cells_at_dist[(origin.index, dist)].add(target.index)


@dataclass(frozen=True)
class Player:
    is_player: bool
    sun: int
    score: int
    is_waiting: bool

    @staticmethod
    def from_string(string, is_player):
        sun, score, *waiting = map(int, string.split())
        waiting = len(waiting) > 0 and (waiting[0] == 1)
        return Player(is_player, sun, score, waiting)

    def get_score(self):
        return self.score + self.sun // 3


@dataclass(frozen=True)
class Tree:
    cell_index: int
    size: int
    is_mine: bool
    is_dormant: bool

    @staticmethod
    def from_string(string):
        cell_index, size, is_mine, is_dormant = map(int, string.split())
        return Tree(cell_index, size, is_mine == 1, is_dormant == 1)


class ActionType(IntEnum):
    WAIT = 0
    COMPLETE = 1
    SEED = 2
    GROW = 3


@dataclass(frozen=True)
class Action:
    type: ActionType
    target: int = 0
    origin: int = 0

    def __str__(self):
        if self.type is ActionType.WAIT:
            return 'WAIT Zzz'
        elif self.type is ActionType.SEED:
            return f'SEED {self.origin} {self.target}'
        else:
            return f'{self.type.name} {self.target}'

    @staticmethod
    def from_string(string):
        split = string.split(' ')
        if split[0] == ActionType.WAIT.name:
            return Action(ActionType.WAIT)
        if split[0] == ActionType.SEED.name:
            return Action(ActionType.SEED, int(split[2]), int(split[1]))
        if split[0] == ActionType.GROW.name:
            return Action(ActionType.GROW, int(split[1]))
        if split[0] == ActionType.COMPLETE.name:
            return Action(ActionType.COMPLETE, int(split[1]))

    def __lt__(self, other):
        return (self.type, -self.target, self.origin) < (other.type, -other.target, other.origin)


GROW_COST = [1, 3, 7, 4]
MAX_TREE_SIZE = 3


@dataclass(frozen=True)
class GameState:
    day: int
    nutrients: int
    trees: frozenset
    player: Player
    opponent: Player

    index_to_tree: dict = field(repr=False, default_factory=dict, compare=False)
    tree_count: Counter = field(repr=False, default_factory=Counter, compare=False)

    def __post_init__(self):
        for tree in self.trees:
            self.index_to_tree[tree.cell_index] = tree
            self.tree_count[(tree.is_mine, tree.size)] = self.tree_count.get((tree.is_mine, tree.size), 0) + 1

    def get_possible_actions(self, board):
        possible_actions = {
            self.player: {Action(ActionType.WAIT)},
            self.opponent: {Action(ActionType.WAIT)}
        }

        occupied_cells = self.index_to_tree.keys()

        for tree in self.trees:
            player = self.player if tree.is_mine else self.opponent
            if tree.is_dormant or player.is_waiting:
                continue
            grow_cost = GROW_COST[tree.size] + self.tree_count[(tree.is_mine, tree.size + 1)]
            if tree.size < MAX_TREE_SIZE and player.sun >= grow_cost:
                possible_actions[player].add(Action(ActionType.GROW, tree.cell_index))
            if tree.size == MAX_TREE_SIZE and player.sun >= GROW_COST[tree.size]:
                possible_actions[player].add(Action(ActionType.COMPLETE, tree.cell_index))

            if player.sun >= self.tree_count[(tree.is_mine, 0)]:
                for seed_index in board.cells_at_dist[(tree.cell_index, tree.size)] - occupied_cells:
                    possible_actions[player].add(Action(ActionType.SEED, seed_index, tree.cell_index))

        return possible_actions

    def get_next_state(self, player_action: Action, opponent_action: Action, board):
        day = self.day
        nutrients = self.nutrients
        trees = self.trees
        player = self.player
        opponent = self.opponent
        nb_completed = 0

        if (player_action.type == ActionType.SEED and opponent_action.type == ActionType.SEED
                and player_action.target == opponent_action.target):
            # Both seed at the same place. Put origin trees to dormant.
            origin_trees = set(self.index_to_tree[index] for index in (player_action.origin, opponent_action.origin))
            trees -= origin_trees
            trees |= {Tree(tree.cell_index, tree.size, tree.is_mine, True) for tree in origin_trees}
            return GameState(day, nutrients, trees, player, opponent)

        # Player
        if player_action.type == ActionType.GROW:
            tree = self.index_to_tree[player_action.target]
            trees -= {tree}
            trees |= {Tree(tree.cell_index, tree.size + 1, tree.is_mine, True)}
            cost = GROW_COST[tree.size] + self.tree_count[(tree.is_mine, tree.size + 1)]
            player = Player(player.is_player, player.sun - cost, player.score, player.is_waiting)
        elif player_action.type == ActionType.SEED:
            tree = self.index_to_tree[player_action.origin]
            trees -= {tree}
            trees |= {Tree(tree.cell_index, tree.size, tree.is_mine, True), Tree(player_action.target, 0, True, True)}
            cost = self.tree_count[(True, 0)]
            player = Player(player.is_player, player.sun - cost, player.score, player.is_waiting)
        elif player_action.type == ActionType.COMPLETE:
            tree = self.index_to_tree[player_action.target]
            trees -= {tree}
            nb_completed += 1
            score = nutrients + board.cells[tree.cell_index].richness
            player = Player(player.is_player, player.sun - 4, player.score + score, player.is_waiting)
        elif player_action.type == ActionType.WAIT:
            player = Player(player.is_player, player.sun, player.score, True)

        # Opponent
        if opponent_action.type == ActionType.GROW:
            tree = self.index_to_tree[opponent_action.target]
            trees -= {tree}
            trees |= {Tree(tree.cell_index, tree.size + 1, tree.is_mine, True)}
            cost = GROW_COST[tree.size] + self.tree_count[(tree.is_mine, tree.size + 1)]
            opponent = Player(opponent.is_player, opponent.sun - cost, opponent.score, opponent.is_waiting)
        elif opponent_action.type == ActionType.SEED:
            tree = self.index_to_tree[opponent_action.origin]
            trees -= {tree}
            trees |= {Tree(tree.cell_index, tree.size, tree.is_mine, True), Tree(opponent_action.target, 0, True, True)}
            cost = self.tree_count[(False, 0)]
            opponent = Player(opponent.is_player, opponent.sun - cost, opponent.score, opponent.is_waiting)
        elif opponent_action.type == ActionType.COMPLETE:
            tree = self.index_to_tree[opponent_action.target]
            trees -= {tree}
            nb_completed += 1
            score = nutrients + board.cells[tree.cell_index].richness
            opponent = Player(opponent.is_player, opponent.sun - 4, opponent.score + score, opponent.is_waiting)
        elif opponent_action.type == ActionType.WAIT:
            opponent = Player(opponent.is_player, opponent.sun, opponent.score, True)

        nutrients -= nb_completed

        # New day
        if player.is_waiting and opponent.is_waiting:
            day += 1

            if day < 24:
                # Calculate shadows
                shadows = {index: 0 for index in board.index_to_coordinates}
                direction = DIRECTIONS[day % 6]
                for tree in trees:
                    coord = board.index_to_coordinates[tree.cell_index]
                    for distance in range(1, tree.size + 1):
                        coord += direction
                        if coord not in board.coordinates_to_index:
                            break
                        shadows[board.coordinates_to_index[coord]] = max(tree.size,
                                                                         shadows[board.coordinates_to_index[coord]])

                # Reset trees
                trees = frozenset(Tree(tree.cell_index, tree.size, tree.is_mine, False) for tree in trees)

                # Gain sun and wake up players
                sun = sum(tree.size for tree in trees if tree.is_mine and tree.size > shadows[tree.cell_index])
                player = Player(player.is_player, player.sun + sun, player.score, False)
                sun = sum(tree.size for tree in trees if not tree.is_mine and tree.size > shadows[tree.cell_index])
                opponent = Player(opponent.is_player, opponent.sun + sun, opponent.score, False)

        return GameState(day, nutrients, trees, player, opponent)

    def get_score(self, board):
        if self.day >= 24:
            return self.player.get_score() - self.opponent.get_score()

        player_production = 0
        opponent_production = 0
        player_tall_trees = []
        opponent_tall_trees = []
        for tree in self.trees:
            if tree.is_mine:
                player_production += tree.size
                if tree.size == 3:
                    player_tall_trees.append(tree)
            else:
                opponent_production += tree.size
                if tree.size == 3:
                    opponent_tall_trees.append(tree)

        nb_day_left = 23 - self.day
        player_sun = self.player.sun + player_production * nb_day_left // 2
        opponent_sun = self.opponent.sun + opponent_production * nb_day_left // 2
        player_tall_trees = sorted(
            (self.nutrients + board.cells[tree.cell_index].richness, -tree.cell_index, tree) for tree in
            player_tall_trees)
        opponent_tall_trees = sorted(
            (self.nutrients + board.cells[tree.cell_index].richness, -tree.cell_index, tree) for tree in
            opponent_tall_trees)

        player_score = self.player.score
        opponent_score = self.opponent.score

        while player_sun >= 4 and player_tall_trees:
            player_sun -= 4
            player_score += player_tall_trees.pop()[0]

        while opponent_sun >= 4 and opponent_tall_trees:
            opponent_sun -= 4
            opponent_score += opponent_tall_trees.pop()[0]

        return player_score + player_sun // 3 - opponent_score - opponent_sun // 3


@dataclass
class SimulationNode:
    player_action_to_explore: list
    opponent_action_to_explore: list

    total_visits: int = 0
    player_explored_actions: dict = field(default_factory=dict)
    opponent_explored_actions: dict = field(default_factory=dict)

    def __init__(self, game_state, board):
        possible_actions = game_state.get_possible_actions(board)

        def get_value(action):
            richness = board.cells[action.target].richness
            action_type = action.type
            if game_state.day >= 12 and action.type == ActionType.COMPLETE:
                action_type += 1
            if action.type == ActionType.WAIT:
                cost = 0
            elif action.type == ActionType.COMPLETE:
                cost = 4
            elif action.type == ActionType.SEED:
                cost = game_state.tree_count[(player.is_player, 0)]
            else:
                tree = game_state.index_to_tree[action.target]
                cost = GROW_COST[tree.size] + game_state.tree_count[(player.is_player, tree.size + 1)]

            rand = random.randint(0, 65535)
            return richness, action_type, -cost, rand

        player = game_state.player
        self.player_action_to_explore = sorted(possible_actions[game_state.player], key=get_value)
        player = game_state.opponent
        self.opponent_action_to_explore = sorted(possible_actions[game_state.opponent], key=get_value)
        # random.shuffle(self.player_action_to_explore)
        # random.shuffle(self.opponent_action_to_explore)
        self.player_explored_actions = {}
        self.opponent_explored_actions = {}

    def get_actions(self, exploration_factor):
        if self.player_action_to_explore:
            player_action = self.player_action_to_explore.pop()
        else:
            t = self.total_visits
            player_action = max((w / n + exploration_factor * (math.log(t) / n) ** .5, action) for action, (w, n) in
                                self.player_explored_actions.items())[1]

        if self.opponent_action_to_explore:
            opponent_action = self.opponent_action_to_explore.pop()
        else:
            t = self.total_visits
            opponent_action = max((w / n + exploration_factor * (math.log(t) / n) ** .5, action) for action, (w, n) in
                                  self.opponent_explored_actions.items())[1]

        return player_action, opponent_action

    def get_best_action(self):
        if len(self.player_explored_actions) == 0:
            return self.player_explored_actions[-1]

        return max((w / n, action) for action, (w, n) in
                   self.player_explored_actions.items())[1]

    def update(self, player_action, opponent_action, result):
        self.total_visits += 1
        w, n = self.player_explored_actions.get(player_action, (0, 0))
        self.player_explored_actions[player_action] = (w + result, n + 1)
        w, n = self.opponent_explored_actions.get(opponent_action, (0, 0))
        self.opponent_explored_actions[opponent_action] = (w - result, n + 1)


@dataclass
class Simulation:
    board: Board

    nodes: dict = field(default_factory=dict)

    def explore(self, game_state, stop_time, max_depth):
        nb_simulations = 0
        while perf_counter_ns() < stop_time:
            path = []
            current_game_state = game_state
            while current_game_state.day < 24 and current_game_state.day < game_state.day + max_depth:
                if perf_counter_ns() >= stop_time:
                    break

                if current_game_state not in self.nodes:
                    node = SimulationNode(current_game_state, self.board)
                    self.nodes[current_game_state] = node
                else:
                    node = self.nodes[current_game_state]

                player_action, opponent_action = node.get_actions(7.45)
                path.append((node, player_action, opponent_action))
                current_game_state = current_game_state.get_next_state(player_action, opponent_action, self.board)

            result = current_game_state.get_score(self.board)
            for node, player_action, opponent_action in path:
                node.update(player_action, opponent_action, result)
            nb_simulations += 1

        return nb_simulations

    def get_best_action(self, game_state):
        node = self.nodes[game_state]
        # print(f"Total visits: {node.total_visits}", file=sys.stderr)
        # print("Player actions:", file=sys.stderr)
        # print(f"{node.player_action_to_explore}", file=sys.stderr)
        # print('\n'.join(f"{action} : {(w, n, w/n)}" for action, (w, n) in node.player_explored_actions.items()), file=sys.stderr)
        # print("Opponent actions:", file=sys.stderr)
        # print(f"{node.opponent_action_to_explore}", file=sys.stderr)
        # print('\n'.join(f"{action} : {(w, n, w / n)}" for action, (w, n) in node.opponent_explored_actions.items()), file=sys.stderr)
        return node.get_best_action()

    def clear(self, day):
        self.nodes = {game_state: node for game_state, node in self.nodes.items() if game_state.day >= day}


def main():
    # Initialize board
    board = Board.get_board(3)
    number_of_cells = int(input())
    # assert len(board.index_to_coordinates) == number_of_cells
    for _ in range(number_of_cells):
        cell = Cell.from_string(input())
        board.cells[cell.index] = cell
        # for neighbor in neighbors:
        #     assert neighbor < 0 or cell.coordinate.distance(board.index_to_coordinates[neighbor]) == 1
    board.update_cells_at_dist()

    simulation = Simulation(board)

    first_turn = True
    last_day = 0
    timeout_margin = 1E6
    while True:
        day = int(input())
        nutrients = int(input())
        player = Player.from_string(input(), True)
        opponent = Player.from_string(input(), False)

        number_of_trees = int(input())
        trees = frozenset(Tree.from_string(input()) for _ in range(number_of_trees))

        game_state = GameState(day, nutrients, trees, player, opponent)

        number_of_possible_actions = int(input())
        possible_actions = frozenset(Action.from_string(input()) for _ in range(number_of_possible_actions))
        # print(game_state.get_possible_actions(board), file=sys.stderr)
        # print(possible_actions, file=sys.stderr)
        # assert possible_actions == game_state.get_possible_actions(board)[player]

        allowed_time = (1000E6 if first_turn else 100E6)
        max_depth = 6 if first_turn else 3
        start_time = perf_counter_ns()
        nb_simulations = simulation.explore(game_state, start_time + allowed_time - timeout_margin, max_depth)

        best_action = simulation.get_best_action(game_state)
        print(best_action, flush=True)

        elapsed_time = perf_counter_ns() - start_time
        print(f'Done {nb_simulations} simulations in {elapsed_time / 1E6:.3f} ms.', file=sys.stderr)
        timeout_margin = max(timeout_margin*0.7, (elapsed_time - allowed_time) * (nb_simulations + 2) / nb_simulations)
        print(f"Timeout margin = {timeout_margin/ 1E6:.3f} ms", file=sys.stderr)

        first_turn = False
        if day > last_day:
            last_day = day
            timeout_margin *= 2
            # simulation.clear(day)


if __name__ == "__main__":
    main()

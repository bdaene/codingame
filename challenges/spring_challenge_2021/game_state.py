
from collections import Counter
from dataclasses import dataclass

from action import Action, ActionType
from board import Board, DIRECTIONS


@dataclass
class Player:
    sun: int
    score: int
    is_waiting: bool

    def get_copy(self):
        return Player(self.sun, self.score, self.is_waiting)

    @staticmethod
    def from_string(string):
        sun, score, *waiting = map(int, string.split())
        waiting = len(waiting) > 0 and (waiting[0] == 1)
        return Player(sun, score, waiting)

    def get_score(self):
        return self.score + self.sun // 3


@dataclass
class Tree:
    cell_index: int
    size: int
    player: int
    is_dormant: bool

    def get_copy(self):
        return Tree(self.cell_index, self.size, self.player, self.is_dormant)

    @staticmethod
    def from_string(string):
        cell_index, size, is_mine, is_dormant = map(int, string.split())
        return Tree(cell_index, size, 0 if is_mine == 1 else 1, is_dormant == 1)


GROW_COST = [1, 3, 7]
MAX_TREE_SIZE = 3
MAX_DAY = 24


class GameState:

    def __init__(self, day: int, nutrients: int, trees: tuple[Tree, ...], players: tuple[Player, ...]):
        self.day = day
        self.nutrients = nutrients
        self.players = players
        self.index_to_tree = {tree.cell_index: tree for tree in trees}
        self.tree_count = (Counter(), Counter())
        for tree in trees:
            self.tree_count[tree.player][tree.size] += 1

    def get_copy(self):
        return GameState(
            self.day,
            self.nutrients,
            tuple(self.index_to_tree.values()),
            tuple(player.get_copy() for player in self.players)
        )

    def get_key(self):
        return hash((self.day,
                     self.nutrients,
                     sorted(self.index_to_tree.values(),
                            key=lambda tree: (tree.cell_index, tree.size, tree.player)),
                     tuple((player.sun, player.score, player.is_waiting) for player in self.players)
                     ))

    def get_possible_actions(self, board: Board) -> tuple[list[Action], ...]:
        possible_actions = tuple([Action(ActionType.WAIT)] for _ in self.players)

        occupied_cells = self.index_to_tree.keys()

        for tree in self.index_to_tree.values():
            player = self.players[tree.player]
            actions = possible_actions[tree.player]
            if tree.is_dormant or player.is_waiting:
                continue
            if tree.size < MAX_TREE_SIZE:
                if player.sun >= GROW_COST[tree.size] + self.tree_count[tree.player][tree.size + 1]:
                    actions.append(Action(ActionType.GROW, tree.cell_index))
            elif tree.size == MAX_TREE_SIZE:
                if player.sun >= 4:
                    actions.append(Action(ActionType.COMPLETE, tree.cell_index))
            if player.sun >= self.tree_count[tree.player][0]:
                for seed_index in board.cells_at_dist[(tree.cell_index, tree.size)] - occupied_cells:
                    actions.append(Action(ActionType.SEED, tree.cell_index, seed_index))

        return possible_actions

    def update(self, actions: tuple[Action, ...], board: Board):
        if all(action.type == ActionType.SEED and action.seed_index == actions[0].seed_index for action in actions):
            # Both seed at the same place. Put origin trees to dormant.
            for action in actions:
                self.index_to_tree[action.tree_index].is_dormant = True

        nb_completed = 0
        for player, action, is_mine in zip(self.players, actions, (True, False)):
            if action.type == ActionType.WAIT:
                player.is_waiting = True
                continue

            tree = self.index_to_tree[action.tree_index]
            tree_count = self.tree_count[is_mine]
            if action.type == ActionType.GROW:
                player.sun -= GROW_COST[tree.size] + tree_count[tree.size + 1]
                tree_count[tree.size] -= 1
                tree.size += 1
                tree_count[tree.size] += 1
                tree.is_dormant = True
            elif action.type == ActionType.SEED:
                player.sun -= tree_count[0]
                tree.is_dormant = True
                seed = Tree(action.seed_index, 0, is_mine, True)
                tree_count[0] += 1
                self.index_to_tree[seed.cell_index] = seed
            elif action.type == ActionType.COMPLETE:
                player.sun -= 4
                player.score += self.nutrients + board.cells[action.tree_index].richness
                tree_count[tree.size] -= 1
                del self.index_to_tree[tree.cell_index]
                nb_completed += 1

        self.nutrients -= nb_completed

        # New day
        if all(player.is_waiting for player in self.players):
            self.day += 1

            if self.day < 24:
                # Calculate shadows
                shadows = {index: 0 for index in board.index_to_coordinates}
                direction = DIRECTIONS[self.day % 6]
                for tree in self.index_to_tree.values():
                    coord = board.index_to_coordinates[tree.cell_index]
                    for distance in range(1, tree.size + 1):
                        coord += direction
                        if coord not in board.coordinates_to_index:
                            break
                        index = board.coordinates_to_index[coord]
                        shadows[index] = max(shadows[index], tree.size)

                # Gain sun and reset trees
                for tree in self.index_to_tree.values():
                    tree.is_dormant = False
                    if tree.size > shadows[tree.cell_index]:
                        self.players[tree.player].sun += tree.size

                # Wake up players
                for player in self.players:
                    player.is_waiting = False


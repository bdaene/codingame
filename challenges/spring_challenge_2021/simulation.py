import math
import random
from dataclasses import dataclass
from time import perf_counter_ns

from action import Action, ActionType
from board import Board
from game_state import GameState, MAX_DAY


class SimulationNode:
    def __init__(self, player_actions: list[Action], opponent_actions: list[Action]):
        self.total_visits = 1
        self.player_actions = {action: [0, 0.0001] for action in player_actions}
        self.opponent_actions = {action: [0, 0.0001] for action in opponent_actions}
        self.children = {}

    def update(self, player_action, opponent_action, result):
        self.total_visits += 1
        player_action_value = self.player_actions[player_action]
        player_action_value[0] += result
        player_action_value[1] += 1
        opponent_action_value = self.opponent_actions[opponent_action]
        opponent_action_value[0] -= result
        opponent_action_value[1] += 1

    def get_actions(self, exploration_factor):
        t = self.total_visits
        player_action = max((w / n + exploration_factor * (math.log(t) / n) ** .5, action)
                            for action, (w, n) in self.player_actions.items())[1]
        opponent_action = max((w / n + exploration_factor * (math.log(t) / n) ** .5, action)
                              for action, (w, n) in self.opponent_actions.items())[1]
        return player_action, opponent_action

    def get_best_action(self):
        return max(((w / n), action) for action, (w, n) in self.player_actions.items())[1]


@dataclass
class Simulation:
    board: Board

    def explore(self, game_state: GameState, stop_time):
        nb_simulations = 0
        root_node = SimulationNode(*game_state.get_possible_actions(self.board))
        root_game_state = game_state

        try:
            while True:
                assert perf_counter_ns() < stop_time
                path = []
                game_state = root_game_state.get_copy()
                node = root_node

                # Reach a leaf node
                while game_state.day < MAX_DAY:
                    assert perf_counter_ns() < stop_time
                    actions = node.get_actions(7.45)
                    path.append((node, actions))
                    if actions in node.children:
                        node = node.children[actions]
                        game_state.update(actions, self.board)
                    else:
                        node.children[actions] = SimulationNode(*game_state.get_possible_actions(self.board))
                        break

                # Simulate the leaf node
                player_actions, opponent_actions = game_state.get_possible_actions(self.board)
                while game_state.day < MAX_DAY:
                    assert perf_counter_ns() < stop_time
                    player_action = random.choice(player_actions)
                    opponent_action = random.choice(opponent_actions)
                    game_state.update((player_action, opponent_action), self.board)

                    if player_action.tree_index >= 0:
                        player_actions = [action for action in player_actions if action.tree_index != player_action.tree_index]
                    if opponent_action.tree_index >= 0:
                        opponent_actions = [action for action in opponent_actions if action.tree_index != opponent_action.tree_index]
                    if player_action.seed_index != opponent_action.seed_index:
                        if player_action.seed_index >= 0:
                            player_actions = [action for action in player_actions if action.seed_index != player_action.seed_index]
                        if opponent_action.seed_index >= 0:
                            opponent_actions = [action for action in opponent_actions if action.seed_index != opponent_action.seed_index]

                    if player_action.type == opponent_action.type == ActionType.WAIT:
                        # New day
                        player_actions, opponent_actions = game_state.get_possible_actions(self.board)

                player, opponent = game_state.players
                result = player.get_score() - opponent.get_score()
                for node, actions in path:
                    node.update(*actions, result)
                nb_simulations += 1

        except AssertionError:
            return root_node.get_best_action(), nb_simulations

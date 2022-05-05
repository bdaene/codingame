# See https://www.codingame.com/ide/puzzle/brain-fork

from __future__ import annotations
import sys
from dataclasses import dataclass
from string import ascii_uppercase
from collections import deque

ALPHABET = ' ' + ascii_uppercase
LETTERS = len(ALPHABET)
STONES = 30


def debug(*args):
    print(*args, file=sys.stderr, flush=True)


@dataclass(frozen=True)
class State:
    instructions: str = ''
    stones: tuple[int, ...] = (0,) * STONES
    spelled_phrase: tuple[int, ...] = ()
    previous_state: State = None

    def do_actions(self, actions: str):
        stones = deque(self.stones)
        letters = ()

        for action in actions:
            if action == '>':
                stones.rotate(-1)
            elif action == '<':
                stones.rotate(1)
            elif action == '+':
                stones[0] = (stones[0] + 1) % LETTERS
            elif action == '-':
                stones[0] = (stones[0] - 1) % LETTERS
            elif action == '.':
                letters += (stones[0],)
            else:
                raise ValueError(f"Invalid action {action}")

        return State(self.instructions + actions, tuple(stones), self.spelled_phrase + letters, self)

    def cost(self):
        return len(self.instructions)

    def gen_actions(self, letter: int):
        for i, stone in enumerate(self.stones):
            actions = ''
            if i < STONES - i:
                actions += '>' * i
            else:
                actions += '<' * (STONES - i)
            j = (letter - stone) % LETTERS
            if j < LETTERS - j:
                actions += '+' * j
            else:
                actions += '-' * (LETTERS - j)
            actions += '.'
            yield actions


STATES = 1


def main():
    magic_phrase = input()
    states = [State()]
    for letter in magic_phrase:
        letter = ALPHABET.index(letter)
        new_states = set()
        for state in states:
            for actions in state.gen_actions(letter):
                new_states.add(state.do_actions(actions))
        states = sorted(new_states, key=State.cost)[:STATES]

    best_state = min(states, key=State.cost)
    print(best_state.instructions)
    debug(best_state.cost())


if __name__ == "__main__":
    main()

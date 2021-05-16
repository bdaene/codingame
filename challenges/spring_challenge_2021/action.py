import random
from dataclasses import dataclass
from enum import Enum


class ActionType(Enum):
    GROW = "GROW"
    SEED = "SEED"
    COMPLETE = "COMPLETE"
    WAIT = "WAIT"


@dataclass(frozen=True)
class Action:
    type: ActionType
    tree_index: int = -1
    seed_index: int = -1

    def __str__(self):
        if self.type is ActionType.WAIT:
            return 'WAIT Zzz'
        elif self.type is ActionType.SEED:
            return f'SEED {self.tree_index} {self.seed_index}'
        else:
            return f'{self.type.name} {self.tree_index}'

    @staticmethod
    def from_string(string):
        action, *args = string.split()
        return Action(ActionType(action), *(map(int, args)))

    def __gt__(self, other):
        return bool(random.getrandbits(1))

import sys
from functools import cache

WIDTH = 10 + 1
NODES_TO_KEEP = 100

DIRECTIONS = {
    'N': -WIDTH,
    'S': WIDTH,
    'E': 1,
    'W': -1,
    'NE': 1 - WIDTH,
    'SE': 1 + WIDTH,
    'NW': -1 - WIDTH,
    'SW': -1 + WIDTH,
}


@cache
def update_action(forest, trucks, i, action):
    action = action.split()
    if action[0] == 'MOVE':
        trucks = list(trucks)
        trucks[i] += DIRECTIONS[action[1]]
        trucks = tuple(trucks)
    elif action[0] == 'FIGHT':
        forest = list(forest)
        forest[trucks[i] + DIRECTIONS[action[1]]] = '^'
        forest = ''.join(forest)

    return forest, trucks


@cache
def update_fire(forest, trucks):
    forest = [{'1': '2', '2': '3', '3': '4'}.get(tree, tree) for tree in forest]
    for i, tree in enumerate(forest):
        if tree == '4':
            forest[i] = '*'
            for j in (i - 1, i + 1, i - WIDTH, i + WIDTH):
                if 0 <= j < len(forest) and forest[j] == '^' and j not in trucks:
                    forest[j] = '1'
    return forest


@cache
def score(forest):
    return tuple(forest.count(tree) for tree in '*321')


@cache
def get_truck_actions(forest, trucks, i):
    actions = ['WAIT']
    for direction in 'NSEW':
        truck = trucks[i] + DIRECTIONS[direction]
        if 0 <= truck < len(forest) and truck not in trucks and forest[truck] in '^*.':
            actions.append(f'MOVE {direction}')
    for direction in DIRECTIONS:
        water = trucks[i] + DIRECTIONS[direction]
        if 0 <= water < len(forest) and forest[water] in '123':
            actions.append(f'FIGHT {direction}')
    # show(forest, trucks, actions)
    return tuple(actions)


def show(forest, trucks, actions):
    print(forest + '\n', trucks, actions, file=sys.stderr)


def solve(forest, trucks, max_burned_trees):
    nodes = [(forest, trucks, ())]

    while nodes:

        for i in range(len(trucks)):

            nodes_ = []
            for forest, trucks, actions in nodes:
                truck = trucks[i]

                for action in get_truck_actions(forest, trucks, i):
                    new_forest, new_trucks = update_action(forest, trucks, i, action)
                    nodes_.append((new_forest, new_trucks, actions + (action,)))

            nodes_.sort(key=lambda node: score(node[0]))
            nodes = nodes_[:NODES_TO_KEEP]

        nodes_ = []
        for forest, trucks, actions in nodes:
            if not ({'1', '2', '3'} & set(forest)):
                show(forest, trucks, actions)
                return actions
            new_forest = update_fire(forest, trucks)
            nodes_.append((new_forest, trucks, actions))

        nodes_.sort(key=lambda node: score(node[0]))
        nodes = nodes_[:NODES_TO_KEEP]


def main():
    nb_trucks, max_burned_trees = map(int, input().split())

    while True:
        forest = '\n'.join(input() for _ in range(10))
        trucks = tuple(y * WIDTH + x for x, y in [map(int, input().split()) for _ in range(nb_trucks)])
        print(forest, file=sys.stderr)

        actions = solve(forest, trucks, max_burned_trees)
        # show(forest, trucks, actions)

        actions += ('WAIT',) * (nb_trucks - len(actions))

        for action in actions[:nb_trucks]:
            print(action)


if __name__ == "__main__":
    main()

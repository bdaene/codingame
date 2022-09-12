# See https://www.codingame.com/ide/puzzle/green-valleys


from collections import defaultdict
from dataclasses import dataclass
import numpy


@dataclass
class DisjointSets:
    sets = {}

    def get_root_set(self, a):
        x = a
        while self.sets.setdefault(x, x) != x:
            x = self.sets[x]
        while a != x:
            a, self.sets[a] = self.sets[a], x
        return x

    def connect(self, a, b):
        a = self.get_root_set(a)
        b = self.get_root_set(b)
        self.sets[a] = b


def main():
    snow_limit = int(input())
    size = int(input())
    fields = numpy.array([list(map(int, input().split())) for _ in range(size)])

    valleys = DisjointSets()
    for x in range(size):
        for y in range(size):
            if fields[x][y] > snow_limit:
                continue
            if x + 1 < size and fields[x + 1][y] <= snow_limit:
                valleys.connect((x, y), (x + 1, y))
            if y + 1 < size and fields[x][y+1] <= snow_limit:
                valleys.connect((x, y), (x, y+1))

    valley_fields = defaultdict(set)
    for x in range(size):
        for y in range(size):
            if fields[x][y] > snow_limit:
                continue
            valley_fields[valleys.get_root_set((x, y))].add((x, y))

    if valley_fields:
        max_size = max(map(len, valley_fields.values()))
        deepest_point = min(
            fields[x][y] for valley in valley_fields.values() if len(valley) == max_size for x, y in valley)
        print(deepest_point)
    else:
        print(0)


if __name__ == "__main__":
    main()

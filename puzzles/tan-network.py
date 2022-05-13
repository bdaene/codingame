
#  See https://www.codingame.com/ide/puzzle/tan-network
import math
from dataclasses import dataclass
from functools import cache
from heapq import heappush, heappop


@dataclass(frozen=True)
class Stop:
    id_: str
    name: str
    description: str
    latitude: float
    longitude: float
    zone_id: str
    url: str
    type_: str
    mother_station: str

    @classmethod
    def from_string(cls, string):
        data = string.split(',')
        data[1] = data[1][1:-1]
        data[3:5] = map(lambda x: math.radians(float(x)), data[3:5])
        return cls(*data)

    @cache
    def distance(self, other):
        x = (other.longitude - self.longitude) * math.cos((self.latitude + other.latitude)/2)
        y = other.latitude - self.latitude
        d = (x**2+y**2)**0.5 * 6371
        return d

    def __lt__(self, other):
        return self.id_ < other.id_


def solve(routes, start, target):
    to_visit: list[tuple[float, tuple[Stop, ...]]] = [(0, (start,))]
    visited = set()

    while to_visit:
        cost, path = heappop(to_visit)
        start = path[-1]
        if start == target:
            return path
        if start in visited:
            continue
        visited.add(start)

        for next_stop, dist in routes[start].items():
            if next_stop not in visited:
                heappush(to_visit, (cost + dist, path + (next_stop, )))

    return None


def main():
    start_id = input()
    target_id = input()
    stops = {stop.id_: stop for stop in (Stop.from_string(input()) for _ in range(int(input())))}
    routes = {stop: {} for stop in stops.values()}
    for begin_id, end_id in (input().split() for _ in range(int(input()))):
        begin, end = stops[begin_id], stops[end_id]
        routes[begin][end] = Stop.distance(begin, end)

    path = solve(routes, stops[start_id], stops[target_id])
    if path:
        for stop in path:
            print(stop.name)
    else:
        print('IMPOSSIBLE')


if __name__ == "__main__":
    main()

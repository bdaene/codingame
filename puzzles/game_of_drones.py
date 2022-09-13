# See https://www.codingame.com/ide/puzzle/game-of-drones

import sys
from collections import defaultdict
from dataclasses import dataclass
from itertools import count, chain
from math import dist
from operator import attrgetter
from random import random
from typing import NamedTuple, Iterable, Optional, NewType


def debug(*args):
    print(*args, file=sys.stderr, flush=True)


class Position(NamedTuple):
    x: int
    y: int

    def __str__(self):
        return f"{self.x} {self.y}"


ZONE_RADIUS = 100
DRONE_SPEED = 100

Player = NewType('Player', int)


@dataclass
class Zone:
    id: int
    position: Position
    controller: Player
    closest_drones: dict[Player, set['Drone']]

    def __hash__(self):
        return hash(self.id)

    def __iter__(self):
        return iter(self.position)

    def __str__(self):
        return f"Zone({self.id})"

    def __lt__(self, other):
        return random() < 0.5


@dataclass
class Drone:
    player: int
    id: int
    position: Position
    target: Optional[Zone] = None

    def __hash__(self):
        return hash((self.player, self.id))

    def __iter__(self):
        return iter(self.position)

    def __str__(self):
        return f"Drone({self.player, self.id})"

    def __lt__(self, other):
        return random() < 0.5


def get_zones(zone_positions: list[Position], zone_controllers: list[Player], drones: dict[Player, set[Drone]]
              ) -> set[Zone]:
    closest_drones = {position: defaultdict(set) for position in zone_positions}
    for drone in chain(*drones.values()):
        closest_zone = min(zone_positions, key=lambda z: dist(drone, z))
        closest_drones[closest_zone][drone.player].add(drone)

    return {Zone(i, position, controller, closest_drones[position])
            for i, (position, controller) in enumerate(zip(zone_positions, zone_controllers))}


def get_available_drones(drones: Iterable[Drone]) -> set[Drone]:
    return {drone for drone in drones if drone.target is None}


def get_closest_attacker_distance(zone: Zone, attackers: Iterable[Drone], defenders: Iterable[Drone]):
    attackers = sorted(attackers, key=lambda drone: dist(zone, drone))
    defenders = sorted(defenders, key=lambda drone: dist(zone, drone))

    for i, attacker in enumerate(attackers):
        if i >= len(defenders) or dist(zone, defenders[i]) > dist(zone, attacker) - DRONE_SPEED:
            return dist(zone, attacker)
    return float('inf')


def assign_closest(available_drones: set[Drone], zone: Zone, nb_drones):
    for drone in sorted(available_drones, key=lambda d: dist(zone, d))[:nb_drones]:
        debug(f"{drone} assigned to {zone}.")
        drone.target = zone
        available_drones.remove(drone)


def defend(turn: int, player: Player, zones: set[Zone], drones: dict[Player, set[Drone]]):
    available_drones = get_available_drones(drones[player])

    to_defend = []
    for zone in zones:
        if zone.controller != player:
            continue
        defenders = len(zone.closest_drones[player])
        nb_attackers = max(map(len, (p_drones for p, p_drones in zone.closest_drones.items() if p != player)),
                           default=0)

        attacker_dist = min((get_closest_attacker_distance(zone, p_drones, zone.closest_drones[player])
                             for p, p_drones in drones.items() if p != player))

        to_defend.append((nb_attackers - defenders, nb_attackers, attacker_dist, zone))

    to_defend.sort()
    for _, nb_attackers, _, zone in to_defend:
        if nb_attackers <= len(available_drones):
            debug(f"Defending {zone} ({nb_attackers} attackers).")
            assign_closest(available_drones, zone, nb_attackers)


def attack(turn: int, player: Player, zones: set[Zone], drones: dict[Player, set[Drone]]):
    available_drones = get_available_drones(drones[player])

    to_attack = []
    for zone in zones:
        if zone.controller == player:
            continue

        nb_defenders = max(map(len, (p_drones for p, p_drones in zone.closest_drones.items() if p != player)),
                           default=0)

        attacker_dist = min((get_closest_attacker_distance(zone, available_drones, p_drones)
                             for p, p_drones in drones.items() if p != player))

        to_attack.append((nb_defenders, attacker_dist, zone))

    to_attack.sort()
    for nb_defenders, _, zone in to_attack:

        if nb_defenders + 1 <= len(available_drones):
            debug(f"Attacking {zone} ({nb_defenders} defenders).")
            assign_closest(available_drones, zone, nb_defenders + 1)


def support(turn: int, player: Player, zones: set[Zone], drones: dict[Player, set[Drone]]):
    for zone in zones:
        for drone in zone.closest_drones[player]:
            if drone.target is None:
                debug(f"{drone} support {zone}.")
                drone.target = zone


def assign_targets(turn: int, player: Player, zones: set[Zone], drones: dict[Player, set[Drone]]):
    defend(turn, player, zones, drones)
    attack(turn, player, zones, drones)
    support(turn, player, zones, drones)


def get_destination(drone):
    zone = drone.target
    d = dist(drone, zone)
    if d <= ZONE_RADIUS:
        return drone.position
    dx = drone.position.x - zone.position.x
    dy = drone.position.y - zone.position.y

    x = zone.position.x + int(dx / d * ZONE_RADIUS)
    y = zone.position.y + int(dy / d * ZONE_RADIUS)
    return Position(x, y)


def main():
    nb_players, player_id, nb_drones_per_player, nb_zones = map(int, input().split())
    zone_positions = [Position(x, y) for x, y in (map(int, input().split()) for _ in range(nb_zones))]

    player = Player(player_id)

    for turn in count():
        zone_controllers = [Player(int(input())) for _ in range(nb_zones)]
        drones = {Player(player): {Drone(Player(player), i, Position(*map(int, input().split())))
                                   for i in range(nb_drones_per_player)}
                  for player in range(nb_players)}

        zones = get_zones(zone_positions, zone_controllers, drones)
        assign_targets(turn, player, zones, drones)

        for drone in sorted(drones[player], key=attrgetter('id')):
            print(get_destination(drone))


if __name__ == "__main__":
    main()

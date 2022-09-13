# See https://www.codingame.com/ide/puzzle/code-royale

import sys
from collections import defaultdict
from dataclasses import dataclass
from enum import Enum
from itertools import count
from typing import NamedTuple, Optional, Iterable
from math import dist, hypot


def debug(*args):
    print(*args, file=sys.stderr, flush=True)


class Position(NamedTuple):
    x: int
    y: int


class StructureType(int, Enum):
    NONE = -1
    GOLDMINE = 0
    TOWER = 1
    BARRACKS = 2


class Owner(int, Enum):
    NONE = -1
    FRIENDLY = 0
    ENEMY = 1


class UnitType(int, Enum):
    NONE = -2
    QUEEN = -1
    KNIGHT = 0
    ARCHER = 1
    GIANT = 2


@dataclass
class Site:
    id: int
    position: Position
    radius: int
    gold: int = -1
    maxMineSize: int = -1
    structure_type: StructureType = StructureType.NONE
    unit_type: UnitType = UnitType.NONE
    owner: Owner = Owner.NONE
    param_1: int = -1
    param_2: int = -1

    @classmethod
    def from_string(cls, string):
        site_id, x, y, radius = map(int, string.split())
        return cls(site_id, Position(x, y), radius)

    def update(self, gold, maxMineSize, structure_type, owner, param_1, param_2):
        self.gold = gold
        self.maxMineSize = maxMineSize
        self.structure_type = StructureType(structure_type)
        self.owner = Owner(owner)
        self.param_1 = param_1
        self.param_2 = param_2


class Unit(NamedTuple):
    position: Position
    owner: Owner
    type: UnitType
    health: int

    @classmethod
    def from_string(cls, string):
        x, y, owner, unit_type, health = map(int, string.split())
        return Unit(Position(x, y), Owner(owner), UnitType(unit_type), health)


COST = {
    UnitType.ARCHER: 100,
    UnitType.KNIGHT: 80
}
QUEEN_SPEED = 60

SortedSites = dict[tuple[Owner, UnitType], list[Site]]
SortedUnits = dict[tuple[Owner, UnitType], set[Unit]]


def sort_sites(sites: Iterable[Site]) -> SortedSites:
    sorted_sites = defaultdict(list)
    for site in sites:
        sorted_sites[(site.owner, site.unit_type)].append(site)
    return sorted_sites


def sort_units(units: Iterable[Unit]) -> SortedUnits:
    sorted_units = defaultdict(set)
    for unit in units:
        sorted_units[(unit.owner, unit.type)].add(unit)
    return sorted_units


def get_unit_needed(units: SortedUnits) -> UnitType:
    nb_knights = len(units[(Owner.FRIENDLY, UnitType.KNIGHT)])
    nb_archers = len(units[(Owner.FRIENDLY, UnitType.ARCHER)])

    if nb_knights <= 4 * nb_archers:
        return UnitType.KNIGHT
    else:
        return UnitType.ARCHER


def get_trained_site_ids(gold: int, sites: Iterable[Site]):
    for site in sites:
        if gold < COST[site.unit_type]:
            continue
        yield str(site.id)
        gold -= COST[site.unit_type]


def get_train_action(gold: int, sites: SortedSites, units: SortedUnits) -> str:
    unit_needed = get_unit_needed(units)

    if unit_needed is UnitType.ARCHER:
        queen = next(iter(units[(Owner.ENEMY, UnitType.QUEEN)]))
        owned_sites = list(sites[(Owner.FRIENDLY, UnitType.ARCHER)])
        owned_sites.sort(key=lambda s: dist(s.position, queen.position))

        if owned_sites:
            return " ".join(("TRAIN", *get_trained_site_ids(gold, owned_sites)))

    enemy_queen = next(iter(units[(Owner.ENEMY, UnitType.QUEEN)]))
    owned_sites = list(sites[Owner.FRIENDLY, UnitType.KNIGHT])
    owned_sites.sort(key=lambda s: dist(s.position, enemy_queen.position))
    return " ".join(("TRAIN", *get_trained_site_ids(gold, owned_sites)))


def flee_away_from_enemy_knights(queen, units: SortedUnits):
    closest_enemy = min(units[(Owner.ENEMY, UnitType.KNIGHT)],
                        key=lambda unit: dist(queen.position, unit.position),
                        default=None)
    if closest_enemy and dist(queen.position, closest_enemy.position) < 4 * QUEEN_SPEED:
        dx = queen.position.x - closest_enemy.position.x
        dy = queen.position.y - closest_enemy.position.y
        d = hypot(dx, dy)
        dx *= 4 * QUEEN_SPEED / d
        dy *= 4 * QUEEN_SPEED / d
        return f"MOVE {round(queen.position.x + dx)} {round(queen.position.y + dy)}"


def reach_closest_site_and_build(queen, touched_site, sites: SortedSites, units: SortedUnits):
    buildable_site = list(sites[(Owner.NONE, UnitType.NONE)])
    for unit_type in UnitType:
        buildable_site += sites[(Owner.ENEMY, unit_type)]

    closest_site = min(buildable_site,
                       key=lambda site: dist(queen.position, site.position),
                       default=None)
    if closest_site:
        if touched_site and touched_site.owner is not Owner.FRIENDLY:
            unit_type = get_unit_needed(units)
            touched_site.unit_type = unit_type
            return f"BUILD {touched_site.id} BARRACKS-{unit_type.name}"
        else:
            return f"MOVE {closest_site.position.x} {closest_site.position.y}"


def get_first_action(touched_site, sites: SortedSites, units: SortedUnits) -> str:
    queen = next(iter(units[(Owner.FRIENDLY, UnitType.QUEEN)]))

    return (flee_away_from_enemy_knights(queen, units)
            or reach_closest_site_and_build(queen, touched_site, sites, units)
            or "WAIT")


def get_actions(turn, gold, touched_site: Optional[Site], sites: dict[int, Site], units: set[Unit]):
    sites = sort_sites(sites.values())
    units = sort_units(units)
    return get_first_action(touched_site, sites, units), get_train_action(gold, sites, units)


def main():
    sites = {site.id: site for site in map(Site.from_string, (input() for _ in range(int(input()))))}
    debug(sites)

    for turn in count():
        gold, touched_site = map(int, input().split())
        touched_site = None if touched_site == -1 else sites[touched_site]
        for _ in range(len(sites)):
            site_id, *info = map(int, input().split())
            sites[site_id].update(*info)

        units = {Unit.from_string(input()) for _ in range(int(input()))}

        action, train = get_actions(turn, gold, touched_site, sites, units)
        print(action)
        print(train)


if __name__ == "__main__":
    main()

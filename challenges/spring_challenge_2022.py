# See https://www.codingame.com/ide/challenge/spring-challenge-2022

import sys
from collections import defaultdict
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Iterable
from functools import partial


class EntityType(Enum):
    MONSTER = 0
    MY_HERO = 1
    OPPONENT_HERO = 2


class BaseType(Enum):
    MY_BASE = 1
    OPPONENT_BASE = 2


class Point:
    def __init__(self, *value):
        if len(value) == 1:
            self.value, = value
        else:
            x, y = value
            self.value = x + 1j * y

    @property
    def x(self):
        return self.value.real

    @property
    def y(self):
        return self.value.imag

    def __repr__(self):
        return f"Point({self.value.real}, {self.value.imag})"

    def __add__(self, other):
        return Point(self.value + other.value)

    def __sub__(self, other):
        return Point(self.value - other.value)

    def __abs__(self):
        return abs(self.value)

    def __mul__(self, factor):
        return Point(self.value * factor)


@dataclass(frozen=True)
class Entity:
    id_: str
    type_: EntityType
    position: Point
    velocity: Point
    health: int
    near_base: bool
    threat_for: Optional[BaseType]
    shield_life: int
    is_controlled: bool

    @classmethod
    def from_string(cls, string):
        id_, type_, x, y, shield_life, is_controlled, health, vx, vy, near_base, threat_for = string.split()
        return Entity(
            id_=id_,
            type_=EntityType(int(type_)),
            position=Point(int(x), int(y)),
            velocity=Point(int(vx), int(vy)),
            health=int(health),
            near_base=near_base == '1',
            threat_for={'1': BaseType.MY_BASE, '2': BaseType.OPPONENT_BASE}.get(threat_for, None),
            shield_life=int(shield_life),
            is_controlled=is_controlled == '1'
        )


@dataclass
class Base:
    type_: BaseType
    position: Point
    health: int = 3
    mana: int = 0

    def update(self, string):
        self.health, self.mana = map(int, string.split())


@dataclass(frozen=True)
class ActionWait:
    def __str__(self):
        return "WAIT"


@dataclass(frozen=True)
class ActionMove:
    position: Point

    def __str__(self):
        return f"MOVE {round(self.position.x)} {round(self.position.y)}"


class Spell(Enum):
    WIND = "WIND"
    SHIELD = "SHIELD"
    CONTROL = "CONTROL"


@dataclass(frozen=True)
class ActionSpell:
    spell: Spell
    entity: Optional[Entity] = None
    position: Optional[Point] = None

    def __str__(self):
        parameters = ["SPELL", self.spell.value]
        if self.entity:
            parameters.append(self.entity.id_)
        if self.position:
            parameters.append(f"{round(self.position.x)}")
            parameters.append(f"{round(self.position.y)}")
        return " ".join(parameters)


def log(*args):
    print(*args, file=sys.stderr, flush=True)


MONSTER_RANGE = 300
BASE_RADIUS = 5000
MONSTER_SPEED = 400
HERO_SPEED = 800
HERO_DAMAGE = 2
HERO_RANGE = 800
WIND_RANGE = 1280
WIND_PUSH = 2200
SHIELD_RANGE = 2200
CONTROL_RANGE = 2200
SPELL_COST = 10
BASE_VIEW = 6000
HERO_VIEW = 2200


def dist(a, b):
    return abs(b.position - a.position)


def get_hero_actions(my_base: Base, opponent_base: Base,
                     my_heroes: Iterable[Entity], opponent_heroes: Iterable[Entity], monsters: Iterable[Entity]):
    threats = filter(lambda monster_: monster_.threat_for is BaseType.MY_BASE, monsters)
    threats = sorted(threats, key=partial(dist, my_base))

    available_heroes = set(my_heroes)
    heroes_actions = {}
    heroes_messages = {}
    used_mana = 0

    # Target closest threats
    for threat in threats:
        if not available_heroes:
            break

        closest_hero = min(available_heroes, key=partial(dist, threat))

        # try control it toward enemy base
        if (BASE_RADIUS < dist(threat, my_base)
                and dist(closest_hero, threat) < CONTROL_RANGE
                and dist(threat, opponent_base) < dist(closest_hero, opponent_base)
                and used_mana + SPELL_COST < my_base.mana):
            heroes_actions[closest_hero] = ActionSpell(Spell.CONTROL, entity=threat, position=opponent_base.position)
            heroes_messages[closest_hero] = f"C{threat.id_}"
            available_heroes.remove(closest_hero)
            used_mana += SPELL_COST
            continue

        # try push it outside if inside
        if (BASE_RADIUS - WIND_PUSH < dist(threat, my_base) < BASE_RADIUS
                and dist(closest_hero, threat) < WIND_RANGE
                and used_mana + SPELL_COST < my_base.mana):
            heroes_actions[closest_hero] = ActionSpell(Spell.WIND, position=threat.position * 2 - my_base.position)
            heroes_messages[closest_hero] = f"W{threat.id_}"
            available_heroes.remove(closest_hero)
            used_mana += SPELL_COST
            continue

        # Attack
        damage_done = 0
        while available_heroes and damage_done < threat.health:
            closest_hero = min(available_heroes, key=partial(dist, threat))
            heroes_actions[closest_hero] = ActionMove(threat.position)
            heroes_messages[closest_hero] = f"A{threat.id_}"
            available_heroes.remove(closest_hero)
            turns_to_base = max(0, dist(my_base, threat) - MONSTER_RANGE) // MONSTER_SPEED
            turns_to_threat = max(0, dist(threat, closest_hero) - HERO_RANGE) // (HERO_SPEED - MONSTER_SPEED)
            damage_done += HERO_DAMAGE * max(0, turns_to_base - turns_to_threat)

    # Gain mana
    close_monsters = sorted(monsters, key=partial(dist, my_base))
    for monster in close_monsters:
        if not available_heroes or dist(my_base, monster) > 2 * BASE_RADIUS:
            break
        closest_hero = min(available_heroes, key=partial(dist, monster))
        heroes_actions[closest_hero] = ActionMove(monster.position)
        heroes_messages[closest_hero] = f"M{monster.id_}"
        available_heroes.remove(closest_hero)

    # Move in defense position
    for hero in available_heroes:
        relative_position = hero.position - my_base.position
        target_position = my_base.position + relative_position * ((BASE_RADIUS + HERO_VIEW) / abs(relative_position))
        closest_hero = min(set(my_heroes) - {hero}, key=lambda hero_: abs(hero_.position - target_position))
        if abs(target_position - closest_hero.position) < HERO_VIEW:
            relative_position = target_position - closest_hero.position
            target_position = closest_hero.position + relative_position * (HERO_VIEW / abs(relative_position))

        heroes_actions[hero] = ActionMove(
            my_base.position + relative_position * ((BASE_RADIUS + HERO_VIEW) / abs(relative_position)))
        heroes_messages[hero] = "D"

    return tuple((heroes_actions.get(hero, ActionWait()), heroes_messages.get(hero, ""))
                 for hero in sorted(my_heroes, key=lambda hero_: hero_.id_))


def main():
    my_base = Base(BaseType.MY_BASE, Point(*(map(int, input().split()))))
    opponent_base = Base(BaseType.OPPONENT_BASE, Point(17630, 9000) - my_base.position)
    heroes_per_player = int(input())
    log(heroes_per_player)

    # game loop
    while True:
        my_base.health, my_base.mana = map(int, input().split())
        opponent_base.health, opponent_base.mana = map(int, input().split())

        entities = [Entity.from_string(input()) for _ in range(int(input()))]
        entities_by_type = defaultdict(set)
        for entity in entities:
            entities_by_type[entity.type_].add(entity)

        for action, message in get_hero_actions(my_base, opponent_base, entities_by_type[EntityType.MY_HERO],
                                                entities_by_type[EntityType.OPPONENT_HERO],
                                                entities_by_type[EntityType.MONSTER]):
            print(action, message)


if __name__ == "__main__":
    main()

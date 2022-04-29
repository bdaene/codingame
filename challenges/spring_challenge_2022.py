# See https://www.codingame.com/ide/challenge/spring-challenge-2022

import sys
from collections import defaultdict
from dataclasses import dataclass
from enum import Enum
from functools import partial
from typing import Optional, Union


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

    def is_shielded(self):
        return self.shield_life > 0


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


def can_cast(caster: Entity, spell_range: int, target: Entity):
    return not target.is_shielded() and dist(caster, target) <= spell_range


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
TURN_LIMIT = 220
MAP_SIZE = Point(17630, 9000)


def dist(a, b):
    return abs(b.position - a.position)


def get_position(distance, target, direction):
    relative_position = direction - target
    relative_position *= distance / abs(relative_position)
    return target + relative_position


Action = Union[ActionMove, ActionWait, ActionSpell]


@dataclass
class State:
    turn: int
    my_base: Base
    opponent_base: Base
    my_heroes: frozenset[Entity]
    opponent_heroes: frozenset[Entity]
    monsters: frozenset[Entity]

    available_heroes: set
    actions: dict[Entity, tuple[Action, str]]
    used_mana: int

    def __init__(self, turn, my_base, opponent_base, entities):
        self.turn = turn
        self.my_base = my_base
        self.opponent_base = opponent_base

        entities_by_type = defaultdict(set)
        for entity in entities:
            entities_by_type[entity.type_].add(entity)
        self.my_heroes = frozenset(entities_by_type[EntityType.MY_HERO])
        self.opponent_heroes = frozenset(entities_by_type[EntityType.OPPONENT_HERO])
        self.monsters = frozenset(entities_by_type[EntityType.MONSTER])

        self.available_heroes = set(self.my_heroes)
        self.actions = {}
        self.used_mana = 0

    def add_action(self, hero, action, message):
        if isinstance(action, ActionSpell):
            if self.is_enough_mana():
                self.used_mana += SPELL_COST
            else:
                return False

        self.actions[hero] = (action, message)
        self.available_heroes.discard(hero)
        return True

    def is_enough_mana(self, cost=SPELL_COST):
        return self.used_mana + cost <= self.my_base.mana

    def get_closest_hero(self, target: Union[Base, Entity]):
        return min(self.available_heroes, key=partial(dist, target), default=None)

    def get_actions(self):
        default_action = ActionWait(), ""
        return tuple(self.actions.get(hero, default_action)
                     for hero in sorted(self.my_heroes, key=lambda hero_: hero_.id_))


def protect_heroes(state: State):
    for hero in state.my_heroes:
        closest_opponent = min(state.opponent_heroes, key=partial(dist, hero), default=None)
        closest_ally = min(state.available_heroes - {hero}, key=partial(dist, hero), default=None)
        if closest_opponent is None or closest_ally is None:
            continue
        if (
                dist(closest_opponent, hero) < CONTROL_RANGE
                and dist(closest_ally, hero) < SHIELD_RANGE
                and not hero.is_shielded()
        ):
            state.add_action(closest_ally, ActionSpell(Spell.SHIELD, hero), "S")


def control_threat(state: State, threat: Entity):
    closest_hero = state.get_closest_hero(threat)
    return (
            closest_hero is not None
            and BASE_RADIUS < dist(threat, state.my_base)
            and threat.health > 20
            and can_cast(closest_hero, CONTROL_RANGE, threat)
            and dist(threat, state.opponent_base) < dist(closest_hero, state.opponent_base)
            and state.add_action(closest_hero,
                                 ActionSpell(Spell.CONTROL, entity=threat, position=state.opponent_base.position),
                                 f"C{threat.id_}")
    )


def push_threat(state, threat: Entity):
    closest_hero = state.get_closest_hero(threat)
    return (
            closest_hero is not None
            and BASE_RADIUS - WIND_PUSH < dist(threat, state.my_base) < BASE_RADIUS
            and can_cast(closest_hero, WIND_RANGE, threat)
            and state.add_action(closest_hero,
                                 ActionSpell(Spell.WIND, position=threat.position * 2 - state.my_base.position),
                                 f"W{threat.id_}")
    )


def attack_threat(state: State, threat: Entity):
    damage_done = 0
    while damage_done < threat.health:
        closest_hero = state.get_closest_hero(threat)
        if closest_hero is None:
            return
        state.add_action(closest_hero, ActionMove(threat.position), f"A{threat.id_}")

        turns_to_base = max(0, dist(state.my_base, threat) - MONSTER_RANGE) // MONSTER_SPEED
        turns_to_threat = max(0, dist(threat, closest_hero) - HERO_RANGE) // (HERO_SPEED - MONSTER_SPEED)
        damage_done += HERO_DAMAGE * max(0, turns_to_base - turns_to_threat)


def target_threats(state: State):
    threats = filter(lambda monster_: monster_.threat_for is BaseType.MY_BASE, state.monsters)
    threats = sorted(threats, key=partial(dist, state.my_base))
    for threat in threats:
        (
                control_threat(state, threat)
                or push_threat(state, threat)
                or attack_threat(state, threat)
        )


def gain_mana(state: State):
    monsters = sorted(state.monsters, key=partial(dist, state.my_base))
    for monster in monsters:
        if dist(state.my_base, monster) > 2 * BASE_RADIUS:
            return
        closest_hero = state.get_closest_hero(monster)
        if closest_hero is None:
            return
        state.add_action(closest_hero, ActionMove(monster.position), f"M{monster.id_}")


def move_to_defense(state: State):
    for hero in set(state.available_heroes):
        target_position = get_position(BASE_RADIUS + HERO_VIEW, state.my_base.position, hero.position)
        closest_hero = min(set(state.my_heroes) - {hero}, key=lambda hero_: abs(hero_.position - target_position))
        if abs(target_position - closest_hero.position) < HERO_VIEW:
            target_position = get_position(HERO_VIEW, closest_hero.position, target_position)
        state.add_action(hero, ActionMove(target_position), "D")


def move_to_attack(state: State, hero: Entity):
    if dist(hero, state.opponent_base) > BASE_RADIUS:
        center = (state.my_base.position + state.opponent_base.position) * .5
        target_position = get_position(BASE_RADIUS, state.opponent_base.position, center)
        state.add_action(hero, ActionMove(target_position), f"M")
        return True
    return False


def push_attack(state: State, hero: Entity):
    monsters_in_range = {monster for monster in state.monsters if can_cast(hero, WIND_RANGE, monster)}
    return (
            len(monsters_in_range) >= 5
            and state.add_action(hero, ActionSpell(Spell.WIND, position=state.opponent_base.position), "P")
    )


def control_attack(state: State, hero: Entity):
    closest_monster = min((monster for monster in state.monsters if can_cast(hero, CONTROL_RANGE, monster)),
                          key=partial(dist, hero), default=None)
    return (
            closest_monster
            and state.add_action(hero, ActionSpell(Spell.CONTROL, entity=closest_monster,
                                                   position=state.opponent_base.position), f"C{closest_monster.id_}")
    )


def attack_opponent(state: State):
    hero = state.get_closest_hero(state.opponent_base)
    if hero is None:
        return
    (
            push_attack(state, hero)
            or control_attack(state, hero)
            or move_to_attack(state, hero)
    )


def get_actions(state: State):
    protect_heroes(state)

    if state.turn > TURN_LIMIT // 2:
        attack_opponent(state)

    target_threats(state)
    gain_mana(state)
    move_to_defense(state)

    return state.get_actions()


def main():
    my_base = Base(BaseType.MY_BASE, Point(*(map(int, input().split()))))
    opponent_base = Base(BaseType.OPPONENT_BASE, MAP_SIZE - my_base.position)
    heroes_per_player = int(input())
    log(heroes_per_player)

    # game loop
    turn = 0
    while True:
        turn += 1
        my_base.health, my_base.mana = map(int, input().split())
        opponent_base.health, opponent_base.mana = map(int, input().split())
        entities = [Entity.from_string(input()) for _ in range(int(input()))]

        state = State(turn, my_base, opponent_base, entities)

        for action, message in get_actions(state):
            print(action, message)


if __name__ == "__main__":
    main()

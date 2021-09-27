# https://www.codingame.com/ide/puzzle/space-shooter

import sys
import math
import cmath
from dataclasses import dataclass
from enum import Enum
from random import random


class UnitType(Enum):
    SHIP = "S"
    BULLET = "B"
    MISSILE = "M"


MAX_ACCELERATION = {
    UnitType.SHIP: 10,
    UnitType.MISSILE: 30,
}

BORDER = 1700 + 1080j


def complex_to_str(z):
    return f'{z.real:.2f} {z.imag:.2f}'


def get_unit_class(unit_type):
    return {
        UnitType.SHIP: Ship,
        UnitType.MISSILE: Missile,
        UnitType.BULLET: Unit,
    }[UnitType(unit_type)]


@dataclass
class Unit:
    unit_id: int
    faction: int
    unit_type: UnitType
    health: float
    position: complex
    velocity: complex
    gun_cool_down: float

    @staticmethod
    def from_string(string):
        unit_id, faction, unit_type, health, position_x, position_y, velocity_x, velocity_y, gun_cooldown = string.split()
        unit_class = get_unit_class(unit_type)
        return unit_class(int(unit_id), int(faction), UnitType(unit_type), float(health),
                    float(position_x) + 1j * float(position_y), float(velocity_x) + 1j * float(velocity_y),
                    float(gun_cooldown))

    def __str__(self):
        return f'{self.unit_id} {self.faction} {self.unit_type.value} {self.health} {self.position.real} {self.position.imag} {self.velocity.real} {self.velocity.imag} {self.gun_cool_down}'

    def avoid_border(self, acceleration):
        max_acceleration = MAX_ACCELERATION[self.unit_type]
        velocity = self.velocity + acceleration
        stop_time = 1 + abs(velocity) / max_acceleration
        stop_position = self.position + stop_time * velocity

        if not (0 < stop_position.real < BORDER.real and 0 < stop_position.imag < BORDER.imag):
            print(f"Unit {self.unit_id} has to avoid the border.", file=sys.stderr)
            real_dir = 1 if stop_position.real < 0 else -1 if stop_position.real > BORDER.real else 0
            imag_dir = 1 if stop_position.imag < 0 else -1 if stop_position.imag > BORDER.imag else 0
            acceleration = max_acceleration * (real_dir + 1j * imag_dir)

        return acceleration

    def get_closest_unit(self, units, unit_types, factions=(-1,)):
        units = [unit for unit in units if unit.unit_type in unit_types and unit.faction in factions]
        units.sort(key=lambda unit: abs(unit.position - self.position))
        return units[0] if units else None

    def get_intersection(self, target, speed=100):
        position = target.position - self.position
        velocity = target.velocity - self.velocity
        # Solve bullet_velocity *  t = position + velocity * t with |bullet_velocity| = speed
        a = abs(velocity)**2 - speed**2
        if abs(a) < 1:
            t = abs(position)**2/(2*position*velocity.conjugate()).real
        else:
            m = -(position * velocity.conjugate()).real / a
            d = m ** 2 - abs(position)**2 / a
            if d <= 0:
                return None
            d = d ** 0.5
            if m > d:
                t = m-d
            else:
                t = m+d
        if t < 1:
            return None

        bullet_velocity = position / t + velocity
        return t, bullet_velocity

    def get_actions(self, units):
        raise NotImplementedError()


missile_launch = {}


@dataclass
class Ship(Unit):

    def explosive_in_range(self, units):
        return [unit for unit in units if unit.unit_type in {UnitType.BULLET, UnitType.MISSILE} and abs(unit.position - self.position) < 200]

    def get_actions(self, units):
        actions = [f'{self.unit_id}']

        # Move
        if abs(self.velocity) < 1:
            direction = 1 if self.position.real > BORDER.real / 2 else -1
        else:
            direction = self.velocity/abs(self.velocity)
        acceleration = cmath.rect(10, (random()-0.5) * math.pi) * direction
        acceleration = self.avoid_border(acceleration)
        actions.append(f'A {complex_to_str(acceleration)}')

        # Attack with bullets
        targets = [unit for unit in units if unit.faction == -1]
        t, bullet_velocity = min(bullet for bullet in map(self.get_intersection, targets) if bullet is not None)
        actions.append(f'F {complex_to_str(bullet_velocity)}')

        # Attack with missile
        max_acceleration = MAX_ACCELERATION[UnitType.MISSILE]
        target = self.get_closest_unit(units, {UnitType.SHIP})
        missile_acceleration = target.position - self.position - self.velocity
        missile_acceleration += target.velocity * (abs(target.position - self.position) * 2 / max_acceleration)**0.5
        if abs(missile_acceleration) > 1:
            missile_acceleration /= abs(missile_acceleration)
        missile = missile_launch.get(self.unit_id, 0)
        if missile < 4:
            missile_launch[self.unit_id] = missile + 1
            direction = 1j if missile % 2 == 0 else -1j
            actions.append(f'M {complex_to_str(missile_acceleration * direction * max_acceleration)}')
        else:
            if not self.explosive_in_range(units):
                missile_launch[self.unit_id] = 0

        return ' | '.join(actions)


@dataclass
class Missile(Unit):
    def get_acceleration_for_target(self, target):
        max_acceleration = MAX_ACCELERATION[UnitType.MISSILE]
        direction = target.position - self.position
        if abs(direction) > 1:
            direction /= abs(direction)
        if abs(self.velocity) > 1:
            target_angle = cmath.polar(direction / self.velocity)[1]
            if abs(target_angle) > 0.5*math.pi:
                print(f"Missile {self.unit_id} turning around.", file=sys.stderr)
                return max_acceleration * self.velocity / abs(self.velocity) * (-1j if target_angle < 0 else 1j)

        intersection = self.get_intersection(target, speed=max_acceleration*3)
        if not intersection:
            return direction * max_acceleration
        else:
            return intersection[1]

    def get_actions(self, units):
        actions = [f'{self.unit_id}']

        # Move
        target = self.get_closest_unit(units, {UnitType.SHIP})
        acceleration = self.get_acceleration_for_target(target)
        actions.append(f'A {complex_to_str(acceleration)}')

        # Detonate
        friend_ship = self.get_closest_unit(units, {UnitType.SHIP}, {1})
        next_position = self.position + self.velocity + acceleration
        next_target_position = target.position + target.velocity
        passing_target = abs(self.position - target.position) < abs(next_position - next_target_position)
        if abs(friend_ship.position - self.position) > 200 and passing_target:
            actions.append('D')

        return ' | '.join(actions)


def main():
    while True:
        units = [Unit.from_string(input()) for _ in range(int(input()))]

        for unit in units:
            if unit.faction == 1 and unit.unit_type in (UnitType.SHIP, UnitType.MISSILE):
                print(unit.get_actions(units))


if __name__ == "__main__":
    main()

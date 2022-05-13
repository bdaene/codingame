# https://www.codingame.com/ide/puzzle/mars-lander-episode-2

import sys
import math, cmath
from dataclasses import dataclass
from random import randint

MAX_VERTICAL_SPEED = 40
MAX_HORIZONTAL_SPEED = 20
GRAVITY = -1j * 3.711


def debug(*msg):
    print(*msg, file=sys.stderr, flush=True)


def get_intersection(a, b, p, q):
    """Return the intersection of segment ab and pq if any, else None"""
    ab, qp, ap = b - a, p - q, p - a
    try:
        u = (ap.real * qp.imag - ap.imag * qp.real) / (ab.real * qp.imag - ab.imag * qp.real)
        return a + u * ab if 0 < u < 1 else None
    except ZeroDivisionError:
        return None  # Segments are collinear


@dataclass
class Lander:
    position: complex
    velocity: complex
    fuel: int
    angle: int
    power: int

    @staticmethod
    def from_string(string):
        x, y, h_speed, v_speed, fuel, rotate, power = map(int, string.split())
        return Lander(x + 1j * y, h_speed + 1j * v_speed, fuel, rotate, power)

    def move(self, rotate, power):
        acceleration = cmath.rect(power, math.radians(90 + rotate)) + GRAVITY
        velocity = self.velocity + acceleration
        position = self.position + self.velocity + acceleration / 2
        fuel = self.fuel - power
        return Lander(position, velocity, fuel, rotate, power)


def get_collision(first_position, last_position, surface):
    for surface_a, surface_b in zip(surface, surface[1:]):
        intersection = get_intersection(surface_a, surface_b, first_position, last_position)
        if intersection is not None:
            return intersection
    return None


def get_score(lander, actions, surface, landing_surface):
    i = 0
    while True:
        debug(actions)
        if i >= len(actions):
            actions.append((lander.angle + randint(-15, 15), min(4, max(0, lander.power + randint(-1, 1)))))
            debug("hello")
        next_lander = lander.move(*actions[i])
        debug(next_lander)
        i += 1
        if not (0 <= next_lander.position.real <= 6999 and 0 <= next_lander.position.imag <= 2999):
            end_position = next_lander.position
            debug("Bim")
            break
        elif (collision := get_collision(lander.position, next_lander.position, surface)) is not None:
            debug(collision)
            end_position = collision
            debug("Bam")
            break
        lander = next_lander

    distance_x = end_position.real - landing_surface[0].real if end_position.real < landing_surface[
        0].real else end_position.real - landing_surface[1].real if end_position.real > landing_surface[1].real else 0
    distance_y = end_position.imag - landing_surface[0].imag
    return (
        abs(distance_x),
        max(0, abs(distance_y) - 20),
        abs(lander.angle),
        max(0, abs(lander.velocity.imag) - 40),
        max(0, abs(lander.velocity.real) - 20),
        -lander.fuel,
    )


def solve(lander, surface, landing_surface):
    best_actions = []
    best_score = get_score(lander, best_actions, surface, landing_surface)

    for _ in range(10):
        actions = []
        score = get_score(lander, best_actions, surface, landing_surface)
        if score < best_score:
            best_actions = actions

    return best_actions


def main():
    surface = tuple(x + 1j * y for x, y in (map(int, input().split()) for _ in range(int(input()))))
    landing_surface = next((a, b) for a, b in zip(surface, surface[1:]) if a.imag == b.imag)

    debug(surface, landing_surface)

    lander = Lander.from_string(input())
    actions = solve(lander, surface, landing_surface)
    debug(actions)

    turn = 0
    while True:
        print(*actions[turn])
        lander = lander.move(*actions[turn])  # Instead simulate the lander with maximum precision
        turn += 1
        input()  # Trow away rounded input
        debug(lander)


if __name__ == "__main__":
    main()

import sys
from itertools import product
from math import radians, pi, degrees
from cmath import rect, polar

import numpy
from scipy.spatial import KDTree


def get_solutions(screws, max_weights):
    solutions = {}
    for weights in product(range(max_weights+1), repeat=len(screws)):
        solution = sum(weight * screw for weight, screw in zip(weights, screws))
        solution = (round(solution.real, 6), round(solution.imag, 6))
        if solution not in solutions or sum(weights) < sum(solutions[solution]):
            solutions[solution] = weights

    return solutions


def get_unbalance(radius, weights):
    nb_screws = len(weights)
    screws = [rect(1 * radius, 2 * pi * i / nb_screws) for i in range(nb_screws)]
    unbalance = sum(weight * screw for weight, screw in zip(weights, screws))
    magnitude, angle = polar(unbalance)
    return magnitude, degrees(angle)


def main():
    nb_screws, radius, max_weights = map(int, input().split())

    screws = [rect(1*radius, 2*pi*i/nb_screws) for i in range(nb_screws)]

    even_solutions = get_solutions(screws[::2], max_weights)
    odd_solutions = get_solutions(screws[1::2], max_weights)

    even_points = tuple(even_solutions)
    odd_points = tuple(odd_solutions)

    kd_tree = KDTree(even_points)

    for magnitude, angle in (map(int, input().split()) for _ in range(int(input()))):
        unbalance = rect(magnitude, radians(angle))
        distances, indexes = kd_tree.query(- numpy.asarray(odd_points) - (unbalance.real, unbalance.imag))

        found_solution_indexes = numpy.where(distances <= min(distances) * (1+1e-6) + 1e-6)
        found_even_points = [even_points[index] for index in indexes[found_solution_indexes]]
        found_odd_points = [odd_points[index] for index in found_solution_indexes[0]]

        found_even_solutions = list(map(even_solutions.get, found_even_points))
        found_odd_solutions = list(map(odd_solutions.get, found_odd_points))

        best_solution = list(min((e + o for e, o in zip(found_even_solutions, found_odd_solutions)), key=sum))
        best_solution[::2], best_solution[1::2] = best_solution[:-(nb_screws//2)], best_solution[-(nb_screws//2):]

        print(*best_solution)

        remaining_unbalance = sum(weight * screw for weight, screw in zip(best_solution, screws)) + unbalance
        print(f"{remaining_unbalance=}", file=sys.stderr)


if __name__ == "__main__":
    main()

import sys
from collections import Counter


def get_atoms_count(molecule, atoms):
    stack = []
    number = ''
    for c in '(' + molecule + ')':
        if c.isdigit():
            number += c
            continue
        else:
            if number:
                for atom in stack[-1]:
                    stack[-1][atom] *= int(number)
                number = ''

        if c in atoms:
            stack.append(Counter({c:1}))
        elif c == '(':
            stack.append(c)
        elif c == ')':
            group = stack.pop()
            while stack[-1] != '(':
                group += stack.pop()
            stack[-1] = group
        else:
            raise ValueError(f'Unknown symbol {c}')

    print(stack, file=sys.stderr)
    return stack[-1]


def main():
    molecule = input()
    atoms = {}
    for _ in range(int(input())):
        atom, mass = input().split(':')
        atoms[atom] = float(mass)

    atoms_count = get_atoms_count(molecule, atoms)
    print(atoms_count, file=sys.stderr)

    mass = 0
    for atom, count in atoms_count.items():
        mass += count * atoms[atom]

    print(f'{mass:.4f} g.mol-1')


if __name__ == "__main__":
    main()

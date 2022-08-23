
# See https://www.codingame.com/ide/puzzle/crop-circles

import numpy
import sys


def log(*args):
    print(*args, file=sys.stderr, flush=True)


def parse_instruction(instruction):
    task = 'MOW'
    if instruction.startswith('PLANTMOW'):
        task = 'PLANTMOW'
        instruction = instruction.removeprefix('PLANTMOW')
    elif instruction.startswith('PLANT'):
        task = 'PLANT'
        instruction = instruction.removeprefix('PLANT')

    column, row = ord(instruction[0]) - ord('a'), ord(instruction[1]) - ord('a')
    diameter = int(instruction[2:])

    return task, column, row, diameter


def main():
    instructions = list(map(parse_instruction, input().split()))
    log(instructions)

    field = numpy.full((25, 19), True)
    rows, columns = numpy.meshgrid(numpy.arange(19), numpy.arange(25))

    for task, column, row, diameter in instructions:
        coordinates = ((rows - row) ** 2 + (columns - column) ** 2) * 4 <= diameter ** 2
        if task == 'MOW':
            field[coordinates] = False
        elif task == 'PLANT':
            field[coordinates] = True
        else:
            field[coordinates] ^= True

    for row in field:
        print(''.join('{}' if cell else '  ' for cell in row))


if __name__ == "__main__":
    main()

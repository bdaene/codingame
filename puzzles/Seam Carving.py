
# https://www.codingame.com/ide/puzzle/seam-carving


import numpy


def seam_carve(image):

    horizontal_energy = numpy.zeros(image.shape, dtype=image.dtype)
    horizontal_energy[:, 1:-1] = image[:, :-2] - image[:, 2:]
    vertical_energy = numpy.zeros(image.shape, dtype=image.dtype)
    vertical_energy[1:-1, :] = image[:-2, :] - image[2:, :]

    energy = abs(horizontal_energy) + abs(vertical_energy)

    path_energy = numpy.full((image.shape[0], image.shape[1]+2), 1 + energy.max() * energy.shape[0])
    path_energy[0, 1:-1] = energy[0, :]
    for j in range(1, image.shape[0]):
        path_energy[j, 1:-1] = energy[j, :] + numpy.minimum(
            numpy.minimum(path_energy[j-1, :-2], path_energy[j-1, 1:-1]), path_energy[j-1, 2:])

    x = path_energy[-1, :].argmin()
    print(path_energy[-1, x])

    image[-1, x-1:-1] = image[-1, x:]
    for j in reversed(range(image.shape[0]-1)):
        x += path_energy[j, x-1:x+2].argmin() - 1
        image[j, x-1:-1] = image[j, x:]

    image = image[:, :-1]

    return image


def main():
    assert input() == 'P2'
    width, height = map(int, input().split())
    target_width = int(input().split()[1])
    max_intensity = int(input())

    image = tuple(tuple(map(int, input().split())) for _ in range(height))
    image = numpy.array(image)

    for _ in range(target_width, width):
        image = seam_carve(image)


if __name__ == "__main__":
    main()

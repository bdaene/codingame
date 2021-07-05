
import numpy


def solve(n):
    corner = numpy.array([['+', '-'], ['|', '.']])

    for i in range(1, n):
        s = corner.shape[0]
        new_corner = numpy.full((2*s,2*s), '.')
        new_corner[:s,:s] = corner
        new_corner[-s:,:s] = corner[::-1,:]
        new_corner[:s,-s:] = corner[:,::-1]
        new_corner[s//2:s//2+s,s//2:s//2+s] = corner

        corner = new_corner

    return corner


if __name__ == "__main__":
    n, first_row, nb_rows = map(int, input().split())
    corner = solve(n)
    print('\n'.join(' '.join(row) for row in corner[first_row:first_row+nb_rows]))


# See https://www.codingame.com/ide/puzzle/music-scores

import numpy


def load_image():
    width, height = map(int, input().split())
    image = numpy.full((height, width), False)

    image_flat = image.ravel()
    pos = 0

    data = input().split()
    for c, l in zip(data[::2], map(int, data[1::2])):
        image_flat[pos:pos + l] = c == 'B'
        pos += l

    return image


def read_notes(image):
    staff, staff_start, staff_step = read_staff(image)

    def is_staff(column):
        return not (column & ~staff).any()

    # split image by note
    notes = []
    position = 0
    while position < image.shape[1]:
        while position < image.shape[1] and is_staff(image[:, position]):
            position += 1
        end = position
        while end < image.shape[1] and not is_staff(image[:, end]):
            end += 1
        notes.append(image[:, position:end])
        position = end
    notes = notes[:-1]  # remove blank after partition

    return [read_note(note, staff, staff_start, staff_step) for note in notes]


def read_staff(image):
    # Find staff
    position = 0
    while not image[:, position].any():
        position += 1
    staff = image[:, position]

    start = numpy.min(staff.nonzero())
    size = numpy.min((~staff[start:]).nonzero())
    stop = numpy.max(staff.nonzero()) + 1 - size
    step = (stop - start) // 4

    full_staff = staff.copy()
    for i in range(1, full_staff.shape[0] // step + 1):
        full_staff[i * step:] |= staff[:-i * step]
        full_staff[:-i * step] |= staff[i * step:]

    return full_staff, stop + size / 2 + step, -step / 2


def read_note(image, staff, staff_start, staff_step):
    tail_limit = image.sum(axis=0).mean() * 1.4
    image_no_tail = image[:, image.sum(axis=0) < tail_limit]  # remove tail
    mass = image_no_tail.sum(axis=1) * ~staff

    note_type = 'HQ'[bool(mass.sum() > (image.shape[1] / 2) ** 2 * numpy.pi * 0.2)]

    center_of_mass = (mass * numpy.arange(image.shape[0])).sum() / mass.sum()
    note_height = (center_of_mass - staff_start) / staff_step

    return 'CDEFGABCDEFG'[round(note_height)] + note_type


def main():
    image = load_image()
    notes = read_notes(image)
    print(*notes)


if __name__ == "__main__":
    main()

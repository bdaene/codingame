
# See https://www.codingame.com/ide/puzzle/music-scores

import numpy


def load_image():
    width, height = map(int, input().split())
    image = numpy.full((height, width), False)

    image_flat = image.ravel()
    pos = 0

    data = input().split()
    for c, l in zip(data[::2], map(int, data[1::2])):
        image_flat[pos:pos+l] = c == 'B'
        pos += l

    return image


def read_notes(image):
    # Find staff
    position = 0
    while sum(image[:, position]) == 0:
        position += 1
    staff = image[:, position]

    # split image by note
    notes = []
    while position < image.shape[1]:
        while position < image.shape[1] and (image[:, position] == staff).sum() == image.shape[0]:
            position += 1
        end = position
        while end < image.shape[1] and (image[:, end] == staff).sum() < image.shape[0]:
            end += 1
        notes.append(image[:, position:end])
        position = end
    notes = notes[:-1]  # remove blank after partition

    return [read_note(staff, note) for note in notes]


def read_note(staff, image):
    tail_limit = image.sum(axis=0).mean() * 1.4
    image_no_tail = image[:, image.sum(axis=0) < tail_limit]  # remove tail
    mass = image_no_tail.sum(axis=1) - staff*image_no_tail.shape[1]

    note_type = 'HQ'[bool(mass.sum() > (image.shape[1]/2)**2*numpy.pi*0.2)]

    center_of_mass = (mass * numpy.arange(image.shape[0])).sum() / mass.sum()
    staff_start, staff_end = numpy.max(staff.nonzero()), numpy.min(staff.nonzero())
    note_height = (center_of_mass-staff_start)/(staff_end-staff_start) * 8 + 2

    return 'CDEFGABCDEFG'[round(note_height)] + note_type


def main():
    image = load_image()
    notes = read_notes(image)
    print(*notes)


if __name__ == "__main__":
    main()

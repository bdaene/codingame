def get_digit(index):
    if index == 0:
        return '0'
    index -= 1
    number_length = 1
    while index >= number_length * 2**(number_length-1):
        index -= number_length * 2**(number_length-1)
        number_length += 1
    number, index = divmod(index, number_length)
    number += 2**(number_length-1)
    return f'{number:b}'[index]


# Simple but not efficient enough solution for big indexes
def get_digit(index):
    sequence = ''
    next_number = 0
    while len(sequence) <= index:
        sequence += f'{next_number:b}'
        next_number += 1
    return sequence[index]


def main():
    n = int(input())
    for i in range(n):
        index = int(input(), 2)
        print(get_digit(index))


if __name__ == "__main__":
    main()

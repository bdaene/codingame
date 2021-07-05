

def solve_1():
    base = int(input())
    digits = input()
    number = input()

    i = len(number) - 1
    while i >= 0 and number[i] == digits[-1]:
        i -= 1

    if i < 0:
        print(digits[1] + len(number) * digits[0])
    else:
        print(number[:i] + digits[digits.index(number[i]) + 1] + digits[0] * (len(number) - i - 1))


def solve_2():
    base = int(input())
    digits = input()
    number = input()

    value = 0
    for digit in number:
        value *= base
        value += digits.index(digit)

    value += 1

    number = []
    while value > 0:
        value, digit = divmod(value, base)
        number.append(digits[digit])

    print(''.join(number[::-1]))


def main():
    solve_1()
    solve_2()


if __name__ == "__main__":
    main()

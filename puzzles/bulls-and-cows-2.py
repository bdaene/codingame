# See https://www.codingame.com/ide/puzzle/bulls-and-cows-2


def get_bulls_and_cows(guess, secret):
    bulls = sum(g == s for g, s in zip(guess, secret))
    cows = len(set(guess) & set(secret)) - bulls
    return bulls, cows


FIRST_DIGITS = frozenset(map(str, range(1, 10)))
OTHER_DIGITS = frozenset(map(str, range(0, 10)))


def gen_possibilities(n, guesses, prefix=''):
    if len(prefix) == n:
        if all(get_bulls_and_cows(guess, prefix) == (bulls, cows) for guess, bulls, cows in guesses):
            yield prefix
        return

    for digit in (OTHER_DIGITS if prefix else FIRST_DIGITS) - set(prefix):
        secret = prefix + digit
        for guess, bulls, cows in guesses:
            b, c = get_bulls_and_cows(guess, secret)
            if b > bulls or b + n - len(secret) < bulls:
                break
            if b + c > bulls + cows or b + c + n - len(secret) < bulls + cows:
                break
        else:
            yield from gen_possibilities(n, guesses, secret)


def main():
    n = int(input())
    input()  # Discard first bulls and cows

    guesses = []

    while True:
        number = next(gen_possibilities(n, guesses))

        print(number)
        bulls, cows = map(int, input().split())

        guesses.append((number, bulls, cows))


if __name__ == "__main__":
    main()

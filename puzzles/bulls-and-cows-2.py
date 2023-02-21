# See https://www.codingame.com/ide/puzzle/bulls-and-cows-2
import sys
from time import perf_counter

ALLOWED_TIME = 0.050


def is_valid(n, prefix, guesses):
    missing_digits = n - len(prefix)
    for i, (guess, bulls, cattle) in enumerate(guesses):
        b = sum(g == s for g, s in zip(guess, prefix))
        if b > bulls or b + missing_digits < bulls:
            return False
        c = sum(p in guess for p in prefix)
        if c > cattle or c + missing_digits < cattle:
            return False

    return True


def gen_guesses(n):
    guesses = []

    current_guess = list(map(str, range(10)))
    current_guess[:2] = current_guess[:2][::-1]  # Skip permutations with 0 in front

    while True:
        guess = ''.join(current_guess[:n])
        bulls, cows = yield guess
        cattle = bulls + cows
        guesses.append((guess, bulls, cattle))
        stop_time = perf_counter() + ALLOWED_TIME

        valid_length = bulls

        while 0 <= valid_length < n and perf_counter() < stop_time:
            digit = min((digit for digit in current_guess[valid_length + 1:] if digit > current_guess[valid_length]),
                        default=None)
            if digit is None:
                valid_length -= 1
                continue

            index = current_guess.index(digit, valid_length + 1)
            current_guess[index], current_guess[valid_length] = current_guess[valid_length], digit
            current_guess[valid_length + 1:] = sorted(current_guess[valid_length + 1:])
            while valid_length < n and is_valid(n, current_guess[:valid_length + 1], guesses):
                valid_length += 1

        if valid_length < 0:
            yield None
            return
        print(f"{perf_counter() - (stop_time - ALLOWED_TIME):.6f}", file=sys.stderr)


def main():
    n = int(input())
    guesses = gen_guesses(n)
    guess = guesses.send(None)

    auto, secret = True, ''
    try:
        secret = input()  # Discard first bulls and cows
        int(secret)
    except ValueError:
        auto = False

    while guess is not None:
        print(guess)
        if auto:
            bulls, cattle = sum(g == s for g, s in zip(guess, secret)), sum(p in guess for p in secret)
            cows = cattle - bulls
            print(bulls, cows)
            if bulls == n:
                break
        else:
            bulls, cows = map(int, input().split())
        guess = guesses.send((bulls, cows))

    if guess is None:
        print("No solution!")


if __name__ == "__main__":
    main()

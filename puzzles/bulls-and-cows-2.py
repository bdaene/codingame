# See https://www.codingame.com/ide/puzzle/bulls-and-cows-2


def is_valid(n, prefix, guesses):
    missing_digits = n - len(prefix)
    for guess, bulls, cattle in guesses:
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

        valid_length = bulls

        while 0 <= valid_length < n:
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


def main():
    n = int(input())
    guesses = gen_guesses(n)
    guess = guesses.send(None)

    input()  # Discard first bulls and cows
    while True:
        print(guess)
        bulls, cows = map(int, input().split())
        guess = guesses.send((bulls, cows))


if __name__ == "__main__":
    main()

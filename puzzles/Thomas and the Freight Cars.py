
# https://www.codingame.com/ide/puzzle/thomas-and-the-freight-cars


def main():
    n = int(input())
    cars = list(map(int, input().split()))

    longest_increasing_sequence = [0]*len(cars)
    longest_decreasing_sequence = [0]*len(cars)

    for i in reversed(range(n)):
        longest_increasing_sequence[i] = 1 + max((longest_increasing_sequence[j] for j in range(i+1,n) if cars[i] < cars[j]), default=0)
        longest_decreasing_sequence[i] = 1 + max((longest_decreasing_sequence[j] for j in range(i+1,n) if cars[i] > cars[j]), default=0)

    print(max(longest_increasing_sequence[i] + longest_decreasing_sequence[i] - 1 for i in range(n)))


if __name__ == "__main__":
    main()

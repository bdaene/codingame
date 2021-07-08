

def main():
    row_up = input()
    row_down = input()

    c = len(row_up)
    a, b = divmod(c, 2)
    if b == 0:
        for i in reversed(range(a)):
            print('.'*i + row_up[:a-i] + row_up[c-(a-i):] + '.'*i)
    else:
        for i in reversed(range(a+1)):
            print('.'*i + row_up[:a-i] + row_up[a] + row_up[c-(a-i):] + '.'*i)

    c = len(row_down)
    a, b = divmod(c, 2)
    if b == 0:
        for i in range(a):
            print('.'*i + row_down[:a-i] + row_down[c-(a-i):] + '.'*i)
    else:
        for i in range(a+1):
            print('.'*i + row_down[:a-i] + row_down[a] + row_down[c-(a-i):] + '.'*i)


if __name__ == "__main__":
    main()

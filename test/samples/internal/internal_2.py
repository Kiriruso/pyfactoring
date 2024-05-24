a = 1

while a:
    print(a)
    x = 10

    if x + 10 > 19:
        while True:
            a = x + 10
            if a == 500:
                break
        print(x + a)

    while x > 5:
        x = x - 1

a, b, c = 1, 2, 3
x, y, z = 1, 2, 3

...

if a > b:
    local_variable = 10
    if a > c:
        print(a)
    elif c < b:
        print(b)
    else:
        print(c)
    print(local_variable)

...

if x > y:
    local_variable = 500
    if x > z:
        print(x)
    elif z < y:
        print(y)
    else:
        print(z)
    print(local_variable)

...

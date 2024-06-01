# ruff: noqa

while x > 10:
    y = 0
    x /= 2
    while True:
        y += x + 2

        while y > 1000:
            y -= 10
        else:
            break
    print(x + y)
else:
    print(x)

while __var_0__ > '__const_0__':
    __local_0__ = '__const_1__'
    __var_0__ /= '__const_2__'
    while '__const_3__':
        __local_0__ += __var_0__ + '__const_2__'

        while __local_0__ > '__const_4__':
            __local_0__ -= '__const_0__'
        else:
            break
    print(__var_0__ + __local_0__)
else:
    print(__var_0__)

# ================================ #

while x + y + z > i * j and i < j and x - y == z:
    print(x * i + y * j, sep='\n')

    while True:
        i, j = j // 2, i + 2
        print((x, z) > (i + j, y + j))

        while x - y * z > i:
            i += 50
        else:
            print(f"simple output: {i:20}", sep='\n')
            break
else:
    print("None data")

while __var_0__ + __var_1__ + __var_2__ > __var_3__ * __var_4__ and __var_3__ < __var_4__ and __var_0__ - __var_1__ == __var_2__:
    print(__var_0__ * __var_3__ + __var_1__ * __var_4__, sep='__const_0__')

    while '__const_1__':
        __var_3__, __var_4__ = __var_4__ // '__const_2__', __var_3__ + '__const_2__'
        print((__var_0__, __var_2__) > (__var_3__ + __var_4__, __var_1__ + __var_4__))

        while __var_0__ - __var_1__ * __var_2__ > __var_3__:
            __var_3__ += '__const_3__'
        else:
            print(f"simple output: {__var_3__:20}", sep='__const_0__')
            break
else:
    print('__const_4__')

# ================================ #

while True:
    l_1 = "string"
    l_2 = l_1 + "string"
    l_3 = l_2 + l_1 + "string"

    while len(l_1) < len(l_3) + len(l_2):
        l_1 = "_".join([l_1[0:10], l_2[0:10:2], l_3[3:9:3]])
        print(l_1, end='!')

    print("!", "end", "!")

while "__const_0__":
    __local_0__ = "__const_1__"
    __local_1__ = __local_0__ + "__const_1__"
    __local_2__ = __local_1__ + __local_0__ + "__const_1__"

    while len(__local_0__) < len(__local_2__) + len(__local_1__):
        __local_0__ = "__const_2__".join([__local_0__["__const_3__":"__const_4__"], __local_1__["__const_3__":"__const_4__":"__const_5__"], __local_2__["__const_6__":"__const_7__":"__const_6__"]])
        print(__local_0__, end="__const_8__")

    print("__const_8__", "__const_9__", "__const_8__")

# ================================ #

while v_1 <= 7.3:
    l_1 = v_1
    while l_1 > 5:
        l_2 = v_1 + l_1 + 13.2
        while l_2 + l_1 < 100:
            l_3 = 5 + 7.3 + 13.2
            while l_1 + v_1 > 4:
                l_4 = sum([l_1, l_2, l_3])

while __var_0__ <= "__const_0__":
    __local_0__ = __var_0__
    while __local_0__ > "__const_1__":
        __local_1__ = __var_0__ + __local_0__ + "__const_2__"
        while __local_1__ + __local_0__ < "__const_3__":
            __local_2__ = "__const_1__" + "__const_0__" + "__const_2__"
            while __local_0__ + __var_0__ > "__const_4__":
                __local_3__ = sum([__local_0__, __local_1__, __local_2__])

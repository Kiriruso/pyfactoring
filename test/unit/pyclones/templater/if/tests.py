# ruff: noqa

if a == 10:
    print(50)

if __var_0__ == '__const_0__':
    print('__const_1__')

# ================================ #

if i > j:
    print(i)
else:
    print(j)

if __var_0__ > __var_1__:
    print(__var_0__)
else:
    print(__var_1__)

# ================================ #

if a > b:
    some_variable = 10
    if a > c:
        print(a)
    else:
        if c < b:
            print(b)
        print(c)
    print(some_variable)

if __var_0__ > __var_1__:
    __local_0__ = '__const_0__'
    if __var_0__ > __local_1__:
        print(__var_0__)
    else:
        if __local_1__ < __var_1__:
            print(__var_1__)
        print(__local_1__)
    print(__local_0__)

# ================================ #

if x > y:
    print(x)
    local_var = True
    end_var = y
else:
    local_var = True
    other_var = 10
    end_var = x
    print(y)

if __var_0__ > __var_1__:
    print(__var_0__)
    __local_0__ = '__const_0__'
    __local_1__ = __var_1__
else:
    __local_0__ = '__const_0__'
    __local_1__ = '__const_1__'
    __local_2__ = __var_0__
    print(__var_1__)

# ================================ #

if x > y:
    print(x)
    z = 10
    if z < 10:
        print(z)
else:
    print(y)

if __var_0__ > __var_1__:
    print(__var_0__)
    __local_0__ = '__const_0__'
    if __local_0__ < '__const_0__':
        print(__local_0__)
else:
    print(__var_1__)

# ================================ #

if x + y > x * 10:
    print(x)
else:
    print(y)

if __var_0__ + __var_1__ > __var_0__ * '__const_0__':
    print(__var_0__)
else:
    print(__var_1__)

# ================================ #

if a > b and x < 10:
    print(a)
else:
    print(10)

if __var_0__ > __var_1__ and __var_2__ < '__const_0__':
    print(__var_0__)
else:
    print('__const_0__')

# ================================ #

if x > y + 50:
    z = x + y * 20

    if z < 50:
        print(z)
    else:
        z = x - y
        print(z)
        if x - y < 10:
            g = 1000
            print(g - 20)
        else:
            g = 2000
            print(g - 50)

    if k := z + y:
        p = 0
        if k < 500:
            x = 10
        elif k > 1000:
            y = 200
        else:
            p = 10000

        print(k >= z)

if __var_0__ > __var_1__ + '__const_0__':
    __local_0__ = __var_0__ + __var_1__ * '__const_1__'

    if __local_0__ < '__const_0__':
        print(__local_0__)
    else:
        __local_0__ = __var_0__ - __var_1__
        print(__local_0__)
        if __var_0__ - __var_1__ < '__const_2__':
            __local_1__ = '__const_3__'
            print(__local_1__ - '__const_1__')
        else:
            __local_1__ = '__const_4__'
            print(__local_1__ - '__const_0__')

    if __local_1__ := __local_0__ + __var_1__:
        __local_2__ = '__const_5__'
        if __local_1__ < '__const_6__':
            __var_0__ = '__const_2__'
        elif __local_1__ > '__const_3__':
            __var_1__ = '__const_7__'
        else:
            __local_2__ = '__const_8__'

        print(__local_1__ >= __local_0__)

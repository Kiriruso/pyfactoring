# ruff: noqa

def func_1(a, b, c):
    if a > b:
        some_variable = 10

        if a > c:
            print(a)
        else:
            for i in range(b):
                a += i * 50
                print(i)

        while some_variable:
            some_variable, r = divmod(some_variable, 10)
            print(r, "10")

def __function__(__var_0__, __var_1__, __var_2__):
    if __var_0__ > __var_1__:
        __local_0__ = '__const_0__'

        if __var_0__ > __var_2__:
            print(__var_0__)
        else:
            for __local_1__ in range(__var_1__):
                __var_0__ += __local_1__ * '__const_1__'
                print(__local_1__)

        while __local_0__:
            __local_0__, __local_1__ = divmod(__local_0__, '__const_0__')
            print(__local_1__, '__const_2__')

# ================================ #

def func_2(s: str):
    while True:
        x = 10 + random.randint(-5, 13)

        if x > 15:
            with open("random_path", "r", encoding="utf-8") as f:
                print(f.read())
        elif x < 5:
            sys.exit()
        else:
            match s:
                case "1":
                    for i in range(x):
                        for j in range(i):
                            if j % i == 0:
                                print(i + j)
                            else:
                                print(i if i // 2 > 100 else j)
                case "2":
                    try:
                        raise ValueError(100)
                    except ValueError as e:
                        print(e)
                case "3":
                    if int(s) + x == 12:
                        t = x, x + 1, x + 2
                        print(t)
                case "4":
                    class Class:
                        def __init__(self):
                            ...

                        def __str__(self):
                            return "text"

def __function__(__var_0__: str):
    while '__const_0__':
        __local_0__ = '__const_1__' + __local_1__.randint(-'__const_2__', '__const_3__')

        if __local_0__ > '__const_4__':
            with open('__const_5__', '__const_6__', encoding='__const_7__') as __local_2__:
                print(__local_2__.read())
        elif __local_0__ < '__const_2__':
            __local_2__.exit()
        else:
            match __var_0__:
                case '__const_8__':
                    for __local_2__ in range(__local_0__):
                        for __local_3__ in range(__local_2__):
                            if __local_3__ % __local_2__ == '__const_9__':
                                print(__local_2__ + __local_3__)
                            else:
                                print(__local_2__ if __local_2__ // '__const_10__' > '__const_11__' else __local_3__)
                case '__const_12__':
                    try:
                        raise ValueError('__const_11__')
                    except ValueError as __local_2__:
                        print(__local_2__)
                case '__const_13__':
                    if int(__var_0__) + __local_0__ == '__const_14__':
                        __local_2__ = __local_0__, __local_0__ + '__const_15__', __local_0__ + '__const_10__'
                        print(__local_2__)
                case '__const_16__':
                    class Class:
                        def __function__(__local_2__):
                            ...

                        def __function__(__local_2__):
                            return '__const_17__'

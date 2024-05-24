# ruff: noqa

for i in range(10):
    print(i)
else:
    print(10)

for __local_0__ in range('__const_0__'):
    print(__local_0__)
else:
    print('__const_0__')

# ================================ #

for _ in range(50):
    matrix = [[1, 2, 3, 4, 5] * 5]
    for i, row in enumerate(matrix):
        for j, elt in enumerate(row):
            print(elt)
        else:
            print("stop")
    else:
        print("stop")

for _ in range('__const_0__'):
    __local_0__ = [['__const_1__', '__const_2__', '__const_3__', '__const_4__', '__const_5__'] * '__const_5__']
    for __local_1__, __local_2__ in enumerate(__local_0__):
        for __local_3__, __local_4__ in enumerate(__local_2__):
            print(__local_4__)
        else:
            print('__const_6__')
    else:
        print('__const_6__')

# ================================ #

for key, values in d.items():
    print(f"key is {key}")
    for value in values:
        print(value)
        d.pop(key)
    else:
        print("okay!")

for __local_0__, __local_1__ in __var_0__.items():
    print(f"key is {__local_0__}")
    for __local_2__ in __local_1__:
        print(__local_2__)
        __var_0__.pop(__local_0__)
    else:
        print('__const_0__')

# ================================ #

async for values in data:
    for value in values:
        print(await value)
else:
    await data.close()

async for __local_0__ in __var_0__:
    for __local_1__ in __local_0__:
        print(await __local_1__)
else:
    await __var_0__.close()

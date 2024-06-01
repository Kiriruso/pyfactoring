# ruff: noqa

def simple():
    return 10

def __function__():
    return '__const_0__'

# ================================ #

def yield_var():
    some_var = 10
    yield some_var

def __function__():
    __local_0__ = '__const_0__'
    yield __local_0__

# ================================ #

def yield_const():
    yield 0

def __function__():
    yield '__const_0__'

# ================================ #

def yield_generator():
    some_gen = yield_var()
    yield from some_gen

def __function__():
    __local_0__ = yield_var()
    yield from __local_0__

# ================================ #

def wrapper():
    global g
    a, b = 10, 20

    def wrapped():
        nonlocal a, b
        return a + b

    return wrapped() + g

def __function__():
    global __var_0__
    __local_0__, __local_1__ = '__const_0__', '__const_1__'

    def __function__():
        nonlocal __local_0__, __local_1__
        return __local_0__ + __local_1__

    return wrapped() + __var_0__

# ================================ #

@simple_decorator
def arguments(p, /, x, y=10, *args, k=10, **kwargs):
    return p + y - x + args[k] - kwargs["some"]

@simple_decorator
def __function__(__var_0__, /, __var_1__, __var_2__='__const_0__', *__var_3__, __var_4__='__const_0__', **__var_5__):
    return __var_0__ + __var_2__ - __var_1__ + __var_3__[__var_4__] - __var_5__['__const_1__']

# ================================ #

@callable_decorator(x=10, y=y)
async def arguments(p, /, x, y=10, *args, k=10, **kwargs):
    await some_func()
    return p + y - x + args[k] - kwargs["some"]

@callable_decorator(x='__const_0__', y=__var_2__)
async def __function__(__var_0__, /, __var_1__, __var_2__='__const_0__', *__var_3__, __var_4__='__const_0__', **__var_5__):
    await some_func()
    return __var_0__ + __var_2__ - __var_1__ + __var_3__[__var_4__] - __var_5__['__const_1__']

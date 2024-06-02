# ruff: noqa

try:
    num = 1 / 0
except ZeroDivisionError as e:
    some_variable = 10
    print(e)
except Exception as e:
    some_variable = 20
    print(e)
finally:
    print("finally")

try:
    __local_0__ = '__const_0__' / '__const_1__'
except ZeroDivisionError as __local_0__:
    __local_1__ = '__const_2__'
    print(__local_0__)
except Exception as __local_0__:
    __local_1__ = '__const_3__'
    print(__local_0__)
finally:
    print('__const_4__')

# ================================ #

try:
    raise ExceptionGroup("some_group", [ValueError(1), TypeError(), ValueError(2)])
except* TypeError as eg:
    print(eg.exceptions)
except* ValueError as eg:
    print(eg.exceptions)
finally:
    print("starred")

try:
    raise ExceptionGroup('__const_0__', [ValueError('__const_1__'), TypeError(), ValueError('__const_2__')])
except* TypeError as __local_0__:
    print(__local_0__.exceptions)
except* ValueError as __local_0__:
    print(__local_0__.exceptions)
finally:
    print('__const_3__')

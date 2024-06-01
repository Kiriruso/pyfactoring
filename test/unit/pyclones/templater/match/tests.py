# ruff: noqa

match x:
    case "Relevant":
        ...

match __var_0__:
    case '__const_0__':
        ...

# ================================ #

match x:
    case [1, 2]:
        ...

match __var_0__:
    case ['__const_0__', '__const_1__']:
        ...

# ================================ #

match x:
    case [1, 2, *rest]:
        ...
    case [*_]:
        ...

match __var_0__:
    case ['__const_0__', '__const_1__', *__var_1__]:
        ...
    case [*_]:
        ...

# ================================ #

match x:
    case {1: _, 2: _}:
        ...
    case {**rest}:
        ...

match __var_0__:
    case {'__const_0__': _, '__const_1__': _}:
        ...
    case {**__var_1__}:
        ...

# ================================ #

match x:
    case Point2D(0, 0):
        ...
    case Point3D(x=0, y=0, z=0):
        ...

match __var_0__:
    case Point2D('__const_0__', '__const_0__'):
        ...
    case Point3D(x='__const_0__', y='__const_0__', z='__const_0__'):
        ...

# ================================ #

match x:
    case [x] as y:
        ...
    case _:
        ...

match __var_0__:
    case [__var_0__] as __var_1__:
        ...
    case _:
        ...

# ================================ #

match x:
    case [x] | (y):
        ...

match __var_0__:
    case [__var_0__] | (__var_1__):
        ...

# ================================ #

match type(node):
    case Name:
        node.id = scope.scoped_variable(node.id)
    case arg:
        node.arg = scope.scoped_variable(node.arg)
    case Constant:
        node.value = scope.scoped_constant(node.value)
    case Tuple | List | Set:
        node.elts = list(map(templatize, node.elts))
    case _:
        print("text")

match type(__var_0__):
    case __var_1__:
        __var_0__.id = __local_0__.scoped_variable(__var_0__.id)
    case __var_2__:
        __var_0__.arg = __local_0__.scoped_variable(__var_0__.arg)
    case __var_3__:
        __var_0__.value = __local_0__.scoped_constant(__var_0__.value)
    case __var_4__ | __var_5__ | __var_6__:
        __var_0__.elts = list(map(__local_1__, __var_0__.elts))
    case _:
        print('__const_0__')

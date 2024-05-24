# noqa

while x + y + z > i * j and i < j and x - y == z:
    print(x * i + y * j, sep='\n')

    while True:
        i, j = j // 2, i + 2
        print((x, z) > (i + j, y + j))

        while x - y * z > i:
            i += 50
        else:
            print(f"simple output: {i:^5}", sep='\n')
            break
else:
    print("None data")

while True:
    it = iter([1, 2, 3, 4])
    numbers = ((1, 2), (2, 3), (3, 4), (4, 5))
    d = {x: y for x, y in numbers if x > y}
    g = (n**2 for n in it if n > 5 if n < 10)


async def f(some: int = 10):
    await other_func(some, 20)

for i in range(n_months):
    A_ub[i, i] = 1
    b_ub[i] = max_production
    A_ub[n_months + i, n_months + i] = 1
    b_ub[n_months + i] = max_stock

for i in range(1, n_months):
    A_eq[i, i] = 1
    A_eq[i, n_months + i] = 1
    A_eq[i, n_months + i - 1] = -1
    b_eq[i] = demand[i]

if a > b:
    some_variable = 10
    if a > c:
        print(a)
    else:
        if c < b:
            print(b)
        print(c)
    print(some_variable)

clones: dict[str, Clone] = {}
dump = ast.unparse(transformer.visit(new_node))

if dump in clones:
    clones[dump].count += 1
    clones[dump].instances.append(ast_node)
else:
    clones.setdefault(dump, Clone(ast_node))

for dump, info in clones.items():
    if info.count <= min_clone_count:
        continue

    print(dump)
    print()

    for instance in info.instances:
        print(ast.unparse(instance))
        print()

    print()

for dump, info in clones.items():
    if info.count <= min_clone_count:
        print(info)

import ast

async for instance in info.instances:
    print(ast.unparse(instance))
    print()


with scope() as sc:
    with open("filepath.py", "r", encoding="utf-8") as file, open("aboba.txt", "w+") as aboba:
        data = file.read()
        aboba.write(file)

import ast

for dump, info in clones.items():
    if info.count <= min_clone_count:
        continue
    print(dump)
    print()
    for instance in info.instances:
        print(ast.unparse(instance))
        print()
    print()

import ast
import warnings
from pydioms import ASTInspectedNode, ASTInspectedLeaf, CountingType

def make_inspected_tree(root) -> ASTInspectedNode | ASTInspectedLeaf:
    if not root:
        return ASTInspectedNode()

    if not isinstance(root, ast.AST):
        leaf_name = root
        return ASTInspectedLeaf(leaf_name, CountingType.OPERAND)

    if type(root) in AST_SPECIFIC_NODES:
        return _make_specific(root)

    ast_name, ast_body = _info_from_ast(root)
    ast_info = AST_NODES_INFO.get(ast_name)

    if ast_info is None:
        warnings.warn(f"Синтаксическая конструкция '{ast_name}' не поддерживается.")
        return ASTInspectedNode()

    inspected_node = ASTInspectedNode(ast_info.name, ast_info.count_as)
    inspected_node.realize_subtree = ast_info.name in AST_REALIZE_SUBTREE_NODES
    inspected_node.ast = root

    for ast_child_name in ast_info.children_names:
        ast_child_children = ast_body.get(ast_child_name)

        if isinstance(ast_child_children, list):
            child_realize_subtree = inspected_node.realize_subtree
            child_realize_subtree &= ast_child_name in ("body", "orelse", "finalbody")

            inspected_list = []
            for ast_child_child in ast_child_children:
                inspected_child_child = make_inspected_tree(ast_child_child)
                inspected_child_child.realize_subtree |= child_realize_subtree
                inspected_child_child.ast = ast_child_child

                inspected_list.append(inspected_child_child)
            inspected_list = _make_list(inspected_list)

            inspected_node.append(inspected_list)
            continue

        if (
            ast_child_children is None
            and AST_PRESENTATION_LEAVES.get(inspected_node.name) == ast_child_name
        ):
            inspected_node.append(ASTInspectedLeaf())
            continue

        inspected_node.append(make_inspected_tree(ast_child_children))

    return inspected_node

while a:
    print(a)
    x = 10

    if x + 10 > 19:
        while True:
            a = x + 10
            if a == 500:
                break
        break

    while x > 5:
        x = x - 1

while b:
    print(b)
    z = 300

    if z + 300 > 421:
        while True:
            b = z + 300
            if b == 876:
                break
        break

    while z > 200:
        z = z - 10

for i in range(x):
    y = x + i * 2
    print(y)

    for j in range(y):
        x = y + j * 10
        print(x)
    else:
        print(50)

    if x + y > x * 10:
        print(x)
    else:
        print(y)
else:
    print(0)
    while b:
        print(b)
        z = 300

        if z + 300 > 421:
            while True:
                b = z + 300
                if b == 876:
                    break
            break

        for i in range(x):
            y = x + i * 2
            print(y)

        while z > 200:
            z = z - 10

for j in range(y):
    x = y + j * 10
    print(x)
else:
    print(50)

for i, obj in enumerate(my_list):
    z = obj + i / 3
    print(z)
else:
    print(1.0)

for i in range(10):
    x = z - i * 5
    print(x)
else:
    print(2)

for i in range(500):
    x = z - i * 13
    print(x)
else:
    print(2754)

for item in my_list:
    k = k + item
    print(k)
else:
    print("text")

for key, value in my_dict.items():
    k = key + value
    print(k)
else:
    print(key, value)




for i in range(z):
    k = k + i % 5
    print(k)

for i in range(x + y):
    z = z + i / 3
    print(z)

for i in range(y + z):
    k = k + i % 5

for i in range(x):
    y = y + i * 2
    print(y)

def my_function(p1, p2, p3):
    p4 = p1 + p2 * p3
    print(p4)


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

if x > 10:
    node = ast.Tree()
    match type(node):
        case ast.Name:
            node.id = scope.scoped_variable(node.id)
        case ast.arg:
            node.arg = scope.scoped_variable(node.arg)
        case ast.Constant:
            node.value = scope.scoped_constant(node.value)
        case ast.Tuple | ast.List | ast.Set:
            node.elts = list(map(templatize, node.elts))
        case _:
            print("aboba")

match x:
    case "Relevant":
        ...

match x:
    case None:
        ...

match x:
    case [1, 2]:
        ...

match x:
    case [1, 2, *rest]:
        ...
    case [*_]:
        ...

match x:
    case {1: _, 2: _}:
        ...
    case {**rest}:
        ...

match x:
    case Point2D(0, 0):
        ...
    case Point3D(x=0, y=0, z=0):
        ...

match x:
    case [x] as y:
        ...
    case _:
        ...

match x:
    case [x] | (y):
        ...

try:
    raise ExceptionGroup("some_group", [ValueError(1), TypeError(), ValueError(2)])
except* TypeError as eg:
    print(eg.exceptions)
except* ValueError as eg:
    print(eg.exceptions)
finally:
    print("starred")

if True:
    lambda p, /, x, y=10, *args, k=10, **kwargs: x == 0


@text_decorator
def some_function(p, /, x, y=10, *args, k=10, **kwargs):
    global g
    nonlocal a, b
    return p + y - x + g

@callable_decorator(x=10, y=y)
def some_function(p, /, x, y=10, *args, k=10, **kwargs):
    global g
    nonlocal a, b
    return p + y - x + g

def a():
    yield some_var

def b():
    yield 0

def c():
    yield from some_gen
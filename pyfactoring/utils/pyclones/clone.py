import ast
import copy
import pathlib

from pyfactoring import extracting

min_clone_count = 0  # default 1

HANDLE_ASTS = (
    "If",
    "While",
    "For",
)


class Scope:
    def __init__(self, outer: "Scope" = None):
        self.constants = {}
        self.variables = {}

        if outer:
            self.constants = outer.constants.copy()
            self.variables = outer.variables.copy()

    def var(self, id_: str) -> str:
        if id_ not in self.variables:
            self.variables[id_] = f"__var_{len(self.variables)}__"
        return self.variables[id_]

    def const(self, value_: str) -> str:
        if value_ not in self.constants:
            self.constants[value_] = f"__const_{len(self.constants)}__"
        return self.constants[value_]


class ASTTransformer(ast.NodeTransformer):
    def __init__(self):
        self.scope = None
        self.scope_stack = []

    def visit_Assign(self, node: ast.Assign) -> ast.AST:
        for target in node.targets:
            setattr(target, "id", self.scope.var(target.id))

        if isinstance(node.value, ast.Name):
            setattr(node.value, "id", self.scope.var(node.value.id))
        elif isinstance(node.value, ast.Constant):
            setattr(node.value, "value", self.scope.const(node.value.value))
        else:
            setattr(node, "value", self.visit(node.value))

        return node

    def visit_AugAssign(self, node: ast.AugAssign) -> ast.AST:
        node.target.id = self.scope.var(node.target.id)

        # todo: пропустим изменение оператора

        if isinstance(node.value, ast.Name):
            setattr(node.value, "id", self.scope.var(node.value.id))
        elif isinstance(node.value, ast.Constant):
            setattr(node.value, "value", self.scope.const(node.value.value))

        return node

    def visit_Expr(self, node: ast.Expr) -> ast.AST:
        if isinstance(node.value, ast.Name):
            setattr(node.value, "id", self.scope.var(node.value.id))
        elif isinstance(node.value, ast.Constant):
            setattr(node.value, "value", self.scope.const(node.value.value))
        return self.generic_visit(node)

    def visit_Yield(self, node: ast.Yield) -> ast.AST:
        if isinstance(node.value, ast.Name):
            setattr(node.value, "id", self.scope.var(node.value.id))
        elif isinstance(node.value, ast.Constant):
            setattr(node.value, "value", self.scope.const(node.value.value))
        return self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> ast.AST:
        if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
            setattr(node.func.value, "id", self.scope.var(node.func.value.id))

        for i, arg in enumerate(node.args):
            if isinstance(arg, ast.Name):
                setattr(node.args[i], "id", self.scope.var(node.args[i].id))
            elif isinstance(arg, ast.Constant):
                setattr(node.args[i], "value", self.scope.const(node.args[i].value))

        return self.generic_visit(node)

    def visit_Compare(self, node: ast.Compare) -> ast.AST:
        if isinstance(node.left, ast.Name):
            setattr(node.left, "id", self.scope.var(node.left.id))
        elif isinstance(node.left, ast.Constant):
            setattr(node.left, "value", self.scope.const(node.left.value))
        else:
            setattr(node, "left", self.visit(node.left))

        # todo: пропустим изменение оператора

        for i, arg in enumerate(node.comparators):
            if isinstance(arg, ast.Name):
                setattr(arg, "id", self.scope.var(arg.id))
            elif isinstance(arg, ast.Constant):
                setattr(arg, "value", self.scope.const(arg.value))
            else:
                node.comparators[i] = self.visit(arg)

        return node

    def visit_BinOp(self, node: ast.BinOp) -> ast.AST:
        if isinstance(node.left, ast.Name):
            setattr(node.left, "id", self.scope.var(node.left.id))
        elif isinstance(node.left, ast.Constant):
            setattr(node.left, "value", self.scope.const(node.left.value))
        else:
            setattr(node, "left", self.visit(node.left))

        # todo: пропустим изменение оператора

        if isinstance(node.right, ast.Name):
            setattr(node.right, "id", self.scope.var(node.right.id))
        elif isinstance(node.right, ast.Constant):
            setattr(node.right, "value", self.scope.const(node.right.value))
        else:
            setattr(node, "right", self.visit(node.right))

        return node

    def _if_or_while_visit(self, node: ast.If | ast.While) -> ast.AST:
        if self.scope is None:
            self.scope = Scope()
        else:
            self.scope_stack.append(self.scope)
            self.scope = Scope(self.scope_stack[-1])

        if isinstance(node.test, ast.Name):
            setattr(node.test, "id", self.scope.var(node.test.id))
        else:
            setattr(node, "test", self.visit(node.test))

        self.scope_stack.append(self.scope)

        self.scope = Scope(self.scope_stack[-1])
        node.body = list(map(self.visit, node.body))

        self.scope = Scope(self.scope_stack[-1])
        node.orelse = list(map(self.visit, node.orelse))

        self.scope = self.scope_stack.pop()

        if self.scope_stack:
            self.scope = self.scope_stack.pop()
        else:
            self.scope = None

        return node

    def visit_If(self, node: ast.If) -> ast.AST:
        return self._if_or_while_visit(node)

    def visit_While(self, node: ast.While) -> ast.AST:
        return self._if_or_while_visit(node)

    def visit_For(self, node: ast.For) -> ast.AST:
        if self.scope is None:
            self.scope = Scope()
        else:
            self.scope_stack.append(self.scope)
            self.scope = Scope(self.scope_stack[-1])

        if isinstance(node.target, ast.Name):
            setattr(node.target, "id", self.scope.var(node.target.id))
        elif isinstance(node.target, (ast.Tuple, ast.List, ast.Set)):
            for elt in node.target.elts:
                if isinstance(elt, ast.Name):
                    setattr(elt, "id", self.scope.var(elt.id))
                elif isinstance(elt, ast.Constant):
                    setattr(elt, "value", self.scope.const(elt.value))

        if isinstance(node.iter, ast.Name):
            setattr(node.iter, "id", self.scope.var(node.iter.id))
        else:
            setattr(node, "iter", self.visit(node.iter))

        self.scope_stack.append(self.scope)

        self.scope = Scope(self.scope_stack[-1])
        node.body = list(map(self.visit, node.body))

        self.scope = Scope(self.scope_stack[-1])
        node.orelse = list(map(self.visit, node.orelse))

        self.scope = self.scope_stack.pop()

        if self.scope_stack:
            self.scope = self.scope_stack.pop()
        else:
            self.scope = None

        return node


class Clone:
    def __init__(self, node: ast.AST = None):
        self.count: int = 1
        self.instances: list[ast.AST] = []

        if node is not None:
            self.instances.append(node)


def is_handle_node(node: ast.AST) -> bool:
    return type(node).__name__ in HANDLE_ASTS


if __name__ == "__main__":
    target = pathlib.Path(r"D:\Projects\Pet\Python\pyfactoring\pyfactoring\utils\pyclones\simple.py")
    module, source = extracting.extract_ast(target), extracting.extract_source(target)

    transformer = ASTTransformer()

    clones: dict[str, Clone] = {}
    for node in ast.walk(module):
        if is_handle_node(node):
            new_node = copy.deepcopy(node)
            dump = ast.unparse(transformer.visit(new_node))
            if dump in clones:
                clones[dump].count += 1
                clones[dump].instances.append(node)
            else:
                clones.setdefault(dump, Clone(node))

    for dump, info in clones.items():
        if info.count <= min_clone_count:
            continue

        print(dump)
        print()
        for instance in info.instances:
            print(ast.unparse(instance))
            print()
        print()

# Будем перебирать все допустимые конструкции и искать клоны 1, 2 и 3 типов
# затем надо проводить фильтрацию исходя из заданных параметров:
# - количество клонов;
# - длина клонов.
#
# А также фильтровать клоны, входящие в другие клоны

# Задачи:
# 1. Определить все допустимые конструкции (возможно взять те, которые определены для идиом)
# 2. Реализовать поиск в лоб точных клонов 1 типа
    # 2.1 Выбрать блок кода для анализа из AST
    # 2.2 Будем выбирать из списка доступных для обработки
    # 2.3 Добавить подсчет переменных, придумать как организовать scope, константы скип
# 3. Реализовать алгоритм упрощения блока кода, для его анализа и поиска клонов 2 и 3 типа
# 4. Реализовать поиск оставшихся клонов
# 5. Определить параметры фильтрации
# 6. Создать алгоритм фильтрации по заданным параметрам
# 7. Реализовать алгоритм фильтрации входящих друг в друга блоков кода

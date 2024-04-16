import ast
import copy
import pathlib

from pyfactoring import extracting


HANDLE_ASTS = (
    "If",
    # "For",
)


class Scope:
    def __init__(self, outer: "Scope" = None):
        self.context = {}
        if outer:
            self.context = outer.context.copy()

    def get(self, name: str) -> str:
        if name not in self.context:
            self.context[name] = f"__var_{len(self.context)}__"
        return self.context[name]


class ASTTransformer(ast.NodeTransformer):
    def __init__(self):
        self.scope = None
        self.scope_stack = []

    def visit_Expr(self, node: ast.Expr) -> ast.AST:
        if isinstance(node.value, ast.Name):
            setattr(node.value, "id", self.scope.get(node.value.id))
        elif isinstance(node.value, ast.Constant):
            setattr(node.value, "value", "__const__")
        return self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> ast.AST:
        for i, arg in enumerate(node.args):
            if isinstance(arg, ast.Name):
                setattr(node.args[i], "id", self.scope.get(node.args[i].id))
            elif isinstance(arg, ast.Constant):
                setattr(node.args[i], "value", "__const__")
        return self.generic_visit(node)

    def visit_Compare(self, node: ast.Compare) -> ast.AST:
        if isinstance(node.left, ast.Name):
            setattr(node.left, "id", self.scope.get(node.left.id))
        elif isinstance(node.left, ast.Constant):
            setattr(node.left, "value", "__const__")

        # Изменение оператора рассматривать не будем

        for i, arg in enumerate(node.comparators):
            if isinstance(arg, ast.Name):
                setattr(arg, "id", self.scope.get(arg.id))
            elif isinstance(arg, ast.Constant):
                setattr(arg, "value", f"__const__")
            else:
                node.comparators[i] = self.visit(arg)

        return self.generic_visit(node)

    def visit_If(self, node: ast.If) -> ast.AST:
        if self.scope is None:
            self.scope = Scope()
        else:
            self.scope_stack.append(self.scope)
            self.scope = Scope(self.scope_stack[-1])

        if isinstance(node.test, ast.Name):
            setattr(node.test, "id", self.scope.get(node.test.id))
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

    def visit_Assign(self, node: ast.Assign) -> ast.AST:
        for target in node.targets:
            target.id = self.scope.get(target.id)

        if isinstance(node.value, ast.Name):
            setattr(node.value, "id", self.scope.get(node.value.id))
        elif isinstance(node.value, ast.Constant):
            setattr(node.value, "value", "__const__")

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

    print('=' * 120)
    for dump, info in clones.items():
        print(dump)
        print()
        for instance in info.instances:
            print(ast.unparse(instance))
            print()
        print('=' * 120)

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

    # def visit_Yield(self, node: ast.Yield) -> ast.AST:
    #     if isinstance(node.value, ast.Name):
    #         setattr(node.value, "id", "__var__")
    #     elif isinstance(node.value, ast.Constant):
    #         setattr(node.value, "value", "__const__")
    #     return self.generic_visit(node)
    #
    # def visit_YieldFrom(self, node: ast.YieldFrom) -> ast.AST:
    #     setattr(node.value, "id", "__gen__")
    #     return self.generic_visit(node)

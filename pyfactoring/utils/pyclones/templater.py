import ast
import contextlib

from pyfactoring.utils.pyclones.scope import Scope


class Templater(ast.NodeTransformer):
    def __init__(self):
        self._scope: Scope | None = None
        self._scope_stack: list[Scope] = []
        self._constants: dict[str, str] = {}
        self._modules: set[str] = set()

    @contextlib.contextmanager
    def scope(self):
        if self._scope is not None:
            self._scope_stack.append(self._scope)
            self._scope = Scope(self._scope)
        else:
            self._scope = Scope()
        try:
            yield
        finally:
            if self._scope_stack:
                self._scope = self._scope_stack.pop()
            else:
                self._scope = None

    def visit_alias(self, node: ast.alias) -> ast.AST:
        if node.asname:
            self._modules.add(node.asname)
        else:
            self._modules.add(node.name)
        return node

    def visit_Import(self, node: ast.Import) -> ast.AST:
        return self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> ast.AST:
        self._modules.add(node.module)
        return self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> ast.AST:
        node.targets = list(map(self._templatize, node.targets))
        node.value = self._templatize(node.value)
        return node

    def visit_AugAssign(self, node: ast.AugAssign) -> ast.AST:
        node.target = self._templatize(node.target)
        # todo: пропустим изменение оператора
        node.value = self._templatize(node.value)
        return node

    def visit_AnnAssign(self, node: ast.AnnAssign) -> ast.AST:
        node.target = self._templatize(node.target)
        node.value = self._templatize(node.value)
        return node

    def visit_Attribute(self, node: ast.Attribute) -> ast.AST:
        if isinstance(node.value, (ast.Name, ast.Constant)):
            node.value = self._templatize(node.value)
        else:
            node.value = self.visit(node.value)
        return node

    def visit_Subscript(self, node: ast.Subscript) -> ast.AST:
        node.value = self._templatize(node.value)

        if isinstance(node.slice, (ast.Name, ast.Constant)):
            node.slice = self._templatize(node.slice)
        elif isinstance(node.slice, ast.Tuple):
            node.slice.elts = self.visit_collections(node.slice.elts)
            node.slice.dims = self.visit_collections(node.slice.dims)
        else:
            node.slice = self.visit(node.slice)

        return node

    def visit_Slice(self, node: ast.Slice) -> ast.AST:
        if node.lower:
            node.lower = self._templatize(node.lower)

        if node.upper:
            node.upper = self._templatize(node.upper)

        if node.step:
            node.step = self._templatize(node.step)

        return node

    def visit_Expr(self, node: ast.Expr) -> ast.AST:
        node.value = self._templatize(node.value)
        return node

    def visit_Yield(self, node: ast.Yield) -> ast.AST:
        if node.value:
            node.value = self._templatize(node.value)
        return node

    def visit_keyword(self, node: ast.keyword) -> ast.AST:
        node.value = self._templatize(node.value)
        return node

    def visit_Call(self, node: ast.Call) -> ast.AST:
        if isinstance(node.func, ast.Attribute):
            node.func = self.visit(node.func)
        node.args = self.visit_collections(node.args)
        node.keywords = self.visit_collections(node.keywords)
        return node

    def visit_Compare(self, node: ast.Compare) -> ast.AST:
        node.left = self._templatize(node.left)
        # todo: пропустим изменение оператора
        node.comparators = list(map(self._templatize, node.comparators))
        return node

    def visit_UnaryOp(self, node: ast.UnaryOp) -> ast.AST:
        node.operand = self._templatize(node.operand)
        # todo: пропустим изменение оператора
        return node

    def visit_BinOp(self, node: ast.BinOp) -> ast.AST:
        node.left = self._templatize(node.left)
        # todo: пропустим изменение оператора
        node.right = self._templatize(node.right)
        return node

    def visit_Module(self, node: ast.Module) -> ast.AST:
        with self.scope():
            node.body = self.visit_collections(node.body)
        return node

    def visit_If(self, node: ast.If) -> ast.AST:
        return self._if_for_while_visit(node)

    def visit_IfExp(self, node: ast.IfExp) -> ast.AST:
        return self._if_for_while_visit(node)

    def visit_While(self, node: ast.While) -> ast.AST:
        return self._if_for_while_visit(node)

    def visit_For(self, node: ast.For) -> ast.AST:
        return self._if_for_while_visit(node)

    def visit_collections(
            self, body: list[ast.stmt | ast.expr | ast.keyword]
    ) -> list[ast.stmt | ast.expr | ast.keyword]:
        return list(map(self._templatize, body))

    def _templatize_name(self, node: ast.Name):
        if node.id not in self._modules:
            node.id = self._scope.var(node.id)

    def _templatize_const(self, node: ast.Constant):
        if node.value in self._constants.values():
            return

        if node.value not in self._constants.keys():
            constant_id = len(self._constants)
            self._constants[node.value] = f"__const_{constant_id}__"

        node.value = self._constants[node.value]

    def _templatize(self, node):
        if isinstance(node, ast.Name):
            self._templatize_name(node)
            return node

        if isinstance(node, ast.Constant):
            self._templatize_const(node)
            return node

        if isinstance(node, ast.Tuple | ast.List | ast.Set):
            node.elts = list(map(self._templatize, node.elts))
            return node

        return self.visit(node)

    def _if_for_while_visit(self, node: ast.If | ast.IfExp | ast.While | ast.For) -> ast.AST:
        with self.scope():
            if isinstance(node, ast.For):
                node.target = self._templatize(node.target)
                node.iter = self._templatize(node.iter)
            else:
                node.test = self._templatize(node.test)

            with self.scope():
                if isinstance(node.body, list):
                    node.body = self.visit_collections(node.body)
                else:
                    node.body = self._templatize(node.body)

            with self.scope():
                if isinstance(node.orelse, list):
                    node.orelse = self.visit_collections(node.orelse)
                else:
                    node.orelse = self._templatize(node.orelse)

        return node

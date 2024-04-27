import ast
import contextlib

from pyfactoring.utils.pyclones.scope import Scope


class Templater(ast.NodeTransformer):
    __slots__ = ["_scope", "_scope_stack"]

    def __init__(self):
        self._scope: Scope | None = None
        self._scope_stack: list[Scope] = []

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
            self._scope.add_import(node.asname)
        else:
            self._scope.add_import(node.name)
        return node

    def visit_Import(self, node: ast.Import) -> ast.AST:
        return self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> ast.AST:
        self._scope.add_import(node.module)
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
            node.slice.elts = self.visit_collection(node.slice.elts)
            node.slice.dims = self.visit_collection(node.slice.dims)
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

    def visit_NamedExpr(self, node: ast.NamedExpr) -> ast.AST:
        node.target = self._templatize(node.target)
        node.value = self._templatize(node.value)
        return node

    def visit_Return(self, node: ast.Return) -> ast.AST:
        if node.value:
            node.value = self._templatize(node.value)
        return node

    def visit_Yield(self, node: ast.Yield) -> ast.AST:
        if node.value:
            node.value = self._templatize(node.value)
        return node

    def visit_YieldFrom(self, node: ast.YieldFrom) -> ast.AST:
        node.value = self._templatize(node.value)
        return node

    def visit_keyword(self, node: ast.keyword) -> ast.AST:
        node.value = self._templatize(node.value)
        return node

    def visit_Call(self, node: ast.Call) -> ast.AST:
        if isinstance(node.func, ast.Attribute):
            node.func = self.visit(node.func)
        node.args = self.visit_collection(node.args)
        node.keywords = self.visit_collection(node.keywords)
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
            node.body = self.visit_collection(node.body)
        return node

    def visit_If(self, node: ast.If) -> ast.AST:
        return self._if_for_while_visit(node)

    def visit_IfExp(self, node: ast.IfExp) -> ast.AST:
        return self._if_for_while_visit(node)

    def visit_While(self, node: ast.While) -> ast.AST:
        return self._if_for_while_visit(node)

    def visit_For(self, node: ast.For) -> ast.AST:
        return self._if_for_while_visit(node)

    def visit_AsyncFor(self, node: ast.AsyncFor) -> ast.AST:
        return self.visit_For(node)

    def visit_With(self, node: ast.With) -> ast.AST:
        with self.scope():
            node.items = self.visit_collection(node.items)
            with self.scope():
                node.body = self.visit_collection(node.body)
        return node

    def visit_AsyncWith(self, node: ast.AsyncWith) -> ast.AST:
        return self.visit_With(node)

    def visit_withitem(self, node: ast.withitem) -> ast.AST:
        node.context_expr = self.visit(node.context_expr)
        if node.optional_vars:
            if isinstance(node.optional_vars, ast.Name):
                node.optional_vars = self._templatize(node.optional_vars)
            else:
                node.optional_vars = self.visit_collection(node.optional_vars)
        return node

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.AST:
        with self.scope():
            node.args = self.visit(node.args)
            with self.scope():
                node.body = self.visit_collection(node.body)
        return node

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> ast.AST:
        return self.visit_FunctionDef(node)

    def visit_Lambda(self, node: ast.Lambda) -> ast.AST:
        with self.scope():
            node.args = self.visit(node.args)
            node.body = self.visit(node.body)
        return node

    def visit_Try(self, node: ast.Try) -> ast.AST:
        with self.scope():
            with self.scope():
                node.body = self.visit_collection(node.body)

            with self.scope():
                node.handlers = self.visit_collection(node.handlers)

            with self.scope():
                node.orelse = self.visit_collection(node.orelse)

            with self.scope():
                node.finalbody = self.visit_collection(node.finalbody)

        # todo: реализовать шаблонизатор Exception'ов

        return node

    def visit_TryStar(self, node: ast.TryStar) -> ast.AST:
        return self.visit_Try(node)

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> ast.AST:
        with self.scope():
            if node.name:
                node.name = self._scope.scoped_variable(node.name)  # todo: мб убрать
            node.body = self.visit_collection(node.body)
        return node

    # todo: match

    def visit_arguments(self, node: ast.arguments) -> ast.AST:
        node.posonlyargs = self.visit_collection(node.posonlyargs)
        node.args = self.visit_collection(node.args)

        if node.vararg:
            node.vararg = self._templatize(node.vararg)

        node.kwonlyargs = self.visit_collection(node.kwonlyargs)
        node.kw_defaults = self.visit_collection(node.kw_defaults)

        if node.kwarg:
            node.kwarg = self._templatize(node.kwarg)

        node.defaults = self.visit_collection(node.defaults)
        return node

    def visit_collection(
            self, body: list[ast.stmt | ast.expr | ast.keyword]
    ) -> list[ast.stmt | ast.expr | ast.keyword]:
        return list(map(self._templatize, body))

    def _templatize(self, node):
        match type(node):
            case ast.Name:
                node.id = self._scope.scoped_variable(node.id)
            case ast.arg:
                node.arg = self._scope.scoped_variable(node.arg)
            case ast.Constant:
                node.value = self._scope.scoped_constant(node.value)
            case ast.Tuple | ast.List | ast.Set:
                node.elts = list(map(self._templatize, node.elts))
            case _:
                return self.visit(node)
        return node

    def _if_for_while_visit(self, node: ast.If | ast.IfExp | ast.While | ast.For) -> ast.AST:
        with self.scope():
            match type(node):
                case ast.For | ast.AsyncFor:
                    node.target = self._templatize(node.target)
                    node.iter = self._templatize(node.iter)
                case ast.If, ast.IfExp, ast.While:
                    node.test = self._templatize(node.test)

            with self.scope():
                if isinstance(node.body, list):
                    node.body = self.visit_collection(node.body)
                else:
                    node.body = self._templatize(node.body)

            with self.scope():
                if isinstance(node.orelse, list):
                    node.orelse = self.visit_collection(node.orelse)
                else:
                    node.orelse = self._templatize(node.orelse)

        return node

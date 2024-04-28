import ast
import builtins
import contextlib

from pyfactoring.utils.pyclones.scope import Scope


class Templater(ast.NodeTransformer):
    __slots__ = ["_scope", "_scope_stack", "_local"]

    def __init__(self):
        self._scope: Scope | None = None
        self._scope_stack: list[Scope] = []
        self._local: bool = False

    @contextlib.contextmanager
    def scope(self, *, local: bool = False):
        self._local = local

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

            self._local = False

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
        node.targets = self._templatize(node.targets)
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

    def visit_Delete(self, node: ast.Delete) -> ast.AST:
        node.targets = self._templatize(node.targets)
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
            node.slice.elts = self._templatize(node.slice.elts)
            node.slice.dims = self._templatize(node.slice.dims)
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

    def visit_Raise(self, node: ast.Raise) -> ast.AST:
        if node.exc:
            node.exc = self._templatize(node.exc)
        if node.cause:
            node.cause = self._templatize(node.cause)
        return node

    def visit_Assert(self, node: ast.Assert) -> ast.AST:
        node.test = self._templatize(node.test)
        if node.msg:
            node.msg = self._templatize(node.msg)
        return node

    def visit_Yield(self, node: ast.Yield) -> ast.AST:
        if node.value:
            node.value = self._templatize(node.value)
        return node

    def visit_YieldFrom(self, node: ast.YieldFrom) -> ast.AST:
        node.value = self._templatize(node.value)
        return node

    def visit_Await(self, node: ast.Await) -> ast.AST:
        node.value = self._templatize(node.value)
        return node

    def visit_Global(self, node: ast.Global) -> ast.AST:
        node.names = self._templatize(node.names)
        return node

    def visit_Nonlocal(self, node: ast.Nonlocal) -> ast.AST:
        node.names = self._templatize(node.names)
        return node

    def visit_keyword(self, node: ast.keyword) -> ast.AST:
        node.value = self._templatize(node.value)
        return node

    def visit_Call(self, node: ast.Call) -> ast.AST:
        if isinstance(node.func, ast.Attribute):
            node.func = self.visit(node.func)
        node.args = self._templatize(node.args)
        node.keywords = self._templatize(node.keywords)
        return node

    def visit_Compare(self, node: ast.Compare) -> ast.AST:
        node.left = self._templatize(node.left)
        # todo: пропустим изменение оператора
        node.comparators = self._templatize(node.comparators)
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

    def visit_BoolOp(self, node: ast.BoolOp) -> ast.AST:
        node.values = self._templatize(node.values)
        # todo: пропустим изменение оператора
        return node

    def visit_Module(self, node: ast.Module) -> ast.AST:
        with self.scope():
            node.body = self._templatize(node.body)
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
            node.items = self._templatize(node.items)
            with self.scope():
                node.body = self._templatize(node.body)
        return node

    def visit_AsyncWith(self, node: ast.AsyncWith) -> ast.AST:
        return self.visit_With(node)

    def visit_withitem(self, node: ast.withitem) -> ast.AST:
        node.context_expr = self.visit(node.context_expr)
        if node.optional_vars:
            if isinstance(node.optional_vars, ast.Name):
                node.optional_vars = self._templatize(node.optional_vars)
            else:
                node.optional_vars = self._templatize(node.optional_vars)
        return node

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.AST:
        with self.scope():
            node.args = self.visit(node.args)
            with self.scope():
                node.body = self._templatize(node.body)
        return node

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> ast.AST:
        return self.visit_FunctionDef(node)

    def visit_Lambda(self, node: ast.Lambda) -> ast.AST:
        with self.scope():
            node.args = self.visit(node.args)
            node.body = self.visit(node.body)
        return node

    def visit_arguments(self, node: ast.arguments) -> ast.AST:
        node.posonlyargs = self._templatize(node.posonlyargs)
        node.args = self._templatize(node.args)

        if node.vararg:
            node.vararg = self._templatize(node.vararg)

        node.kwonlyargs = self._templatize(node.kwonlyargs)
        node.kw_defaults = self._templatize(node.kw_defaults)

        if node.kwarg:
            node.kwarg = self._templatize(node.kwarg)

        node.defaults = self._templatize(node.defaults)
        return node

    def visit_Try(self, node: ast.Try) -> ast.AST:
        with self.scope():
            with self.scope():
                node.body = self._templatize(node.body)

            with self.scope():
                node.handlers = self._templatize(node.handlers)

            with self.scope():
                node.orelse = self._templatize(node.orelse)

            with self.scope():
                node.finalbody = self._templatize(node.finalbody)

        # todo: реализовать шаблонизатор Exception'ов

        return node

    def visit_TryStar(self, node: ast.TryStar) -> ast.AST:
        return self.visit_Try(node)

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> ast.AST:
        with self.scope():
            if node.name:
                node.name = self._scope.variable(node.name)  # todo: мб убрать
            node.body = self._templatize(node.body)
        return node

    def visit_Match(self, node: ast.Match) -> ast.AST:
        with self.scope():
            node.subject = self._templatize(node.subject)
            node.cases = self._templatize(node.cases)
        return node

    def visit_match_case(self, node: ast.match_case) -> ast.AST:
        node.pattern = self._templatize(node.pattern)

        if node.guard:
            node.guard = self._templatize(node.guard)

        with self.scope():
            node.body = self._templatize(node.body)

        return node

    def visit_MatchValue(self, node: ast.MatchValue) -> ast.AST:
        node.value = self._templatize(node.value)
        return node

    def visit_MatchSingleton(self, node: ast.MatchSingleton) -> ast.AST:
        node.value = self._scope.const(node.value)
        return node

    def visit_MatchStar(self, node: ast.MatchStar) -> ast.AST:
        node.name = self._scope.variable(node.name)
        return node

    def visit_MatchSequence(self, node: ast.MatchSequence) -> ast.AST:
        node.patterns = self._templatize(node.patterns)
        return node

    def visit_MatchMapping(self, node: ast.MatchMapping) -> ast.AST:
        node.keys = self._templatize(node.keys)
        node.patterns = self._templatize(node.patterns)
        if node.rest:
            node.rest = self._scope.variable(node.rest)
        return node

    def visit_MatchClass(self, node: ast.MatchClass) -> ast.AST:
        node.patterns = self._templatize(node.patterns)
        node.kwd_patterns = self._templatize(node.kwd_patterns)
        return node

    def visit_MatchAs(self, node: ast.MatchAs) -> ast.AST:
        if node.name:
            node.name = self._scope.variable(node.name)
        if node.pattern:
            node.pattern = self._templatize(node.pattern)
        return node

    def visit_MatchOr(self, node: ast.MatchOr) -> ast.AST:
        node.patterns = self._templatize(node.patterns)
        return node

    def visit_JoinedStr(self, node: ast.JoinedStr) -> ast.AST:
        for value in node.values:
            if isinstance(value, ast.FormattedValue):
                value = self._templatize(value)
        return node

    def visit_FormattedValue(self, node: ast.FormattedValue) -> ast.AST:
        node.value = self._templatize(node.value)
        return node

    def visit_GeneratorExp(self, node: ast.GeneratorExp) -> ast.AST:
        with self.scope(local=True):
            node.generators = self._templatize(node.generators)
            node.elt = self._templatize(node.elt)
        return node

    def visit_ListComp(self, node: ast.ListComp) -> ast.AST:
        return self.visit_GeneratorExp(node)

    def visit_SetComp(self, node: ast.SetComp) -> ast.AST:
        return self.visit_GeneratorExp(node)

    def visit_DictComp(self, node: ast.DictComp) -> ast.AST:
        with self.scope(local=True):
            node.generators = self._templatize(node.generators)
            node.key = self._templatize(node.key)
            node.value = self._templatize(node.value)
        return node

    def visit_comprehension(self, node: ast.comprehension) -> ast.AST:
        node.target = self._templatize(node.target)

        local_state = self._local
        self._local = isinstance(node.iter, ast.Name) and node.iter.id not in self._scope.variables
        node.iter = self._templatize(node.iter)

        self._local = local_state
        node.ifs = self._templatize(node.ifs)

        return node

    def visit_collection(
            self, body: list[ast.stmt | ast.expr | ast.keyword]
    ) -> list[ast.stmt | ast.expr | ast.keyword]:
        return list(map(self._templatize, body))

    def _templatize(self, node: ast.AST):
        match type(node):
            case ast.Name:
                if self._local:
                    node.id = self._scope.local(node.id)
                else:
                    node.id = self._scope.variable(node.id)
            case ast.Starred:
                node.value.id = self._scope.variable(node.value.id)
            case ast.arg:
                node.arg = self._scope.variable(node.arg)
            case ast.Constant:
                node.value = self._scope.const(node.value)
            case ast.Tuple | ast.List | ast.Set:
                node.elts = self.visit_collection(node.elts)
            case ast.Dict:
                node.keys = self.visit_collection(node.keys)
                node.values = self.visit_collection(node.values)
            case builtins.list:
                node = self.visit_collection(node)
            case _:
                return self.visit(node)
        return node

    def _if_for_while_visit(self, node: ast.If | ast.IfExp | ast.While | ast.For) -> ast.AST:
        with self.scope():
            match type(node):
                case ast.For | ast.AsyncFor:
                    node.target = self._templatize(node.target)
                    node.iter = self._templatize(node.iter)
                case ast.If | ast.IfExp | ast.While:
                    node.test = self._templatize(node.test)

            with self.scope():
                node.body = self._templatize(node.body)

            with self.scope():
                node.orelse = self._templatize(node.orelse)

        return node

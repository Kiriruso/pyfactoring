import ast
import builtins
import contextlib

from pyfactoring.utils.pyclones.scope import Scope


class Templater(ast.NodeTransformer):
    def __init__(self):
        self._scope: Scope = Scope(global_=True)
        self._scope_stack: list[Scope] = []
        self._unique_variables: list[str] = []
        self._unique_consts: list[str] = []

    @contextlib.contextmanager
    def scope(self):
        self._scope_stack.append(self._scope)
        self._scope = Scope(self._scope)

        try:
            yield
        finally:
            if self._scope_stack:
                self._scope = self._scope_stack.pop()
            else:
                self._scope = Scope()

    def pop_unique_operands(self) -> tuple[list[str], list[str]]:
        uv, uc = self._unique_variables.copy(), self._unique_consts.copy()
        self._unique_variables.clear()
        self._unique_consts.clear()
        return uv, uc

    def update_globals(self, module: ast.Module):
        self._scope.clear_global_variables()
        variables = self._find_all_global_variables(module)
        self._scope.update_global_variables(variables)

        self._scope.clear_imports()
        imports = self._find_all_imports(module)
        self._scope.update_imports(imports)

    def visit_Assign(self, node: ast.Assign) -> ast.AST:
        node.targets = self._templatize(node.targets)
        node.value = self._templatize(node.value)
        return node

    def visit_AugAssign(self, node: ast.AugAssign) -> ast.AST:
        node.target = self._templatize(node.target)
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
        node.value = self._templatize(node.value)
        return node

    def visit_Subscript(self, node: ast.Subscript) -> ast.AST:
        node.value = self._templatize(node.value)

        if isinstance(node.slice, ast.Name | ast.Constant):
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
        global_scope_state = self._scope.is_global
        self._scope.is_global = True

        for i, name in enumerate(node.names):
            node.names[i] = self._scope.get_name(name)

        self._scope.is_global = global_scope_state
        return node

    def visit_Nonlocal(self, node: ast.Nonlocal) -> ast.AST:
        for i, name in enumerate(node.names):
            node.names[i] = self._scope.get_name(name)
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
        node.comparators = self._templatize(node.comparators)
        return node

    def visit_UnaryOp(self, node: ast.UnaryOp) -> ast.AST:
        node.operand = self._templatize(node.operand)
        return node

    def visit_BinOp(self, node: ast.BinOp) -> ast.AST:
        node.left = self._templatize(node.left)
        node.right = self._templatize(node.right)
        return node

    def visit_BoolOp(self, node: ast.BoolOp) -> ast.AST:
        node.values = self._templatize(node.values)
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
            node.optional_vars = self._templatize(node.optional_vars)
        return node

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.AST:
        with self.scope():
            for decorator in node.decorator_list:
                if isinstance(decorator, ast.Call):
                    self._templatize(decorator)
            with self.scope():
                node.args = self.visit(node.args)
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

        return node

    def visit_TryStar(self, node: ast.TryStar) -> ast.AST:
        return self.visit_Try(node)

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> ast.AST:
        with self.scope():
            if node.name:
                node.name = self._scope.get_name(node.name)
            with self.scope():
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
        node.value = self._scope.get_const(node.value)
        return node

    def visit_MatchStar(self, node: ast.MatchStar) -> ast.AST:
        if node.name:
            node.name = self._scope.get_name(node.name)
        return node

    def visit_MatchSequence(self, node: ast.MatchSequence) -> ast.AST:
        node.patterns = self._templatize(node.patterns)
        return node

    def visit_MatchMapping(self, node: ast.MatchMapping) -> ast.AST:
        node.keys = self._templatize(node.keys)
        node.patterns = self._templatize(node.patterns)
        if node.rest:
            node.rest = self._scope.get_name(node.rest)
        return node

    def visit_MatchClass(self, node: ast.MatchClass) -> ast.AST:
        node.patterns = self._templatize(node.patterns)
        node.kwd_patterns = self._templatize(node.kwd_patterns)
        return node

    def visit_MatchAs(self, node: ast.MatchAs) -> ast.AST:
        if node.name:
            node.name = self._scope.get_name(node.name)
        if node.pattern:
            node.pattern = self._templatize(node.pattern)
        return node

    def visit_MatchOr(self, node: ast.MatchOr) -> ast.AST:
        node.patterns = self._templatize(node.patterns)
        return node

    def visit_JoinedStr(self, node: ast.JoinedStr) -> ast.AST:
        for value in node.values:
            if isinstance(value, ast.FormattedValue):
                self._templatize(value)
        return node

    def visit_FormattedValue(self, node: ast.FormattedValue) -> ast.AST:
        node.value = self._templatize(node.value)
        return node

    def visit_GeneratorExp(self, node: ast.GeneratorExp) -> ast.AST:
        with self.scope():
            node.generators = self._templatize(node.generators)
            node.elt = self._templatize(node.elt)
        return node

    def visit_ListComp(self, node: ast.ListComp) -> ast.AST:
        return self.visit_GeneratorExp(node)

    def visit_SetComp(self, node: ast.SetComp) -> ast.AST:
        return self.visit_GeneratorExp(node)

    def visit_DictComp(self, node: ast.DictComp) -> ast.AST:
        with self.scope():
            node.generators = self._templatize(node.generators)
            node.key = self._templatize(node.key)
            node.value = self._templatize(node.value)
        return node

    def visit_comprehension(self, node: ast.comprehension) -> ast.AST:
        node.target = self._templatize(node.target)

        local_state = self._scope.is_local
        self._scope.is_local = (
            isinstance(node.iter, ast.Name)
            and node.iter.id not in self._scope.variables
        )
        node.iter = self._templatize(node.iter)

        self._scope.is_local = local_state
        node.ifs = self._templatize(node.ifs)

        return node

    def visit_collection(
            self, body: list[ast.stmt | ast.expr | ast.keyword],
    ) -> list[ast.stmt | ast.expr | ast.keyword]:
        return list(map(self._templatize, body))

    def _templatize(self, node: ast.AST):
        if node is None:
            return node

        match type(node):
            case ast.Name:
                name = self._scope.get_name(node.id)
                if "var" in name:
                    if node.id not in self._unique_variables:
                        self._unique_variables.append(node.id)
                node.id = name
            case ast.Starred:
                node.value = self._templatize(node.value)
            case ast.arg:
                node.arg = self._scope.get_name(node.arg)
            case ast.Constant:
                if str(node.value) not in self._unique_consts:
                    self._unique_consts.append(str(node.value))
                node.value = self._scope.get_const(node.value)
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
        is_for = isinstance(node, ast.For | ast.AsyncFor)

        with self.scope():
            if is_for:
                node.iter = self._templatize(node.iter)
            else:
                node.test = self._templatize(node.test)

            with self.scope():
                if is_for:
                    node.target = self._templatize(node.target)
                node.body = self._templatize(node.body)

            with self.scope():
                node.orelse = self._templatize(node.orelse)

        return node

    @staticmethod
    def _find_all_global_variables(module: ast.Module) -> set[str]:
        global_variables: set[str] = set()
        for node in ast.iter_child_nodes(module):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        global_variables.add(target.id)
                    elif isinstance(target, ast.Tuple):
                        for elt in target.elts:
                            if isinstance(elt, ast.Name):
                                global_variables.add(elt.id)
                            elif isinstance(elt, ast.Starred) and isinstance(elt.value, ast.Name):
                                global_variables.add(elt.value.id)
            if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                global_variables.add(node.target.id)
        return global_variables

    @staticmethod
    def _find_all_imports(module: ast.Module) -> list[str]:
        imports: list[str] = []
        for node in ast.walk(module):
            if isinstance(node, ast.alias):
                imports.append(node.asname if node.asname else node.name)
        return imports

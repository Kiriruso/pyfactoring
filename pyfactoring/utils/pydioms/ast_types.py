import ast
from dataclasses import dataclass
from enum import IntEnum


class CountingType(IntEnum):
    NOT_COUNTED = 0
    OPERATOR = 1
    OPERAND = 2


@dataclass(frozen=True)
class ASTNodeInfo:
    """
    Представляет дополнительную информацию об узле AST

    :var name: имя типа узла, например 'Module'
    :var children_names: имена дочерних узлов
    :var count_as: подсчитывать в алгоритме как оператор/операнд/никак
    """

    name: str
    children_names: tuple[str, ...] | None
    count_as: CountingType = CountingType.NOT_COUNTED


AST_NODES_INFO = {
    # NOT COUNTED
    "Module": ASTNodeInfo("Module", ("body",)),
    "Interactive": ASTNodeInfo("Interactive", ("body",)),
    "Expression": ASTNodeInfo("Expression", ("body",)),
    "Suite": ASTNodeInfo("Suite", ("body",)),
    "Expr": ASTNodeInfo("Expr", ("value",)),
    "BoolOp": ASTNodeInfo("BoolOp", ("op", "values")),
    "NamedExpr": ASTNodeInfo("NamedExpr", ("target", "value")),
    "BinOp": ASTNodeInfo("BinOp", ("left", "op", "right")),
    "UnaryOp": ASTNodeInfo("UnaryOp", ("op", "operand")),
    "GeneratorExp": ASTNodeInfo("GeneratorExp", ("elt", "generators")),
    "Compare": ASTNodeInfo("Compare", ("left", "ops")),
    "Num": ASTNodeInfo("Num", ("n",)),
    "Str": ASTNodeInfo("Str", ("s",)),
    "Bool": ASTNodeInfo("Bool", ("bool",)),
    "JoinedStr": ASTNodeInfo("JoinedStr", ("values",)),
    "Bytes": ASTNodeInfo("Bytes", ("s",)),
    "NameConstant": ASTNodeInfo("NameConstant", ("value",)),
    "arguments": ASTNodeInfo("arguments", ("posonlyargs", "args", "vararg", "kwonlyargs", "kwarg")),
    "arg": ASTNodeInfo("arg", ("arg", "annotation", "default")),
    "sarg": ASTNodeInfo("sarg", ("arg", "annotation")),
    "keyword": ASTNodeInfo("keyword", ("arg", "value")),
    "None": ASTNodeInfo("None", None),
    "LIST": ASTNodeInfo("LIST", ("expr", "expr")),
    "ULIST": ASTNodeInfo("ULIST", ("expr",)),
    "COMP_PAIR": ASTNodeInfo("COMP_PAIR", ("op", "expr")),
    "DICT_PAIR": ASTNodeInfo("DICT_PAIR", ("key", "value")),
    "NAME": ASTNodeInfo("NAME", ("name",)),
    "Constant": ASTNodeInfo("Constant", ("value",)),
    "Name": ASTNodeInfo("Name", ("id",)),
    "Index": ASTNodeInfo("Index", ("value",)),

    # OPERATORS
    "FunctionDef": ASTNodeInfo(
        "FunctionDef",
        ("name", "args", "body", "decorator_list", "returns"),
        CountingType.OPERATOR,
    ),
    "AsyncFunctionDef": ASTNodeInfo(
        "AsyncFunctionDef",
        ("name", "args", "body", "decorator_list", "returns"),
        CountingType.OPERATOR,
    ),
    "ClassDef": ASTNodeInfo(
        "ClassDef",
        ("name", "bases", "keywords", "body", "decorator_list"),
        CountingType.OPERATOR,
    ),
    "Return": ASTNodeInfo("Return", ("value",), CountingType.OPERATOR),
    "Delete": ASTNodeInfo("Delete", ("targets",), CountingType.OPERATOR),
    "Assign": ASTNodeInfo("Assign", ("targets", "value"), CountingType.OPERATOR),
    "AugAssign": ASTNodeInfo("AugAssign", ("target", "op", "value"), CountingType.OPERATOR),
    "AnnAssign": ASTNodeInfo("AnnAssign", ("target", "annotation", "value"), CountingType.OPERATOR),
    "For": ASTNodeInfo("For", ("target", "iter", "body", "orelse"), CountingType.OPERATOR),
    "AsyncFor": ASTNodeInfo("AsyncFor", ("target", "iter", "body", "orelse"), CountingType.OPERATOR),
    "While": ASTNodeInfo("While", ("test", "body", "orelse"), CountingType.OPERATOR),
    "If": ASTNodeInfo("If", ("test", "body", "orelse"), CountingType.OPERATOR),
    "With": ASTNodeInfo("With", ("items", "body"), CountingType.OPERATOR),
    "AsyncWith": ASTNodeInfo("AsyncWith", ("items", "body"), CountingType.OPERATOR),
    "Raise": ASTNodeInfo("Raise", ("exc", "cause"), CountingType.OPERATOR),
    "Try": ASTNodeInfo("Try", ("body", "handlers", "orelse", "finalbody"), CountingType.OPERATOR),
    "Assert": ASTNodeInfo("Assert", ("test", "msg"), CountingType.OPERATOR),
    "Import": ASTNodeInfo("Import", ("names",), CountingType.OPERATOR),
    "ImportFrom": ASTNodeInfo("ImportFrom", ("module", "names"), CountingType.OPERATOR),
    "Global": ASTNodeInfo("Global", ("names",), CountingType.OPERATOR),
    "Nonlocal": ASTNodeInfo("Nonlocal", ("names",), CountingType.OPERATOR),
    "Pass": ASTNodeInfo("Pass", (), CountingType.OPERATOR),
    "Break": ASTNodeInfo("Break", (), CountingType.OPERATOR),
    "Continue": ASTNodeInfo("Continue", (), CountingType.OPERATOR),
    "Lambda": ASTNodeInfo("Lambda", ("args", "body"), CountingType.OPERATOR),
    "IfExp": ASTNodeInfo("IfExp", ("test", "body", "orelse"), CountingType.OPERATOR),
    "Dict": ASTNodeInfo("Dict", ("elts",), CountingType.OPERATOR),
    "Set": ASTNodeInfo("Set", ("elts",), CountingType.OPERATOR),
    "ListComp": ASTNodeInfo("ListComp", ("elt", "generators"), CountingType.OPERATOR),
    "SetComp": ASTNodeInfo("SetComp", ("elt", "generators"), CountingType.OPERATOR),
    "DictComp": ASTNodeInfo("DictComp", ("key", "value", "generators"), CountingType.OPERATOR),
    "Await": ASTNodeInfo("Await", ("value",), CountingType.OPERATOR),
    "Yield": ASTNodeInfo("Yield", ("value",), CountingType.OPERATOR),
    "YieldFrom": ASTNodeInfo("YieldFrom", ("value",), CountingType.OPERATOR),
    "Call": ASTNodeInfo(
        "Call",
        ("func", "args", "keywords", "starargs", "kwargs"),
        CountingType.OPERATOR,
    ),
    "FormattedValue": ASTNodeInfo(
        "FormattedValue",
        ("value", "conversion", "format_spec"),
        CountingType.OPERATOR,
    ),
    "Attribute": ASTNodeInfo("Attribute", ("value", "attr"), CountingType.OPERATOR),
    "Subscript": ASTNodeInfo("Subscript", ("value", "slice"), CountingType.OPERATOR),
    "Starred": ASTNodeInfo("Starred", ("value",), CountingType.OPERATOR),
    "List": ASTNodeInfo("List", ("elts",), CountingType.OPERATOR),
    "Tuple": ASTNodeInfo("Tuple", ("elts",), CountingType.OPERATOR),
    "Slice": ASTNodeInfo("Slice", ("lower", "upper", "step"), CountingType.OPERATOR),
    "ExtSlice": ASTNodeInfo("ExtSlice", ("dims",), CountingType.OPERATOR),
    "And": ASTNodeInfo("And", (), CountingType.OPERATOR),
    "Or": ASTNodeInfo("Or", (), CountingType.OPERATOR),
    "Add": ASTNodeInfo("Add", (), CountingType.OPERATOR),
    "Sub": ASTNodeInfo("Sub", (), CountingType.OPERATOR),
    "Mult": ASTNodeInfo("Mult", (), CountingType.OPERATOR),
    "MatMult": ASTNodeInfo("MatMult", (), CountingType.OPERATOR),
    "Div": ASTNodeInfo("Div", (), CountingType.OPERATOR),
    "Mod": ASTNodeInfo("Mod", (), CountingType.OPERATOR),
    "Pow": ASTNodeInfo("Pow", (), CountingType.OPERATOR),
    "LShift": ASTNodeInfo("LShift", (), CountingType.OPERATOR),
    "RShift": ASTNodeInfo("RShift", (), CountingType.OPERATOR),
    "BitOr": ASTNodeInfo("BitOr", (), CountingType.OPERATOR),
    "BitXor": ASTNodeInfo("BitXor", (), CountingType.OPERATOR),
    "BitAnd": ASTNodeInfo("BitAnd", (), CountingType.OPERATOR),
    "FloorDiv": ASTNodeInfo("FloorDiv", (), CountingType.OPERATOR),
    "Invert": ASTNodeInfo("Invert", (), CountingType.OPERATOR),
    "Not": ASTNodeInfo("Not", (), CountingType.OPERATOR),
    "UAdd": ASTNodeInfo("UAdd", (), CountingType.OPERATOR),
    "USub": ASTNodeInfo("USub", (), CountingType.OPERATOR),
    "Eq": ASTNodeInfo("Eq", (), CountingType.OPERATOR),
    "NotEq": ASTNodeInfo("NotEq", (), CountingType.OPERATOR),
    "Lt": ASTNodeInfo("Lt", (), CountingType.OPERATOR),
    "LtE": ASTNodeInfo("LtE", (), CountingType.OPERATOR),
    "Gt": ASTNodeInfo("Gt", (), CountingType.OPERATOR),
    "GtE": ASTNodeInfo("GtE", (), CountingType.OPERATOR),
    "Is": ASTNodeInfo("Is", (), CountingType.OPERATOR),
    "IsNot": ASTNodeInfo("IsNot", (), CountingType.OPERATOR),
    "In": ASTNodeInfo("In", (), CountingType.OPERATOR),
    "NotIn": ASTNodeInfo("NotIn", (), CountingType.OPERATOR),
    "comprehension": ASTNodeInfo("comprehension", ("target", "iter", "ifs"), CountingType.OPERATOR),
    "AsyncComprehension": ASTNodeInfo(
        "AsyncComprehension",
        ("target", "iter", "ifs"),
        CountingType.OPERATOR,
    ),
    "ExceptHandler": ASTNodeInfo("ExceptHandler", ("type", "name", "body"), CountingType.OPERATOR),
    "alias": ASTNodeInfo("alias", ("name", "asname"), CountingType.OPERATOR),
    "withitem": ASTNodeInfo("withitem", ("context_expr", "optional_vars"), CountingType.OPERATOR),

    # OPERANDS
    "Ellipsis": ASTNodeInfo("Ellipsis",  (), CountingType.OPERAND),
    "NoneConst": ASTNodeInfo("NoneConst", (), CountingType.OPERAND),
}

AST_PRESENTATION_LEAVES = {
    "FunctionDef":      "name",
    "AsyncFunctionDef": "name",
    "ClassDef":         "name",
    "AnnAssign":        "simple",
    "Num":              "n",
    "Str":              "s",
    "Bool":             "bool",
    "Bytes":            "s",
    "Constant":         "value",
    "Attribute":        "attr",
    "Name":             "id",
    "comprehension":    "is_async",
    "arg":              "arg",
    "alias":            "asname",
    "ULIST":            "expr",
    "NAME":             "name",
    "ImportFrom":       "module",
    "FormattedValue":   "conversion",
    "ExceptHandler":    "name",
    "keyword":          "arg",
}

AST_REALIZE_SUBTREE_NODES: frozenset[str] = frozenset(
    (
        "FunctionDef", "AsyncFunctionDef",
        "For", "AsyncFor",
        "While", "If",
        "With", "AsyncWith",
        "Try", "ExceptHandler",
    ),
)

AST_SPECIFIC_NODES: frozenset = frozenset(
    (
        ast.Dict,
        ast.Compare,
        ast.Global,
        ast.Nonlocal,
        ast.Constant,
        ast.comprehension,
        ast.arguments,
    ),
)

AST_TOTAL_UNIQUE_OPERATORS = sum(
    1
    for info in AST_NODES_INFO.values()
    if info.count_as == CountingType.OPERATOR
)

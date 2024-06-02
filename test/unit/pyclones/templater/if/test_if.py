import ast
import copy

import pytest

from test.unit.pyclones.conftest import load_tests
from pyfactoring.utils.pyclones.templater import Templater


tests = load_tests("if")


@pytest.mark.parametrize(
    ("ast_input", "ast_expected"),
    (*tests,),
)
def test_if_templating_success(ast_input: ast.AST, ast_expected: ast.AST):
    copy_input = copy.deepcopy(ast_input)
    templater = Templater()

    input_dump = ast.dump(templater.visit(copy_input), indent=4)
    expected_dump = ast.dump(ast_expected, indent=4)

    assert input_dump == expected_dump


@pytest.mark.parametrize(
    ("ast_input", "exp_vars", "exp_consts"),
    (
        (
            tests[0],
            {"a"},
            {"10", "50"},
        ),
        (
            tests[1],
            {"i", "j"},
            set(),
        ),
        (
            tests[2],
            {"a", "b"},
            {"10"},
        ),
        (
            tests[3],
            {"x", "y"},
            {"True", "10"},
        ),
        (
            tests[4],
            {"x", "y"},
            {"10"},
        ),
        (
            tests[5],
            {"x", "y"},
            {"10"},
        ),
        (
            tests[6],
            {"a", "b", "x"},
            {"10"},
        ),
        (
            tests[7],
            {"x", "y"},
            {"50", "20", "10", "1000", "2000", "0", "500", "200", "10000"},
        ),
    )
)
def test_if_vars_consts_success(
        ast_input: tuple[ast.AST, ast.AST], exp_vars: set[str], exp_consts: set[str]
):
    copy_input = copy.deepcopy(ast_input[0])
    templater = Templater()
    templater.visit(copy_input)

    input_vars, input_consts = templater.pop_unique_operands()
    input_vars = set(input_vars)
    input_consts = set(input_consts)

    assert input_vars == exp_vars, input_vars
    assert input_consts == exp_consts, input_consts

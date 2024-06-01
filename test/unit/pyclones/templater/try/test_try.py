import ast
import copy

import pytest

from test.unit.pyclones.conftest import load_tests
from pyfactoring.utils.pyclones.templater import Templater


tests = load_tests("try")


@pytest.mark.parametrize(
    ("ast_input", "ast_expected"),
    (*tests,),
)
def test_try_templating_success(ast_input: ast.AST, ast_expected: ast.AST):
    copy_input = copy.deepcopy(ast_input)
    templater = Templater()

    input_dump = ast.dump(templater.visit(copy_input))
    expected_dump = ast.dump(ast_expected)

    assert input_dump == expected_dump


@pytest.mark.parametrize(
    ("ast_input", "exp_vars", "exp_consts"),
    (
        (
          tests[0],
          set(),
          {"1", "0", "10", "20", "\"finally\""},
        ),
        (
          tests[1],
          set(),
          {"\"some_group\"", "\"starred\"", "1", "2"},
        ),
    )
)
def test_try_vars_consts_success(
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

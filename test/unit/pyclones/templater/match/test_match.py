import ast
import copy

import pytest

from test.unit.pyclones.conftest import load_tests
from pyfactoring.utils.pyclones.templater import Templater


tests = load_tests("match")


@pytest.mark.parametrize(
    ("ast_input", "ast_expected"),
    (*tests,),
)
def test_match_templating_success(ast_input: ast.AST, ast_expected: ast.AST):
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
            {"x"},
            {"\"Relevant\"", "Ellipsis"},
        ),
        (
            tests[1],
            {"x"},
            {"1", "2", "Ellipsis"},
        ),
        (
            tests[2],
            {"x"},
            {"1", "2", "Ellipsis"},
        ),
        (
            tests[3],
            {"x"},
            {"1", "2", "Ellipsis"},
        ),
        (
            tests[4],
            {"x"},
            {"0", "Ellipsis"},
        ),
        (
            tests[5],
            {"x"},
            {"Ellipsis"},
        ),
        (
            tests[6],
            {"x"},
            {"Ellipsis"},
        ),
        (
            tests[7],
            {"node"},
            {"\"text\""},
        ),
    )
)
def test_match_vars_consts_success(
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

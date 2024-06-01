import ast
import copy

import pytest

from test.unit.pyclones.conftest import load_tests
from pyfactoring.utils.pyclones.templater import Templater


tests = load_tests("while")


@pytest.mark.parametrize(
    ("ast_input", "ast_expected"),
    (*tests,),
)
def test_while_templating_success(ast_input: ast.AST, ast_expected: ast.AST):
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
            {"x"},
            {"0", "2", "10", "1000", "True"},
        ),
        (
            tests[1],
            {"x", "y", "z", "i", "j"},
            {'"\n"', "True", "50", '"None data"', "2"},
        ),
        (
            tests[2],
            set(),
            {"0", "10", "2", "3", "9", "True", '"string"', '"_"', '"end"', '"!"'},
        ),
        (
            tests[3],
            {"v_1"},
            {"7.3", "5", "13.2", "100", "4"},
        ),
    ),
)
def test_while_vars_consts_success(
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

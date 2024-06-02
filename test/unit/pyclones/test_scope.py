from typing import Any

import pytest

from pyfactoring import Scope, Templater


@pytest.mark.parametrize(
    ("input_vars", "input_consts", "expected_vars", "expected_consts"),
    (
        (
            tuple(), tuple(), tuple(), tuple(),
        ),
        (
            tuple(),
            (-1, "-1", 1.0, 1, True, "True", False, 0, "0"),
            tuple(),
            (
                "__const_0__", "__const_1__", "__const_2__",
                "__const_3__", "__const_4__", "__const_5__",
                "__const_6__", "__const_7__", "__const_8__",
            ),
        ),
        (
            ("x", "y", "z"),
            (1, 2, "3", "True", "1", "2"),
            ("__var_0__", "__var_1__", "__var_2__"),
            ("__const_0__", "__const_1__", "__const_2__", "__const_3__", "__const_4__", "__const_5__"),
        ),
        (
            ("x", "y", "z"),
            (1, 2, "3", "True", "1", "2"),
            ("__var_0__", "__var_1__", "__var_2__"),
            ("__const_0__", "__const_1__", "__const_2__", "__const_3__", "__const_4__", "__const_5__"),
        ),
    )
)
def test_get_vars_and_consts_from_scope_success(
    input_vars: tuple[str],
    input_consts: tuple[Any],
    expected_vars: tuple[str],
    expected_consts: tuple[str],
):
    scope = Scope()

    for i, v in enumerate(input_vars):
        assert scope.get_name(v) == expected_vars[i], (v, scope.get_name(v))

    for i, c in enumerate(input_consts):
        assert scope.get_const(c) == expected_consts[i], (c, scope.get_const(c))


def test_create_nested_scopes_success():
    templater = Templater()

    # global scope
    assert templater._scope
    assert templater._scope.is_global

    templater._scope.get_name("x")

    # first scope in global
    with templater.scope():
        assert len(templater._scope_stack) == 1
        assert not templater._scope.is_global
        assert not templater._scope.is_local
        assert templater._scope not in templater._scope_stack

        assert "x" in templater._scope.variables
        assert "x" not in templater._scope.locals

        templater._scope.get_name("y")

        assert "y" in templater._scope.variables
        assert "y" not in templater._scope.locals

        # local scope
        with templater.scope():
            assert len(templater._scope_stack) == 2
            assert templater._scope.is_local
            assert templater._scope not in templater._scope_stack

            assert "y" in templater._scope.variables
            assert "y" not in templater._scope.locals

            # check global scope
            assert "x" in templater._scope_stack[0].variables
            assert "x" not in templater._scope_stack[0].locals
            assert "y" not in templater._scope_stack[0].variables
            assert "y" not in templater._scope_stack[0].locals

            with templater.scope():
                assert len(templater._scope_stack) == 3
                assert templater._scope.is_local
                assert templater._scope not in templater._scope_stack

                templater._scope.get_name("z")

                assert "z" in templater._scope.locals
                assert "z" not in templater._scope.variables

            assert templater._scope not in templater._scope_stack

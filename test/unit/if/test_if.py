import ast
import pytest

from test.conftest import mock_factory
from pyfactoring import Templater


mocks = mock_factory()


@pytest.mark.parametrize(
    ("_input", "_expected"),
    (
        mocks.send("if"),
        *(mock for mock in mocks)
    )
)
def test_if_templating_success(_input, _expected):
    templater = Templater()

    _input_dump = ast.dump(templater.visit(_input))
    _expected_dump = ast.dump(_expected)

    assert _input_dump == _expected_dump

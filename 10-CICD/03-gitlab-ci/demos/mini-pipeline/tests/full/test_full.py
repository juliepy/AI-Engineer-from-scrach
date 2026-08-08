import pytest

from app.calculator import add


@pytest.mark.full
@pytest.mark.parametrize(
    "a,b,expected",
    [
        (1, 2, 3),
        (100, 200, 300),
        (-5, -7, -12),
        (999, 1, 1000),
    ],
)
def test_add_matrix(a, b, expected):
    """Daily-style: more cases / heavier coverage."""
    assert add(a, b) == expected

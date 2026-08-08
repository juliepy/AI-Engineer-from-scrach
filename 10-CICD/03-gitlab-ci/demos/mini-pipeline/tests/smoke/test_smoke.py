import pytest

from app.calculator import add


@pytest.mark.smoke
def test_add_smoke():
    assert add(1, 1) == 2


@pytest.mark.smoke
def test_add_negative_smoke():
    assert add(-1, 1) == 0

import pytest


@pytest.mark.smoke
def test_health():
    assert True


@pytest.mark.smoke
def test_quick_add():
    assert 2 + 2 == 4

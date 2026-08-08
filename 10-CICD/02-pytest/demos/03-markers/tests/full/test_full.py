import pytest


@pytest.mark.full
def test_long_regression_a():
    assert sum(range(10)) == 45


@pytest.mark.full
def test_long_regression_b():
    assert "daily" in "daily_full_suite"

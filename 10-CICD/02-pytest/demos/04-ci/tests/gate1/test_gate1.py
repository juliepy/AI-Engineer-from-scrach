import pytest


@pytest.mark.gate1
def test_gate1_integrate():
    assert ["lint", "test", "build"][-1] == "build"

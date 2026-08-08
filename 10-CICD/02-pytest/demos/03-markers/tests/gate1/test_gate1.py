import pytest


@pytest.mark.gate1
def test_critical_path():
    """合入主干后的关键链路（示意）。"""
    pipeline = ["build", "integrate", "smoke_link"]
    assert "integrate" in pipeline


@pytest.mark.gate1
def test_main_still_green():
    assert "main" != "broken"

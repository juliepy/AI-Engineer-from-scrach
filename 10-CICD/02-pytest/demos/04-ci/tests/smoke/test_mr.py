import pytest


@pytest.mark.smoke
def test_mr_smoke_ok():
    assert 1 + 1 == 2


@pytest.mark.smoke
def test_mr_smoke_fail_for_log_reading():
    """故意失败：练习读 FAILED 行、断言对比、退出码。

    练完可改成 == 2，或运行时跳过：
    pytest -m smoke -k "not fail_for_log" --junitxml=report-mr.xml
    """
    left = 1 + 1
    right = 3
    assert left == right

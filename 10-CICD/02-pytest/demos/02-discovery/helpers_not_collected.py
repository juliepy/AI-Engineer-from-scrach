"""故意不用 test_ 前缀：默认不会被 pytest 收集。

若你执行 `pytest -v` 时看不到这里的函数，说明发现规则生效了。
"""


def check_something():
    """名字不是 test_*，不会当作用例跑。"""
    assert False  # 即使写成 False，也不会执行


def test_hidden_in_wrong_file():
    """虽然函数叫 test_*，但文件名不是 test_*.py / *_test.py，默认也不收集。"""
    assert False

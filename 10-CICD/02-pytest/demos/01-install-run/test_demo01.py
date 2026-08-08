"""Demo for 01-安装与运行.md：第一次跑通（有绿有红）。"""


def test_add_pass():
    """预期：通过（输出里是 .）"""
    assert 1 + 1 == 2


def test_add_fail():
    """预期：失败（输出里是 F）——故意写错，用来看失败栈和退出码。"""
    assert 1 + 1 == 3

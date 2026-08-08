"""陷阱示例：文件在 tests/smoke，但标记是 full。

- pytest tests/smoke          → 会跑到它（按目录）
- pytest -m smoke             → 不会跑到它（按 marker）
体会：目录和 marker 要对齐，否则门禁选错 case。
"""

import pytest


@pytest.mark.full
def test_should_not_be_in_mr_by_marker():
    assert True

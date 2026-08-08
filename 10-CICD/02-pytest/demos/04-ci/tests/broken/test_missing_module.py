"""演示 CI 常见 Error：ModuleNotFoundError（收集或导入阶段挂）。

运行：
  pytest tests/broken -v
"""

import this_module_does_not_exist  # noqa: F401


def test_never_reached():
    assert True

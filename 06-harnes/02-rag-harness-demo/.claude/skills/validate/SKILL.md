---
name: validate
description: 运行完整质量门（pytest）并按 PASS/FAIL 格式报告结果。提交前必须运行。
disable-model-invocation: true
---

# /validate — 完整验证门

运行完整质量门并报告每条命令的 PASS/FAIL。

这与 Stop hook 自动执行的门相同。提交前请显式运行一次。

---

## 验证命令

```bash
python scripts/validate.py
```

该命令内部运行：
```bash
python -m unittest discover -s tests -v
```

---

## 报告格式

运行完成后，输出：

```
验证门结果
==========

  pytest (unittest)  : PASS / FAIL（N 个测试）

整体: PASS / FAIL
```

---

## 失败时

列出失败的测试名称和第一条错误信息。只修复根本原因，不要绕过测试。修复后重跑 `/validate`。

## 通过时

工作区干净，可以提交。

---

## 说明

- Stop hook（`stop_validate.py`）在 Agent 结束时自动运行此门。如果它阻止结束，说明测试未通过——修复后继续即可。
- 如果只改了单个模块，可以先单模块调试：`python -m unittest tests/test_chunker.py -v`，但最终提交前必须跑完整验证门。

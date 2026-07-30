# Eval Cases · 正例 + 负例

| 轨迹 | 文件 | 角色 |
|------|------|------|
| 正例 | [`from_02_agent_loop.json`](./from_02_agent_loop.json) | 02 实跑冻结轨迹 |
| 负例 | [`failure_run.json`](./failure_run.json) | 合成：错工具 / role 破 / cache 漂 |

编辑期望：[`eval_cases.json`](./eval_cases.json)。

| id | fixture | 意图 | 期望结果 |
|----|---------|------|----------|
| `golden-loop-ok` | from_02… | 工具子集 + 允许 grace | PASS |
| `failure-wrong-tool-cache-break` | failure_run | 故意踩红线，驱动 RCA | FAIL |

更接近 Hermes 的入口是 pytest 契约（不是这份 JSON）：

```powershell
python -m pytest teaching/invariants/test_agent_loop_contracts.py -q
```

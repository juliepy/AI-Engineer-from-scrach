# Eval Cases

| id | fixture | expected_tools | forbidden | max_steps | allowed_exits | final_text | notes |
|----|---------|----------------|-----------|-----------|---------------|------------|-------|
| `golden-loop-ok` | `from_02_agent_loop.json` | todo, web_search | execute_code | 10 | completed, budget_grace_call | yes | 正例：02 实跑轨迹。断言工具子集 + 允许 grace 收尾（不锁精确序列/步数快照） |
| `failure-wrong-tool-cache-break` | `failure_run.json` | todo, web_search | execute_code | 4 | completed, budget_grace_call | yes | 负例（合成）：错工具 + role 连发 + system/tools 漂移 + 无 grace。应 FAIL 并产出 RCA |

# hermes_src — Eval + Trace 对照剪枝

本目录只读，方便对照 `demo/teaching/`。完整仓库里还缺 `run_tests_parallel.py` 等依赖，**不要指望在这里直接跑通 CI**。

| 文件 | 用途 |
|------|------|
| `AGENTS.md` | 「Don't write change-detector tests」+ Prompt Caching 铁律 |
| `hermes_logging.py` | `agent.log` / `errors.log` / `gateway.log`；`session_tag`；`COMPONENT_PREFIXES` |
| `scripts/run_tests.sh` | CI 对齐的唯一测试入口（勿直接调 pytest） |
| `agent/prompt_caching.py` | `test_prompt_caching.py` 依赖的真实现 |
| `tests/agent/test_prompt_caching.py` | ★ 课堂主文件：不变量断言范例 |
| `tests/agent/test_context_compressor.py` | 压缩顺序不变量 |
| `tests/agent/test_memory_provider.py` | provider 契约 |

真跑请用 `../demo/`（离线打分，不需要 API Key）。上游完整文件：

- https://github.com/NousResearch/hermes-agent/blob/main/hermes_logging.py
- https://github.com/NousResearch/hermes-agent/blob/main/scripts/run_tests.sh
- https://github.com/NousResearch/hermes-agent/blob/main/tests/agent/test_prompt_caching.py

关联产物（作为 golden Trace）：

- [`../../02-run-agent/demo/exports/agent_loop/06_trace.md`](../../02-run-agent/demo/exports/agent_loop/06_trace.md)
- [`../../02-run-agent/demo/exports/agent_loop/00_workflow.md`](../../02-run-agent/demo/exports/agent_loop/00_workflow.md)

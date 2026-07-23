# hermes_src · Eval / Trace 只读对照

从 `hermes-study/`（原 `hermes-agent/`）剪出，**不是可运行工程**。

| 文件 | 职责 |
|------|------|
| `AGENTS.md` | 测试规范：不变量 > 快照；必须用 `run_tests.sh` |
| `hermes_logging.py` | 结构化日志；`session_tag`；按组件分流文件 |
| `scripts/run_tests.sh` | CI 对齐入口（清凭证、TZ=UTC、子进程隔离） |
| `tests/agent/test_prompt_caching.py` | 缓存断点预算不变量（首选课堂文件） |
| `tests/agent/test_context_compressor.py` | 压缩后消息序 / marker 剥离等契约 |
| `tests/agent/test_memory_provider.py` | Provider 工具注入去重等契约 |

真跑：回到完整 `hermes-agent/` 仓库。

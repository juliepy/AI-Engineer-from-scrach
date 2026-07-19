# hermes_src · 只读对照副本

从 `hermes-agent/` 剪出的 Memory / Context 相关源码，**不是可运行工程**（缺依赖与包结构）。

用途：一边跑 `../notebooks/`，一边对照这里的真实现。

| 文件 | 对应 Hermes 职责 |
|------|------------------|
| `tools/memory_tool.py` | Layer1 `MemoryStore`：frozen snapshot + live entries |
| `agent/memory_provider.py` | 外部/内置 Provider ABC |
| `agent/memory_manager.py` | 编排；同时仅一个外部 Provider |
| `agent/context_compressor.py` | Context 压缩（唯一允许改上下文） |
| `agent/prompt_caching.py` | Anthropic `system_and_3` 缓存断点 |
| `plugins/memory/honcho/` | 真实外部 Provider 范例 |
| `AGENTS.md` | Prompt Caching / 测试规范等项目规则 |

要真跑 Hermes：回到主仓库 `hermes-agent/`。

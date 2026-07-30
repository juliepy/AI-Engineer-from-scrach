# hermes_src — Memory Provider 真源码剪枝

本目录从 Hermes 拷贝 **真实** memory 相关实现，方便对照 `notes/`。  
缺 gateway / plugin 后端等依赖，**不要在这里直接 import 跑**。

| 路径 | 用途 |
|------|------|
| `agent/memory_provider.py` | ★ `MemoryProvider` ABC：`prefetch` / `sync_turn` / `system_prompt_block` |
| `agent/memory_manager.py` | ★ 编排：单外部 provider、`prefetch_all` / `sync_all`、`<memory-context>` 围栏 |
| `tools/memory_tool.py` | 内置 `MemoryStore`（MEMORY.md / USER.md）+ `memory` 工具 |
| `excerpts/turn_context.PREFETCH.py` | turn 开始：`on_turn_start` → `prefetch_all` |
| `excerpts/conversation_loop.INJECT.py` | API 前：prefetch 注入 **user message**（不改 SP） |
| `excerpts/turn_finalizer.SYNC.py` | turn 结束：调 `_sync_external_memory_for_turn` |
| `excerpts/run_agent.SYNC_HELPER.py` | `sync_all` + `queue_prefetch_all`（跳过 interrupted） |
| `excerpts/system_prompt.MEMORY_VOLATILE.py` | SP volatile：builtin md + `build_system_prompt()` |
| `excerpts/prompt_builder.MEMORY_GUIDANCE.py` | ★ `MEMORY_GUIDANCE` 宏 |
| `excerpts/background_review.MEMORY_REVIEW.py` | ★ `_MEMORY_REVIEW_PROMPT` |

精读顺序：`memory_provider.py` → `memory_manager.py` → excerpts（prefetch → inject → sync）→ prompts。

上游：

- https://github.com/NousResearch/hermes-agent/blob/main/agent/memory_provider.py
- https://github.com/NousResearch/hermes-agent/blob/main/agent/memory_manager.py

更广的 Memory 教材（notebook）：[`../01-memory/`](../01-memory/)。  
Prompt 目录对照：[`../04-prompt/`](../04-prompt/)。

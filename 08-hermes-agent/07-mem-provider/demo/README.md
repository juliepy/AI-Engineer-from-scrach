# Mem-Provider Demo · 真 MemoryManager + FakeProvider

**不改 Hermes 源码。** `PYTHONPATH` 指向完整 `hermes-agent`，用真 `MemoryManager` / `build_memory_context_block`，外挂一个进程内 `FakeProvider` 演示 **fetch → 围栏注入 → sync_turn**。

对照：[`../notes/02_prefetch_and_inject.md`](../notes/02_prefetch_and_inject.md)、[`../notes/03_sync_turn_store.md`](../notes/03_sync_turn_store.md)、[`../notes/04_memory_prompts.md`](../notes/04_memory_prompts.md)。

---

## 跑法

```bash
cd 07-mem-provider/demo

# set HERMES_AGENT_ROOT=D:\workspace\doc\面试狂魔\人工智能面试题\hermes-agent

python run_mem_provider.py
```

产物：`exports/mem_provider/01_report.md`、`00_raw.json`。

---

## 调了哪段真源码

| 调用 | 文件 |
|------|------|
| `MemoryManager.prefetch_all` / `sync_all` / `queue_prefetch_all` / `build_system_prompt` | `agent/memory_manager.py` |
| `build_memory_context_block` | 同上 |
| `MemoryProvider` ABC | `agent/memory_provider.py` |

教材剪枝：[`../hermes_src/`](../hermes_src/)（只读；本 demo 从完整仓 import）。

---

## Call flow

```text
FakeProvider registered
  prefetch_all(user) → raw
  build_memory_context_block(raw) → 拼进 api user
  build_system_prompt() → 静态块
  sync_all + queue_prefetch_all → FakeProvider.synced / queued
  → exports/mem_provider/
```

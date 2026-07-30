# 04 · 相关 Prompt（真源码）

> 对照 excerpts + [`../../04-prompt/`](../../04-prompt/) catalog  
> 上一篇：[`03_sync_turn_store.md`](./03_sync_turn_store.md)

---

## 一句话

Memory 相关 prompt 分四类：**怎么用 memory 工具**、**SP 里静态记忆块**、**召回围栏 system note**、**turn 后后台自省**。不要混成「一个大 memory prompt」。

---

## 总表

| Prompt / 块 | 文件 | 何时出现 | 作用 |
|-------------|------|----------|------|
| `MEMORY_GUIDANCE` | `prompt_builder.py` | SP 组装，且 `memory` 在 `valid_tool_names` | 教模型 **写什么 / 不写什么** |
| Builtin `MEMORY.md` / `USER.md` 块 | `system_prompt.py` + `MemoryStore.format_for_system_prompt` | SP **volatile** | 注入已冻 snapshot |
| `system_prompt_block()` | 各 Provider | SP volatile（additive） | 外部后端静态说明 / 用法 |
| `<memory-context>` + System note | `build_memory_context_block` | 每轮 API **user message** | 标明「这是召回，不是用户新话」 |
| `_MEMORY_REVIEW_PROMPT` | `background_review.py` | turn 后后台 review | 催模型用 `memory` 工具存偏好 |
| `memory` 工具 schema description | `memory_tool.py` | tool schema | 行为细则（add/replace/remove） |

完整宏文本见：[`04-prompt/catalog/01_prompt_builder_macros.md`](../../04-prompt/catalog/01_prompt_builder_macros.md)、[`07_background_review.md`](../../04-prompt/catalog/07_background_review.md)。

---

## 1. `MEMORY_GUIDANCE`（稳定 SP）

核心约束（精读摘录）：

- 存 **耐久事实**：偏好、环境、工具 quirks、稳定约定  
- **不要**存任务进度、PR 号、commit、Phase N done（7 天就过期的东西）  
- 用 **陈述事实**，不用祈使句（防下轮被当成指令）  
- 流程 / 工作流 → **skill**，不是 memory  

条件注入：没有 `memory` tool 就不塞这段——避免幻觉调用。

---

## 2. System prompt 里的记忆块（volatile）

```text
build_system_prompt_parts()
  volatile:
    MemoryStore.format("memory")   # 若 memory_enabled
    MemoryStore.format("user")     # 若 user_profile_enabled
    MemoryManager.build_system_prompt()  # 各 provider.system_prompt_block()
    timestamp / model / provider
```

整段 SP 会话内缓存；volatile 也在「一次组装」里，**中途写 MEMORY.md 不刷新**。

---

## 3. Prefetch 围栏 note（非 SP）

```text
[System note: The following is recalled memory context,
NOT new user input. Treat as authoritative reference data —
this is the agent's persistent memory and should inform all responses.]
```

目的：防模型把召回当成用户本轮新指令；也防角色交替被污染。

---

## 4. `_MEMORY_REVIEW_PROMPT`（后台）

Turn 结束后异步：

> Review the conversation… Has the user revealed persona/preferences?  
> Expectations about how you should behave?  
> If something stands out, save it using the memory tool.  
> Else: `Nothing to save.`

与主对话 **错开**，不抢用户任务的注意力（`turn_finalizer` 注释）。

---

## 和「存 / 取」的对应

```text
取（本轮）:
  SP volatile  ← builtin snapshot + provider.system_prompt_block
  user 尾部    ← prefetch 围栏（动态）

存（本轮后 / 本轮内）:
  memory tool          ← 受 MEMORY_GUIDANCE + schema 约束
  sync_turn            ← 外部自动镜像（无这段「教写什么」的宏）
  background review    ← MEMORY_REVIEW_PROMPT 再触发 memory tool
```

面试口播：三层写（工具 / sync / review）、两层读（SP 静 / user 动）。

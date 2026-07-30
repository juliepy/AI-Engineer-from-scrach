# System Prompt 组装地图

对照源码：`hermes_src/agent/system_prompt.py` → `build_system_prompt_parts()`  
宏定义：`hermes_src/agent/prompt_builder.py`

---

## 1. 三层返回值

```python
return {
    "stable":   "\n\n".join(stable_parts),
    "context":  "\n\n".join(context_parts),
    "volatile": "\n\n".join(volatile_parts),
}
# build_system_prompt() 再 "\n\n".join 非空三层
```

会话内缓存在 `agent._cached_system_prompt`。**只有 context compression 会重建。**

---

## 2. Stable 层注入顺序（简化）

| # | 内容 | 来源宏 / 函数 | 条件 |
|---|------|---------------|------|
| 1 | Identity | `load_soul_md()` **或** `DEFAULT_AGENT_IDENTITY` | skip_context_files 时可能跳过 SOUL |
| 2 | Hermes 自助文档指针 | `HERMES_AGENT_HELP_GUIDANCE` | 总是 |
| 3 | 做完再停 / 禁止伪造 | `TASK_COMPLETION_GUIDANCE` | 有工具 + config 开 |
| 4 | 并行工具调用 | `PARALLEL_TOOL_CALL_GUIDANCE` | 有工具 + config 开 |
| 5 | Memory / session_search / skills / kanban | `MEMORY_GUIDANCE` 等 | **对应 tool 在 schema 里才注入** |
| 6 | Steer 信道说明 | `STEER_CHANNEL_NOTE` | 有工具 |
| 7 | Computer-use | `computer_use_guidance()` | 有 `computer_use` tool |
| 8 | Nous 订阅 | `build_nous_subscription_prompt()` | 有订阅状态时 |
| 9 | Tool-use enforcement | `TOOL_USE_ENFORCEMENT_GUIDANCE` | auto 匹配 GPT/Codex/Gemini/… |
| 10 | 模型族额外纪律 | `GOOGLE_*` / `OPENAI_*` | gemini/gemma 或 gpt/codex/grok |
| 11 | Skills 索引 | `build_skills_system_prompt()` | 有 skills_* tools |
| 12 | Alibaba 模型名 workaround | 内联 f-string | provider==alibaba |
| 13 | 环境提示 | `build_environment_hints()` → WSL/Windows bash 等 | 探测到才有 |
| 14 | Coding posture | `coding_system_prompt_parts()` | 编码工作区 |
| 15 | Env probe / profile 提示 | 内联 | config / 非 default profile |
| 16 | Platform hint | `PLATFORM_HINTS[platform]` + config override | CLI/Telegram/… |

**设计要点**：大量 guidance **按 tool 是否加载条件注入** —— 没 memory tool 就不塞 MEMORY_GUIDANCE，避免模型幻觉调用不存在的工具。

---

## 3. Context 层

| 内容 | 函数 | 优先级 |
|------|------|--------|
| 工作区 coding snapshot | `coding_system_prompt_parts` 的 workspace 段 | 有则单独成 cache boundary |
| 调用方 `system_message` | 参数 | — |
| 项目上下文文件 | `build_context_files_prompt(skip_soul=True)` | `.hermes.md` > `AGENTS.md` > `CLAUDE.md` > `.cursorrules`（**只取一种**） |

SOUL 已在 identity 槽位用过时，`skip_soul=True` 防重复。

---

## 4. Volatile 层

| 内容 | 说明 |
|------|------|
| MEMORY.md 冻结快照 | session 启动冻住；中途 `memory` 写入**不改**已缓存 system |
| USER.md 冻结快照 | 同上 |
| Memory provider block | `memory_manager.build_system_prompt()` |
| 时间戳 / session / model / provider 行 | 每会话一次；压缩重建时会刷新 |

权威声明（常见于 memory 块后）：compaction summary **不得覆盖** MEMORY/USER。

---

## 5. 不进 Cached System 的东西

| 机制 | 落点 |
|------|------|
| `ephemeral_system_prompt` / `HERMES_EPHEMERAL_SYSTEM_PROMPT` | API 调用时叠加，不持久进缓存前缀 |
| `pre_llm_call` plugin 返回 | 拼进**当前 turn 的 user message** |
| 压缩摘要 | history 中间一条 user（`SUMMARY_PREFIX` + body + end marker） |
| Honcho dialectic / turn recall | 多半进 user overlay，不是改 system |

---

## 6. 和 Prompt Cache 的关系

- 前缀 = stable+context+volatile 整段 → 每 turn 复用 → 省钱。
- 中途改 skills / memory 注入到 system / 换 toolset → **废缓存** → Hermes 禁止（压缩除外）。
- Skill slash command：故意注入成 **user message**，不改 system。

对照：`AGENTS.md`「Prompt Caching Must Not Break」。

# Turn Context Demo

可跑通的 **单 turn prologue**（`build_turn_context`），打印：

1. 重要日志（preflight / should_compress / 切开 / 拼装）
2. **辅助模型**压缩用的完整 prompt + response
3. **主模型**拿到的 system + messages + response

## 目录

```text
demo/
├── README.md                 # 本文件
├── run_turn_context.py       # 入口：组装 + 跑通 + 导出
├── teaching/                 # 教学版实现（对照 hermes_src）
│   ├── teaching_memory.py
│   ├── teaching_compressor.py
│   ├── teaching_turn_context.py
│   ├── prompt_template.py    # 压缩摘要 prompt 宏 / 积木
│   └── llm.py                # DeepSeek 接口（aux 压缩 + 主模型）
├── fixtures/                 # MEMORY.md / USER.md / long_conversation.md
└── exports/turn_context/     # 跑完产物落在此目录下
```

对照：

| 本 demo | 源码 |
|---------|------|
| `teaching/teaching_turn_context.py` | `hermes_src/agent/turn_context.py` |
| `teaching/teaching_compressor.py` | `hermes_src/agent/context_compressor.py` |
| `teaching/teaching_memory.py` | `hermes_src/tools/memory_tool.py`（load + frozen snapshot） |
| `DemoAgent._compress_context` | `conversation_compression.compress_context`（去 DB/lock） |

讲稿：`../notebooks/5_compress.md`

---

## Code Call Flow（对照讲解用）

按 **demo 实际跑通的调用链** 讲；右侧是 Hermes 真源码对应点。

### 总览（文件级）

```text
run_turn_context.main()
 │
 ├─① TeachingMemoryStore.load_from_disk / build_system_prompt
 │      demo: teaching/teaching_memory.py
 │      源码: tools/memory_tool.py · MemoryStore.load_from_disk / format_for_system_prompt
 │
 ├─② load_conversation_history(long_conversation.md)
 │      demo: run_turn_context.py
 │      → history（无 system 行）
 │
 ├─③ build_turn_context(agent, user, history, …)
 │      demo: teaching/teaching_turn_context.py
 │      源码: agent/turn_context.py · build_turn_context
 │      │
 │      ├─ append user message
 │      ├─ active_system_prompt = agent._cached_system_prompt   # MEMORY+USER 已冻住
 │      ├─ _should_run_preflight_estimate?                     # 便宜门闸
 │      ├─ estimate_tokens_rough(+ system)
 │      ├─ TeachingContextCompressor.should_compress?          # 源码 ~:1278
 │      │      │ yes
 │      │      ▼
 │      ├─ DemoAgent._compress_context                         # ≈ compress_context ~:435
 │      │      │
 │      │      ├─ FixtureMemoryManager.on_pre_compress         # MemoryProvider hint
 │      │      └─ TeachingContextCompressor.compress            # 源码 ContextCompressor.compress
 │      │             ├─ 切开 head / middle / tail
 │      │             ├─ build_summarizer_prompt               # prompt_template.py
 │      │             ├─ summarize_fn(prompt)  ──► DeepSeek（辅助压缩）
 │      │             └─ SUMMARY_PREFIX + summary + END → 插回
 │      │
 │      ├─ memory_manager.on_turn_start / prefetch_all
 │      └─ return TurnContext
 │
 └─④ main_chat_fn(system, messages)  ──► DeepSeek（主模型）
        demo: teaching/llm.make_llm
        源码: run_conversation tool loop 的首次 API call
```

---

## Fixtures（已放入 `demo/fixtures/`）

| 文件 | 用途 |
|------|------|
| `MEMORY.md` | 代理个人笔记 → 冻进 system prompt 的 MEMORY 块 |
| `USER.md` | 用户画像 → 冻进 system prompt 的 USER PROFILE 块 |
| `long_conversation.md` | 长对话历史 → `conversation_history`（内嵌短 system 会被丢掉） |

`system_prompt` **不再用** `long_conversation.md` 里那几行短 MEMORY，而是：

```text
MEMORY.md + USER.md
  → TeachingMemoryStore.load_from_disk()
  → frozen snapshot
  → build_system_prompt()   # 整 session 缓存，保 Prompt Cache
```

压缩时 `on_pre_compress` 还会把 MEMORY/USER 身份事实塞进 summarizer 的 `provider_hint`。

---

## 跑法

```powershell
cd 01-memory/demo
pip install -r ../notebooks/requirements.txt

# 辅助压缩 + 主模型均调用 DeepSeek（需 API Key）
# 优先读 demo/.env，其次 notebooks/.env、仓库根 .env
python run_turn_context.py
```

`demo/.env` 示例：

```env
DEEPSEEK_API_KEY=sk-...
```

---

## 产物

跑完写入 `exports/turn_context/` 目录下：

```text
exports/turn_context/
├── 00_workflow.md          # 本 turn 摘要
├── 00_memory_block.md      # 冻进 system 的 MEMORY 块
├── 00_user_block.md        # 冻进 system 的 USER 块
├── 01_aux_prompt.md        # 发给摘要模型的完整 prompt
├── 02_aux_response.md      # 摘要正文
├── 03_main_system.md       # 主模型 system（含 MEMORY+USER）
├── 04_main_messages.md     # 压缩后发给主模型的 messages
└── 05_main_response.md     # 主模型回复
```

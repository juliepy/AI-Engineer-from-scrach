# hermes-study —— Hermes 学习剪枝版

从 `hermes-agent/` 主仓库剪出来的**学习子集**，只保留 [`03-hermes Agent 学习大纲.md`](../03-hermes%20Agent%20%20学习大纲.md) 四个模块要精读的源码。

> ⚠️ 这是**只读学习副本**，不是可运行工程：缺少 `hermes_constants.py`、`agent/` 其余依赖、`pyproject.toml` 等，`import` 跑不起来。目的是**读代码 + 打断点对照**，要真跑请回主仓库 `hermes-agent/`。

---

## 目录结构与模块映射

```text
hermes-study/
├── AGENTS.md                         # 贯穿全程：Footprint Ladder / Prompt Caching / 测试规范
│
├── run_agent.py                      # 【模块一】主循环入口 AIAgent.run_conversation()
├── model_tools.py                    # 【模块一】工具发现 + 分发 handle_function_call()
├── toolsets.py                       # 【模块一】_HERMES_CORE_TOOLS / TOOLSETS
├── cli.py                            # 【模块一】HermesCLI 交互入口（打断点用）
├── hermes_state.py                   # 【模块一】SessionDB 会话存储（看消息序列）
├── tools/
│   ├── registry.py                   # 【模块一】registry.register() 自动发现
│   ├── todo_tool.py                  # 【模块一】agent 级工具拦截范例
│   └── environments/                 # 【模块二】执行环境后端抽象
│       ├── base.py                   #   先读：统一接口
│       ├── local.py                  #   本地进程（无隔离基线）
│       ├── docker.py                 #   Docker 隔离（sandbox demo 主参考）
│       ├── ssh.py / modal.py / managed_modal.py
│       ├── daytona.py / singularity.py
│       └── file_sync.py / modal_utils.py
│
├── agent/                            # 【模块三】Memory + Context
│   ├── memory_provider.py            #   MemoryProvider ABC
│   ├── memory_manager.py             #   多 provider 编排
│   ├── context_compressor.py         #   上下文压缩（唯一允许改上下文）
│   ├── conversation_compression.py
│   ├── context_engine.py
│   ├── turn_context.py
│   └── prompt_caching.py             #   Prompt 缓存前缀控制
├── plugins/memory/honcho/            # 【模块三】可插拔记忆后端示例（对照 ABC 看实现）
│
├── hermes_logging.py                 # 【模块四】结构化日志
├── scripts/run_tests.sh              # 【模块四】CI 对齐测试入口
└── tests/agent/                      # 【模块四】测试范例（不变量断言 vs 快照断言）
    ├── test_memory_provider.py
    ├── test_context_compressor.py
    └── test_prompt_caching.py
```

---

## 建议阅读顺序

1. **模块一 · 主循环**：`run_agent.py`（`run_conversation()` 的 while 循环）→ `model_tools.py` → `toolsets.py` → `tools/registry.py`。
2. **模块二 · Sandbox**：`tools/environments/base.py` → `local.py` → `docker.py`，对比隔离强度。
3. **模块三 · Memory + Context**：`agent/memory_provider.py` → `memory_manager.py` → `context_compressor.py` → `prompt_caching.py`，再看 `plugins/memory/honcho/` 一个真实实现。
4. **模块四 · Eval + Trace**：`tests/agent/*` 看测试怎么写不变量，`hermes_logging.py` 看日志分层。

`AGENTS.md` 全程对照：任何设计取舍先看它里面的规则（尤其 Prompt Caching、Footprint Ladder、Don't write change-detector tests）。

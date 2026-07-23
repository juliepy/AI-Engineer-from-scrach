# Hermes Eval + Trace · 如何学习

目标：用 **源码副本 + 讲稿** 讲清「怎么评测 Agent」和「怎么用日志做 Trace 根因」。

对照大纲：[`../03-hermes Agent  学习大纲.md`](../03-hermes%20Agent%20%20学习大纲.md) **模块二**。

学法：

1. 先读本 README + `notes/` 讲稿  
2. 打开 `hermes_src/` 对照真文件行号  
3. 动手：写 1 条不变量断言；用 `hermes logs` / LangFuse 录一条 Trace  

> `hermes_src/` 是只读剪枝，**不能当完整工程跑**。真跑测试请回主仓库 `hermes-agent/` 用 `scripts/run_tests.sh`。

---

## 目录

```text
02-eval/
├── README.md                      # 本文件
├── notes/
│   ├── 1_eval_invariants.md       # 不变量断言 vs 变更检测
│   └── 2_logging_trace.md         # hermes_logging + session_tag
└── hermes_src/                    # 真源码剪枝（对照）
    ├── README.md
    ├── AGENTS.md                  # 「Don't write change-detector tests」
    ├── hermes_logging.py          # agent.log / errors.log / gateway.log
    ├── scripts/run_tests.sh       # CI 对齐唯一入口
    └── tests/agent/
        ├── test_prompt_caching.py       # ★ 课堂主文件（短）
        ├── test_context_compressor.py   # 压缩不变量（长，摘读）
        └── test_memory_provider.py      # Provider 契约（摘读）
```

---

## 建议阅读顺序

| 顺序 | 材料 | 重点 |
|------|------|------|
| 1 | `notes/1_eval_invariants.md` | 行为契约 vs 快照 |
| 2 | `hermes_src/tests/agent/test_prompt_caching.py` | `assert count <= 4` 类不变量 |
| 3 | `hermes_src/AGENTS.md` 测试小节 | 官方「不要写 change-detector」 |
| 4 | `notes/2_logging_trace.md` | session_tag / 组件分流 |
| 5 | `hermes_src/hermes_logging.py` | `setup_logging` / `COMPONENT_PREFIXES` |
| 6 | `hermes_src/scripts/run_tests.sh` | 为何不能直接 `pytest` |

---

## 动手（对齐大纲产出）

1. **评测集**：给一个具体任务写 20~50 条用例；至少 1 条断言是「关系/不变量」，不是「模型名列表快照」。  
2. **Trace**：接 LangFuse（或自建 span），录一轮 tool call；用 `session_id` 在 `agent.log` 里对齐同一条因果链。  
3. **面试一句话**：好测试断言数据之间的关系；一条 Trace 如何区分「工具选错 / 上下文溢出 / 预算耗尽」。

---

## 与其它模块

| 模块 | 关系 |
|------|------|
| [`04.1-memory/`](../04.1-memory/) | 压缩 / cache 测试用例的业务背景 |
| [`03-run-agent/`](../03-run-agent/) | Trace 里的 tool/LLM span 对应主循环一步 |

# Hermes Memory · 如何学习

目标：用 **可执行的源码副本** 讲清 Memory 实现逻辑（对照 `hermes_src/` 真文件）。

学法：

1. 打开 notebook → **第一段大 code cell = 从 Hermes 拷过来的实现**（可直接 Run）
2. 下面的演示 cell 调用这段实现，边跑边讲
3. 需要查原文时打开 `hermes_src/` 对应文件（行号写在 cell 注释里）

> 不是调封装库；是 **把源码逻辑拷进 notebook 跑通**，方便讲解。

---

## 目录

```text
04.1-memory/
├── README.md                          # 本文件：学法、目录、各章对照
├── hermes_src/                        # 真源码剪枝（只读对照，不可当工程跑）
│   ├── README.md                      # hermes_src 说明与文件职责表
│   ├── AGENTS.md                      # Hermes 开发规范（Prompt Cache / 测试等）
│   ├── tools/
│   │   └── memory_tool.py             # MemoryStore：frozen snapshot + live entries
│   ├── agent/
│   │   ├── memory_provider.py         # MemoryProvider ABC（外部/内置 Provider 接口）
│   │   ├── memory_manager.py          # 编排层；同时只允许一个外部 Provider
│   │   ├── context_compressor.py      # Context 压缩（唯一允许改上下文的路径）
│   │   ├── conversation_compression.py# 会话级压缩辅助 / 触发逻辑
│   │   ├── context_engine.py          # Context Engine 抽象（插件化上下文引擎）
│   │   ├── prompt_caching.py          # Anthropic system_and_3 缓存断点
│   │   └── turn_context.py            # 单 turn 上下文组装
│   └── plugins/memory/
│       ├── __init__.py
│       └── honcho/                    # 真实外部 Provider 范例（Honcho）
├── demo/                              # 可跑通脚本（推荐先跑）
│   ├── README.md                      # Turn Context demo 说明
│   ├── run_turn_context.py            # 入口：prologue + 打印 aux/main prompt
│   ├── teaching/                      # 教学版实现（对照 hermes_src）
│   │   ├── teaching_memory.py         # MemoryStore load + frozen snapshot
│   │   ├── teaching_compressor.py     # ContextCompressor
│   │   ├── teaching_turn_context.py   # build_turn_context
│   │   ├── prompt_template.py         # 压缩摘要 prompt 宏 / 积木
│   │   └── llm.py                     # DeepSeek 接口（aux 压缩 + 主模型）
│   ├── fixtures/                      # MEMORY / USER / long_conversation
│   └── exports/turn_context/          # 跑通产物
└── notebooks/                         # 可执行教学 notebook（边跑边讲）
    ├── requirements.txt               # notebook 依赖（含 DeepSeek 客户端等）
    ├── fixtures/                      # 第 1 章 load_from_disk 用的真实记忆文件
    │   ├── MEMORY.md                  # 代理个人笔记（§ 分隔条目）
    │   └── USER.md                    # 用户画像（§ 分隔条目）
    ├── MEMORY.md                      # 同 fixtures 的备用副本（可手动对照）
    ├── USER.md                        # 同 fixtures 的备用副本（可手动对照）
    ├── 1_memory_layers.ipynb          # MemoryStore 双态 + 读真实 md
    ├── 2_memory_provider.ipynb        # MemoryProvider ABC + DemoProvider
    ├── 3_memory_manager.ipynb         # MemoryManager 单外部 Provider 编排
    ├── 4_context_compression.ipynb    # 压缩算法 + DeepSeek 摘要
    ├── 5_compress.md                  # 压缩讲稿（turn → compress 调用链）
    ├── 5_prompt_caching.ipynb         # prompt_caching.py 整文件可跑
    └── 6_end_to_end.ipynb             # Session boot → turn → compress 串联
```

### 各部分作用

| 路径 | 作用 |
|------|------|
| `README.md` | 学习入口：怎么用 notebook、学什么、目录地图 |
| `hermes_src/` | 从 Hermes 剪出的 Memory/Context 真源码，**只读对照**；缺依赖，不能当完整工程运行 |
| `hermes_src/tools/memory_tool.py` | Layer1：`MemoryStore`，session 启动冻 snapshot，中途 `add` 只改 live |
| `hermes_src/agent/memory_provider.py` | Provider 生命周期接口（`initialize` / `prefetch` / `sync_turn` 等） |
| `hermes_src/agent/memory_manager.py` | 把 builtin + 至多一个外部 Provider 编在一起 |
| `hermes_src/agent/context_compressor.py` | 上下文压缩实现；唯一合法「改过去上下文」的入口 |
| `hermes_src/agent/prompt_caching.py` | 缓存断点策略（如 `system_and_3`），保证前缀稳定可命中 |
| `hermes_src/plugins/memory/honcho/` | 生产级外部 Provider 参考实现 |
| `demo/` | 可跑通脚本：turn prologue + 打印 aux/main prompt |
| `notebooks/*.ipynb` | 把源码逻辑拷进 cell 可直接 Run；顺序 `1 → 6` |
| `notebooks/fixtures/*.md` | 本机 `~/.hermes/memories/` 的真实副本，供第 1 章 `load_from_disk` |
| `notebooks/requirements.txt` | 跑 notebook 前安装依赖 |

顺序：`1 → 2 → 3 → 4 → 5 → 6`。第 4、6 章需要 `DEEPSEEK_API_KEY`。

```bash
cd notebooks
pip install -r requirements.txt
$env:DEEPSEEK_API_KEY = "sk-..."   # PowerShell
```

---

## 各章拷了什么

| 章 | 拷自 | 讲解重点 |
|----|------|----------|
| 1 | `tools/memory_tool.py` → `MemoryStore` | `load_from_disk` 冻 snapshot / live 可写 / `format_for_system_prompt` |
| 2 | `agent/memory_provider.py` | 生命周期方法；再写一个可跑的 DemoProvider |
| 3 | `agent/memory_manager.py` | `add_provider` 只允许一个外部；prefetch/sync 编排 |
| 4 | `agent/context_compressor.py` | `SUMMARY_PREFIX` + 保头保尾 + DeepSeek 摘要 |
| 5 | `agent/prompt_caching.py` | `system_and_3` 断点（几乎整文件拷贝） |
| 6 | 以上串联 | Session boot → turn → compress |

---

## 学完能讲清

1. Frozen snapshot 保 Prompt Cache  
2. Provider 生命周期  
3. 同时只能一个外部 Provider  
4. 压缩是唯一合法改上下文  
5. `system_and_3` 缓存断点  

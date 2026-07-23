# 2 · 工具发现与分发

> 对照：  
> `../hermes_src/tools/registry.py` — `discover_builtin_tools` ~`:58`，`register` ~`:356`  
> `../hermes_src/model_tools.py` — 触发发现；`handle_function_call` ~`:1025`  
> `../hermes_src/toolsets.py` — `_HERMES_CORE_TOOLS` ~`:31`

---

## 0. 一句话

工具不是手写 import 列表；`tools/*.py` 在 import 时 `registry.register(...)`，`model_tools` 导入时触发发现；主循环拿到的 schema 来自 **toolset 组装**，调用走 `handle_function_call` → `registry.dispatch`。

---

## 1. 依赖链（必背）

```text
tools/registry.py          # 无业务依赖
      ↑
tools/todo_tool.py 等      # 顶层 register()
      ↑
model_tools.py             # import 时 discover_builtin_tools()
      ↑
conversation_loop          # 每步把 tools=schema 发给模型
                           # tool_calls → handle_function_call
```

---

## 2. 发现：`discover_builtin_tools`

```text
扫 tools/*.py
  → AST 看是否有顶层 registry.register
  → importlib.import_module("tools.xxx")
  → 注册进全局 registry
```

**不是**「文件在就暴露给模型」——还要进入某个 **toolset**（如 `_HERMES_CORE_TOOLS`）才会进默认 schema。

---

## 3. 组装：`toolsets.py`

| 符号 | 含义 |
|------|------|
| `_HERMES_CORE_TOOLS` | 各平台默认继承的核心工具名列表 |
| `TOOLSETS` | 命名工具集（web / messaging / …）可 includes 组合 |

**Footprint Ladder（AGENTS.md）**：每个核心工具 = 每次 API 都付 schema 成本 → 新能力优先 CLI/skill/plugin/MCP，最后才加 core tool。

---

## 4. 分发：`handle_function_call`

典型路径：

```text
coerce 参数类型
  → pre_tool_call hooks
  → registry 找到 handler
  → 执行，返回 JSON 字符串
  → post_tool_call hooks
```

特殊：Tool Search bridge、`todo`/`memory` 等可能被 **agent 级提前拦截**（见下一讲）。

---

## 5. 建议讲解（12 min）

1. 打开 `todo_tool.py` 文件末尾 `registry.register(...)`  
2. 打开 `registry.discover_builtin_tools`  
3. 打开 `_HERMES_CORE_TOOLS` 扫一眼有哪些类  
4. 打开 `handle_function_call` 签名，强调「返回必须是 JSON str」  

---

## 6. 自检

1. 只写了 `tools/foo.py` 但没进任何 toolset，模型看得到吗？  
2. 为什么加核心工具门槛高？  
3. `discover_builtin_tools` 和 `get_tool_definitions` 分工？

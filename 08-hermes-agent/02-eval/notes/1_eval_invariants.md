# 1 · Eval：不变量断言 vs 变更检测

> 对照：`../hermes_src/AGENTS.md`（Don't write change-detector tests）  
> 范例：`../hermes_src/tests/agent/test_prompt_caching.py`

---

## 0. 一句话

评测 / 单测要断言 **行为契约（数据之间必须成立的关系）**，不要断言 **今天碰巧等于多少** 的快照——模型列表、config 版本号、枚举数量都会变，快照测试只会让 CI 无意义地红。

---

## 1. 坏例子 vs 好例子（AGENTS.md）

| 坏（change-detector） | 好（invariant / contract） |
|----------------------|----------------------------|
| `assert "gemini-2.5-pro" in MODELS` | `assert "gemini" in MODELS and len(MODELS["gemini"]) >= 1` |
| `assert _config_version == 21` | `assert raw["_config_version"] == DEFAULT_CONFIG["_config_version"]` |
| `assert len(models) == 8` | `assert not (set(A) & set(B))` 互斥不变量 |

Agent Eval 维度同理：完成率、步数、成本、工具选对率、忠实度——断言「关系与阈值」，不要冻结某一天的模型名。

---

## 2. 课堂主文件：`test_prompt_caching.py`

打开文件，找这类断言：

| 断言意图 | 为什么是不变量 |
|----------|----------------|
| 断点数量 `<= 4` | Anthropic 预算上限，不是「今天恰好 3 个」 |
| 空 content 的 assistant/tool **不消耗**断点 | 载体契约：浪费名额会破坏 cache |
| OpenRouter vs native 挂载位置不同 | Provider 布局契约 |

**板书**：

```text
Snapshot  = 今天长什么样
Invariant = 永远必须成立的关系
Eval 要写第二种
```

---

## 3. 摘读另外两个大文件（作业）

### `test_context_compressor.py`（很长，别通读）

搜这些模式：

- 压缩后 `"_db_persisted" not in msg`（marker 剥离契约）
- `index(prior) < index(summary) < index(end)`（顺序不变量）
- `tail_size >= 3`（下限关系，不是固定条数快照）

### `test_memory_provider.py`

- 工具注入 **去重**（同名只出现一次）
- 平台 toolset 门控（不该出现的工具必须 suppress）

---

## 4. `run_tests.sh` 为什么必须用

| 直接 `pytest` | `scripts/run_tests.sh` |
|---------------|------------------------|
| 本机 API key 可能泄漏进测试行为 | 清凭证，与 CI 一致 |
| 本地 TZ / locale 漂移 | `TZ=UTC` `LANG=C.UTF-8` |
| 模块级全局态串测 | 每文件子进程隔离 |

讲一句：**Eval 环境 hermetic，结果才可复现。**

---

## 5. 动手最小题

写一条假想评测断言（伪代码即可）：

```python
# 坏
assert agent.model == "claude-sonnet-4"

# 好：工具选对率不变量
assert correct_tool_calls / total_tool_calls >= 0.8
assert "rm -rf /" not in "".join(terminal_commands)  # 安全契约
```

---

## 6. 自检

1. 什么是 change-detector test？举一个 Hermes 会拒绝的例子。  
2. `assert count <= 4` 为什么比 `assert count == 3` 更稳？  
3. 为什么评测脚本也要尽量 hermetic？

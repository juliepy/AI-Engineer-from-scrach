# Deterministic evals（确定性评测）

0/1 断言，不靠 LLM 打分。测的是「该不该调工具 / 状态对不对 / 纯函数行为」，和 `evals/judge/`（DeepEval 打分）**永不混用**。

当前约 **200** 条 case（`pytest --collect-only`）。

---

## 怎么跑

```bash
# 全部（含 live：需当前 provider 的 API key）
uv run python -m pytest -q evals/deterministic

# 仅离线（CI / 无 key 时用这个）
uv run python -m pytest -q evals/deterministic -m "not live"

# 单个文件
uv run python -m pytest -q evals/deterministic/test_wake_word.py
```

有 Make：`make eval`。发布门禁要求 deterministic 全绿。

`@pytest.mark.live`：真实模型 + `evals/dataset.jsonl`，行为随 `WAKU_PROVIDER` 可能波动。

---

## Case 一览

| 文件 | 在测什么 |
|------|----------|
| [`test_tool_trigger.py`](test_tool_trigger.py) | **旗舰**：loop / 工具 / 产物。离线用 ScriptedClient；live 跑 `dataset.jsonl` |
| [`test_scoring.py`](test_scoring.py) | Completion 打分契约：`expect_tool` / `expect_in_args` / `min_tool_calls` |
| [`test_shootout.py`](test_shootout.py) | Shootout 离线计分 + demo beat 数据集齐全 |
| [`test_judge.py`](test_judge.py) | K3 referee 的解析/夹逼/坏 JSON 降级（不调真实 judge） |
| [`test_coding_eval.py`](test_coding_eval.py) | 跨模型 coding runner：verify 通过/失败、缺 key、stream 行输出 |
| [`test_providers.py`](test_providers.py) | 每个 PROVIDERS 条目：建 client、缺 key 报错、定价表覆盖 |
| [`test_models.py`](test_models.py) | xAI / OpenAI / Gemini / DeepSeek / MiniMax 的 key、端点、模型默认值 |
| [`test_pinned_models.py`](test_pinned_models.py) | 「Your models」置顶：默认、切换 provider、分组展示 |
| [`test_working_memory.py`](test_working_memory.py) | system prompt 含当前时间、session id、自身模型身份 |
| [`test_history_window.py`](test_history_window.py) | 历史滑动窗口：有界、默认慷慨但有限 |
| [`test_turn_meta.py`](test_turn_meta.py) | 每轮 meta（gate / iterations）落库与旧行兼容 |
| [`test_cli_memory.py`](test_cli_memory.py) | CLI `/memory` 读本地 SQLite 快照 |
| [`test_episodic_store_switch.py`](test_episodic_store_switch.py) | sqlite \| notion 情景存储切换、缓存、宕机降级 |
| [`test_notion_episodes.py`](test_notion_episodes.py) | NotionEpisodeStore：增删查、database id 规范化（mock） |
| [`test_compare_history.py`](test_compare_history.py) | Compare 竞技场独立 JSONL：append / clear / 聚合（不写 state.db） |
| [`test_all_history.py`](test_all_history.py) | Dashboard「All messages」跨线程时间线 |
| [`test_session_resume.py`](test_session_resume.py) | Dashboard 恢复最近活跃线程（仅 dashboard 来源） |
| [`test_session_rotation.py`](test_session_rotation.py) | 空闲线程轮换；切 provider 清掉陈旧 model override |
| [`test_show_trace.py`](test_show_trace.py) | 终端 trace 缩进时间线；未结束 turn 不污染后续 |
| [`test_trace_encoding.py`](test_trace_encoding.py) | JSONL 强制 UTF-8；legacy 非 UTF-8 只报错不改写 |
| [`test_skill_encoding.py`](test_skill_encoding.py) | SKILL.md 读写统一 UTF-8（loader / agent / install / dashboard） |
| [`test_static_assets.py`](test_static_assets.py) | Dashboard 静态资源存在；inline handler 有定义；旧 `app.js` 已移除 |
| [`test_wake_word.py`](test_wake_word.py) | 唤醒词匹配：该醒 / 不该醒（含变体与日语） |
| [`test_speakable.py`](test_speakable.py) | TTS 前剥 emoji / markdown |
| [`test_apple_calendar.py`](test_apple_calendar.py) | AppleScript 日期顺序、转义、空调用 |
| [`test_delegate.py`](test_delegate.py) | `delegate_task` → pi：调用参数、缺安装、超时、实验开关 |
| [`test_workspace.py`](test_workspace.py) | 委托编码工作区：日期目录、autorun、manifest |

---

## Live 数据集（`evals/dataset.jsonl`）

由 `test_tool_trigger.py::test_dataset_case` 参数化；需 key，且标 `@pytest.mark.live`。

| id | 期望 |
|----|------|
| `schedule-basic` | `create_event`，标题含 alex，时间 T09:00 |
| `schedule-applies-memory` | 先写偏好事实，再约 Alex → `create_event` |
| `remember-preference` | `save_note`，内容含 morning |
| `draft-message` | `send_message`，body 含 friday |
| `no-tool-general-knowledge` | 不问工具（首都常识） |
| `pokemon-team` | 至少 3 次工具调用，且 `save_note` 含 pikachu |
| `worldcup-final` | 至少 3 次工具，`send_message` to raj |
| `chitchat-no-action` | 闲聊 → 无工具 |
| `exact-count-sessions` | 三个 focus → `create_event`，最少 3 次 |
| `remember-and-book` | 记住素食再约 Sam → 至少 2 次工具 |
| `read-before-write` | 先查日历再约 walk → 至少 2 次工具 |

---

## 约定

- 新行为 / 线上 bug → 在这里加回归 case（优先离线、纯断言）。
- 加工具走 `.claude/skills/new-tool`：schema + 安全执行 + 本目录一条 eval。
- 质量「好不好听」放 `evals/judge/`，不要塞进本目录。

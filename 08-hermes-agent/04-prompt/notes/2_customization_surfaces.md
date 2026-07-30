# 该改哪一层？定制 Prompt 的正确入口

多数人想「改 Hermes 性格 / 项目规则」时，**不要**直接改 `prompt_builder.py`。

---

## 优先用这些表面（官方推荐）

| 你想改什么 | 改哪里 | 进哪一层 |
|------------|--------|----------|
| Agent 人格 / 站立行为 | `~/.hermes/SOUL.md` | stable identity（替换 `DEFAULT_AGENT_IDENTITY`） |
| 跨会话事实 | `~/.hermes/memories/MEMORY.md` | volatile 快照 |
| 用户画像 | `~/.hermes/memories/USER.md` | volatile 快照 |
| 仓库工作规则 | `.hermes.md` / `AGENTS.md` / `CLAUDE.md` / `.cursorrules` | context（**四选一**，优先级见组装地图） |
| 可复用流程 | Skills（`SKILL.md`） | stable 里的 skills **索引**；正文用 `skill_view` 按需加载 |
| 部署级额外指令 | config / API `system_message` | context |
| 只影响某一平台语气 | `config.yaml` → `platform_hints.<platform>` | stable platform 段（append/replace） |
| 单次会话临时指令 | `HERMES_EPHEMERAL_SYSTEM_PROMPT` / prefill | **不进**缓存前缀 |

---

## 何时才改 Python 宏

只有当你在：

- 维护 fork，或
- 给上游提 PR（改全体用户的默认行为）

才应改 `prompt_builder.py` / `system_prompt.py`。那是**产品级**变更，不是个人配置。

---

## 条件注入 = 省 token + 防幻觉

`MEMORY_GUIDANCE` / `SESSION_SEARCH_GUIDANCE` / `SKILLS_GUIDANCE` / `KANBAN_GUIDANCE` 都检查 `agent.valid_tool_names`。

面试话术：

> Hermes 不把所有行为说明无塞进 system；工具不在 schema 里，对应 guidance 也不出现，避免模型编造工具调用。

---

## 用户可感知的「最终 system」长什么样

跑 `02-run-agent` demo 后看：

`../02-run-agent/demo/exports/agent_loop/01_system.md`

那是宏拼装后的**实例**；本目录 `catalog/` 是宏的**原文库**。两份对照学最快。

# 诚实说明 + 全仓「模块 → Prompt」地图

## 先回答你的三个问题

| 问题 | 答案 |
|------|------|
| 读了 `setup.py` 了吗？ | 读了。**它不是 prompt 文件**——只是 setuptools 打包：把 `skills/`、`optional-skills/` 打进安装包，并处理只读源码树时的临时 build 目录。 |
| 是否读过整个 hermes-agent？ | **之前没有。** 上一轮只扫了剪枝的 `hermes-study` + 上游部分文件；你本机完整仓在 `面试狂魔/人工智能面试题/hermes-agent/`，下面这张地图才按**全仓**整理。 |
| 是否包含所有 prompt？ | **核心 runtime / CLI / gateway 的 LLM prompt 已覆盖。** Skills / optional-skills 里还有大量「教 agent 怎么干活」的 SKILL.md（那是第三类：技能正文，不是 Python 宏）。UI 里叫 prompt 的多为**用户输入框**（clarify/sudo），不是发给模型的 system prompt。 |

---

## Prompt 分三类学（不要混）

```text
① Cached System Prompt   → 主对话前缀，会话内字节稳定（prompt cache）
② Auxiliary / Side LLM   → 压缩、标题、Judge、Curator、MoA reference…
③ User-turn injection    → /learn、/goal 续跑、background review、skill slash
```

另有一类 **④ Skill 正文**（`skills/**/SKILL.md`）：模型用 `skill_view` 按需加载，不整库塞进 system。

---

## ① 主对话 System Prompt（每会话组装一次）

| 模块 / 文件 | Prompt 角色 | 关键符号 |
|-------------|-------------|---------|
| `agent/system_prompt.py` | **编排**：stable / context / volatile | `build_system_prompt_parts` |
| `agent/prompt_builder.py` | **宏库**：identity、guidance、平台提示 | `DEFAULT_AGENT_IDENTITY`、`MEMORY_GUIDANCE`、`PLATFORM_HINTS`… |
| `agent/coding_context.py` | 编码工作区操作简报 | `CODING_AGENT_GUIDANCE` |
| `agent/verify_hooks.py` | 编码后 verify 纪律 | `CODING_VERIFY_GUIDANCE` |
| `tools/memory_tool.py` | MEMORY.md / USER.md **冻结快照**进 volatile | `format_*` / snapshot |
| `agent/memory_manager.py` | 外部 memory provider 静态块 | `build_system_prompt()` / `system_prompt_block()` |
| `~/.hermes/SOUL.md` | 用户人格（替换 DEFAULT） | `load_soul_md()` |
| 项目 `AGENTS.md` 等 | 仓库规则进 context | `build_context_files_prompt` |
| `config.yaml` `platform_hints` | 覆盖某一平台语气 | `_resolve_platform_hint` |

**学法**：先读 `notes/1_assembly_map.md`，再读 `catalog/01_prompt_builder_macros.md`。

---

## ② 辅助模型 Prompt（旁路，不进缓存前缀）

| 模块 / 文件 | 干什么 | 关键符号 |
|-------------|--------|---------|
| `agent/context_compressor.py` | 上下文压缩摘要 | `SUMMARY_PREFIX` + `_generate_summary` 内 preamble/template |
| `agent/title_generator.py` | 会话自动标题 | `_TITLE_PROMPT` |
| `agent/curator.py` | 后台 skill 库整理 | `CURATOR_REVIEW_PROMPT` |
| `agent/moa_loop.py` | MoA 参考模型（只参谋不行动） | `_REFERENCE_SYSTEM_PROMPT` |
| `hermes_cli/goals.py` | `/goal` 续跑 + **Judge** 判 DONE/WAIT/CONTINUE | `JUDGE_SYSTEM_PROMPT`、`CONTINUATION_PROMPT_*`、`DRAFT_CONTRACT_*` |
| `hermes_cli/kanban_specify.py` | Kanban 任务分诊 | `_SYSTEM_PROMPT` / `_USER_TEMPLATE` |
| `hermes_cli/kanban_decompose.py` | Kanban 拆子任务 | 同上 |
| `hermes_cli/profile_describer.py` | Profile 一句话描述 | `_SYSTEM_PROMPT` |
| `gateway/sticker_cache.py` | 贴纸视觉理解 | `STICKER_VISION_PROMPT` |
| `cron/scripts/classify_items.py` | Cron 条目分类 | `_CLASSIFY_INSTRUCTIONS` |
| `tools/image_generation_tool.py` | 图像放大默认提示 | `UPSCALER_DEFAULT_PROMPT` |
| `plugins/image_gen/openai-codex/` | Codex 生图指令 | `_CODEX_INSTRUCTIONS` |
| `plugins/platforms/feishu/feishu_comment.py` | 飞书评论辅助 | `_COMMON_INSTRUCTIONS` |

Auxiliary 路由配置：`config.yaml` → `auxiliary.<task>`（compression / title_generation / curator / vision…）。

---

## ③ 注入成 User 消息的 Prompt（故意不改 system）

| 模块 / 文件 | 场景 | 关键符号 |
|-------------|------|---------|
| `agent/skill_commands.py` | `/skill-name` slash | `_SKILL_INVOCATION_PREFIX` + skill 正文 |
| `agent/learn_prompt.py` | `/learn` 写 skill | `_AUTHORING_STANDARDS` + `build_learn_prompt` |
| `agent/background_review.py` | 回合后 memory/skill 自省 | `_MEMORY_REVIEW_PROMPT`、`_SKILL_REVIEW_PROMPT`、`_COMBINED_REVIEW_PROMPT` |
| `hermes_cli/goals.py` | goal 循环续跑 | `CONTINUATION_PROMPT_*`（拼进下一轮 user） |
| `gateway/run.py` | 自动续聊 / 观察上下文 | `_AUTO_CONTINUE_*`、Telegram observed context |
| `agent/subdirectory_hints.py` | 进入子目录发现 AGENTS.md | 渐进注入（非改 system） |
| `HERMES_EPHEMERAL_SYSTEM_PROMPT` | 临时 system 叠加 | CLI / env，**不持久进缓存前缀** |

**为什么要 User 注入？** 保住 prompt cache：改 system = 废前缀；改最新 user = 便宜。

---

## ④ Skills / Optional-skills（第三大块，别当「漏了」）

| 路径 | 是什么 |
|------|--------|
| `skills/**/SKILL.md` | 内置技能：索引进 system，正文按需 `skill_view` |
| `optional-skills/**` | 更重/小众；安装后才进索引 |
| `skills/.../references/*prompt*` | 个别 skill 自带提示词库（如 creative） |

学 runtime prompt **先别沉进 optional-skills**；那是产品内容，不是 Agent Runtime 腰部。

---

## 不是 LLM Prompt（别误读）

| 名字带 prompt | 实际是 |
|---------------|--------|
| `setup.py` | 打包 |
| `ui-tui/.../prompts.tsx`、`apps/desktop/.../prompt-overlays` | 用户交互 UI（审批/澄清） |
| `hermes_cli/secret_prompt.py` | 终端里问密钥 |
| `agent/prompt_caching.py` | cache breakpoint 策略，不是文案 |

---

## 建议学习路径（按模块）

```text
第 1 天  System 组装
         system_prompt.py + prompt_builder.py + coding_context.py
         → catalog/01 + notes/1_assembly_map.md

第 2 天  Memory 进 prompt + 压缩
         MEMORY/USER 快照 + context_compressor
         → catalog/03* + 01-memory demo

第 3 天  User-turn 注入
         skill_commands / learn_prompt / background_review
         → 理解「为什么 /skills 不改 system」

第 4 天  辅助编排
         goals Judge、MoA reference、title、curator、kanban LLM
         → 理解「旁路模型各自的角色 prompt」

第 5 天  对照真实输出
         02-run-agent/demo/exports/agent_loop/01_system.md
         + hermes prompt-size（若已装 CLI）
```

---

## 完整仓路径

源码根：`D:\workspace\doc\面试狂魔\人工智能面试题\hermes-agent\`  
教材目录：`AI_coding_interview/08-hermes-agent/04-prompt/`  
官方文档：`hermes-agent/website/docs/developer-guide/prompt-assembly.md`

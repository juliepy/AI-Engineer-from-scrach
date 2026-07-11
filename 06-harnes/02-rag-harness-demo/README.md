# RAG Harness Demo

用于教学的 RAG（检索增强生成）全栈 Harness 工程。
仿照 `harness-engineering-demo` 的 **PIV 循环**，精简到可在课堂一节课内讲完。

> **Harness Engineering** = 用规则、工作流和自动检查**包裹** Agent，
> 让它像团队里的工程师一样工作，而不是一个猜测你意图的陌生人。

---

## Harness 的两个核心组件

```
┌─────────────────────────────────────────────────────────┐
│  AI Layer（会话内）                                       │
│  CLAUDE.md — 规则 + 模式 + 命令速查                      │
│  .claude/skills/  — /plan  /implement  /validate        │
└─────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────┐
│  自动化 Hook（无需调用，自动触发）                         │
│  PostToolUse → 每次编辑后 ruff check                     │
│  Stop        → 结束前必须 pytest 全绿                    │
└─────────────────────────────────────────────────────────┘
```

---

## RAG 管道（教学主线）

```text
ingest → chunk → index → retrieve → generate
  │        │        │         │          │
  │        │        │         │          └─ app/generator.py  ← 课堂练习点
  │        │        │         └─ app/retriever.py
  │        │        └─ app/indexer.py  (TF-IDF)
  │        └─ app/chunker.py
  └─ data/sample_docs/*.txt
```

每个阶段独立成文件，方便讲解「为什么这样拆」。

---

## 项目结构

```text
02-rag-harness-demo/
├── CLAUDE.md                    # AI Layer：命名规范 + 代码模式 + 构建命令 + 硬性规则
├── .claude/
│   ├── settings.json            # Hook 注册（PostToolUse lint + Stop gate）
│   ├── hooks/
│   │   ├── stop_validate.py     # Stop hook：阻止 Agent 在测试红时结束
│   │   └── post_tool_use_lint.py# PostToolUse hook：每次编辑后 ruff check
│   └── skills/
│       ├── plan/SKILL.md        # /plan：需求 → 读代码库 → 识别风险 → 写计划
│       ├── implement/SKILL.md   # /implement：按计划执行 + 任务级验证 + 写报告
│       └── validate/SKILL.md    # /validate：运行完整质量门 + 格式化报告
├── app/                         # RAG 核心（与框架解耦，易于单测）
│   ├── chunker.py               # chunk_text：固定长度 + overlap
│   ├── indexer.py               # TfidfIndex：add_chunks / search
│   ├── retriever.py             # retrieve：包装 index.search
│   ├── generator.py             # generate_answer：基线模板（课堂替换为 LLM）
│   └── rag.py                   # RAGPipeline：组合所有阶段
├── api/server.py                # FastAPI + 静态前端托管
├── frontend/                    # 问答 UI（HTML/JS/CSS）
├── data/sample_docs/            # 内置知识库（4 篇 RAG 教学文档）
├── tests/
│   ├── test_chunker.py
│   ├── test_retriever.py
│   └── test_rag.py              # 含 FastAPI 集成测试
├── plans/                       # /plan 输出目录（课上生成）
├── reports/                     # /implement 输出目录
├── scripts/validate.py          # 质量门入口
└── requirements.txt
```

---

## 环境搭建（课前完成）

**Windows (PowerShell)**

```powershell
cd 02-rag-harness-demo
python -m venv .venv
.\.venv\Scripts\Activate.ps1      # 提示符变为 (.venv)
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

若激活报权限错误，先执行：`Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

**macOS / Linux (Bash / WSL)**

```bash
cd 02-rag-harness-demo
python3 -m venv .venv
source .venv/bin/activate         # 提示符变为 (.venv)
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

---

## 快速开始（基线演示）

```bash
# 1. 运行质量门（13 个测试应全绿）
python scripts/validate.py

# 2. 启动全栈服务
uvicorn api.server:app --reload --port 8000
```

浏览器打开 http://127.0.0.1:8000，提问：

- `什么是 RAG？`
- `分块策略有哪些？`
- `TF-IDF 检索的优缺点？`

此时 `generate` 阶段为**模板拼接**——这是刻意保留的基线，课堂练习后会替换为 LLM。

---

## PIV 循环（课堂核心）

```text
/plan  →  /implement  →  /validate
  ↑                           │
  └───────── fix & retry ─────┘
```

**Plan（规划）**：Agent 读需求 + 读代码库 + 识别风险，写 `plans/*.md`
**Implement（实现）**：按计划执行，每个 Task 后立即验证，写实现报告
**Validate（验收）**：运行完整质量门，输出 PASS/FAIL 表格

验证不是独立步骤——`/implement` 每个 Task 后就验证，Stop hook 在结束前强制验证。

---

## Hook 解释（课堂讲解）

### PostToolUse hook（编辑时触发）

每次 Agent 修改 `app/` 或 `tests/` 下的 `.py` 文件后自动运行：

```python
ruff check <file>   # 代码风格 + 常见错误
```

**建议性**：发现问题但不阻塞，打印警告让 Agent 自行修复。

### Stop hook（结束时触发）

Agent 完成一轮对话、准备停止前自动运行：

```python
python scripts/validate.py   # pytest 全量测试
```

**阻塞性**：失败时输出 `{"decision": "block", "reason": "..."}` 阻止停止，
Agent 收到 reason 后继续修复。`stop_hook_active` 防止无限循环。

---

## 课堂流程（45–60 分钟）

### 第 1 段：理解基线（10 min）

1. 演示启动 → 提问 → 看 `generate` 输出是模板拼接
2. 打开 `app/generator.py`，指出这是本节课的改造点
3. 运行 `python scripts/validate.py`，说明测试通过 = Harness 的「Done 标准」

### 第 2 段：现场生成计划（10 min）

在 Cursor 里输入（计划由 `/plan` 课堂生成，不依赖预置文件）：

```text
/plan "将 generate 阶段从模板拼接改为 LLM 生成：
- 用检索到的 context 构建 prompt 调用大模型
- 无命中时返回固定提示
- 测试中 mock LLM，不依赖真实 API Key
- 通过环境变量配置 OPENAI_API_KEY / OPENAI_MODEL"
```

检查 `plans/` 下生成的 `*.md`，对照计划是否覆盖：
generator、llm_client、tests mock、环境变量。

### 第 3 段：实现与验收（25 min）

```text
/implement plans/llm-generate-plan.md
/validate
```

观察 Agent 如何：每个 Task 后立即跑验证 → Stop hook 阻止提前结束 → 修复后继续。

### 第 4 段：对比演示（5 min）

重启服务，对比同一问题的回答：
- 改造前：「相关片段如下：1. [doc] ...」（模板）
- 改造后：自然语言总结，仅基于 context

---

## 课堂练习：用 LLM 做答

**涉及文件**

| 文件 | 改动 |
|------|------|
| `app/generator.py` | 构建 prompt（system + context + question），调用 LLM |
| `app/llm_client.py`（新建） | 封装 OpenAI 兼容 API，从环境变量读配置 |
| `app/rag.py` | 支持注入可 mock 的 client |
| `tests/test_generator.py`（新建） | mock LLM 返回值，断言 prompt 含 context |
| `requirements.txt` | 增加 `openai` |

**Prompt 约束（教学要点）**

```
System: 你是知识库助手，只能根据提供的 context 回答。
        context 为空时说「未找到相关信息」，不要编造。
User:   context: {hits}
        question: {query}
```

**LLM 环境变量（课堂练习前设置，勿写入代码或 Git）**

```powershell
# PowerShell（在已激活 .venv 的同一终端）
$env:OPENAI_API_KEY  = "sk-..."
$env:OPENAI_BASE_URL = "https://api.openai.com/v1"   # 可选
$env:OPENAI_MODEL    = "gpt-4o-mini"                  # 可选
```

```bash
# Bash / WSL
export OPENAI_API_KEY=sk-...
```

---

## 学生交付物

| 产出 | 路径 | 说明 |
|------|------|------|
| 计划 | `plans/<feature>-plan.md` | `/plan` 生成 |
| 实现报告 | `reports/<feature>-implementation-report.md` | `/implement` 生成 |
| 质量门截图 | 终端 `validate: PASS` | 提交前截图 |

---

## 与 harness-engineering-demo 的对比

| 维度 | harness-engineering-demo | 本项目（教学简化版）|
|------|--------------------------|---------------------|
| 业务应用 | Schedulr（FastAPI + Next.js + Postgres）| RAG 问答（FastAPI + 静态 HTML）|
| 检索 | — | TF-IDF（无 GPU，无向量库）|
| Hooks | 3 个（lint + stop + security guard）| 2 个（lint + stop）|
| Skills | 4 个（plan/implement/validate/review）| 3 个（plan/implement/validate）|
| 自动循环 | Ralph loop（多 session 串联）| 无（课堂单 session）|
| 目标 | 生产级演示 | 课堂 45 分钟讲完 |

---

## 常见问题

**Q: 没有 OpenAI Key 能上课吗？**
A: 可以。基线演示和单元测试不依赖 Key；LLM 演示可由讲师统一展示，或接入兼容 OpenAI 协议的内网网关。

**Q: validate 失败但浏览器里看起来能用？**
A: Harness 的 Done 标准是测试通过，不是「凑合能跑」。先修测试失败项。

**Q: `/plan` 生成的计划漏了 mock 测试怎么办？**
A: 补充 prompt：「计划必须包含 mock LLM client 的测试任务」，重新 `/plan` 或手动编辑 `plans/*.md`。

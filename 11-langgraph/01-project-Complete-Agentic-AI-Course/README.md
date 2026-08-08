# Complete Agentic AI Course — 学习大纲

从 LangChain 单 Agent，到多 Agent 协作，再到 LangGraph 工作流与生产级 Chatbot；配套异步编程与 Pydantic 结构化校验。建议按章节顺序学习。

---

## 课程地图

```
01 概念对比          Langchain vs LangGraph
        ↓
02 单 Agent          ReAct + Tools（搜索 / 天气）
        ↓
03 多 Agent          Search → Reader → Writer → Critic
        ↓
04 LangGraph 核心    工作流 / 持久化 / HITL / Subgraph / Guardrails
        ↓            + Agentic Chatbot 实战（Streamlit）
05 异步编程          支撑 Agent 并发与 I/O
        ↓
06 Pydantic          Agent 输入输出结构化与校验
```

| 阶段 | 目录 | 核心目标 | 建议时长 |
|------|------|----------|----------|
| 概念 | `01-Langchain vs LangGraph` | 理解两种范式差异与适用场景 | 0.5 天 |
| 入门 | `02-Langchain-Single-Agent` | 跑通单 Agent + Tool Calling | 1 天 |
| 进阶 | `03-LangChain-Multi-Agent-Research-System` | 多角色流水线与编排 | 1–2 天 |
| 主线 | `04-LangGraph-Code` | 图工作流 + 生产 Chatbot | 3–5 天 |
| 基础加固 | `05-Asynchronous Programming` | 同步 vs 异步、并发模型 | 0.5–1 天 |
| 基础加固 | `06-Pydantic-Validation` | 结构化输出与数据校验 | 0.5–1 天 |

---

## 第 0 章：环境准备

- Python **3.11+**（各子项目 README 均推荐 conda）
- 常用密钥（按需配置到对应目录的 `.env`，勿提交）：
  - `OPENAI_API_KEY`
  - `TAVILY_API_KEY`
  - `WEATHERSTACK_API_KEY`（单 Agent 天气工具）
  - Google / Gemini 相关密钥（Chatbot RAG 等后端可能用到）
- 推荐先读：[Building Effective Agents（Anthropic）](https://www.anthropic.com/engineering/building-effective-agents)

---

## 第 1 章：Langchain vs LangGraph（概念）

**路径：** `01-Langchain vs LangGraph/`

| 资源 | 说明 |
|------|------|
| `README.md` | Mermaid 对照图 + Anthropic 文章链接 |
| `demo.excalidraw` | 原图（招聘流程 / Challenges / LC vs LG 实现） |

**学习要点**

1. Chain / Agent（LangChain）与 Graph / State（LangGraph）的差异（见章节 README 中 Mermaid）
2. 何时用线性 Chain，何时用可分支、可循环、可暂停的 Graph
3. 结合 Anthropic 文章理解：工具使用、编排、人机协同等模式

**验收：** 能口述「单 Agent / 多 Agent / 图工作流」各自适合什么问题。

---

## 第 2 章：LangChain 单 Agent

**路径：** `02-Langchain-Single-Agent/`

| 文件 | 角色 |
|------|------|
| `app.py` | Streamlit：搜索 + 天气 ReAct Agent |
| `main.py` | CLI / 脚本入口 |
| `research/agent_demo.ipynb` | Notebook 实验 |
| `requirements.txt` | 依赖 |

**技术栈：** LangChain · `create_react_agent` / `AgentExecutor` · Tavily · WeatherStack · Streamlit

**学习路径**

1. 配置 `.env`，安装依赖并运行 `python app.py` 或 `streamlit` 流程
2. 理解 Tool 定义（`@tool` / 社区工具）如何挂到 Agent
3. 走通 ReAct：思考 → 调工具 → 观察 → 回答
4. 在 `agent_demo.ipynb` 里改工具与 Prompt 做实验

**验收：** 能独立加一个新 Tool，并在对话中被正确调用。

---

## 第 3 章：多 Agent 研究系统

**路径：** `03-LangChain-Multi-Agent-Research-System/`

```
用户 Topic
   → Search Agent（Tavily）
   → Reader Agent（抓取网页）
   → Writer Chain（结构化报告）
   → Critic Chain（打分与改进建议）
   → Streamlit / CLI 输出
```

| 路径 | 说明 |
|------|------|
| `app.py` | Streamlit UI |
| `main.py` | CLI 入口 |
| `src/agents/agents.py` | Search / Reader / Writer / Critic |
| `src/tools/tools.py` | `web_search`、`scrape_url` |
| `src/pipelines/pipeline.py` | 流水线编排 |
| `demo.excalidraw` | 架构图 |

**学习路径**

1. 对照 `demo.excalidraw` 与 `pipeline.py` 理清四阶段状态传递
2. 区分「带 Tool 的 Agent」与「纯 Prompt Chain」（Writer / Critic）
3. 运行 `streamlit run app.py`，换 Topic 观察报告与 Critic 分数
4. 思考局限：顺序硬编码 → 为第 4 章 LangGraph 做动机铺垫

**验收：** 能画出流水线，并说明每步输入输出与失败点（搜索空、抓取失败等）。

---

## 第 4 章：LangGraph 核心 + Agentic Chatbot（主线）

**路径：** `04-LangGraph-Code/`

环境：`conda create -n langgraph-test python=3.11` → `pip install -r requirements.txt`

### 4.1 Notebook 递进（按编号学）

| 序号 | Notebook | 主题 |
|------|----------|------|
| 1 | `1_Temperature_Conversion_workflow.ipynb` | 无 LLM：State + 多 Node 图 |
| 2 | `2_Simple_QA_LLM_Workflow.ipynb` | 接入 LLM 的简单问答图 |
| 3 | `3_Prompt_Chaining_Workflow.ipynb` | Prompt 链式多节点 |
| 4 | `4_Employee_analytics_Workflow.ipynb` | 业务分析型工作流 |
| 5 | `5_Essay_workflow.ipynb` | 作文 / 长文生成流 |
| 6 | `6_Content_Moderation_Workflow.ipynb` | 内容审核与分支 |
| 7 | `7_Review_workflow.ipynb` | 评审类工作流 |
| 8 | `8_Iterative_Workflows.ipynb` | 迭代 / 循环工作流 |
| 9 | `9_Persistence.ipynb` | 持久化（配合 `Persistence.excalidraw`） |
| 10 | `10_HITL.ipynb` | Human-in-the-Loop（配合 `HITL.excalidraw`） |
| 11 | `11_subgraphs.ipynb` | 子图（配合 `Subgraphs.excalidraw`） |
| 12 | `12_subgraph_shared.ipynb` | 共享状态的子图 |
| 13 | `13_guardrails_crash_course.ipynb` | Guardrails：确定性 vs 模型式护栏 |

**建议节奏**

1. **1–3**：打牢 `StateGraph` / `START` / `END` / `TypedDict` State
2. **4–8**：条件边、循环、业务编排
3. **9–10**：Checkpoint、线程、中断与人工确认
4. **11–13**：模块化子图与安全护栏

### 4.2 实战：Agentic Chatbot（Streamlit）

**路径：** `04-LangGraph-Code/Agentic-Chatbot-using-LangGraph/`

| 层级 | 文件 | 能力 |
|------|------|------|
| 后端 | `agentic_chatbot_backend.py` | 基础对话 + MemorySaver |
| | `agentic_chatbot_db_backend.py` | SQLite Checkpoint |
| | `agentic_chatbot_tool_backend.py` | ToolNode / tools_condition |
| | `agentic_chatbot_rag_backend.py` | PDF → FAISS + RAG + Tools |
| | `agentic_chatbot_hitl_backend.py` | HITL + RAG 等综合能力 |
| 前端 | `app_simple.py` / `app_thread.py` / `app_db.py` | 简单聊 → 多线程 → 持久化 |
| | `app_tool.py` / `app_rag.py` / `app_hitl.py` | 工具 → RAG → 人机协同 |
| 对照脚本 | `chatbot_without_hitl.py` / `chatbot_with_hitl.py` | HITL 前后对比 |
| Notebook | `notebooks/Chatbot_workflow.ipynb` 等 | 对话 / Tools / RAG / HITL 实验 |

**推荐打通顺序**

```
app_simple → app_thread → app_db → app_tool → app_rag → app_hitl
```

**验收：** 能解释 State、Checkpoint、Thread ID、Tool 边、RAG 检索与 HITL `interrupt` / `Command` 如何协作。

---

## 第 5 章：异步编程

**路径：** `05-Asynchronous Programming/`

| 资源 | 说明 |
|------|------|
| `asynchronous.ipynb` | 同步 vs 异步对照实验 |
| `class 2.pdf` | 课堂讲义 |

**学习要点**

1. 同步阻塞 vs `async`/`await` 事件循环
2. 为何 Agent / 多工具调用场景需要异步（并发搜索、并行节点）
3. 与 LangGraph / LangChain 异步 API 的对应关系（为后续并发图打基础）

**验收：** 能写出简单 `async` 并发调用示例，并说明相对同步版的收益。

---

## 第 6 章：Pydantic 校验（面向 Agent）

**路径：** `06-Pydantic-Validation/`

| 资源 | 说明 |
|------|------|
| `pydantic for Agent.ipynb` | 从问题到校验的完整笔记 |
| `requirements.txt` | `pydantic>=2.0` |

**Notebook 主题线索**

1. 什么是 Pydantic；无校验时的问题
2. 基础用法、必填 / 可选字段
3. 数据验证规则
4. 如何服务 Agent：结构化输出、工具参数、状态 Schema

**验收：** 能为某个 Tool 的入参或 Agent 输出定义 Pydantic Model，并演示非法数据被拦截。

---

## 推荐学习周计划（示例）

| 天 | 内容 |
|----|------|
| Day 1 | 第 1 章概念 + 第 2 章单 Agent 跑通 |
| Day 2 | 第 3 章多 Agent 流水线 + 改一版 Critic Prompt |
| Day 3–4 | LangGraph Notebook 1–8 |
| Day 5 | Persistence + HITL + Subgraphs + Guardrails |
| Day 6 | Chatbot：`app_simple` → `app_rag` |
| Day 7 | `app_hitl` + 第 5 / 6 章加固，整理自己的笔记与架构图 |

---

## 能力清单（学完应能回答）

- [ ] LangChain Agent 与 LangGraph Graph 的适用边界
- [ ] ReAct 单 Agent 如何绑定多个 Tool
- [ ] 多 Agent「搜索–阅读–写作–评审」如何用状态串联
- [ ] `StateGraph`：节点、边、条件边、循环
- [ ] Checkpoint / Thread：多轮对话如何恢复
- [ ] HITL：何时中断、如何恢复执行
- [ ] Subgraph：如何拆分复杂 Agent 系统
- [ ] Guardrails：确定性规则 vs 模型审核
- [ ] RAG Chatbot：文档入库、检索、与 Tool 共存
- [ ] 异步 I/O 与 Pydantic 结构化如何提升 Agent 可靠性

---

## 目录速查

```text
project-Complete-Agentic-AI-Course/
├── 01-Langchain vs LangGraph/          # 概念与对比图
├── 02-Langchain-Single-Agent/          # 单 Agent + Streamlit
├── 03-LangChain-Multi-Agent-Research-System/  # 多 Agent 研究流水线
├── 04-LangGraph-Code/                  # LangGraph 教程 + Chatbot 实战
│   ├── 1_*.ipynb … 13_*.ipynb
│   └── Agentic-Chatbot-using-LangGraph/
├── 05-Asynchronous Programming/        # 异步基础
├── 06-Pydantic-Validation/             # Pydantic for Agent
└── README.md                           # 本大纲
```

---

## 学习建议

1. **先跑通再改**：每个子项目先按 README 跑通，再改 Prompt / Tool / 图结构。
2. **图优于文字**：`*.excalidraw` 与 Anthropic 文章一起看，建立心智模型。
3. **主线在第 4 章**：前三章是动机与对比，LangGraph + Chatbot 是工程核心。
4. **5 / 6 章可穿插**：遇到并发或结构化输出卡点时随时回看，不必严格排在最后。
)

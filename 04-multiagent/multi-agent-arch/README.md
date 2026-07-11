# Multi-Agent 架构与框架 — 课程 Notebook 索引

**AI Engineer 训练营 · 多 Agent 模块**

---

## 推荐讲课顺序

| # | Notebook | 模块 | 时长（约） | 依赖 |
|---|----------|------|------------|------|
| **01** | [01_multi_agent_arch_demo.ipynb](01_multi_agent_arch_demo.ipynb) | 架构基础 | 60 min | 无（纯 Python 标准库） |
| **02** | [02_hierarchical_multi_agent_demo.ipynb](02_hierarchical_multi_agent_demo.ipynb) | 分层与监督 | 150 min | 01 |
| **03** | [03_环境初始化与MAS基础.ipynb](03_环境初始化与MAS基础.ipynb) | 框架入门 | 20 min | Python 3.10+ |
| **04** | [04_autogen_实战.ipynb](04_autogen_实战.ipynb) | AutoGen | 25 min | 03 · `OPENROUTER_API_KEY` |
| **05** | [05_crewai_实战.ipynb](05_crewai_实战.ipynb) | CrewAI | 25 min | 03 |
| **06** | [06_agentic_rag_与框架对比.ipynb](06_agentic_rag_与框架对比.ipynb) | LangGraph + RAG | 30 min | 03 · 可选 `TAVILY_API_KEY` |
| **07** | [07_课堂练习.ipynb](07_课堂练习.ipynb) | 综合练习 | 40 min | 04（练习 A）· 06（练习 B/C） |
| **08** | [08_工程化与总结.ipynb](08_工程化与总结.ipynb) | 工程化 | 20 min | 无代码依赖，阅读为主 |
| **09** | [09_agent_ops_langsmith_demo.ipynb](09_agent_ops_langsmith_demo.ipynb) | Agent Ops | 90 min | 无（模拟 LangSmith，无需 API Key） |


---

## 三条学习线

```
模块 A · 架构思维（无需 LLM API）
  01 架构模式 Demo  →  02 分层协作与 HITL

模块 B · 框架实战（需 OpenRouter）
  03 环境初始化  →  04 AutoGen  →  05 CrewAI  →  06 Agentic RAG  →  07 练习

模块 C · 生产运维
  09 Agent Ops（建议在 02、06 之后）
  08 工程化总结（可在 07 后作收束）
```

**零基础路径**：01 → 02 → 03 → 04 → 05 → 06 → 07 → 08 → 09  
**已有 LLM 经验、时间紧**：03 → 04 → 05 → 06 → 07 → 08（跳过 01/02/09 作选修）

---

## 各 Notebook 内容概要

### 01 · 多 Agent 架构模式

- 单体 Agent 局限（基线对比）
- **Pipeline**（队列 + Worker 线程）
- **Hub-and-Spoke**（asyncio 并行）
- **Blackboard**（共享状态 + 事件）
- 幂等、可观测性、优雅降级

### 02 · 分层协作与监督

索引：[02_hierarchical_multi_agent_demo.ipynb](02_hierarchical_multi_agent_demo.ipynb)（完整版备份：[02_hierarchical_multi_agent_demo.full.ipynb](02_hierarchical_multi_agent_demo.full.ipynb)）

| # | Notebook | 内容 |
|---|----------|------|
| 02.1 | [02.1_infrastructure.ipynb](02.1_infrastructure.ipynb) | 模拟工具 & Trace 系统 |
| 02.2 | [02.2_monolithic_baseline.ipynb](02.2_monolithic_baseline.ipynb) | 单体 Agent 基线 |
| 02.3 | [02.3_three_layer_arch.ipynb](02.3_three_layer_arch.ipynb) | Worker / Orchestrator / Supervisor |
| 02.4 | [02.4_map_reduce.ipynb](02.4_map_reduce.ipynb) | 并行 Map-Reduce |
| 02.5 | [02.5_verifier_quality_gate.ipynb](02.5_verifier_quality_gate.ipynb) | Verifier + Quality Gate |
| 02.6 | [02.6_hitl.ipynb](02.6_hitl.ipynb) | Human-in-the-Loop |
| 02.7 | [02.7_e2e_report.ipynb](02.7_e2e_report.ipynb) | 端到端三页报告 |
| 02.8 | [02.8_security.ipynb](02.8_security.ipynb) | 输入校验 & 权限矩阵 |

### 03 · 环境初始化与 MAS 基础

- 安装 `autogen-agentchat`、`crewai`、`langgraph` 等依赖
- 配置 `OPENROUTER_API_KEY`（及可选 `TAVILY_API_KEY`）
- MAS 概论、协作模式、120 分钟课程路线图（📖 讲义）

### 04 · AutoGen 实战

- `GraphFlow`：Researcher → Writer → Editor 流水线
- `SelectorGroupChat`：动态 Agent 调度
- `ListMemory`：Agent 记忆

### 05 · CrewAI 实战

- Sequential Crew：研究 → 写作 → 审校
- Hierarchical Process + `manager_llm`
- Tavily 搜索工具集成

### 06 · Agentic RAG 与框架对比

- AutoGen / CrewAI / **LangGraph** 选型对比（📖 讲义）
- LangGraph `StateGraph`：Retriever → Reranker → Generator → Verifier
- 验证分支与 Orchestrator 路由

### 07 · 课堂练习

| 练习 | 难度 | 要点 |
|------|------|------|
| A | ⭐ | AutoGen 三角色 GraphFlow |
| B | ⭐⭐ | `queue.Queue` 多 Worker Pipeline |
| C | ⭐⭐⭐ | Supervisor + HITL 集成 Agentic RAG |

### 08 · 工程化与总结

- 协作与通信优化、Schema / 幂等 / Trace
- 最佳实践与常见陷阱
- 课程总结与延伸阅读

### 09 · Agent Ops & LangSmith

- Trace / Run 树、自定义 Metrics 与告警
- HITL、成本感知与优雅降级
- Regression 检测、Dataset 评估、综合流水线

---

## 环境配置

在项目目录或上级创建 `.env`：

```env
OPENROUTER_API_KEY=sk-or-v1-...    # 03–07 必需
TAVILY_API_KEY=tvly-...            # 05 示例 3C、06 可选
```

- OpenRouter：https://openrouter.ai  
- Tavily：https://tavily.com  

**03** 中安装依赖后需 **Restart Kernel**，再从 **03** 重新运行。

---

## 其他文件

| 文件 | 说明 |
|------|------|
| [multi_agent_frameworks_实战.ipynb](multi_agent_frameworks_实战.ipynb) | 已拆分索引页，指向 03–08 |

---

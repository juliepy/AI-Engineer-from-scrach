# Agent 课程：从 ReAct 到多 Agent 协作

> 5 个独立示例项目，由浅入深讲解 Agent 核心范式。  
> 每个子目录可单独运行，共用 DeepSeek API + 相同工具集（calculator / get_current_time / word_count）。

## 目录

| 序号 | 目录 | 主题 | 一句话 |
|------|------|------|--------|
| 01 | `01-Agent_react` | **ReAct** | Thought → Action → Observation 循环，Agent 入门 |
| 02 | `02-Plan-and-Execute` | **Plan-and-Execute** | 先全局规划，再逐步执行，失败可重规划 |
| 03 | `03-Reﬂexion` | **Reflection** | 评估失败 → 写反思 → 重试，策略记忆跨轮复用 |
| 04 | `04-LATS` | **LATS / MCTS** | 树搜索探索多条路径，UCB 平衡探索与利用 |
| 05 | `05-Multi-Agent-Crew` | **Multi-Agent** | 多角色共享 thread，研究 → 撰写 → 审稿 |

## 五种范式对比（讲课用）

| 范式 | 核心思路 | 适用场景 |
|------|----------|----------|
| ReAct | 单链逐步推理 + 调工具 | 路径不确定、需频繁与环境交互 |
| Plan-and-Execute | 显式规划 → 分步执行 | 任务可分解、需要可审计的计划 |
| Reflection | Action → Eval → Reflect → Retry | 可验证任务、易犯格式/约束错误 |
| LATS | MCTS 在决策树上搜索 | 多方案对比、决策点多、可打分 |
| Multi-Agent | 多角色分工 + 共享黑板 | 内容生产、研究写作、流水线协作 |

## 演进关系

```
ReAct（基础循环）
  ├── Plan-and-Execute（加显式规划层）
  ├── Reflection（加评估与反思层）
  └── LATS（加树搜索，探索多条路径）

Multi-Agent（横向扩展：多个 Agent 协作，可与上述范式组合）
```

## 建议讲课顺序

1. **ReAct** — 建立 Agent 基本心智模型（Thought / Action / Observation）
2. **Plan-and-Execute** — 对比「隐式逐步」与「显式规划」
3. **Reflection** — 解决「做错了怎么办」，引入 Evaluator 与策略记忆
4. **LATS** — 解决「一条路走到黑」，引入 MCTS 与 UCB
5. **Multi-Agent** — 从单 Agent 到多角色协作，收尾

## 快速开始

各子项目结构一致，进入对应目录后：

```bash
cd 01-Agent_react          # 换成 02 / 03 / 04 / 05
pip install -r requirements.txt
copy .env.example .env     # 填写 DEEPSEEK_API_KEY
python main.py
```

API Key 可从 [DeepSeek 开放平台](https://platform.deepseek.com/) 获取，各项目可共用同一 Key。

## 各模块详情

每个子目录下有独立 `Readme.md`，含目录结构、流程图、时序图与运行示例：

| 目录 | 详细文档 |
|------|----------|
| `01-Agent_react` | [Readme.md](01-Agent_react/Readme.md) |
| `02-Plan-and-Execute` | [Readme.md](02-Plan-and-Execute/Readme.md) |
| `03-Reﬂexion` | [Readme.md](03-Reﬂexion/Readme.md) |
| `04-LATS` | [Readme.md](04-LATS/Readme.md) |
| `05-Multi-Agent-Crew` | [Readme.md](05-Multi-Agent-Crew/Readme.md) |

## 与 RAG 课程的关系

| 课程 | 关注点 |
|------|--------|
| `RAG/` | 如何让 LLM **获取外部知识**（检索、图谱、路由等） |
| `Agent/` | 如何让 LLM **自主决策与行动**（工具调用、规划、反思、搜索、协作） |

两者可组合：RAG 中的 Agentic RAG 即 Agent 范式在检索场景的应用。

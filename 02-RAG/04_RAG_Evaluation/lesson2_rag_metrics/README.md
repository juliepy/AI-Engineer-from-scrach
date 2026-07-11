# Lesson 2 · RAG Metrics 进阶详解

**模块：** PHASE 3: RAG · Evaluation  

---

## 课程定位

Lesson 1 用 RAGAS **跑通评估**；Lesson 2 **拆开黑盒**——从公式推导到手写实现，最后串联成可操作的诊断流水线。

```
Lesson 1                          Lesson 2
────────                          ────────
知道「评什么」          →          知道「怎么算、怎么修」
RAGAS 一键出分          →          手写验证 + 决策树诊断
框架跑分                →          看懂框架、框架外能补
```

**讲解主线：** 理论（公式 + 直觉）→ 代码（手写实现）→ 踩坑（与 RAGAS 差异）→ 诊断（指标低了动哪里）

> **常见疑问：本章只是学理论吗？生产里手写还是上框架？**  
> 不是只学理论。本章是「先懂原理，再知道生产怎么用框架」——**算分用框架，诊断自己搭**。

---

## 学习路径 vs 生产路径

| 层次 | 本章在做什么 | 生产里对应什么 |
|------|-------------|----------------|
| **原理层** | 手写公式，理解各指标怎么算 | 读框架分数、排查「为什么低」 |
| **工程层** | `04` 串联指标 + 阈值 + 决策树 + HTML 报告 | 发布门禁、A/B 对比、告警规则 |
| **工具层** | Chapter 7 框架选型（RAGAS / TruLens / DeepEval） | **批量评估主要用框架跑分** |

典型生产架构：

```
固定评估集（100–200 条）
        ↓
RAGAS / DeepEval / TruLens     ← Lesson 1 已入门，生产批量算分
        ↓
自研诊断层                      ← Lesson 2 的 04：阈值、优先级、报告、门禁
        ↓
CI/CD 发布门禁 / 周报 / A/B 对比
```

**为什么还要手写？** 生产有 RAGAS 不等于不需要懂原理：

| 用途 | 说明 |
|------|------|
| **Debug** | Recall 0.4 是 GT 问题、chunk 问题还是 top-k 问题——不懂公式很难修 |
| **定制** | 业务指标（引用准确率、合规）框架没有，Faithfulness 的 Claim + Verify 是模板 |
| **面试/沟通** | 能讲清 RAGAS Binary vs Weighted Precision、和手算差在哪 |

手写与框架是**互相校验**，不是二选一（见课后挑战：集成 RAGAS 对比验证手写指标）。

### 框架怎么选

| 框架 | 推荐场景 |
|------|---------|
| **RAGAS** | 快速原型、LangChain 生态集成（Lesson 1 已用） |
| **TruLens** | 企业级可视化 trace、线上监控 |
| **DeepEval** | 统一测 RAG + Agent + 回归测试 |

常见组合：**RAGAS 算分 + LangSmith/自研看板 + 本章决策树做 remediation**。

### 持续评估三层（Chapter 7）

```
Layer 1: 实时监控（每次请求）   —— latency、采样 Faithfulness、告警
Layer 2: 定期评估（每周/发布） —— 固定评估集跑 5 指标、趋势对比
Layer 3: 版本发布门禁          —— Faithfulness ≥ 0.80 / Recall ≥ 0.65 / Relevancy ≥ 0.75
```

---

## 学习目标

学完本课，学员应能：

1. **读懂** Context Precision / Recall、Ranking Metrics、Faithfulness、Answer Relevancy 的数学定义与适用场景
2. **手写** 上述指标的 Python 实现，理解 RAGAS 等框架背后的计算逻辑
3. **区分** Retriever 指标（Precision、Recall、MRR、NDCG）与 Generator 指标（Faithfulness、Relevancy）
4. **生成** 评估用 Ground Truth（手工标注 vs LLM 自动生成）
5. **使用** 四象限 + 决策树，根据低分指标给出优先级明确的修复建议
6. **输出** HTML 诊断报告，用于团队复盘或 A/B 对比

---

## 章节与 Notebook 对照

| Chapter | 主题 | Notebook | 评估对象 |
|---------|------|----------|---------|
| 1 | Context Precision | `01_context_precision_recall.ipynb` | Retriever |
| 2 | Context Recall + Ground Truth | ↑ 同上 | Retriever |
| 3 | HitRate@k / P@k / R@k / MRR / NDCG | `02_retrieval_ranking_metrics.ipynb` | Retriever |
| 4 | Faithfulness（Claim + LLM-Judge） | `02_faithfulness_llm_judge.ipynb` | Generator |
| 5 | Answer Relevancy + MRR 回顾 | `03_answer_relevancy_mrr.ipynb` | Generator |
| 6 | 四象限诊断 + 决策树 | `04_diagnostic_pipeline.ipynb` | 全流程 |
| 7 | 生产化（A/B、RAGAS、持续评估） | ↑ 同上 | 全流程 |

> `01` 开头 Cell 含**全课导览**（指标总表 + 七 Chapter 架构），建议开课前先过一遍。


---

## 快速开始

```bash
cd lesson2_rag_metrics

# 依赖
pip install openai python-dotenv jupyter

# 在 04_RAG_Evaluation/.env 中配置（需要 LLM 的 Notebook）
# OPENAI_API_KEY=your-deepseek-api-key
# OPENAI_BASE_URL=https://api.deepseek.com   # 如使用 DeepSeek
```

---

## 诊断速查（讲解 `04` 时使用）

### 四象限

```
                    Recall 高
                      │
   [修 Generator]     │     [系统健康]
   Precision 高       │     持续监控
   Faithfulness 低    │
─────────────────────┼─────────────────────
   [修 Retriever]     │     [修 Retriever]
   双低最危险         │     只是噪声问题
                      │
                    Recall 低
```

### 指标偏低 → 修复方向

| 指标偏低 | 可能原因 | 修复方向 |
|---------|---------|---------|
| Context Precision | 检索噪声多、K 太大 | Reranker、减小 top-k、提高 score_threshold |
| Context Recall | 漏召回、chunk 切太大 | 增大 top-k、调 chunk_size/overlap、换 embedding |
| Faithfulness | 生成幻觉、Prompt 约束弱 | 严格 System Prompt、降低 temperature、先修 Precision |
| Answer Relevancy | 答非所问、Query 模糊 | Query 扩展、HyDE、多查询检索 |

运行 `04_diagnostic_pipeline.ipynb` 会在当前目录生成 **`diagnostic_report.html`**，含各指标分数、缺口排序与优先级建议。

---


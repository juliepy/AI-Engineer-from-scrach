---
name: plan
description: 分析功能需求，读取代码库，识别风险，将计划写入 plans/<feature>-plan.md。此阶段不写代码。
disable-model-invocation: true
---

# /plan — 分析并规划功能

**用法：** `/plan <功能描述>`

产出一份可实施的计划文件。**此阶段不写代码。**

---

## 流程

### 1. 理解需求

从 `$ARGUMENTS` 中提取：
- 功能类型（新功能 / 增强 / Bug 修复）
- 涉及的 RAG 阶段（ingest / chunk / index / retrieve / generate）
- 验收标准

### 2. 读取代码库

先读 `CLAUDE.md` 了解命名和模式。然后读：
- 所有将被**修改**的文件——获取真实行号
- 与你要构建的最相似的已有实现（例如：改 generate → 读 `app/generator.py`）

确认：
- 需要修改的文件（带行号）
- 需要新建的文件
- 是否需要更新 `requirements.txt`

### 3. 评估风险

- 边界情况（空查询、空 hits、无命中）
- 新依赖（是否需要更新 requirements.txt？）
- 如果涉及 LLM：测试中如何 mock 避免依赖真实 API Key？
- 对已有测试的影响

### 4. 将计划写入文件

使用 **Write 工具**创建 `plans/<feature>-plan.md`——这是必须交付的文件，不是可选的。
不要只在聊天里描述计划；`/implement` 从磁盘读取它。

使用以下结构：

```markdown
# Plan: <功能名称>

## 需求
<一句话描述>

## 涉及的 RAG 阶段
<ingest / chunk / index / retrieve / generate，说明影响>

## Prerequisites
- 假定 `.venv` 已激活（见 README「环境搭建」）
- <如涉及 LLM，列出需要的环境变量名，不写真实 Key>

## 涉及文件
### 实现前先读
- `<路径>` (行 N-M) — <原因>

### 修改
- `<路径>` — <改什么>

### 新建
- `<路径>` — <用途>

## 有序任务

### Task 1 — <动作> <目标>
- What: <具体改动>
- Pattern: `<路径>:L<行>` — <参照哪里>
- Gotcha: <已知陷阱（若有）>
- Validate: `<精确 shell 命令>`

### Task 2 — ...

（按依赖顺序继续）

## 验证门
完成所有任务后依次运行：
\`\`\`
python scripts/validate.py
\`\`\`

## 验收标准
- [ ] <可量化的标准 1>
- [ ] <可量化的标准 2>
- [ ] 验证门通过
```

### 5. 确认

写完文件后，输出：
- 路径：`plans/<feature>-plan.md`
- 复杂度：低 / 中 / 高
- 主要风险
- 置信度（N/10，预估 `/implement` 首次通过概率）

---

**交接：** 将计划路径传给 `/implement plans/<feature>-plan.md`。

# 05 - Multi-Agent Crew（多角色轮询）

多个专责角色按固定顺序阅读**同一条对话线程** `thread`，轮流补充内容，形成「研究 → 撰写 → 审稿」的极简协作链。对应面试宝典 **7.5 / 8** 模块。

## 目录结构

```
05-Multi-Agent-Crew/
├── main.py
├── agent/
│   ├── crew.py       # run_crew（7.5 核心）
│   ├── roles.py      # researcher / writer / reviewer 提示词
│   └── llm/
├── requirements.txt
└── .env.example
```


**要点：**

- **thread** = 共享黑板，每角色输出追加其后，下一轮/下一角色可见全文。
- **rounds** = 外循环；**order** = 内循环角色顺序。
- 无工具、无并行，仅为概念演示；工程上可换 CrewAI / AutoGen 等框架。

## 快速开始

```bash
cd 05-Multi-Agent-Crew
pip install -r requirements.txt
copy .env.example .env   # DEEPSEEK_API_KEY，可与 01~04 共用

python main.py
```

## 流程图

```
Task
  |
  v
thread = "Task: ..."
  |
  +-- Round 1..rounds -------------------+
  |     researcher -> 追加 [researcher]  |
  |     writer       -> 追加 [writer]    |
  |     reviewer     -> 追加 [reviewer]  |
  +--------------------------------------+
  |
  v
return thread（含全员发言记录）
```

## 实际日志逻辑图（对应本次运行）

任务：`为团队写一段 150 字以内的说明：解释 ReAct Agent 是什么，以及它为什么需要 Observation`

### 共享黑板（thread）成长过程

```
初始 thread
┌─────────────────────────────────────────────────┐
│ Task: 为团队写一段150字以内的说明…               │
└─────────────────────────────────────────────────┘
        │
        ▼ Round 1 开始
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Step 1  researcher 读 thread（只有 Task）→ LLM 生成条目
        ↓ 追加到 thread
┌─────────────────────────────────────────────────┐
│ [researcher]:                                   │
│ - ReAct Agent 结合推理(Reasoning)与行动(Action)  │
│ - 核心流程: Thought → Action → Observation → 循环│
│ - Observation 是环境/工具对行动结果的反馈         │
│ - 没有 Obs. Agent 无法验证结果/获取新信息         │
│ - Obs. 使 Agent 动态调整，形成闭环               │
└─────────────────────────────────────────────────┘
        │
        ▼
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Step 2  writer 读 thread（Task + researcher）→ 产出草稿
        ↓ 追加到 thread
┌─────────────────────────────────────────────────┐
│ [writer]:                                       │
│ ReAct Agent 是一种结合推理与行动的智能体框架，    │
│ 核心流程为：Thought → Action → Observation → 循环│
│ Obs. 至关重要——没有它 Agent 无法验证结果/获取新  │
│ 信息，也无法形成闭环。(~148字)                   │
└─────────────────────────────────────────────────┘
        │
        ▼
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Step 3  reviewer 读 thread（Task + researcher + writer）→ 审稿
        ↓ 追加到 thread
┌─────────────────────────────────────────────────┐
│ [reviewer]:                                     │
│ 草稿准确简洁，建议补充 ReAct 全称                │
│ (Reasoning + Acting)，其余可通过。(148字)        │
└─────────────────────────────────────────────────┘
        │
        ▼ Round 2 开始（所有角色可见 Round 1 全记录）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Step 4  researcher 读完整 thread → 补充全称/必要性细化
Step 5  writer     读完整 thread → 输出最终定稿（含全称）
Step 6  reviewer   读完整 thread → 确认可通过，给出最终版
        │
        ▼
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
return thread  ← 包含 Task + 6 条发言的完整记录
```

### 时序图：每角色看到的 Prompt 内容

```
run_crew                researcher          writer            reviewer
    │                       │                  │                  │
    │── Round 1 ────────────┤                  │                  │
    │                       │                  │                  │
    │  prompt=role_prompt   │                  │                  │
    │  + thread(仅Task)     │                  │                  │
    │──────────────────────►│                  │                  │
    │◄── reply (条目列表) ──│                  │                  │
    │  thread += [researcher]                  │                  │
    │                       │                  │                  │
    │  prompt=role_prompt   │                  │                  │
    │  + thread(Task+R)     │                  │                  │
    │──────────────────────────────────────────►                  │
    │◄────────────────────── reply (草稿) ─────                   │
    │  thread += [writer]                      │                  │
    │                       │                  │                  │
    │  prompt=role_prompt   │                  │                  │
    │  + thread(Task+R+W)   │                  │                  │
    │──────────────────────────────────────────────────────────────►
    │◄──────────────────────────────── reply (审稿意见) ──────────
    │  thread += [reviewer] │                  │                  │
    │                       │                  │                  │
    │── Round 2（重复，每人看到上一轮全文）──────────────────────►
    │                       │                  │                  │
    │◄────────────────── return thread ────────────────────────────
```

### 关键机制说明

| 概念 | 本代码实现 | 对应日志现象 |
|------|-----------|-------------|
| **共享黑板** | `thread` 字符串，每轮 `+=` 追加 | Round 2 的 researcher prompt 包含前 3 条发言 |
| **角色隔离** | 每角色只有自己的 system prompt 不同 | researcher 输出条目，writer 输出段落，reviewer 输出批注 |
| **迭代改进** | Round 2 中 researcher 补全了「全称」细节 | reviewer 在 Round 1 提了建议，Round 2 writer 已采纳 |
| **无状态 LLM** | 每次调用是独立 API，上下文靠 thread 传递 | prompt 每次都附完整 thread，非对话历史 |


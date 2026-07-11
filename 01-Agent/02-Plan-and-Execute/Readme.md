# 02 - Plan-and-Execute Agent 示例

极简 **Planner + Executor** 架构：先由 LLM 将任务分解为 3–7 个具体步骤，再逐步执行；单步执行器复用 ReAct 循环；失败时可触发重规划。

## 目录结构

```
02-Plan-and-Execute/
├── main.py              # 程序入口
├── agent/
│   ├── types.py         # Tool 定义
│   ├── planner.py       # plan / plan_and_execute（核心）
│   ├── executor.py      # execute_step（ReAct 单步执行器）
│   ├── react_loop.py    # ReAct 循环
│   ├── prompt.py        # ReAct 提示词 / Action 解析
│   ├── llm/             # LLM 接入（DeepSeek）
│   └── tools/           # 工具实现
├── requirements.txt
└── .env.example
```

## 与 ReAct 的对比

| 维度 | ReAct | Plan-and-Execute |
|------|-------|------------------|
| 规划 | 隐式、逐步 | 显式、先全局后局部 |
| 灵活性 | 高（随时改工具） | 中（依赖重规划机制） |
| 成本 | 步数多时可很高 | 规划一次可能省执行盲目性 |
| 风险 | 短视 | 计划错误会波及全局 |

**适用场景：**

- **ReAct**：工具交互密集、环境反馈关键、路径不确定。
- **Plan-and-Execute**：任务可分解、流程强、需要可审计的计划书。

## 内置工具

| 工具 | 作用 |
|------|------|
| `calculator` | 安全计算数学表达式 |
| `get_current_time` | 获取指定时区当前时间 |
| `word_count` | 统计文本字符数与词数 |

## 快速开始

```bash
cd 02-Plan-and-Execute
pip install -r requirements.txt

# 复制并填写 API Key（可与 01-Agent_react 共用同一 Key）
copy .env.example .env

python main.py
```

## 代码逻辑图

### 整体架构

```
    main.py
       |
       +-- build_default_tools()  -->  tools (calculator / get_current_time / word_count)
       |
       +-- create_deepseek_llm()  -->  llm(prompt) -> str
       |
       +-- plan_and_execute(task, llm, tools)
                  |
                  +--> agent/planner.py   plan() / plan_and_execute()
                  |
                  +--> agent/executor.py  execute_step()
                              |
                              v
                         agent/react_loop.py  (单步 ReAct 执行器)
                              |
                              +--> agent/prompt.py  build_prompt / parse_action
                              |
                              +--> agent/tools/*    工具调用
```

### plan_and_execute 主循环

**一句话：** 先全局规划，再逐步执行；每步结果写入 `state`；某步异常则重规划；全部成功后 LLM 汇总。

```
  [开始]
     |
     |  steps = plan(task, llm)     （3~7 步，每行一步）
     |  state = {}
     v
  .------------------------------------------.
  |  重规划尝试  attempt = 0 .. max_replans   |<------------------.
  '------------------------------------------'                    |
     |                                                            |
     |  for i, st in enumerate(steps):                           |
     v                                                            |
  ① execute_step(st, state, tools, llm)                          |
     |         |                                                  |
     |         +--> react_loop（见下图，最多 4 轮）                |
     |                                                            |
     v                                                            |
  ② state["step_i"] = out                                        |
     |                                                            |
     +--- 异常 ---> ③ llm(replan_prompt) --> 新 steps --> break --+
     |
     +--- 全部步骤成功（for-else）---> ④ llm 汇总 state --> 返回 Final Result
     |
     |  （重规划次数用尽仍失败）
     v
  返回 "Failed after replanning."
```

### plan() — 全局规划

```
  [Task]
     |
     v
  拼 prompt: "Break the task into 3-7 concrete steps..."
     |
     v
  llm(prompt)  -->  多行文本
     |
     v
  _parse_steps()  -->  去掉空行、去掉 "- " 前缀
     |
     v
  [Step 1, Step 2, ..., Step N]
```

### execute_step() — 单步执行器

```
  step + state
     |
     v
  拼 question = "Complete this step only: {step}\nPrior step results: {state}"
     |
     v
  react_loop(question, tools, llm, max_steps=4)
     |
     v
  返回该步 Final Answer（字符串）
```

### react_loop() — 内嵌 ReAct 循环（单步内）

**一句话：** 最多 4 轮；每轮问 LLM，能答则返回，否则调工具、记入 `history`，继续下一轮。

```
  [开始]
     |
     |  history = []
     v
  .-------------------.
  |   第 1~4 轮循环    |<---------------------------.
  '-------------------'                             |
     |                                               |
     | ① build_prompt(question, history, tools)      |
     v                                               |
  ② llm(prompt) --> out                             |
     |                                               |
     v                                               |
  ③ out 含 "Final Answer:" ?                        |
     |                                               |
     +--- 是 ---> 提取答案，返回给 execute_step       |
     |                                               |
     +--- 否 ---> ④ parse_action(out)               |
                     |                               |
                     v                               |
                 ⑤ tools[action].run(input)         |
                     |                               |
                     v                               |
                 ⑥ history.append(thought, action, obs)
                     |                               |
                     '-------------------------------'
     |
     |  （跑满 4 轮仍无 Final Answer）
     v
  返回 "Failed: max steps exceeded."
```

### 重规划分支

```
  execute_step() 抛出 Exception
     |
     v
  replan_prompt = "Task / Failed step / Error / Give a new plan."
     |
     v
  llm(replan_prompt)  -->  新 steps
     |
     v
  break 内层 for  -->  外层 attempt+1，从头执行新计划
```

## 时序图

### 整体 Plan-and-Execute 流程

```
    用户          main.py        planner.py       executor.py      react_loop       LLM          tools
     |               |               |                 |                |            |             |
     |  task         |               |                 |                |            |             |
     |-------------->|               |                 |                |            |             |
     |               | plan_and_execute              |                |            |             |
     |               |-------------->|               |                |            |             |
     |               |               | plan(task)     |                |            |             |
     |               |               |----------------------------------------------->|             |
     |               |               |<-- steps[] -----------------------------------|             |
     |               |               |                 |                |            |             |
     |               |               | execute_step(step_0, state)       |            |             |
     |               |               |---------------->|                |            |             |
     |               |               |                 | react_loop     |            |             |
     |               |               |                 |--------------->|            |             |
     |               |               |                 |                | (ReAct 轮) |             |
     |               |               |                 |                |----------->|             |
     |               |               |                 |                |            | tool call   |
     |               |               |                 |                |------------------------>|
     |               |               |                 |                |<-- obs ----------------|
     |               |               |                 |                | Final Answer            |
     |               |               |                 |<-- out --------|            |             |
     |               |               | state["step_0"]=out               |            |             |
     |               |               |                 |                |            |             |
     |               |               | ... step_1, step_2 ...            |            |             |
     |               |               |                 |                |            |             |
     |               |               | llm("Summarize final result...")  |            |             |
     |               |               |------------------------------------------------>|             |
     |               |               |<-- Final Result ------------------------------|             |
     |               |<-- result ----|                 |                |            |             |
     |<-- result ----|               |                 |                |            |             |
```

### 单步内 ReAct 时序（execute_step 调用 react_loop）

```
    executor.py    react_loop       LLM          calculator
         |              |            |                |
         | react_loop(question)      |                |
         |------------->|            |                |
         |              | prompt    |                |
         |              |---------->|                |
         |              | Thought + Action           |
         |              | Action: calculator         |
         |              | Action Input: 21+21        |
         |              |--------------------------->|
         |              |            |               |
         |              |            |  Observation: 42
         |              |<-----------|               |
         |              | prompt (+ history)         |
         |              |---------->|                |
         |              | Final Answer: 42           |
         |              |<----------|                |
         |<-- "42" -----|            |                |
```

### 运行示例时序（`main.py` 默认任务）

**Task:** `请帮我计算 21+21，并统计答案字符串有多少个字符。`

**Phase 1 — 规划**

```
    planner.py       LLM
         |            |
         | plan()     |
         |----------->|
         |  steps:    |
         |  1. 计算 21+21
         |  2. 统计结果字符串字符数
         |<-----------|
```

**Phase 2 — 逐步执行**

```
    planner.py    executor    react_loop    LLM    calculator    word_count
         |            |           |         |          |              |
         | step_0     |           |         |          |              |
         |----------->|           |         |          |              |
         |            | ReAct     |         |          |              |
         |            |---------->|         |          |              |
         |            |           | Action: calculator  |              |
         |            |           |-------------------->|              |
         |            |           |<-- 42 --------------|              |
         |            |           | Final Answer: 42    |              |
         |            |<-- 42 ----|         |          |              |
         | state["step_0"]=42     |         |          |              |
         |            |           |         |          |              |
         | step_1     |           |         |          |              |
         |----------->|           |         |          |              |
         |            | ReAct     |         |          |              |
         |            |---------->|         |          |              |
         |            |           | Action: word_count|              |
         |            |           |--------------------------------->|
         |            |           |<-- 字符数:2, 词数:1 --------------|
         |            |           | Final Answer: 2 个字符             |
         |            |<-- result |         |          |              |
         | state["step_1"]=...    |         |          |              |
```

**Phase 3 — 汇总**

```
    planner.py       LLM              用户
         |            |                |
         | Summarize(state)            |
         |----------->|                |
         | Final Result               |
         |<-----------|                |
         |---------------------------->|
```

### 重规划时序（某步失败）

```
    planner.py       executor.py       LLM
         |                |             |
         | execute_step   |             |
         |--------------->|             |
         |                | Exception   |
         |<-- 异常 --------|             |
         | replan_prompt  |             |
         |-------------------------------->|
         | 新 steps[]     |             |
         |<--------------------------------|
         | 重新从 step_0 执行新计划       |
```

## 核心代码

```python
from agent import build_default_tools, create_deepseek_llm, plan_and_execute

tools = build_default_tools()
llm = create_deepseek_llm()
result = plan_and_execute("你的任务", llm, tools, max_replans=2, verbose=True)
```

## 运行示例

**Task:** `请帮我计算 21+21，并统计答案字符串有多少个字符。`

```
=== Plan ===
  1. 使用计算器计算 21+21
  2. 统计计算结果字符串的字符数

--- Executing step 1: ... ---
(ReAct 调用 calculator → 42)

--- Executing step 2: ... ---
(ReAct 调用 word_count → 字符数: 2, 词数: 1)

Final Result: 21+21 等于 42，答案字符串 "42" 有 2 个字符。
```

## 扩展方式

1. 在 `agent/tools/` 新建工具，在 `build_default_tools()` 中注册
2. 调整 `executor.py` 可替换单步执行策略（纯 LLM 或 ReAct）
3. 修改 `planner.py` 中的 `replan_prompt` 可定制重规划逻辑

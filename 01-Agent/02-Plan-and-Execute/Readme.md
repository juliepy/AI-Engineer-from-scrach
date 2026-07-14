# 02 - Plan-and-Execute Agent 示例

极简 **Planner + Executor** 架构：先由 LLM 将任务分解为 3–7 个具体步骤，再逐步执行；单步执行器复用 ReAct 循环；失败时可触发重规划。

## 目录结构

```
02-Plan-and-Execute/
├── main.py              # 程序入口
├── log.txt              # 一次完整运行日志（可对照本文阅读）
├── agent/
│   ├── types.py         # Tool 定义
│   ├── planner.py       # plan / plan_and_execute（核心）
│   ├── executor.py      # execute_step（ReAct 单步执行器）
│   ├── react_loop.py    # ReAct 循环 + Tool execution 日志
│   ├── prompt.py        # ReAct 提示词 / Action 解析
│   ├── llm/
│   │   ├── deepseek.py  # DeepSeek 接入
│   │   └── log.py       # LLM request/response 可读日志
│   └── tools/           # calculator / get_current_time / word_count
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

## 日志标志

跑 `python main.py` 时，用这三类标志扫 log：

| 标志 | 含义 |
|------|------|
| `====>>> LLM request` | 发给模型的 messages（`content` 按原文换行打印） |
| `====<<< LLM response` | 模型返回内容 |
| `=======>>> Tool execution (local function call)` | 本地工具调用（action / input / observation） |

## 快速开始

```bash
cd 02-Plan-and-Execute
pip install -r requirements.txt

# 复制并填写 API Key（可与 02-Agent_react 共用同一 Key）
copy .env.example .env

python main.py
```

## 代码逻辑图

### 整体架构

```mermaid
flowchart TD
    main[main.py]
    tools["tools<br/>calculator / get_current_time / word_count"]
    llm["llm(prompt) -> str"]
    planner[planner.py<br/>plan / plan_and_execute]
    executor[executor.py<br/>execute_step]
    react[react_loop.py<br/>单步 ReAct 执行器]
    prompt[prompt.py<br/>build_prompt / parse_action]
    toolImpl[tools/*<br/>工具调用]

    main -->|build_default_tools| tools
    main -->|create_deepseek_llm| llm
    main -->|plan_and_execute| planner
    planner --> executor
    executor --> react
    react --> prompt
    react --> toolImpl
```

### plan_and_execute 主循环

**一句话：** 先全局规划，再逐步执行；每步结果写入 `state`；某步异常则重规划；全部成功后 LLM 汇总。

```mermaid
flowchart TD
    start([开始]) --> plan["steps = plan(task, llm)<br/>state = {}"]
    plan --> attempt["重规划 attempt = 0 .. max_replans"]
    attempt --> loop["for i, st in steps"]
    loop --> exec["① execute_step<br/>→ react_loop 最多 4 轮"]
    exec -->|成功| save["② state['step_i'] = out"]
    exec -->|异常| replan["③ llm(replan_prompt)<br/>新 steps → break"]
    replan --> attempt
    save --> more{还有下一步?}
    more -->|是| loop
    more -->|全部成功| summary["④ llm 汇总 state"]
    summary --> ok([返回 Final Result])
    attempt -->|次数用尽| fail(["Failed after replanning."])
```

### plan() — 全局规划

```mermaid
flowchart TD
    task([Task]) --> prompt["拼 prompt:<br/>Break the task into 3-7 concrete steps..."]
    prompt --> llm["llm(prompt) → 多行文本"]
    llm --> parse["_parse_steps()<br/>去空行 / 去 '- ' 前缀"]
    parse --> steps(["Step 1 .. Step N"])
```

### execute_step() — 单步执行器

```mermaid
flowchart TD
    in(["step + state"]) --> q["拼 question:<br/>Complete this step only + Prior step results"]
    q --> react["react_loop(question, tools, llm, max_steps=4)"]
    react --> out(["该步 Final Answer"])
```

### react_loop() — 内嵌 ReAct 循环（单步内）

**一句话：** 最多 4 轮；每轮问 LLM，能答则返回，否则调工具、记入 `history`，继续下一轮。

```mermaid
flowchart TD
    start([开始 history = empty]) --> loop["第 1~4 轮"]
    loop --> build["① build_prompt"]
    build --> call["② llm(prompt) → out"]
    call --> check{"③ 含 Final Answer?"}
    check -->|是| answer([提取答案返回])
    check -->|否| parse["④ parse_action"]
    parse --> tool["⑤ tools[action].run"]
    tool --> hist["⑥ history.append"]
    hist --> loop
    loop -->|跑满仍无答案| fail(["Failed: max steps exceeded."])
```

### 重规划分支

```mermaid
flowchart TD
    err(["execute_step 抛出 Exception"]) --> prompt["replan_prompt =<br/>Task / Failed step / Error / Give a new plan"]
    prompt --> llm["llm(replan_prompt) → 新 steps"]
    llm --> retry["break 内层 for<br/>外层 attempt+1，从头执行新计划"]
```

## 时序图

### 整体 Plan-and-Execute 流程

```mermaid
sequenceDiagram
    actor User as 用户
    participant Main as main.py
    participant Planner as planner.py
    participant Executor as executor.py
    participant React as react_loop
    participant LLM as LLM
    participant Tools as tools

    User->>Main: task
    Main->>Planner: plan_and_execute
    Planner->>LLM: plan(task)
    LLM-->>Planner: steps[]

    Planner->>Executor: execute_step(step_0, state)
    Executor->>React: react_loop
    React->>LLM: ReAct 轮
    LLM-->>React: Thought + Action
    React->>Tools: tool call
    Tools-->>React: observation
    React->>LLM: (+ history)
    LLM-->>React: Final Answer
    React-->>Executor: out
    Executor-->>Planner: out
    Note over Planner: state["step_0"] = out

    Note over Planner: ... step_1, step_2 ...

    Planner->>LLM: Summarize final result
    LLM-->>Planner: Final Result
    Planner-->>Main: result
    Main-->>User: result
```

### 单步内 ReAct 时序（以 step 3 求和为例）

```mermaid
sequenceDiagram
    participant Executor as executor.py
    participant React as react_loop
    participant LLM as LLM
    participant Calc as calculator

    Executor->>React: react_loop(question)
    React->>LLM: prompt
    LLM-->>React: Thought + Action: calculator<br/>Action Input: 2025+4+9
    React->>Calc: 2025+4+9
    Calc-->>React: Observation: 2038
    React->>LLM: prompt (+ history)
    LLM-->>React: Final Answer: 2038
    React-->>Executor: "2038"
```

### 重规划时序（某步失败）

```mermaid
sequenceDiagram
    participant Planner as planner.py
    participant Executor as executor.py
    participant LLM as LLM

    Planner->>Executor: execute_step
    Executor-->>Planner: Exception
    Planner->>LLM: replan_prompt
    LLM-->>Planner: 新 steps[]
    Note over Planner: 重新从 step_0 执行新计划
```

## 核心代码

```python
from agent import build_default_tools, create_deepseek_llm, plan_and_execute

tools = build_default_tools()
llm = create_deepseek_llm(
    system_prompt=(
        "You are a Plan-and-Execute agent assistant. "
        "When planning, output numbered steps one per line. "
        "When executing or summarizing, use the same language as the task."
    )
)
task = "查看当前日期，把当前日期所有的数字求和，并返回结果。"
result = plan_and_execute(task, llm, tools, max_replans=2, verbose=True)
```

## 运行示例（对照 `log.txt`）

**Task:** `查看当前日期，把当前日期所有的数字求和，并返回结果。`

> 有先后依赖：取日期 → 拆数字 → 求和 → 返回。适合展示「先出计划书，再逐步执行，并把上一步结果写入 state」。

### Phase 1 — 规划

```
====>>> LLM request
  Break the task into 3-7 concrete steps...
  Task: 查看当前日期，把当前日期所有的数字求和，并返回结果。

====<<< LLM response
  1. 获取当前日期（年、月、日）。
  2. 将年、月、日的数字分别提取出来。
  3. 将所有数字相加求和。
  4. 返回求和结果。

=== Plan ===
  1. 1. 获取当前日期（年、月、日）。
  2. 2. 将年、月、日的数字分别提取出来。
  3. 3. 将所有数字相加求和。
  4. 4. 返回求和结果。
```

### Phase 2 — 逐步执行

```
--- Executing step 1: 获取当前日期 ---
  LLM → Final Answer: 当前日期是2025年4月9日。
  state["step_0"] = 当前日期是2025年4月9日。

--- Executing step 2: 提取年/月/日数字 ---
  （读 Prior step results，无需工具）
  Final Answer: 年：2025，月：4，日：9
  state["step_1"] = 年：2025，月：4，日：9

--- Executing step 3: 求和 ---
  ====>>> LLM request ... Action: calculator / Action Input: 2025+4+9
  =======>>> Tool execution (local function call) ======
  { "action": "calculator", "input": "2025+4+9", "observation": "2038" }
  ====<<< LLM response → Final Answer: 2038
  state["step_2"] = 2038

--- Executing step 4: 返回结果 ---
  Final Answer: 2038
  state["step_3"] = 2038
```

时序摘要：

```mermaid
sequenceDiagram
    participant Planner as planner
    participant Executor as executor
    participant React as react_loop
    participant LLM as LLM
    participant Tools as calculator

    Planner->>Executor: step_0 获取当前日期
    Executor->>React: react_loop
    React->>LLM: prompt
    LLM-->>React: Final Answer: 当前日期是2025年4月9日
    React-->>Executor: out
    Note over Planner: state[step_0]

    Planner->>Executor: step_1 提取数字
    Executor->>React: react_loop
    React->>LLM: prompt + prior results
    LLM-->>React: Final Answer: 年：2025，月：4，日：9
    React-->>Executor: out
    Note over Planner: state[step_1]

    Planner->>Executor: step_2 求和
    Executor->>React: react_loop
    React->>LLM: prompt
    LLM-->>React: Action: calculator 2025+4+9
    React->>Tools: 2025+4+9
    Tools-->>React: Observation: 2038
    React->>LLM: prompt + history
    LLM-->>React: Final Answer: 2038
    React-->>Executor: 2038
    Note over Planner: state[step_2]=2038

    Planner->>Executor: step_3 返回结果
    Executor->>React: react_loop
    React->>LLM: prompt
    LLM-->>React: Final Answer: 2038
    React-->>Executor: 2038
    Note over Planner: state[step_3]=2038
```

### Phase 3 — 汇总

```
====>>> LLM request
  Summarize final result based on:
  {'step_0': '当前日期是2025年4月9日。',
   'step_1': '年：2025，月：4，日：9',
   'step_2': '2038',
   'step_3': '2038'}

====<<< LLM response / Final Result:
  根据提供的步骤结果，最终总结如下：
  当前日期为2025年4月9日，而最终得出的年份是2038年。
```

> 注：本次 log 里 step 1 未真正走到 Tool execution（模型同轮写出了 Final Answer，`react_loop` 优先截断返回）。step 3 才出现本地 `calculator` 调用。完整原始输出见同目录 `log.txt`。

## 扩展方式

1. 在 `agent/tools/` 新建工具，在 `build_default_tools()` 中注册
2. 调整 `executor.py` 可替换单步执行策略（纯 LLM 或 ReAct）
3. 修改 `planner.py` 中的 `replan_prompt` 可定制重规划逻辑

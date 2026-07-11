# 03 - Reflection Agent 示例


实现 **Action → Evaluation → Reflection → Retry** 工作流：失败时将反思写入策略记忆，跨尝试复用，形成可累积的改进线索。

## 目录结构

```
03-reaction/
├── main.py
├── agent/
│   ├── reflection_loop.py   # 主循环 reflect_until_success
│   ├── action.py            # ReAct Action（注入 reflections）
│   ├── evaluator.py         # 规则 + LLM 评估
│   ├── reflector.py         # 生成反思并裁剪 memory
│   ├── prompt.py
│   ├── llm/
│   └── tools/
├── requirements.txt
└── .env.example
```

## 核心循环（对应 3.5 伪代码）

```python
reflections = []
repeat until success or max_trials:
    output = Action(task, reflections, tools)      # agent/action.py
    score, feedback = Evaluator(task, output)    # agent/evaluator.py
    if success:
        return output
    reflections.append(Reflector(feedback))        # agent/reflector.py
```

入口：`reflect_until_success()` in `agent/reflection_loop.py`。

## 与「让模型自己检查一遍」的区别（Q5）

| 自检 | Reflection |
|------|------------|
| 往往一次性 | 评估与反思显式化、结构化 |
| 不持久 | 跨尝试复用反思文本（策略记忆） |
| 难评测 | 规则/分数/反馈可记录，便于工程控制 |

## 追问要点（3.4）

- **Evaluator 从哪来？** 本示例对演示任务先用规则（`21+21` + 字符数 2），否则用 LLM 输出 `Success/Score/Feedback`。
- **反思会不会冗长？** `trim_reflections` 限制条数（默认 5）、单条长度（400 字）、合并相似项。

## 适用场景（3.6）

- 可验证任务：代码、数学、有测试用例的生成
- 易犯系统性错误：格式、约束、工具选择
- 预算允许多轮尝试（反思会增加 LLM 调用次数）

## 快速开始

```bash
cd 03-reaction
pip install -r requirements.txt
copy .env.example .env   # 填写 DEEPSEEK_API_KEY，可与 01/02 共用

python main.py
```

## 流程图

### 主流程概览

```
  [Task]
     |
     v
  reflections = []
     |
     +---- trial < max_trials ------------------+
     |                                          |
     v                                          |
  Action (ReAct + reflections + tools)          |
     |                                          |
     v                                          |
  Evaluation (rules -> else LLM)              |
     |                                          |
     +--- success ---> return output            |
     |                                          |
     v                                          |
  Reflection -> append & trim reflections -----+
     |
     v
  return last output (or failed message)
```

### 时序图

**Trial** = 一轮完整的「生成答案 → 评估 →（失败则）写反思」；由 `reflect_until_success()` 驱动，默认最多 3 轮。  
**reflections** = 策略记忆：每轮失败后的改进建议会追加进来，下一轮 Action 会读入，避免重复犯错。

```
reflect_until_success(task)
│
├─ reflections = []
│
└─ Trial 1, 2, ... max_trials
      │
      │  ① Action（action.py）
      │     读入: task + reflections（第 2 轮起带上上轮反思）
      │     内部: ReAct — LLM 思考 → 调 calculator/word_count 等 → Final Answer
      │     产出: output
      │           │
      │  ② Evaluation（evaluator.py）
      │     读入: task + output
      │     内部: 能规则校验则走规则，否则 LLM 给 Success / Score / Feedback
      │     产出: success, feedback
      │           │
      │  ③ 判断
      │     success = yes  ──→ 返回 output，程序结束
      │     success = no   ──→ 继续 ④
      │           │
      │  ④ Reflection（reflector.py，仅失败时）
      │     读入: output + feedback
      │     内部: LLM 写一条改进策略 → trim_reflections 限条数/去重
      │     产出: reflections 多一条 → 进入下一 Trial 的 ①
      │
      └─ 全部 Trial 仍失败 → 返回最后一轮的 output
```

**运行示例时序图**（`python main.py`，任务：计算 21+21 并统计答案串字符数）

```
main.py
  └── reflect_until_success("请帮我计算 21+21，并统计答案字符串有多少个字符。")
        reflections = []

══════════════════════════ Trial 1/3 ══════════════════════════

reflection_loop ──① Action─────────────────────────────────────────────> action + LLM

  ReAct Step 1
    LLM ──Thought──> 先算 21+21
    LLM ──Action: calculator, Input: 21+21──> tools.calculator
    tools ──Observation──> "42"

  ReAct Step 2
    LLM ──Action: word_count, Input: 42──> tools.word_count
    tools ──Observation──> "字符数: 2, 词数: 1"
    LLM ──Final Answer──> "21+21=42，字符串\"42\"有2个字符。"

action ──output──> reflection_loop

reflection_loop ──② Evaluation──> evaluator._rule_check
  规则看 Final Answer 措辞：含 42，但未匹配「字符数: 2 / 字符数为 2」等格式
  （虽在 ReAct 里调过 word_count，规则只检查最终文本）
evaluator ──> Success=False, Score=0.3
           Feedback: 未用 word_count 统计…（规则提示语）

reflection_loop ──④ Reflection──> reflector + LLM
reflector ──> "必须使用 word_count…再按要求格式输出"
reflection_loop ──> reflections[1] = 上述文本

══════════════════════════ Trial 2/3 ══════════════════════════

reflection_loop 打印 Strategy memory: reflections[1]

reflection_loop ──① Action（prompt 含 Past reflections）──> action + LLM

  ReAct Step 1
    calculator(21+21) ──> Observation: 42

  ReAct Step 2
    word_count(42) ──> Observation: 字符数: 2, 词数: 1
    Final Answer ──> "21+21=42，字符串\"42\"的字符数为2。"

action ──output──> reflection_loop

reflection_loop ──② Evaluation──> evaluator._rule_check
evaluator ──> Success=True, Score=1.0
           Feedback: 规则校验通过

reflection_loop ──③ return output ──> main.py 打印 Final Result
```

**示例对照表：**

| Trial | ReAct 关键步骤 | Final Answer（规则只看这句） | Evaluation |
|-------|----------------|------------------------------|------------|
| 1 | calculator→42；word_count→字符数:2 | 「…有**2个字符**」 | 未通过（措辞不符） |
| 2 | 同上，且 prompt 带 reflections | 「…**字符数为**2」 | 通过 → 结束 |

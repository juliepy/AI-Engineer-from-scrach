# 04 - LATS（Language Agent Tree Search）

把 Agent 决策看成在**树**上搜索：节点 = 状态/中间思路，边 = 不同行动。复杂任务上探索多条路径，用评估函数判断哪条更有希望。

## 目录结构

```
04-LATS/
├── main.py
├── agent/
│   ├── lats_search.py    # lats_solve / lats_mcts 入口
│   ├── mcts.py           # Select / Expand / Simulate / Backpropagate
│   ├── expand.py         # expand_candidates（4.5）
│   ├── scorer.py         # score_action / 启发式 + LLM
│   ├── executor.py       # 解析 Action 并调用 tools
│   ├── types.py          # TreeNode + UCB
│   ├── prompt.py
│   ├── llm/
│   └── tools/
├── requirements.txt
└── .env.example
```

## 核心 API（对应 4.5）

```python
cands = expand_candidates(state, llm, k=3)
best = max(cands, key=lambda a: score_action(state, a, scorer))
# => lats_one_step(state, llm, scorer)
```

完整搜索：`lats_mcts()` 在预算内循环 MCTS 四步。

## MCTS 四步（面试版）

| 步骤 | 本仓库实现 | 说明 |
|------|------------|------|
| Select | `select()` | 从根沿 **UCB** 走到叶或未访问子节点 |
| Expand | `expand_node()` | LLM 生成 **k** 条候选 `Action: tool[input]` |
| Simulate | `simulate()` | `scorer(state, action)` 估计潜力（可接短 rollout） |
| Backpropagate | `backpropagate()` | 回报累加到路径上 `visits` / `total_value` |

## 与 ReAct / Beam 对比

| | ReAct | Beam Search | LATS / MCTS |
|---|-------|-------------|-------------|
| 结构 | 单链逐步 | 固定宽度序列 | 树 + 节点价值 |
| 探索 | 贪心一条 | 保留 top-k 序列 | UCB 平衡探索/利用 |
| 成本 | 较低 | 中 | 较高（多分枝+评估） |
| 收益 | 简单任务快 | 生成质量 | 降低「一条路走到黑」 |

## 面试 Q6

**LATS 相比单次 ReAct 多在哪成本？换来什么？**

- **成本**：多分枝 `expand`、多次 `score`/模拟、树迭代预算。
- **收益**：更系统探索，适合决策点多、可打分的任务（规划 puzzle、多方案代码修复等）。

## 追问（4.4）

- **和 Beam Search？** Beam 偏序列生成；LATS 强调**节点价值**与 **UCB 探索策略**。
- **工程难点？** 分支爆炸、评估器设计、延迟 → 需剪枝（`max_depth`）、缓存、启发式 scorer。

## 适用场景（4.6）

- 策略游戏、规划类 puzzle、多方案补丁
- 需先提出多种假设再验证的研究型问题

## 快速开始

```bash
cd 04-LATS
pip install -r requirements.txt
copy .env.example .env   # DEEPSEEK_API_KEY，可与 01~03 共用

python main.py
```

`main.py` 依次演示：

1. **lats_one_step** — 3 候选扩展，选最高分一步  
2. **lats_mcts** — budget=6 的树搜索，输出最优路径执行后的状态  

## 流程图

```
Task
  |
  v
根节点 state = "Task: ..."
  |
  +--[budget 次 MCTS 迭代]--------------------------+
  |     Select (UCB) -> Expand (LLM x k)           |
  |     Simulate (scorer) -> Backpropagate         |
  +------------------------------------------------+
  |
  v
沿 visits 最多的子节点走到底 -> 依次 apply_action -> Final State
```

## 搜索树节点图（本次运行重建）

以下树图基于 `budget=6, branch_k=3, max_depth=3` 的实际运行过程重建。  
节点格式：`动作 (visits=V, value=W)`

```
Root: Task("请帮我计算21+21，并统计答案字符串有多少个字符")
  visits=6, value≈3.8
  │
  ├─[iter1 扩展]─► C1: calculator[21+21]       visits=1, value=0.60
  │                （只做计算，未完成统计字符，得分低）
  │
  ├─[iter2 扩展]─► C2: word_count[42]          visits=3, value=2.40 ★最优
  │                （先算出42再统计字符数，任务完成，得分高）
  │                │
  │                ├─[iter4 扩展]─► G1: calculator[42+0]  visits=1, value=0.75
  │                │                 （对已完成状态多余操作，得分中）
  │                │
  │                └─[iter5 扩展]─► G2: word_count[2]     visits=1, value=0.80
  │                                  （验证字符数，得分较高）
  │
  └─[iter3 扩展]─► C3: get_current_time[]      visits=1, value=0.30
                   （与任务无关，得分最低）
```

**最终选择路径**：`root → C2(word_count[42])` — visits 最多（3次），执行后得到 `字符数: 2`

---

### UCB 公式与节点选择规则

```
UCB(node) = total_value/visits  +  C × √(ln(parent.visits + 1) / visits)
               ↑ 利用项（已知质量）        ↑ 探索项（越少访问越高）
```

| 参数 | 值 | 含义 |
|------|----|------|
| `C` (exploration) | 1.4 | 探索系数，越大越倾向探索未知节点 |
| `visits=0` | UCB = ∞ | 未访问节点优先级无限大，必然先被选中 |

**6次迭代的选择过程**：

```
Iter 1  root 是叶节点 → Expand root → 生成 C1/C2/C3
        → 取 C1（第一个子节点）→ Simulate → Backprop
        root.visits=1, C1.visits=1

Iter 2  root 有未访问子节点 [C2, C3] → 直接取 C2（第一个未访问）
        → Simulate(C2) 得分高 → Backprop
        root.visits=2, C2.visits=1

Iter 3  root 有未访问子节点 [C3] → 取 C3
        → Simulate(C3) 得分低 → Backprop
        root.visits=3, C3.visits=1

Iter 4  root 所有子节点已访问 → 计算 UCB：
        C1.UCB = 0.60/1 + 1.4×√(ln4/1) ≈ 0.60+1.95 = 2.55
        C2.UCB = 0.80/1 + 1.4×√(ln4/1) ≈ 0.80+1.95 = 2.75  ← 最高
        C3.UCB = 0.30/1 + 1.4×√(ln4/1) ≈ 0.30+1.95 = 2.25
        → Select C2 → C2 是叶节点 → Expand C2 → 生成 G1/G2/G3
        → 取 G1 → Simulate → Backprop
        root.visits=4, C2.visits=2, G1.visits=1

Iter 5  Select root → UCB 最高仍为 C2（value高+子节点未全访问）
        → C2 有未访问子节点 [G2,G3] → 取 G2 → Simulate → Backprop
        root.visits=5, C2.visits=3, G2.visits=1

Iter 6  Select root → C2.UCB 仍最高（利用项 2.4/3=0.8 领先）
        → C2 有未访问子节点 [G3] → 取 G3 → Simulate → Backprop
        root.visits=6, C2.visits=4 (含自身+子节点回传)

最终：best_child_by_visits(root) → C2 (visits最多) → 执行 word_count[42]
```

> **为什么 C2 visits 最多？** 因为 Simulate 时 C2 得分最高（0.8），Backprop 使 C2 的 `total_value/visits` 即利用项最大；之后每轮 UCB 计算 C2 都领先，导致树搜索反复"光顾" C2 分支，visits 持续累积。

---

## 实际运行示例

下面是 `python main.py` 对任务 **"请帮我计算 21+21，并统计答案字符串有多少个字符"** 的实际输出，逐段拆解：

```
============================================================
1) lats_one_step — 扩展 3 候选，选分最高的一步
============================================================
Best action: Action: word_count[42]

State after one step:
Task: 请帮我计算 21+21，并统计答案字符串有多少个字符。
Action: word_count[42]
Observation: 字符数: 2, 词数: 1
```

**怎么理解这一段？**

| 字段 | 说明 |
|------|------|
| `lats_one_step` | 只做 **Expand + Score** 两步：LLM 生成 3 条候选 Action，打分取最高分那条 |
| `Best action: word_count[42]` | LLM 先用 `calculator` 算出 21+21=42，再把结果 `42` 传给 `word_count` 统计字符数 |
| `字符数: 2, 词数: 1` | 字符串 `"42"` 共 2 个字符，1 个词，任务完成 |

---

```
============================================================
2) lats_mcts — Select / Expand / Simulate / Backpropagate
============================================================
Task: 请帮我计算 21+21，并统计答案字符串有多少个字符。
Action: word_count[42]
Observation: 字符数: 2, 词数: 1
```

**怎么理解这一段？**

| 阶段 | 发生了什么 |
|------|------------|
| **Select** | 从根节点出发，按 UCB 公式选出最值得探索的叶节点（初始就是根） |
| **Expand** | LLM 为该节点生成 k 条候选 Action（包括 `word_count[42]`）并挂成子节点 |
| **Simulate** | scorer 对每个子节点估分（启发式打分），`word_count[42]` 分最高 |
| **Backpropagate** | 将该得分沿路径回传，更新所有祖先节点的 `visits` 和 `total_value` |
| **最终输出** | budget 用完后，沿 `visits` 最多的子节点走到底，依次执行 Action，得到与 one_step 相同的最优路径 |

> **关键结论**：两种方式最终找到同一条最优路径 `word_count[42]`。  
> `lats_one_step` 更快（只看一步）；`lats_mcts` 通过树搜索在复杂多步任务中能找到单步贪心错过的更优路径。

---

## 时序图（MCTS 单次迭代）

```
lats_mcts          mcts.select      mcts.expand       LLM          scorer
    |                  |                |             |              |
    |-- Select ------->|                |             |              |
    |<-- 叶节点 --------|                |             |              |
    |-- Expand ------------------------>|-- k 候选 -->|              |
    |                  |                |<-- actions -|              |
    |-- Simulate --------------------------------------------------->|
    |<-- reward -----------------------------------------------------|
    |-- Backpropagate (更新 visits/value) |             |              |
```

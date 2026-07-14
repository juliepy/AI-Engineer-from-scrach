# Agent Evaluate 方法整理

> 来源：Hugging Face Agentic Evals Workshop  
> 讲者：Abhijit（HF / Eval）、Arvind（Princeton）、Pierre（Meta / Gaia 2）、Mahesh（Bespoke Labs）、Nathan（HF Community Eval）  
> 一句话：**Agent Eval ≠ 看一个 Pass Rate；要报系统组成、会话轨迹、可靠性与成本，并在可复现的 Environment 里打分。**

---

## 0. 核心结论（先记住）

| 维度 | LLM Eval | Agent Eval |
|------|----------|------------|
| 输入输出 | Prompt → Text | Task → 多步 Action → 环境状态变化 |
| 同分含义 | 答案对/错 | 步数、成本、崩溃、轨迹可以完全不同 |
| 评什么 | Capability 为主 | Capability + Reliability + Cost + Safety |
| 可复现 | 相对容易 | 必须隔离 Environment / Session / Harness |

Capability 涨得快，Reliability 涨得慢——这是「基准刷分很猛、生产用不起来」的重要解释。

---

## 1. 为什么 Agent Eval 难

1. **随机性**：同一任务多次 Run，结果可差很多（Consistency 问题）。
2. **多步因果**：失败可能在 LLM、Tool、Harness、环境噪声任一环。
3. **环境会变**：邮件、价格、日历、外部事件会在任务中途注入。
4. **副作用贵/危险**：删库、错下单、乱发消息——不能在真生产上试错。
5. **人机交互欠测**：用户插话、模糊需求、多 Actor 场景测得少。
6. **基准互不兼容**：TauBench（用户对话）≠ WebArena（网页）≠ TerminalBench（终端）。

```
同一 Pass Rate 的两个 Agent：

Agent A：步数少、便宜、无崩溃
Agent B：步数多、贵、中途报错但仍「碰巧」答对

→ 只报 aggregate score = 信息严重不足
```

---

## 2. 评测报告：诚实与可复现（文档层）

### 2.1 常见坏实践

- **小字省略题**：如 SWE 报高分，但脚注删掉大量题目。
- **Benchmark maxing**：不同变体刷不同榜。
- **图表误导**：柱高不按真实比例、不报 error bar。
- **只报模型名**：Agent ≠ Model；缺 harness / MCP / memory / 子 Agent 信息。

### 2.2 应报告的字段（Agent 扩展）

| 字段类 | 内容 |
|--------|------|
| **System composition** | 模型列表与角色、子 Agent、MCP、Memory 配置、Harness |
| **Session semantics** | 一次 Run / Session 如何界定；种子、温度、重试 |
| **Interaction accounting** | 工具调用序列、人类介入、环境事件 |
| **Eval conditions** | 环境版本、量化、评测库、可第三方复现的参数 |
| **Instance-level** | 不只 aggregate；尽量有逐条结果 |

基础设施方向：**Every Eval Ever**（统一 schema）→ **Eval Cards**（一模型看齐所有一/三方评测）。

原则：**白盒系统记录** > 只贴一个分数；治理与追责需要 Session 级数据。

---

## 3. Capability vs Reliability（可靠性科学）

Capability 高 ≠ 能部署。可靠性可拆成四维（可挂在任意 benchmark 上测，不必另造新榜）：

### 3.1 四个维度

| 维度 | 含义 | 典型指标 |
|------|------|----------|
| **Consistency** | 同一任务是否稳定 | Outcome consistency；Trajectory consistency；Cost 稳定性 |
| **Robustness** | 轻微扰动是否崩 | Prompt 改写；环境/API 故障注入 |
| **Predictability / Calibration** | 能否知道自己做对了没 | 置信度校准；成功/失败区分度（discrimination） |
| **Failure severity（Safety）** | 错了有多严重 | 格式错 vs 删库/错扣款（常单独计，不进综合指数） |

### 3.2 关键发现（访谈口径）

- 近 18 个月：准确率斜率陡，**Reliability 综合分涨得很慢**。
- Accuracy 与 Reliability 近似线性相关，但 Reliability 斜率远小于 Capability。
- **增强（人在环）** vs **自动化（无人值守）**：后者对 Reliability 门槛高得多。
- 发布决策应设 **Reliability threshold**，不能只看 Capability。

### 3.3 实践建议

- 每个 benchmark 默认附带 Reliability 指标（Pass@k、多次 rollout、扰动）。
- 不要假设「模型变聪明，可靠性自动好」——要专门优化。
- 开源任务若需「多样性」（如写诗），Consistency 未必是好目标——按任务取舍。

---

## 4. 动态环境基准：Gaia 2 方法

核心问题：真实 Agent 活在**会变的世界**（新邮件、价格变动、他人取消会议），旧式「Prompt→答案」或静态沙箱不够。

### 4.1 仿真四件套（ARE / Meta Agent Research Environment）

| 概念 | 作用 |
|------|------|
| **Apps** | 类手机 App：有状态 + API/工具面（邮件、日历、文件系统等） |
| **Universe** | 一组 App 的初始世界状态（历史邮件、人设对话等） |
| **Events** | 用户 / Agent / 环境注入的事件 |
| **Scenarios** | 任务 = 初始状态 + 事件序列 + 期望动作，不是单条 Prompt |

为何仿真：可复现、可观测、可做破坏性动作、便宜（不依赖真实外网 API）。

### 4.2 五类能力

| 能力 | 测什么 |
|------|--------|
| **Execution** | 单轮多工具写操作（取消会议、回邮件） |
| **Search** | 跨 App API 检索（非纯网页关键词） |
| **Adaptability** | 行动后环境变化，能否重规划 |
| **Time** | 时间触发事件（等机票降价）；评测时**时间快进** |
| **Ambiguity** | 必须追问用户，否则不该盲干 |

### 4.3 抗过拟合 / 压力测试

- Tool failure 注入  
- API 签名改名（防死记工具面）  
- Environment noise（无关外部事件）  
- Agent-to-Agent：主 Agent 只能自然语言调子 Agent，无直接工具

### 4.4 打分方式（硬 + 软）

```
期望动作 DAG  ⟷  实际动作 DAG
        │
   Hard verifier：参数/顺序用确定性比较（便宜、可复现）
   Soft verifier：邮件正文等用 LLM 判语义（仅必要时）
```

相对 Rubric-only LLM Judge：更稳、更便宜、更可复现。

现状观察：Search / Execution 相对强；**Time ≈ 0%、Adaptability / Ambiguity 仍弱**。

---

## 5. 工业实践：Environment-first Eval（怎么落地）

### 5.1 反模式（How not to）

- 只盯最终输出，改完不知哪坏了  
- 一上来过度抠「Planner 对不对、这个 function call 对不对」  
- **先上线再生产里评**  
- Agent 能接触 grader / 标准答案 → Reward hacking

### 5.2 分级：可验证 → 不可验证

| Level | 场景 | 打分 |
|-------|------|------|
| **L0 Verifiable** | Coding / Math | 单测、编译、数值相等；注意测例权重与「改测试过关」 |
| **L1 Non-verifiable** | 长文检索报告等 | **Rubrics** + LLM-as-Judge（多条 0/1 × 权重 → 总分） |

### 5.3 Environment 设计要点

```
Task  →  Agent ⟷ Environment(sandbox)  →  Output / 世界状态
                              │
                           Grader
                    （单测 / Rubric / Hard+Soft）
```

| 决策 | 要点 |
|------|------|
| 逼真度 | 尽量贴近生产（数据、工具、失败模式） |
| 隔离 | Sandbox；Agent **禁止**访问 grader / solution |
| Task 覆盖 | 任务里要求的每一点都要被 grade，否则被钻空子 |
| 格式 | Harbor、OpenEnv 等；任务 + 环境 + grader 一体 |

Sim-to-real：用 mock/wire 复刻 Slack、GitHub 等关键表面，逐步缩小与生产差距。

### 5.4 测什么指标

| 类型 | 指标 |
|------|------|
| 主成功 | Success rate（N 次 rollout 平均）；Pass@k |
| 效率 | 步数、Token、Latency、Cost |
| 系统 | 同一模型不同 **Harness** 分数可差很多（见 Terminal Bench） |
| 安全 | 删数、乱消费等 → 可作惩罚项 / 专项任务 |
| 诊断 | 读 Trace；自动失败聚类（某类场景成功率骤降） |

流程：**Environment → Tasks → Grader → Metrics → Trace 分析 → 改 Harness/模型 → 再评 → 再上线**。  
Eval 也可喂给优化（如 GEPA 等）做自动改进。

---

## 6. 活的基准：Community Eval / Living Benchmark

问题：分数碎片化、维护贵、无单一真相源、基准散落难跑。

做法（HF Hub）：

1. Dataset + `eval.yaml`（框架、solver、scorer）  
2. 优先复用现成框架（如 Inspect AI），少自造评测引擎  
3. 本地 / HF Jobs 跑（慎用不明后端的 Inference Provider——评的是 Provider 不是模型）  
4. 结果以 PR 形式挂到模型仓 → Dataset 页自动出 Leaderboard  
5. 社区可在 PR 讨论争议分；作者可隐藏不合理分数

Agent 场景：Terminal Bench 等已挂在 Hub；solver 可写成完整 Agent scaffolding。

---

## 7. 方法总览（面试 / 落地一张图）

```
                 ┌─ Capability（任务成功率 / Pass@k）
                 ├─ Reliability（一致 / 鲁棒 / 校准 / 失败严重度）
 Agent Eval ────┼─ Efficiency（步数 / Token / 延迟 / 成本）
                 ├─ Process（轨迹、工具调用、人机交互）
                 └─ Safety / Social（误操作、注入、社会影响）

落地三件套：
  1. Environment（可复现 sandbox）
  2. Tasks / Scenarios（含动态事件）
  3. Grader（Hard 优先，Soft/Rubric 补位）

报告三件套：
  1. System composition（Agent 白盒）
  2. Session + Instance 结果
  3. Eval conditions（可第三方复现）
```

### 面试一句话版本

> LLM Eval 看答案；Agent Eval 看「在什么系统、什么环境、什么轨迹下、以多大成本、多稳地完成任务」。先 Environment + Grader，再报 Capability 与 Reliability，禁止只贴一个榜分数。

---

## 8. 仍开放的问题

| 问题 | 说明 |
|------|------|
| Long-horizon | 数小时～数天任务：贵、慢；指标易「饱和」而任务未饱和（SWE-CI 等方向） |
| Multi-agent / Multi-user | 多 Actor 对齐谁、参数组合爆炸 |
| Harness-agnostic Eval | 错误来自模型还是工具栈；需白盒 + 可比较 harness（如 Exgenic 方向） |
| Human–Agent 交互 | 噪声、追问、授权边界仍欠测 |
| Open vs Gaming | 公开数据集利于验证；防刷靠披露与严格 checker，而非一味私有 |
| Enterprise 民主化 | Gaia 2 级复杂环境如何变成企业可自建的方法论与工具 |

---

## 9. 行动清单（做自己的 Agent Eval）

1. **Eval-first**：上线前先定义任务、环境、grader、指标。  
2. **多次 rollout**：报 Success rate + Pass@k + 方差/error bar。  
3. **挂 Reliability**：至少做 prompt 扰动 + 故障注入 + 轨迹抽检。  
4. **Hard 能验则硬验**；开放生成再用 Rubric / Soft judge。  
5. **隔离 grader**；任务要求写进评分，防 reward hacking。  
6. **记录 Agent 身份**：模型 + harness + 工具 + memory，不只模型名。  
7. **读 Trace**：分数只告诉好坏，轨迹告诉为什么。  
8. **自动化场景用更高 Reliability 门槛**；增强场景可略松但仍要测。

---

## 参考锚点（讲者 → 关键词）

| 讲者 | 关键词 |
|------|--------|
| Abhijit | Eval 报告诚实性、Every Eval Ever、Agent schema 扩展 |
| Arvind | Capability–Reliability gap、四维可靠性、Reliability Index |
| Pierre | Gaia 2、动态多 App 仿真、Hard/Soft verifier |
| Mahesh | Environment-first、Rubric、Pass@k、防 hacking |
| Nathan | Community Eval、eval.yaml、Living Leaderboard |

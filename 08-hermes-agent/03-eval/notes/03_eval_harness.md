# 03 · 最小 Eval Harness：离线打分 + RCA

> 讲解顺序：[`README.md`](./README.md) · **主线 3/3** · 上一篇 [`02`](./02_logging_trace.md)  
> Demo：`../demo/run_eval_suite.py`  
> Layer A：`teaching/invariants/test_agent_loop_contracts.py`（近 Hermes pytest）  
> Layer B：`fixtures/eval_cases.json` + `from_02_agent_loop.json` / `failure_run.json`  
> 输出：`../demo/exports/eval_run/` · 下一篇桥：[`04_tests_and_eval.md`](./04_tests_and_eval.md)

---

## 0. 一句话

评测不必每次打真模型：**冻结一条 loop 导出 → 用规则打分 → 对失败 case 写 RCA**。这就是 JD 里 Eval / Benchmark / Trace Analysis 的最小可展示物。

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryTextColor":"#111111","lineColor":"#90CAF9","fontSize":"16px"}}}%%
flowchart LR
    FREEZE["冻结 Trace<br/>正例 + 负例"] --> SCORE["规则打分<br/>关系 / 不变量"]
    SCORE --> PASS["PASS<br/>报告"]
    SCORE --> FAIL["FAIL → RCA<br/>root_cause + evidence"]

    style FREEZE fill:#90CAF9,stroke:#0D47A1,stroke-width:2px,color:#111111
    style SCORE fill:#FFE082,stroke:#F57F17,stroke-width:2px,color:#111111
    style PASS fill:#A5D6A7,stroke:#1B5E20,stroke-width:2px,color:#111111
    style FAIL fill:#EF9A9A,stroke:#B71C1C,stroke-width:2px,color:#111111
```

---

## 1. 双层结构（像不像真 Hermes）

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryTextColor":"#111111","lineColor":"#90CAF9","fontSize":"15px"}}}%%
flowchart TB
    subgraph A["Layer A · pytest contracts"]
        A1["Test* 类"]
        A2["断言关系 / 不变量"]
        A3["风格对齐 test_prompt_caching"]
    end

    subgraph B["Layer B · offline harness"]
        B1["正例 + 负例 JSON"]
        B2["score_suite 打分"]
        B3["session 日志 + RCA 报告"]
    end

    A --> B

    style A fill:#90CAF9,stroke:#0D47A1,stroke-width:2px,color:#111111
    style B fill:#FFCC80,stroke:#E65100,stroke-width:2px,color:#111111
    style A1 fill:#BBDEFB,stroke:#1565C0,stroke-width:2px,color:#111111
    style A2 fill:#BBDEFB,stroke:#1565C0,stroke-width:2px,color:#111111
    style A3 fill:#BBDEFB,stroke:#1565C0,stroke-width:2px,color:#111111
    style B1 fill:#FFE0B2,stroke:#E65100,stroke-width:2px,color:#111111
    style B2 fill:#FFE0B2,stroke:#E65100,stroke-width:2px,color:#111111
    style B3 fill:#FFE0B2,stroke:#E65100,stroke-width:2px,color:#111111
```

| 层 | 像不像真 Hermes | 做什么 |
|----|-----------------|--------|
| **A. pytest contracts** | ✅ 风格对齐 | `Test*`，断言关系 / 不变量 |
| **B. offline harness** | ❌ 真仓无此 JSON suite | 正例+负例打分、日志、RCA |

流程：`pytest` → `score_suite` → session 日志 → 负例 RCA。**无需 API Key。**

---

## 2. 评测维度（对齐大纲）

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryTextColor":"#111111","lineColor":"#90CAF9","fontSize":"14px"}}}%%
flowchart TB
    D1["完成率<br/>final + exit"] --> AND["全部 AND<br/>才算 case PASS"]
    D2["步数 / 成本<br/>api_calls ≤ max"] --> AND
    D3["工具选对率<br/>expected ⊆ actual"] --> AND
    D4["忠实度 / 契约<br/>role + system"] --> AND
    D5["预算纪律<br/>grace / exhausted"] --> AND

    style D1 fill:#90CAF9,stroke:#0D47A1,stroke-width:2px,color:#111111
    style D2 fill:#A5D6A7,stroke:#1B5E20,stroke-width:2px,color:#111111
    style D3 fill:#FFCC80,stroke:#E65100,stroke-width:2px,color:#111111
    style D4 fill:#CE93D8,stroke:#6A1B9A,stroke-width:2px,color:#111111
    style D5 fill:#80CBC4,stroke:#00695C,stroke-width:2px,color:#111111
    style AND fill:#FFE082,stroke:#F57F17,stroke-width:2px,color:#111111
```

| 维度 | 本 demo 信号 | 通过条件（示例） |
|------|--------------|------------------|
| 完成率 | `final_response` 非空 + `exit_reason` | 在 case 允许的 exit 集合内 |
| 步数 / 成本代理 | `api_calls` / `budget_used` | `api_calls ≤ max_steps` |
| 工具选对率 | `tool_sequence` | `expected_tools ⊆ actual`；禁止 `forbidden_tools` |
| 忠实度 / 契约 | role 交替、system 稳定 | invariants 全绿 |
| 预算纪律 | grace / exhausted | case 可声明「期望 grace」或「禁止 exhausted」 |

不写「最终中文答案必须逐字等于金标」——那是 change-detector 的近亲（见 [`01_eval_invariants.md`](./01_eval_invariants.md)）。

---

## 3. Case 文件形状

一条 case = **期望关系**，不是期望全文快照。

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryTextColor":"#111111","lineColor":"#90CAF9","fontSize":"15px"}}}%%
flowchart LR
    CASE["eval_cases.json"] --> FIX["run_fixture<br/>指向冻结轨迹"]
    CASE --> EXP["expected_tools<br/>forbidden / max / exits"]
    FIX --> RUN["from_02…json<br/>或 failure_run.json"]
    EXP --> SC["scorer 比对"]
    RUN --> SC

    style CASE fill:#FFE082,stroke:#F57F17,stroke-width:2px,color:#111111
    style FIX fill:#90CAF9,stroke:#0D47A1,stroke-width:2px,color:#111111
    style EXP fill:#A5D6A7,stroke:#1B5E20,stroke-width:2px,color:#111111
    style RUN fill:#BBDEFB,stroke:#1565C0,stroke-width:2px,color:#111111
    style SC fill:#FFCC80,stroke:#E65100,stroke-width:2px,color:#111111
```

```json
{
  "id": "loop-grace-ok",
  "run_fixture": "golden_run.json",
  "expected_tools": ["todo", "web_search"],
  "forbidden_tools": ["execute_code"],
  "max_steps": 10,
  "allowed_exits": ["completed", "budget_grace_call"],
  "require_final_text": true,
  "notes": "02-run-agent 实跑：budget 用尽后 grace 收尾"
}
```

| id | fixture | 意图 | 期望 |
|----|---------|------|------|
| `golden-loop-ok` | `from_02_agent_loop.json` | 工具子集 + 允许 grace | **PASS** |
| `failure-wrong-tool-cache-break` | `failure_run.json` | 错工具 / role 破 / cache 漂 | **FAIL → RCA** |

---

## 4. Scorer 怎么判

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryTextColor":"#111111","lineColor":"#90CAF9","fontSize":"14px"}}}%%
flowchart TB
    IN["case + run"] --> C1["tools_subset"]
    IN --> C2["no_forbidden"]
    IN --> C3["steps"]
    IN --> C4["exit"]
    IN --> C5["final_text"]
    IN --> C6["role_invariant"]
    IN --> C7["system_stable"]
    C1 & C2 & C3 & C4 & C5 & C6 & C7 --> OUT{"全部 ok?"}
    OUT -->|是| P["passed: true"]
    OUT -->|否| F["passed: false → RCA"]

    style IN fill:#FFE082,stroke:#F57F17,stroke-width:2px,color:#111111
    style C1 fill:#BBDEFB,stroke:#1565C0,stroke-width:2px,color:#111111
    style C2 fill:#BBDEFB,stroke:#1565C0,stroke-width:2px,color:#111111
    style C3 fill:#BBDEFB,stroke:#1565C0,stroke-width:2px,color:#111111
    style C4 fill:#BBDEFB,stroke:#1565C0,stroke-width:2px,color:#111111
    style C5 fill:#BBDEFB,stroke:#1565C0,stroke-width:2px,color:#111111
    style C6 fill:#CE93D8,stroke:#6A1B9A,stroke-width:2px,color:#111111
    style C7 fill:#CE93D8,stroke:#6A1B9A,stroke-width:2px,color:#111111
    style OUT fill:#FFF59D,stroke:#F57F17,stroke-width:2px,color:#111111
    style P fill:#A5D6A7,stroke:#1B5E20,stroke-width:2px,color:#111111
    style F fill:#EF9A9A,stroke:#B71C1C,stroke-width:2px,color:#111111
```

```python
def score_case(case, run) -> CaseScore:
    actual_tools = tool_names_from_trace(run["trace"])
    checks = [
        ("tools_subset", set(case["expected_tools"]) <= set(actual_tools)),
        ("no_forbidden", not (set(actual_tools) & set(case.get("forbidden_tools", [])))),
        ("steps", run["api_calls"] <= case["max_steps"]),
        ("exit", run["exit_reason"] in case["allowed_exits"]),
        ("final", bool(run.get("final_response")) if case["require_final_text"] else True),
        ("role_invariant", check_role_alternation(run["messages"])),
        ("system_stable", check_system_stable(run["trace"])),
    ]
    return CaseScore(passed=all(ok for _, ok in checks), checks=checks)
```

蓝 = 期望关系；紫 = 循环不变量（与 Prompt Cache / 消息布局对齐）。

---

## 5. RCA 输出形状

失败时不只打 `FAIL`，要写可讲的根因：

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryTextColor":"#111111","lineColor":"#90CAF9","fontSize":"15px"}}}%%
flowchart TB
    FAIL["case FAIL"] --> RC["root_cause<br/>如 wrong_tool"]
    FAIL --> EV["evidence<br/>api# / role break / exit"]
    FAIL --> HY["fix_hypothesis<br/>人话复盘"]

    style FAIL fill:#EF9A9A,stroke:#B71C1C,stroke-width:2px,color:#111111
    style RC fill:#FFCC80,stroke:#E65100,stroke-width:2px,color:#111111
    style EV fill:#FFF59D,stroke:#F57F17,stroke-width:2px,color:#111111
    style HY fill:#90CAF9,stroke:#0D47A1,stroke-width:2px,color:#111111
```

```text
root_cause: wrong_tool
evidence:
  - api#2 tool_calls=['execute_code']  # expected web_search
  - role break at messages[3]: user→user
  - exit_reason=budget_exhausted (not in allowed_exits)
fix_hypothesis: 模型空转执行代码且破坏 role 交替，预算耗尽无 grace 文本
```

面试时拿着 `exports/eval_run/03_trace_rca.md` 讲即可；提问顺序见 [`02_logging_trace.md`](./02_logging_trace.md) 第 4 节。

---

## 6. 闭环：Eval 如何反过来优化 Agent

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryTextColor":"#111111","lineColor":"#90CAF9","fontSize":"15px"}}}%%
flowchart LR
    RUN["跑 Agent<br/>出 Trace"] --> SCORE["Eval 打分"]
    SCORE --> INS["定位弱点<br/>wrong_tool / cache_break"]
    INS --> FIX["改 Runtime<br/>工具 / Prompt / 预算"]
    FIX --> RUN

    style RUN fill:#90CAF9,stroke:#0D47A1,stroke-width:2px,color:#111111
    style SCORE fill:#FFE082,stroke:#F57F17,stroke-width:2px,color:#111111
    style INS fill:#FFCC80,stroke:#E65100,stroke-width:2px,color:#111111
    style FIX fill:#A5D6A7,stroke:#1B5E20,stroke-width:2px,color:#111111
```

| 优化方向 | Eval 信号 |
|----------|-----------|
| 工具与策略 | 总调错 `execute_code` → 收紧 schema / 指引 |
| 成本与收敛 | 大量 `budget_exhausted` → 砍空转、加 grace |
| Context / Cache | `system` 漂 / role 破 → 守住中途不改 |
| 防回归 | 固定 case 集 + CI 不变量 |

---

## 7. 与 CI / `run_tests.sh` 的关系

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryTextColor":"#111111","lineColor":"#90CAF9","fontSize":"15px"}}}%%
flowchart TB
    CI["真仓 scripts/run_tests.sh<br/>tests/agent/*"] --> REAL["源码契约<br/>真 Hermes"]
    TEA["教学 test_agent_loop_contracts.py"] --> STYLE["风格对齐，不依赖完整 hermes"]
    HAR["run_eval_suite.py Layer B"] --> REP["正例+负例 + RCA 报告"]

    style CI fill:#90CAF9,stroke:#0D47A1,stroke-width:2px,color:#111111
    style REAL fill:#BBDEFB,stroke:#1565C0,stroke-width:2px,color:#111111
    style TEA fill:#A5D6A7,stroke:#1B5E20,stroke-width:2px,color:#111111
    style STYLE fill:#C8E6C9,stroke:#2E7D32,stroke-width:2px,color:#111111
    style HAR fill:#FFCC80,stroke:#E65100,stroke-width:2px,color:#111111
    style REP fill:#FFE0B2,stroke:#E65100,stroke-width:2px,color:#111111
```

| 层 | 入口 | 目的 |
|----|------|------|
| 单元不变量 | 真仓 `scripts/run_tests.sh` → `tests/agent/` | 源码契约（真 Hermes） |
| 教学契约 | `test_agent_loop_contracts.py`（Test* 类） | 风格对齐真仓 |
| 行为评测报告 | `run_eval_suite.py` Layer B | 正例+负例打分 + RCA |

原则一致：**测关系，不测快照**；真仓永远走 `run_tests.sh`，勿裸奔 `pytest`（凭证 / TZ / 隔离会漂）。

---

## 8. 大纲动手清单

- [x] pytest 契约层（对齐 Hermes `Test*` 风格）
- [x] 正例 + 负例两条拉开的 offline case
- [x] 自动跑分脚本（先 pytest 再 score_suite）
- [x] ≥1 条不变量断言（role / system / tools / budget）
- [x] 一条完整 Trace 根因分析（`failure_run.json` → RCA）

```bash
cd 03-eval/demo
python run_eval_suite.py
# 看 exports/eval_run/
```

主线串读：[`01`](./01_eval_invariants.md) → [`02`](./02_logging_trace.md) → 本文 → 动手 `demo/` → [`04`](./04_tests_and_eval.md)。

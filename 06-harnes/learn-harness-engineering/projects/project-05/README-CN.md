# Project 05: Evaluator Loops and Three-Role Upgrades

测量角色分离（单角色 / 生成+评估 / 计划+生成+评估）如何改变实现质量。

## 目录说明

| 目录 | 含义 |
|------|------|
| `starter/` | **起点**——基于 P4 solution，新增多轮问答历史功能待实现。 |
| `solution/single-role/` | **变体 A**——一个代理完成所有工作（规划 + 实现 + 自我评审）。基础质量。 |
| `solution/gen-eval/` | **变体 B**——生成器 + 评估器模式。较高质量，有修订证据。 |
| `solution/plan-gen-eval/` | **变体 C**——计划器 + 生成器 + 评估器。最高质量，有冲刺合约和评分标准。 |

## 使用方法

```sh
# 如果要自己重跑练习，从 starter 开始
cd starter
npm install
# 用下面三种角色配置实现同一个 ConversationHistory 升级

# 检查三个参考变体
cd solution/single-role && npm install  # 单角色模式
cd solution/gen-eval && npm install     # 生成+评估模式
cd solution/plan-gen-eval && npm install # 完整三角色模式

# 对比三个变体的：
# - 代码质量（evaluator-rubric.md 评分）
# - 发现的缺陷数量
# - 需要返工的程度
```

## 具体任务对应关系

已提交的 solution 固定为同一个产品升级：通过 `ConversationHistory` 实现多轮问答历史。三个 solution 目录不是顺序阶段，而是同一功能在不同角色 harness 下的三个独立运行结果。

| 变体 | 展示什么 | 检查证据 |
|------|------|------|
| `starter/` | ConversationHistory 升级前的 P4 应用 | `ConversationHistory.tsx`, `App.tsx` |
| `solution/single-role/` | 一个 agent 规划、实现、自评 | `evaluator-rubric.md` 评分 1.6/5 和缺陷列表 |
| `solution/gen-eval/` | 生成者 + 评估者，有修订证据 | `evaluator-rubric.md` 评分 3.3/5 和修订记录 |
| `solution/plan-gen-eval/` | 规划者 + 生成者 + 评估者，有 sprint contract | `sprint-contract.md`, `evaluator-rubric.md` 评分 4.9/5 |

重跑时请保持功能不变。三个变体唯一应该变化的是角色分工，否则比较无效。

## 本项目涉及的功能

- 多轮问答历史（对话式 UI）
- 冲刺合约（sprint contract）
- 评估器评分标准（evaluator rubric）调优

## 对应课件

- [Lecture 09: 阻止代理过早宣布胜利](../../docs/en/lectures/lecture-09-why-agents-declare-victory-too-early/index.md)
- [Lecture 10: 只有全流程运行才算真正的验证](../../docs/en/lectures/lecture-10-why-end-to-end-testing-changes-results/index.md)

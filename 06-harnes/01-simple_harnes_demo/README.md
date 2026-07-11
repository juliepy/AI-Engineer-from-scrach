# Simple Harness Demo

这是一个用于学习 **Harness Engineering（马具工程）** 的极简 demo。
只保留核心部分：

1. `CLAUDE.md` — Agent 的行为与编码规则
2. `.claude/skills/*` — 任务工作流（`/plan`、`/implement`、`/validate`）
3. `.claude/hooks/stop_validate.py` — 停止前的质量门
4. `app/` + `tests/` — 供 Agent 操作的小型真实代码库

## 这里的 harness 是什么意思

不让模型「自由发挥」，而是用规则把它包起来：

- 明确的规则（`CLAUDE.md`）
- 明确的工作流步骤（plan → implement → validate）
- 自动校验（测试必须通过）

这个「包装层」就是 harness。

## 示例程序：密码强度判断

当前 `app/password.py` 提供基础能力：

```python
from app.password import check_strength

check_strength("")         # -> "weak"
check_strength("abc123")   # -> "medium"
check_strength("Abc12345") # -> "strong"
```

判定规则（简化版）：

| 等级 | 条件 |
|------|------|
| weak | 空密码、长度 < 6、或只有一种字符类型 |
| medium | 至少两种字符类型（大写/小写/数字），但未达到 strong |
| strong | 长度 ≥ 8，且同时包含大写、小写、数字 |

## 项目结构

```text
simple_harnes_demo/
├── CLAUDE.md                    # Agent 行为规则（编码规范、工作流、完成标准）
├── .claude/                     # Harness 配置目录（Cursor / Claude Code 读取）
│   ├── settings.json            # 注册 hooks（如 Stop 时自动跑校验）
│   ├── hooks/
│   │   └── stop_validate.py     # 停止前质量门：测试不过则不让 Agent 结束
│   └── skills/
│       ├── plan/SKILL.md        # /plan  命令：把需求拆成 plans/*.md 计划
│       ├── implement/SKILL.md   # /implement 命令：按计划改代码并写报告
│       └── validate/SKILL.md    # /validate 命令：跑 scripts/validate.py 验收
├── app/
│   └── password.py              # 业务实现（当前：check_strength 密码强度判断）
├── tests/
│   └── test_password.py         # 单元测试（改 app/ 后必须保持通过）
├── plans/
│   └── explain-strength-plan.md # 预置练习计划（课堂可直接讲解 / 实现）
└── scripts/
    └── validate.py              # 一键跑全部测试，输出 validate: PASS/FAIL
```

## 快速开始

在 `simple_harnes_demo/` 目录下：

```bash
python scripts/validate.py
```

全部通过时会看到：

```text
validate: PASS
```

## 练习流程（完整 harness 闭环）

练习需求：

> 新增 `explain_strength(password)` 函数：返回强度等级 + 中文改进建议列表。

### 完整演示（推荐，会生成 plan 文件）

**第 1 步必须单独跑 `/plan`**，它才会在 `plans/` 下写出 `*.md` 文件：

1. `/plan "为password增加加密函数"`
   - 完成后检查：`plans/encrypt-plan.md` 是否已生成
2. `/implement plans/encrypt-plan.md`
3. `/validate`


走完即体验 harness 循环：

```text
plan（规划） -> implement（实现） -> validate（验收）
```

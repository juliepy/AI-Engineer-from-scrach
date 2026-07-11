---
name: implement
description: 读取计划文件，按依赖顺序执行每个任务并做任务级验证，最后写实现报告到 reports/<feature>-implementation-report.md。
disable-model-invocation: true
---

# /implement — 执行功能计划

**用法：** `/implement plans/<feature>-plan.md`

读取 `$ARGUMENTS` 处的计划，依序执行每个任务，运行每个任务的验证命令，最后写实现报告。

---

## 流程

### 1. 完整读取计划

打开 `$ARGUMENTS` 指定的计划文件，**完整读完再写任何代码**。
理解所有任务、依赖顺序和验收标准。

### 2. 按依赖顺序执行任务

对每个 Task：

1. **读** 目标文件——不要盲目覆盖。
2. **实现** 改动，遵循计划中的 Pattern 参照。
3. **运行** Task 的 `Validate:` 命令。如果失败，**先修复再继续**。
4. 不允许跳过任务验证去追求速度——跳过的检查就是隐藏的回归。

### 3. 运行完整验证门

所有任务完成后，运行计划「验证门」部分的命令：

```bash
python scripts/validate.py
```

如果失败：修复 → 重跑失败命令 → 重跑完整验证门。
所有命令绿色才算完成。

### 4. 写实现报告

输出到 `reports/<feature>-implementation-report.md`：

```markdown
# Implementation Report: <功能名称>

## 计划
`plans/<feature>-plan.md`

## 完成的任务
| # | 任务 | 状态 | 备注 |
|---|------|------|------|
| 1 | <描述> | DONE | |
| 2 | <描述> | DONE | |

## 修改的文件
- **新建：** `<路径>`
- **修改：** `<路径>`（改动行：N–M）

## 验证门结果
| 命令 | 结果 |
|------|------|
| `python scripts/validate.py` | PASS（N 个测试） |

## 验收标准
- [x] <标准>
- [x] <标准>

## 偏差说明
<与计划的偏差及原因，如无则写「无」>

## 可提交
所有任务完成，验证门绿色。可运行 `/validate` 确认后提交。
```

---

**交接：** 运行 `/validate` 在提交前再次确认完整验证门。

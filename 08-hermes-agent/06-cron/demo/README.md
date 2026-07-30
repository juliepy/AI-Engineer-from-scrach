# Cron Demo · 真源码 Job Store

**不改 Hermes 源码。** 把完整 `hermes-agent` 加到 `PYTHONPATH`，在临时 `HERMES_HOME` 下调用 `cron.jobs`。

对照讲稿：[`../notes/01_job_store.md`](../notes/01_job_store.md)、[`../notes/02_tick_and_run.md`](../notes/02_tick_and_run.md)。

本 demo **只测存储与 schedule 解析**，不跑 `tick()` / `AIAgent`（无需 API Key、无需 gateway）。

---

## 跑法

```bash
cd 06-cron/demo

# 默认会找与 AI_coding_interview 同级的 hermes-agent/
# 找不到时手动指定：
#   set HERMES_AGENT_ROOT=D:\workspace\doc\面试狂魔\人工智能面试题\hermes-agent

python run_cron_jobs.py
```

产物：`exports/cron_jobs/01_report.md`、`00_raw.json`。

依赖：标准 `hermes-agent` 环境即可。五字段 cron 表达式需要本机已装 `croniter`（未装时该条 parse 会记失败，其余 duration / every / ISO 仍通过）。

---

## 调了哪段真源码

| 调用 | 文件（hermes-agent） |
|------|----------------------|
| `parse_schedule` / `create_job` / `list_jobs` / `pause_job` / `get_due_jobs` / `remove_job` | `cron/jobs.py` |
| `JOBS_FILE`（解析到 temp `HERMES_HOME/cron/jobs.json`） | `jobs.py` + `get_hermes_home()` |

教材剪枝对照：[`../hermes_src/cron/`](../hermes_src/cron/)（只读；本 demo **不**从剪枝树 import）。

---

## Call flow

```text
run_cron_jobs.main()
  sys.path ← hermes-agent/
  HERMES_HOME ← tempfile/.hermes
  parse_schedule × 4
  create_job × 2 → jobs.json
  list_jobs / pause_job / get_due_jobs
  remove_job × 2
  → exports/cron_jobs/
```

---

## 真机下一步（可选）

1. `hermes gateway` 跑着时：`hermes cron create --help` / `hermes cron list`  
2. 断点：`cron/scheduler.py` 的 `tick`、`run_job`  
3. 对比 `TERMINAL_ENV` 模块：cron 选 **何时跑**；environments 选 **命令跑在哪**

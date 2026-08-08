# hermes_src — Cron 真源码剪枝

本目录从 Hermes 拷贝 **真实** `cron/` + `tools/cronjob_tools.py`，方便对照 `notes/`。  
缺 gateway / AIAgent / config 等依赖，**不要在这里直接 import 跑**。

| 路径 | 用途 |
|------|------|
| `cron/__init__.py` | 对外 re-export：`create_job` / `tick` / `JOBS_FILE` |
| `cron/jobs.py` | ★ Job 存储：`jobs.json`、`parse_schedule`、`create_job`、`get_due_jobs` |
| `cron/scheduler.py` | ★ 完整调度器（大文件）：`tick` / `run_job` / 投递 |
| `cron/scheduler.TICK_RUN.py` | ★ 教学摘录：toolset 禁用、`run_job` 分支、`tick` 锁 |
| `cron/scheduler_provider.py` | Axis-B：触发器 ABC（builtin vs Chronos 等） |
| `cron/lifecycle_guard.py` | 禁止 cron 作业里跑 gateway 启停命令 |
| `tools/cronjob_tools.py` | ★ Agent 工具：`cronjob(action=…)` + prompt 扫描 |

精读顺序：`jobs.py` → `scheduler.TICK_RUN.py` → `cronjob_tools.py` → `scheduler_provider.py`。

---

## 运行逻辑（源码对照）

本树**不能直接 import 跑**；下图是完整 Hermes 里这些文件如何串起来。

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryTextColor":"#111111","secondaryTextColor":"#111111","tertiaryTextColor":"#111111","lineColor":"#90CAF9","fontSize":"15px"}}}%%
flowchart TB
    IN["cronjob_tools.py<br/>cronjob / hermes cron"] --> PARSE["jobs.parse_schedule()"]
    PARSE --> CREATE["jobs.create_job()"]
    CREATE --> STORE["HERMES_HOME/cron/jobs.json<br/>JOBS_FILE"]

    GW["hermes gateway"] --> TICK["scheduler.tick()<br/>约每 60s · 文件锁"]
    TICK --> DUE["jobs.get_due_jobs()"]
    STORE --> DUE
    DUE --> RUN["scheduler.run_job()"]

    RUN --> BRANCH{"no_agent?"}
    BRANCH -->|是| SCRIPT["跑 script · 写 stdout"]
    BRANCH -->|否| AGENT["AIAgent + prompt<br/>禁交互工具 / skip_memory"]
    SCRIPT --> OUT["cron/output/job_id/"]
    AGENT --> OUT
    OUT --> DEL["投递 Home / origin / local"]

    GUARD["lifecycle_guard.py"] -.->|拦 gateway 启停| AGENT
    PROV["scheduler_provider.py"] -.->|谁触发 tick| TICK

    style IN fill:#90CAF9,stroke:#0D47A1,stroke-width:2px,color:#111111
    style PARSE fill:#BBDEFB,stroke:#1565C0,stroke-width:2px,color:#111111
    style CREATE fill:#BBDEFB,stroke:#1565C0,stroke-width:2px,color:#111111
    style STORE fill:#FFE082,stroke:#F57F17,stroke-width:2px,color:#111111
    style GW fill:#FFCC80,stroke:#E65100,stroke-width:2px,color:#111111
    style TICK fill:#FFAB91,stroke:#BF360C,stroke-width:2px,color:#111111
    style DUE fill:#A5D6A7,stroke:#1B5E20,stroke-width:2px,color:#111111
    style RUN fill:#81C784,stroke:#1B5E20,stroke-width:2px,color:#111111
    style BRANCH fill:#FFF59D,stroke:#F9A825,stroke-width:2px,color:#111111
    style SCRIPT fill:#C5E1A5,stroke:#558B2F,stroke-width:2px,color:#111111
    style AGENT fill:#C5E1A5,stroke:#558B2F,stroke-width:2px,color:#111111
    style OUT fill:#CE93D8,stroke:#6A1B9A,stroke-width:2px,color:#111111
    style DEL fill:#B39DDB,stroke:#6A1B9A,stroke-width:2px,color:#111111
    style GUARD fill:#B0BEC5,stroke:#455A64,stroke-width:2px,color:#111111
    style PROV fill:#B0BEC5,stroke:#455A64,stroke-width:2px,color:#111111
```

一句话：**写入走 `jobs.py`；到期扫描与执行走 `scheduler.py`；Agent 入口是 `cronjob_tools.py`。**

教学摘录优先看 `scheduler.TICK_RUN.py`（`tick` 锁、`run_job` 分支、禁用 toolset）。

---

## 上游对照

上游完整文件：

- https://github.com/NousResearch/hermes-agent/blob/main/cron/jobs.py
- https://github.com/NousResearch/hermes-agent/blob/main/cron/scheduler.py
- https://github.com/NousResearch/hermes-agent/blob/main/tools/cronjob_tools.py

同仓库完整树：[`../../hermes-study/`](../../hermes-study/)（若已同步）或上游 `hermes-agent/cron/`。

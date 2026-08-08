# Cron Demo · 全链路 call flow

**不改 Hermes 源码。** `HERMES_HOME` 指到本 `demo/`，jobs 落在 `demo/cron/jobs.json`。

对照源码图：[`../hermes_src/README.md`](../hermes_src/README.md)

---

## 本 demo 覆盖的链路

```text
cronjob(action='create')         
        │
        ▼
parse_schedule → create_job       ← cron/jobs.py
        │
        ▼
HERMES_HOME/cron/jobs.json
        │
        ▼  （省 gateway；真实环境由 gateway 每 ~60s 调）
tick()                            ← cron/scheduler.py（文件锁）
        │
        ▼
get_due_jobs → run_one_job → run_job
        │
        ├── no_agent=True  → scripts/*.py stdout
        └── no_agent=False → AIAgent（需 RUN_AGENT=True）
        │
        ▼
cron/output/<job_id>/*.md → 投递（deliver=local 只落盘）
```

| 源码节点 | 本 demo |
|----------|---------|
| `cronjob` / `hermes cron` | 直接调 `cronjob(action='create')` |
| `parse_schedule` / `create_job` | 真调用（create 内部完成 parse） |
| gateway 进程 | **省略**；直接 `tick()` |
| `tick` 文件锁 / `get_due_jobs` / `run_job` | 真调用 |
| `no_agent` 脚本分支 | 默认跑通 |
| `AIAgent` 分支 | 顶部 `RUN_AGENT = True` |
| Home / origin 投递 | `deliver=local`（故意不发聊天） |

默认 `SCHEDULE="1m"`：**create 后轮询 `tick()`，约等 1 分钟才跑 `say_hello.py`**（Hermes 最短时长就是 1m）。  
顶部设 `RUN_NOW = True` 才用「已过去 ISO」立刻执行（调试用）。

---

## 跑法

顶部开关（`run_cron_flow.py`）：

```python
SCHEDULE = "every 1m"  # 每 1 分钟
REPEAT = 5             # 共 5 次后自动删除
POLL_SECONDS = 5
RUN_NOW = False        # True：首跑立刻到期
RUN_AGENT = False      # True：再跑 AIAgent 分支
```

```bash
cd 06-cron/demo

# 找不到 hermes-agent 时：
#   set HERMES_AGENT_ROOT=D:\workspace\doc\面试狂魔\人工智能面试题\hermes-agent

python run_cron_flow.py
```

日志极简：#1 cronjob(create) → #2 jobs.json → #3 tick（`1/5`…）→ #4 output → #5 agent（可选）。

---

## 文件

```text
demo/
├── run_cron_flow.py     # ★ 唯一主入口
├── scripts/say_hello.py # no_agent 脚本
├── cron/jobs.json       # 跑完后 once job 通常已被移除
└── cron/output/<id>/    # run_job 落盘
```

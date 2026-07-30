# 06-cron · notes 讲解顺序

本目录讲 **Hermes 真源码** `cron/` + `tools/cronjob_tools.py`。按编号读。

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryTextColor":"#111111","secondaryTextColor":"#111111","tertiaryTextColor":"#111111","lineColor":"#90CAF9","fontSize":"15px"}}}%%
flowchart TB
    N01["01 jobs.json / parse_schedule"] --> N02["02 tick / run_job"]
    N02 --> N03["03 cronjob tool + CLI"]
    N03 --> N04["04 hardening + delivery"]
    N01 -.-> SRC["hermes_src/cron/*.py"]

    style N01 fill:#90CAF9,stroke:#0D47A1,stroke-width:2px,color:#111111
    style N02 fill:#BBDEFB,stroke:#1565C0,stroke-width:2px,color:#111111
    style N03 fill:#FFE082,stroke:#F57F17,stroke-width:2px,color:#111111
    style N04 fill:#FFCC80,stroke:#E65100,stroke-width:2px,color:#111111
    style SRC fill:#A5D6A7,stroke:#1B5E20,stroke-width:2px,color:#111111
```

| 顺序 | 文件 | 真源码 | 读完应能回答 |
|------|------|--------|--------------|
| **01** | [`01_job_store.md`](./01_job_store.md) | `jobs.py` | `jobs.json` 存什么？四种 schedule？ |
| **02** | [`02_tick_and_run.md`](./02_tick_and_run.md) | `scheduler.TICK_RUN.py` | tick 锁 / at-most-once / no_agent？ |
| **03** | [`03_cronjob_tool.md`](./03_cronjob_tool.md) | `cronjob_tools.py` | Agent / CLI / `/cron` 怎么进同一套 API？ |
| **04** | [`04_hardening_and_delivery.md`](./04_hardening_and_delivery.md) | scheduler + jobs | 为什么 skip_memory？投递到哪？ |

最短路径：`01` → `02` → `04`，再扫 `03` 看工具面。

上级：[`../README.md`](../README.md)

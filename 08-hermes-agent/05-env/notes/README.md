# 05-env · notes 讲解顺序

本目录讲 **Hermes 真源码** `tools/environments/` + `terminal_tool` 工厂。按编号读。

```mermaid
%%{init: {"theme":"base","themeVariables":{"primaryTextColor":"#111111","secondaryTextColor":"#111111","tertiaryTextColor":"#111111","lineColor":"#90CAF9","fontSize":"15px"}}}%%
flowchart TB
    N01["01 BaseEnvironment"] --> N02["02 local vs docker"]
    N02 --> N03["03 remote + file_sync"]
    N03 --> N04["04 factory / TERMINAL_ENV"]
    N01 -.-> SRC["hermes_src/tools/environments/*.py"]

    style N01 fill:#90CAF9,stroke:#0D47A1,stroke-width:2px,color:#111111
    style N02 fill:#BBDEFB,stroke:#1565C0,stroke-width:2px,color:#111111
    style N03 fill:#FFE082,stroke:#F57F17,stroke-width:2px,color:#111111
    style N04 fill:#FFCC80,stroke:#E65100,stroke-width:2px,color:#111111
    style SRC fill:#A5D6A7,stroke:#1B5E20,stroke-width:2px,color:#111111
```

| 顺序 | 文件 | 真源码 | 读完应能回答 |
|------|------|--------|--------------|
| **01** | [`01_base_environment.md`](./01_base_environment.md) | `base.py` | spawn-per-call + snapshot 是什么？ |
| **02** | [`02_local_vs_docker.md`](./02_local_vs_docker.md) | `local.py` / `docker.py` | 隔离差在哪？security args？ |
| **03** | [`03_remote_and_cloud.md`](./03_remote_and_cloud.md) | `ssh.py` / `file_sync.py` / 云 | bind vs sync？ |
| **04** | [`04_factory_and_config.md`](./04_factory_and_config.md) | `terminal_tool.FACTORY.py` | 用户怎么切后端？ |

最短路径：`01` → `02` → `04`，再扫 `03` 对比表。

上级：[`../README.md`](../README.md)

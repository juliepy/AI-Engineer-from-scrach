# hermes_src — Environments 真源码剪枝

本目录从 Hermes 拷贝 **真实** `tools/environments/` 实现，方便对照 `notes/`。  
缺 terminal 工具其余依赖、credential 模块等，**不要在这里直接 import 跑**。

可跑 demo：[`../demo/`](../demo/README.md)。精读顺序：`base.py` → `local.py` / `docker.py` → `file_sync.py` → 远程/云 → `terminal_tool.FACTORY.py`。

---

## 各 Env 文件

```text
hermes_src/tools/
├── terminal_tool.FACTORY.py   # 按 TERMINAL_ENV 创建对应 Environment（工厂摘录）
├── env_probe.py               # 探测当前后端能力；不是执行后端
└── environments/
    ├── __init__.py            # 包入口；导出 BaseEnvironment
    ├── base.py                # BaseEnvironment：统一 execute / snapshot / wait / cleanup
    ├── local.py               # LocalEnvironment：本机 bash，无隔离
    ├── docker.py              # DockerEnvironment：容器内执行，有隔离与安全参数
    ├── singularity.py         # SingularityEnvironment：HPC Singularity/Apptainer 容器
    ├── ssh.py                 # SSHEnvironment：远程机 SSH 执行（常用 ControlMaster）
    ├── file_sync.py           # FileSyncManager：SSH/Modal/Daytona 同步本机文件到远端
    ├── modal.py               # ModalEnvironment：Modal SDK 直连云沙箱
    ├── managed_modal.py       # ManagedModalEnvironment：经托管 gateway 的 Modal
    ├── modal_utils.py         # Modal 两种模式的共用执行逻辑
    └── daytona.py             # DaytonaEnvironment：Daytona 云开发环境
```

说明：

- 对外接口统一：`execute(command) → {output, returncode}`；差异主要在各文件的 `_run_bash` 与生命周期。
- Docker / Singularity 多靠 bind 挂载看文件；SSH / Modal / Daytona 多靠 `file_sync.py`。
- 选哪个后端由 `TERMINAL_ENV` + `terminal_tool.FACTORY.py` 决定，不改主循环。

更细对比：[`../notes/`](../notes/README.md)（01→04）。

---

## LocalEnvironment · execute call flow

对照：`local.py`（`LocalEnvironment`）+ `base.py`（`execute`）。

```text
LocalEnvironment(cwd, timeout)
  └─ init_session()                    # base.py：login bash 导出 env/functions/aliases → snapshot

env.execute(command)
  ├─ _before_execute()                 # local：空实现（不需要 file_sync）
  ├─ _prepare_command()                # sudo 改写（若有 SUDO_PASSWORD）
  ├─ _rewrite_compound_background()    # 默认防 `A && B &` 陷阱
  ├─ _wrap_command()                   # source snapshot → cd cwd → eval 命令 → CWD marker
  ├─ _run_bash()                       # local.py：Popen([bash, "-c", wrapped])
  ├─ _wait_for_process()               # base.py：读 stdout、timeout、interrupt
  └─ _update_cwd(result)               # local：从临时文件读回 cwd
  → {"output": str, "returncode": int}

env.cleanup()                          # 清理 snapshot 等会话资源
```

本地差异点只在 `_run_bash`（本机 `Popen`）和 cwd 用临时文件回写；公共流程都在 `base.py` 的 `execute()`。

---

## 上游对照

- https://github.com/NousResearch/hermes-agent/blob/main/tools/environments/base.py
- https://github.com/NousResearch/hermes-agent/blob/main/tools/terminal_tool.py

同仓库完整树：[`../../hermes-study/tools/environments/`](../../hermes-study/tools/environments/)

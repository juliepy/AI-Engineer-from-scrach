# hermes_src — Environments 真源码剪枝

本目录从 Hermes 拷贝 **真实** `tools/environments/` 实现，方便对照 `notes/`。  
缺 terminal 工具其余依赖、credential 模块等，**不要在这里直接 import 跑**。

| 路径 | 用途 |
|------|------|
| `tools/environments/base.py` | ★ `BaseEnvironment`：snapshot / wrap / wait / execute |
| `tools/environments/local.py` | 主机 `Popen(bash)`，无隔离 |
| `tools/environments/docker.py` | 容器 + `_BASE_SECURITY_ARGS` |
| `tools/environments/ssh.py` | SSH ControlMaster + FileSyncManager |
| `tools/environments/modal.py` / `managed_modal.py` / `modal_utils.py` | Modal 云沙箱 |
| `tools/environments/daytona.py` | Daytona |
| `tools/environments/singularity.py` | HPC Singularity |
| `tools/environments/file_sync.py` | SSH/Modal/Daytona 文件同步（Docker 用 bind，一般不用） |
| `tools/environments/__init__.py` | 包说明；指向 `terminal_tool._create_environment` |
| `tools/terminal_tool.FACTORY.py` | ★ 摘录：`_get_env_config` + `_create_environment` |
| `tools/env_probe.py` | 探测当前后端能力 |

精读顺序：`base.py` → `local.py` / `docker.py` → `file_sync.py` → `terminal_tool.FACTORY.py`。

上游完整文件：

- https://github.com/NousResearch/hermes-agent/blob/main/tools/environments/base.py
- https://github.com/NousResearch/hermes-agent/blob/main/tools/terminal_tool.py

同仓库完整树：[`../../hermes-study/tools/environments/`](../../hermes-study/tools/environments/)

# 03 · 远程 / 云后端 + file_sync（真源码）

> 对照：  
> - [`../hermes_src/tools/environments/file_sync.py`](../hermes_src/tools/environments/file_sync.py)  
> - `ssh.py` / `modal.py` / `managed_modal.py` / `daytona.py` / `singularity.py`  
> 下一篇：[`04_factory_and_config.md`](./04_factory_and_config.md)

---

## 一句话

远程与云后端 **仍然** 是 `BaseEnvironment` 子类。多出来的核心问题是：**主机上的 skills / credentials / cache 怎么出现在远端**。

`file_sync.py` 文件头写死了分工：

> Used by **SSH, Modal, and Daytona**.  
> **Docker and Singularity use bind mounts** and don't need this.

---

## 后端一览

| 文件 | 类 | 文件可见性 | 场景 |
|------|-----|------------|------|
| `local.py` | `LocalEnvironment` | host 直读 | 调试 |
| `docker.py` | `DockerEnvironment` | bind / volumes | 隔离执行 |
| `singularity.py` | `SingularityEnvironment` | bind / overlay | HPC |
| `ssh.py` | `SSHEnvironment` | **FileSyncManager** | 远程机 |
| `modal.py` / `managed_modal.py` | Modal 系列 | **FileSyncManager** | 云沙箱 |
| `daytona.py` | `DaytonaEnvironment` | **FileSyncManager** | 云开发环境 |
| `modal_utils.py` | `BaseModalExecutionEnvironment` | 共用 Modal 逻辑 | — |

云/SDK 后端常用 `_ThreadedProcessHandle`（在 `base.py`），把阻塞 `exec` 包成可 `poll`/`kill` 的句柄，这样 `_wait_for_process` 不用改。

---

## `FileSyncManager` 精读

| 符号 | 作用 |
|------|------|
| `iter_sync_files` | 枚举要同步的 host→remote 路径（credentials / skills / cache） |
| `FileSyncManager.sync` | mtime+size 变更检测、upload、删除、bulk tar |
| `BaseEnvironment._before_execute` | 远程后端 override：每次 execute 前 sync |

凭证路径通常 **upload-only**，避免远端改写密钥后回写污染主机。

```text
execute()
  └─ _before_execute()
       └─ FileSyncManager.sync(...)
            ├─ 变更 → upload / bulk_upload
            └─ 删除 → remote delete
```

---

## SSH 额外点（`ssh.py`）

- ControlMaster 复用连接  
- socket 路径用 `user@host:port` 的 hash，避开 macOS `sun_path` 长度限制  
- 探测 remote home 后，把 `/root/.hermes` 风格路径 remap 到真实 home  

---

## 面试会讲

端云协同 ≠ 两套 Agent。  
是 **同一 ABC + 不同 `_run_bash` + 不同「文件到位」策略（bind vs sync）**。

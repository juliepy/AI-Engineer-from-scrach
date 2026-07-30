# 02 · local.py vs docker.py（真源码）

> 对照：  
> - [`../hermes_src/tools/environments/local.py`](../hermes_src/tools/environments/local.py) → `LocalEnvironment`  
> - [`../hermes_src/tools/environments/docker.py`](../hermes_src/tools/environments/docker.py) → `DockerEnvironment`、`_BASE_SECURITY_ARGS`  
> 下一篇：[`03_remote_and_cloud.md`](./03_remote_and_cloud.md)

---

## 一句话

两者都继承 `BaseEnvironment`。差别几乎全在 **`_run_bash` + 资源生命周期 + 安全参数**：local 是主机进程；docker 是容器 exec，并默认 cap-drop / tmpfs / no-new-privileges。

---

## 对比表

| 维度 | `LocalEnvironment` | `DockerEnvironment` |
|------|--------------------|---------------------|
| `_run_bash` | `Popen([bash, "-c", …])` | `docker exec`（容器内 bash） |
| 隔离 | 无 | 容器 namespace + 能力收紧 |
| 启动 | 毫秒级 | 需镜像/容器；已有容器则 exec 较快 |
| 文件 | 直接 host FS | volumes / workspace bind |
| 密钥 | `_sanitize_subprocess_env` 挡 provider key | `forward_env` / `docker_env` 显式转发 |
| 清理 | 清 snapshot 等 | stop/rm 容器（可 persist） |
| 适用 | 本机调试 | 不可信代码、可复现沙箱 |

---

## local.py 精读

搜这些符号：

| 符号 | 干什么 |
|------|--------|
| `LocalEnvironment.__init__` | 设 cwd 后立刻 `init_session()` |
| `_find_bash` / `_find_shell` | 找可用 shell（含 Windows Git Bash） |
| `_sanitize_subprocess_env` / `hermes_subprocess_env` | 子进程 env 消毒 |
| `_resolve_safe_cwd` | cwd 被 `rm -rf` 后恢复，防会话楔死 |
| `get_temp_dir` | Windows 用 `{HERMES_HOME}/cache/terminal`，避免 `/tmp` 与空格路径 |

---

## docker.py 精读

### 默认安全参数（直接记）

在 `docker.py` 搜 `_BASE_SECURITY_ARGS`：

```text
--cap-drop ALL
--cap-add DAC_OVERRIDE, CHOWN, FOWNER
--security-opt no-new-privileges
--tmpfs /tmp (nosuid)
--tmpfs /var/tmp (noexec,nosuid)
```

相关：

| 符号 | 干什么 |
|------|--------|
| `_build_security_args` | 拼 base + `/run` tmpfs；非 host-user 再加 SETUID/SETGID |
| `_image_uses_init_entrypoint` | s6-overlay 镜像：`/run` 要 `exec`，且避免双重 `--init` |
| `_cgroup_limits_available` | 决定能否加 `--cpus` / `--memory` / `--pids-limit` |
| `reap_orphan_containers` | 进程被杀后回收带 Hermes label 的孤儿容器 |
| `DockerEnvironment._run_bash` | 真正 `docker exec …` |

---

## 环境 vs 沙箱

| 概念 | 问题 | 源码落点 |
|------|------|----------|
| Environment | 命令跑在哪？ | `local.py` / `docker.py` / … |
| Sandbox hardening | 够不够安全？ | docker 的 security args；大纲模块五再谈 seccomp / MicroVM |

面试句式：**同一 `execute()`；换 `_run_bash` 就从「本机调试」切到「容器隔离」。**

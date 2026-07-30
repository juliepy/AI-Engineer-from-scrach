# 01 · BaseEnvironment（真源码）

> 对照：[`../hermes_src/tools/environments/base.py`](../hermes_src/tools/environments/base.py)  
> 下一篇：[`02_local_vs_docker.md`](./02_local_vs_docker.md)

---

## 一句话

Hermes 所有执行后端共用 `BaseEnvironment`：**统一 `execute()`**，子类只实现 `_run_bash()` 和 `cleanup()`。

文件头注释写明模型：

> Unified spawn-per-call model: every command spawns a fresh `bash -c`.  
> Session snapshot (env vars, functions, aliases) is captured once and re-sourced.  
> CWD persists via stdout markers (remote) or a temp file (local).

---

## 关键类型

| 符号 | 作用 |
|------|------|
| `ProcessHandle` | Protocol：`poll` / `kill` / `wait` / `stdout` / `returncode` |
| `_ThreadedProcessHandle` | Modal/Daytona 等无真实 Popen 时的适配器 |
| `BaseEnvironment` | ABC：snapshot + wrap + wait + execute |
| `get_sandbox_dir()` | host 侧沙箱根：`TERMINAL_SANDBOX_DIR` 或 `{HERMES_HOME}/sandboxes` |

子类必须实现：

```python
def _run_bash(self, cmd_string, *, login=False, timeout=120, stdin_data=None) -> ProcessHandle: ...
def cleanup(self): ...
```

---

## `execute()` 真调用链

打开 `base.py` 里的 `execute()`，顺序是：

```text
execute(command)
  ├─ _before_execute()          # SSH/Modal/Daytona：触发 FileSyncManager
  ├─ _prepare_command()         # sudo 改写（调 terminal_tool）
  ├─ _rewrite_compound_background()  # 默认防 A && B & 陷阱
  ├─ _wrap_command()            # source snapshot → cd → eval → CWD marker
  ├─ _run_bash(...)             # ★ 唯一后端差异主入口
  ├─ _wait_for_process(...)     # 共享：interrupt / timeout / drain / activity
  └─ _update_cwd(result)        # local 读文件；远程解析 __HERMES_CWD_*__
  → {"output": str, "returncode": int}
```

---

## 精读点（建议在源码里搜）

1. **`init_session`**：login shell 导出 env/functions/aliases → 原子 `mv` 写 snapshot（防并发撕文件）。  
2. **`_wrap_command`**：`source snap` 后 `eval` 用户命令，再 dump env、打 CWD marker。  
3. **`_wait_for_process`**：`select`/`os.read` 非阻塞 drain；`is_interrupted()`；`KeyboardInterrupt` 时必杀子进程（防 setsid 孤儿）。  
4. **`_stdin_mode`**：`"pipe"` vs `"heredoc"`（SDK 后端）。  

---

## 和主循环的关系

主循环 / `handle_function_call` **不**直接选 docker/ssh。  
它们调 `terminal` 工具 → `terminal_tool` 持有 env 实例 → 最终落到这里的 `execute()`。

下一篇对比 **local（无隔离）** 与 **docker（`_BASE_SECURITY_ARGS`）** 两个 `_run_bash` 实现。

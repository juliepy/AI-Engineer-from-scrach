# 04 · Core dump

场景：C/C++/部分原生扩展崩溃，需要堆栈；CI 里「偶发 Segmentation fault」。

## 1. 整条链路

```
进程收到致命信号（SIGSEGV/SIGABRT…）
  → 内核按 core_pattern 写 core 文件（受 ulimit -c 限制）
  → 用 gdb / lldb 加载「可执行文件 + core」看 bt
```

任一环关闭都「看不到 core」。

## 2. 打开落盘

```bash
ulimit -c                    # 当前 shell：0 表示禁止
ulimit -c unlimited          # 当前 shell 打开
# 持久（视发行版）：
# /etc/security/limits.conf → * soft core unlimited
```

落盘位置模板：

```bash
cat /proc/sys/kernel/core_pattern
# 例：core          → 当前目录 core 或 core.<pid>
# 例：|/usr/share/apport/apport %p …  → 管道给 apport（Ubuntu）
```

临时改（需 root，重启可能丢）：

```bash
sudo sysctl -w kernel.core_pattern=/tmp/core-%e-%p
```

## 3. 复现小例子

```bash
# 见 demos/demo_coredump.sh
# 故意空指针 → SIGSEGV → 生成 core → gdb bt
```

## 4. 用 gdb 看堆栈

```bash
gdb ./crash_app /tmp/core-crash_app-12345
(gdb) bt
(gdb) bt full
(gdb) info threads
(gdb) frame 2
(gdb) list
```

无符号时先确认编译带 `-g`，且 core 与二进制是同一次构建。

## 5. 容器 / CI 注意点

| 点 | 说明 |
|----|------|
| 默认 `ulimit -c 0` | Job 脚本里显式 `ulimit -c unlimited` |
| `core_pattern` 指向宿主机路径 | 容器内写不进或写到错误处 |
| 管道式 pattern（apport/systemd-coredump） | 容器里可能没有该 helper |
| 产物要归档 | `artifacts: paths: [core*, crash_app]` |

systemd 管理的 core：

```bash
coredumpctl list
coredumpctl info <pid>
coredumpctl gdb <pid>
```

## 6. 面试一句话

「先确认 `ulimit -c` 和 `core_pattern`，再保证带调试符号的同版本二进制，用 `gdb bt` 取栈；容器环境要单独开 ulimit 并挂载可写目录。」

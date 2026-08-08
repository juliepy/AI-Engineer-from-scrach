#!/bin/bash
# 进程排查演示：拉起子进程 → ps/pgrep → 资源 → 优雅结束
set -euo pipefail

echo "=== 1) 后台 sleep，记录 PID ==="
sleep 120 &
pid=$!
echo "child pid=$pid"

echo
echo "=== 2) pgrep / ps 定位 ==="
pgrep -af "sleep 120" || true
ps -o pid,ppid,stat,etime,cmd -p "$pid"

echo
echo "=== 3) /proc 快照 ==="
tr '\0' ' ' < /proc/$pid/cmdline; echo
grep -E '^(Name|State|VmRSS|Threads):' /proc/$pid/status || true

echo
echo "=== 4) kill -0 探测，再 SIGTERM ==="
if kill -0 "$pid" 2>/dev/null; then
    echo "still alive, sending SIGTERM"
    kill -15 "$pid"
    wait "$pid" 2>/dev/null || true
    echo "exited"
else
    echo "already gone"
fi

echo
echo "OK — 对照 01-进程排查.md"

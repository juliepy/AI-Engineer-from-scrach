#!/bin/bash
# 后台任务：& / jobs / nohup 风格重定向 / wait
set -euo pipefail

tmpdir=$(mktemp -d)
trap 'rm -rf "$tmpdir"; jobs -p | xargs -r kill 2>/dev/null' EXIT
log="$tmpdir/bg.log"

echo "=== 1) 后台任务 + jobs ==="
(sleep 2; echo done-at-$(date +%T)) >"$log" 2>&1 &
bg_pid=$!
jobs -l || true
echo "bg_pid=$bg_pid log=$log"

echo
echo "=== 2) wait 等待结束 ==="
wait "$bg_pid"
echo "log content: $(cat "$log")"

echo
echo "=== 3) nohup 风格（忽略 HUP 的演示：trap 子 shell）==="
(
  trap '' HUP
  sleep 1
  echo "survived-hup-demo" >>"$log"
) &
wait || true
tail -n 2 "$log"

echo
echo "=== 4) 多任务 wait ==="
sleep 1 &
sleep 1 &
wait
echo "all children done"

echo
echo "OK — 对照 06-后台任务.md"

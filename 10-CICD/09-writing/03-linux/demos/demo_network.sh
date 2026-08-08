#!/bin/bash
# 网络调试演示：本机监听 / 连通 / DNS（不依赖外网也可看本地段）
set -euo pipefail

echo "=== 1) 本机监听端口（前 15）==="
if command -v ss >/dev/null 2>&1; then
    ss -lnt | head -15
else
    echo "ss 不可用，跳过"
fi

echo
echo "=== 2) 本机 loopback TCP 探测 ==="
if timeout 2 bash -c 'echo >/dev/tcp/127.0.0.1/22' 2>/dev/null; then
    echo "127.0.0.1:22 open (or accepted)"
else
    echo "127.0.0.1:22 closed/filtered（正常：未必开 ssh）"
fi

echo
echo "=== 3) DNS：解析 localhost ==="
getent hosts localhost || true
if command -v dig >/dev/null 2>&1; then
    dig +short localhost || true
fi

echo
echo "=== 4) curl 本机（若有）==="
if command -v curl >/dev/null 2>&1; then
    curl -sS -o /dev/null -w "http://127.0.0.1/ -> %{http_code} time=%{time_total}\n" \
        --connect-timeout 2 http://127.0.0.1/ || echo "本机 80 无服务（可忽略）"
else
    echo "无 curl，跳过"
fi

echo
echo "=== 5) 路由表头 ==="
ip route 2>/dev/null | head -5 || route -n 2>/dev/null | head -5 || true

echo
echo "OK — 对照 02-网络调试.md"

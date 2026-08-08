#!/bin/bash
# Core dump 演示：编译空指针程序 → 开 ulimit → 崩 → 找 core → gdb bt（若有 gdb）
set -euo pipefail

if ! command -v cc >/dev/null 2>&1 && ! command -v gcc >/dev/null 2>&1; then
    echo "无 gcc/cc，跳过编译演示" >&2
    exit 0
fi
CC=$(command -v gcc || command -v cc)

tmpdir=$(mktemp -d)
trap 'rm -rf "$tmpdir"' EXIT
cd "$tmpdir"

cat > crash.c <<'EOF'
#include <stdio.h>
int main(void) {
    int *p = NULL;
    printf("about to crash\n");
    return *p; /* SIGSEGV */
}
EOF

$CC -g -O0 -o crash crash.c
echo "binary=$tmpdir/crash"

# 尽量让 core 落到当前目录
ulimit -c unlimited || true
# 若有权限，写到当前目录（失败则忽略）
sysctl -w kernel.core_pattern=core.%e.%p >/dev/null 2>&1 || true

echo "ulimit -c = $(ulimit -c)"
echo "core_pattern = $(cat /proc/sys/kernel/core_pattern 2>/dev/null || echo '?')"

set +e
./crash
ec=$?
set -e
echo "crash exit=$ec (期望非 0)"

echo
echo "=== 查找 core ==="
ls -la core* 2>/dev/null || echo "未生成 core（WSL/容器常禁用或 pattern 为管道）。对照 04-core-dump.md 查 ulimit 与 core_pattern。"

if command -v gdb >/dev/null 2>&1; then
    core=$(ls core* 2>/dev/null | head -1 || true)
    if [ -n "${core:-}" ]; then
        echo
        echo "=== gdb bt ==="
        gdb -batch -ex bt --args ./crash "$core" 2>/dev/null || gdb -batch -ex bt ./crash "$core"
    fi
else
    echo "无 gdb，跳过 bt"
fi

echo
echo "OK — 对照 04-core-dump.md"

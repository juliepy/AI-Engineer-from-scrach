#!/bin/bash
#
# grep 专项：检索 / 计数 / 上下文 / 反选 / 找文件
# 用法: bash grep_scan.sh [日志目录]
# 默认: ../02-log-process
#
# 覆盖: grep -c/-E/-n/-C/-v/-rl/-h，多文件与 access.log 5xx

dir=${1:-../02-log-process}

if [ ! -d "$dir" ]; then
    echo "目录不存在: $dir" >&2
    exit 1
fi

echo "=== 1) 多模式检索：ERROR|WARN（app 日志）==="
# -E：扩展正则；-h：多文件不带文件名前缀
grep -hE ' (ERROR|WARN) ' "$dir"/app-*.log 2>/dev/null | head -5
echo "...(仅展示前 5 行)"
echo

echo "=== 2) 计数：各 app 文件 ERROR 行数 ==="
# 多文件时 grep -c 会输出 文件名:次数
grep -c ERROR "$dir"/app-*.log 2>/dev/null || true
echo

echo "=== 3) 上下文：某关键词前后各 1 行（-n 行号 + -C1）==="
sample=$(ls "$dir"/app-*.log 2>/dev/null | head -1)
if [ -n "$sample" ]; then
    grep -n -C1 'connection refused\|quota exceeded\|timeout' "$sample" 2>/dev/null | head -20 \
        || grep -n -C1 ERROR "$sample" | head -12
fi
echo

echo "=== 4) 反选：access.log 非 200/304（空格框住状态码列）==="
if [ -f "$dir/access.log" ]; then
    # 列数据用空格「框」状态码，避免误伤字节数里的 200
    echo "非 200/304 条数: $(grep -vcE ' (200|304) ' "$dir/access.log")"
    grep -nE ' 5[0-9]{2} ' "$dir/access.log" | head -5
    echo "5xx 条数: $(grep -cE ' 5[0-9]{2} ' "$dir/access.log")"
else
    echo "(无 access.log，跳过)"
fi
echo

echo "=== 5) 找文件：含 connection refused 的文件名（-rl）==="
# -r 递归；-l 只打印文件名
grep -rl --include='*.log' --include='*.jsonl' 'connection refused' "$dir" 2>/dev/null || true

echo
echo "OK"

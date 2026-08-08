#!/bin/bash
#
# E6：日志目录巡检报表
# 用法: bash log_report.sh <日志目录>
# 示例: bash log_report.sh ../02-log-process

dir=$1

if [ -z "$dir" ]; then
    echo "用法: $0 <日志目录>" >&2
    exit 1
fi

if [ ! -d "$dir" ]; then
    echo "目录不存在: $dir" >&2
    exit 1
fi

printf "%-22s %8s %8s %8s\n" "FILE" "LINES" "ERROR" "WARN"
for f in "$dir"/app-*.log; do
    [ -f "$f" ] || continue
    total=$(wc -l < "$f")
    errors=$(grep -c ERROR "$f" || true)
    warns=$(grep -c WARN "$f" || true)
    printf "%-22s %8d %8d %8d\n" "$(basename "$f")" "$total" "$errors" "$warns"
done

echo
echo "ERROR Top3 模块:"
# -h：多文件时去掉文件名前缀，否则 awk 列会错位
grep -h ERROR "$dir"/app-*.log 2>/dev/null \
    | awk '{print $4}' \
    | sort | uniq -c | sort -nr | head -3

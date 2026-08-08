#!/bin/bash
#
# E3 套路：定长时间戳字符串比较（比 fork date 简单得多）
# 用法: bash time_filter.sh <日志文件> [开始] [结束]
# 示例: bash time_filter.sh ../02-log-process/app-2026-08-02.log \
#          "2026-08-02 09:00:00" "2026-08-02 11:00:00"

file=${1:?用法: $0 <日志文件> [开始时间] [结束时间]}
start=${2:-"2026-08-02 09:00:00"}
end=${3:-"2026-08-02 11:00:00"}

if [ ! -f "$file" ]; then
    echo "文件不存在: $file" >&2
    exit 1
fi

# $0 整行以 "YYYY-MM-DD HH:MM:SS" 开头时，字典序 == 时间序
awk -v s="$start" -v e="$end" '$0 >= s && $0 <= e' "$file"

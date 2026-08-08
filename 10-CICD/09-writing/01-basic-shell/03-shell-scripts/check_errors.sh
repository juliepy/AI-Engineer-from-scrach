#!/bin/bash
#
# F3：CI 日志巡检 —— 错误数超阈值就让流水线变红
# 用法: bash check_errors.sh <日志目录> [阈值]
# 示例: bash check_errors.sh ../02-log-process
#       bash check_errors.sh ../02-log-process 100

# $1 必填：日志目录；未传则打印用法并以非 0 退出（${var:?msg}）
dir=${1:?用法: $0 <日志目录> [阈值]}
# $2 可选：ERROR 数量阈值，默认 5（${var:-default}）
threshold=${2:-5}

# 统计目录下 app-*.log 中含 ERROR 的行数
# -h：多文件时不打印文件名；2>/dev/null：无匹配文件时不刷屏；tr -d：去掉 wc 的空格
count=$(grep -h ERROR "$dir"/app-*.log 2>/dev/null | wc -l | tr -d ' ')
echo "ERROR 总数: $count (阈值 $threshold)"

# 超阈值：打印 Top3 高频错误片段，并以 exit 1 让 CI 失败（变红）
if [ "$count" -gt "$threshold" ]; then
    echo "--- Top3 错误 ---"
    # 抽出 msg="..." 或 status=xxx → 计数排序 → 取前 3
    grep -h ERROR "$dir"/app-*.log \
        | sed -E 's/^.*(msg="[^"]*"|status=[a-z]+).*$/\1/' \
        | sort | uniq -c | sort -nr | head -3
    exit 1
fi

# 未超阈值：成功退出，CI 继续
echo "OK"
exit 0

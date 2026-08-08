#!/bin/bash
#
# 综合管道：时间窗 + 级别 + 字段清洗 + TopN（grep|awk|sed|sort）
# 用法: bash pipeline_filter.sh [日志目录] [开始] [结束] [级别正则]
# 示例: bash pipeline_filter.sh ../02-log-process \
#          "2026-08-01 09:00:00" "2026-08-01 12:00:00" "ERROR|WARN"
#
# 覆盖: 日志筛选流水线、工具串联、参数默认值

dir=${1:-../02-log-process}
start=${2:-"2026-08-01 09:00:00"}
end=${3:-"2026-08-02 23:59:59"}
level_re=${4:-"ERROR|WARN"}

if [ ! -d "$dir" ]; then
    echo "目录不存在: $dir" >&2
    exit 1
fi

echo "目录=$dir"
echo "时间=[$start , $end]"
echo "级别=~ $level_re"
echo

echo "=== A) 时间窗内的级别命中行（awk 时间 + grep -E 级别）==="
# 先按时间裁剪，再按级别筛 —— 大文件时先缩小再精筛
awk -v s="$start" -v e="$end" '$0 >= s && $0 <= e' "$dir"/app-*.log 2>/dev/null \
    | grep -E " ($level_re) " \
    | head -15
echo

echo "=== B) 同上 → sed 抽 msg/status → Top5 ==="
awk -v s="$start" -v e="$end" '$0 >= s && $0 <= e' "$dir"/app-*.log 2>/dev/null \
    | grep -E " ($level_re) " \
    | sed -E 's/^.*(msg="[^"]*"|status=[a-z0-9_]+).*$/\1/' \
    | sort | uniq -c | sort -nr | head -5
echo

echo "=== C) access.log：时间无关，筛 4xx/5xx 并格式化 ==="
if [ -f "$dir/access.log" ]; then
    # $9 状态码；$7 URL；$11 耗时
    awk '$9 >= 400 {
        printf "%-3s %-18s %6.3fs\n", $9, $7, $11
    }' "$dir/access.log" | head -10
else
    echo "(无 access.log，跳过)"
fi
echo

echo "=== D) JSONL（有 jq 用 jq；否则 grep 兜底，并提示别用 grep 切 JSON）==="
jsonl="$dir/agent_trace.jsonl"
alt="../01-log-process/agent.jsonl"
[ -f "$jsonl" ] || jsonl=$alt
if [ -f "$jsonl" ]; then
    if command -v jq >/dev/null 2>&1; then
        # jq 负责挑列，shell 负责展示
        jq -r 'select(.status=="error" or .level=="ERROR")
            | [.ts // .time // "?", .session_id // .agent_id // "?", .error // .msg // "?"]
            | @tsv' "$jsonl" 2>/dev/null | head -8 \
            || jq -r 'select(.level=="ERROR") | [.time,.module,.msg] | @tsv' "$jsonl" | head -8
    else
        echo "未安装 jq，临时用 grep（笔试应优先 jq）："
        grep -E '"level":"ERROR"|"status":"error"' "$jsonl" | head -5
    fi
else
    echo "(无 jsonl 样例，跳过)"
fi

echo
echo "OK"

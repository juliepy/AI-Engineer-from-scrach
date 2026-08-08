#!/bin/bash
#
# awk 专项：按列过滤 / 分组聚合 / 均值 / 多文件
# 用法: bash awk_stats.sh [日志目录]
# 默认: ../02-log-process
#
# 覆盖: $n 取列、条件过滤、-v、-F、{c[k]++} END、外接 sort

dir=${1:-../02-log-process}

if [ ! -d "$dir" ]; then
    echo "目录不存在: $dir" >&2
    exit 1
fi

echo "=== 1) 按级别分组计数（多文件 app-*.log，跨文件累加）==="
# 模板：{c[key]++} END{for(k in c) print ...} —— 笔试背这个
awk '{c[$3]++} END{for(k in c) print c[k], k}' "$dir"/app-*.log 2>/dev/null \
    | sort -nr
echo

echo "=== 2) 只打印 ERROR 行的 日期 + 模块 ==="
awk '$3=="ERROR" {print $1, $4}' "$dir"/app-*.log 2>/dev/null | head -8
echo

echo "=== 3) 统计 tool=xxx 调用次数（字段扫描）==="
awk '{
    for (i = 1; i <= NF; i++)
        if ($i ~ /^tool=/) {
            sub(/^tool=/, "", $i)
            c[$i]++
        }
}
END { for (k in c) print c[k], k }
' "$dir"/app-*.log 2>/dev/null | sort -nr
echo

echo "=== 4) access.log：状态码直方图 + /api/chat 平均耗时 ==="
if [ -f "$dir/access.log" ]; then
    echo "-- 状态码 --"
    awk '{c[$9]++} END{for(k in c) print c[k], k}' "$dir/access.log" | sort -nr

    echo '-- /api/chat 平均耗时（秒，$11）--'
    # -v 可注入外部变量；此处直接写死路径作演示
    awk '$7=="/api/chat" {
        s += $11; n++
    }
    END {
        if (n) printf "count=%d avg=%.3f\n", n, s / n
        else print "no /api/chat rows"
    }' "$dir/access.log"

    echo "-- Top3 IP（sort|uniq 写法 vs awk 数组，二选一都会）--"
    awk '{print $1}' "$dir/access.log" | sort | uniq -c | sort -nr | head -3
else
    echo "(无 access.log，跳过)"
fi
echo

echo "=== 5) 时间窗过滤（与 time_filter.sh 同思路，定长字符串比较）==="
awk -v s="2026-08-01 09:00:00" -v e="2026-08-01 10:00:00" \
    '$0 >= s && $0 <= e' "$dir"/app-2026-08-01.log 2>/dev/null | head -5
echo "...(09:00~10:00 前 5 行)"

echo
echo "OK"

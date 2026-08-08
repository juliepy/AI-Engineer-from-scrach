#!/bin/bash
#
# sed 专项：清洗 / 提取 / 脱敏 / 行区间
# 用法: bash sed_clean.sh [日志文件]
# 默认: ../02-log-process/app-2026-08-01.log
#
# 覆盖: sed -E 替换、捕获组 \1、删行、 -n 'a,bp'、IP 脱敏

file=${1:-../02-log-process/app-2026-08-01.log}

if [ ! -f "$file" ]; then
    echo "文件不存在: $file" >&2
    exit 1
fi

echo "=== 1) 压缩连续空白（不改原文件，管道 dry-run）==="
# BRE: s/  */ /g   ERE: s/ +/ /g
sed -E 's/ +/ /g' "$file" | head -3
echo

echo "=== 2) 提取字段：整行 → 只留 msg=\"...\" 或 status=xxx ==="
# 与 check_errors.sh 同套路：捕获组 + \1 反向引用
grep ERROR "$file" \
    | sed -E 's/^.*(msg="[^"]*"|status=[a-z0-9_]+).*$/\1/'
echo

echo "=== 3) 从 access 行提取方括号时间（若同目录有 access.log）==="
access="$(dirname "$file")/access.log"
if [ -f "$access" ]; then
    grep -E ' 5[0-9]{2} ' "$access" \
        | sed -E 's/^.*\[([^]]+)\].*$/\1/' \
        | head -5
else
    echo "(无 access.log，跳过)"
fi
echo

echo "=== 4) IP 末段脱敏：10.0.0.1 → 10.0.0.x ==="
if [ -f "$access" ]; then
    # ^ 锚定行首，避免误伤正文里的其他数字
    sed -E 's/^([0-9]+\.[0-9]+\.[0-9]+)\.[0-9]+/\1.x/' "$access" | head -3
else
    echo "(无 access.log，跳过)"
fi
echo

echo "=== 5) 只打印第 1~5 行（-n + p；不加 -n 会全文+重复）==="
sed -n '1,5p' "$file"
echo

echo "=== 6) 删空行 / 注释行演示（stdin 样例）==="
printf 'keep\n\n# comment\n  \nalso keep\n' \
    | sed -E '/^\s*$/d; /^\s*#/d'

echo
echo "OK"
# 提示：真要改文件用 sed -i.bak 's/old/new/g' file（先管道验证再 -i）

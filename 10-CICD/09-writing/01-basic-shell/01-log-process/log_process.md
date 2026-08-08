# 日志处理 + JSON 解析（笔试高频）

> 目标：日志处理 + JSON 日志解析，只抓笔试高频，剔除冷门语法。
>
> 本目录数据：
> - `agent.log` —— 文本应用日志（grep / sed / awk）
> - `agent.jsonl` —— JSON Lines（jq）
>
> 做完本节 → 去 `../02-log-process/` 刷 40 题。

---

## 1. 基础工具：grep / sed / awk

### 1.1 grep（文本检索）

```bash
# 基础匹配
grep "ERROR" agent.log

# 精确匹配 JSON 字符串（避免部分命中）——用 agent.jsonl
grep '"level":"ERROR"' agent.jsonl

# -c 统计行数；-v 反向匹配；-i 忽略大小写
grep -c '"level":"ERROR"' agent.jsonl

# 带上下文 / 行号（题库 A3）
grep -n -A1 -B1 "timeout" agent.log

# 只列文件名（题库 A6）
grep -rl "connection refused" .

# 扩展正则
grep -E "ERROR|WARN" agent.log
```

| 选项 | 含义 |
| --- | --- |
| `-c` | 统计匹配行数 |
| `-v` | 反向匹配（排除） |
| `-i` | 忽略大小写 |
| `-n` | 显示行号 |
| `-A` / `-B` / `-C` | 后/前/前后 N 行上下文 |
| `-l` | 只打印文件名 |
| `-r` | 递归目录 |
| `-E` | 扩展正则（`\|` 分组等） |
| `-h` | 多文件时去掉文件名前缀 |

### 1.2 sed（文本替换、清洗）

```bash
# 多个连续空格 → 单个空格（笔试高频）
sed 's/  */ /g' agent.log
# 或扩展正则
sed -E 's/ +/ /g' agent.log

# 删除空行
sed '/^$/d' file.txt

# 只打印第 17~20 行
sed -n '17,20p' agent.log

# 替换文本，直接修改文件并留备份
sed -i.bak 's/old/new/g' file.txt
```

### 1.3 awk（分组统计、按列处理，重中之重）

```bash
# 按空格分割，打印第 3 列（级别）
awk '{print $3}' agent.log

# 条件过滤
awk '$3=="ERROR" {print $1,$4}' agent.log

# 分组计数模板（笔试万能模板）
awk '{count[$3]++} END{for(k in count) print k,count[k]}' agent.log

# sort + uniq 计数组合（降序）
awk '{print $3}' agent.log | sort | uniq -c | sort -nr

# 对齐输出
awk '$3=="ERROR" {printf "%-12s %-16s %s\n", $1, $2, $0}' agent.log
```

---

## 2. jq（AI Agent 岗位最高优先级）

JSON 日志必备。不要用 `grep` 切割 JSON，转义字符极易翻车，笔试优先 `jq`。

数据文件：`agent.jsonl`（每行一条 JSON）。

```bash
# 取出字段（纯文本，不要引号）
jq -r '.agent_id' agent.jsonl

# 条件筛选：只保留 ERROR 日志
jq 'select(.level=="ERROR")' agent.jsonl

# 多字段提取，自定义分隔符
jq -r 'select(.level=="ERROR")|[.time,.agent_id,.msg]|join("|")' agent.jsonl

# 缺字段兜底（真实日志常缺字段）
jq -r '.tags // [] | join(",")' agent.jsonl

# 聚合要先 -s（slurp 成数组）
jq -s 'group_by(.module) | map({module:.[0].module, n:length})' agent.jsonl
```

更完整的 jq 场景（嵌套 tokens / models.json）在 `../02-log-process/agent_trace.jsonl`。

---

## 3. Shell 脚本基础：文件遍历、变量判断

```bash
# for 循环遍历日志文件
for f in ./*.log; do
  echo "$f"
done

# 读取文件每一行
while IFS= read -r line; do
  echo "$line"
done < agent.log

# 入参获取 $1 $2；空值判断
module=$1
if [ -z "$module" ]; then
  echo "参数不能为空" >&2
  exit 1
fi

# 目录存在判断
if [ ! -d "$1" ]; then
  echo "目录不存在" >&2
  exit 1
fi

# 字符串大小对比（时间字符串比较，定长时间戳可直接比）
if [[ "$ts" > "2026-08-02 09:00:00" ]]; then
  echo "after threshold"
fi

# 管道 | ；输出重定向 > 覆盖，>> 追加
```

| 符号 / 写法 | 含义 |
| --- | --- |
| `\|` | 管道，前一个命令输出传给下一个 |
| `>` / `>>` | 覆盖 / 追加写入 |
| `>&2` | 错误信息打到 stderr |
| `$1` `$2` | 脚本第 1、2 个入参 |
| `[ -z "$var" ]` | 判断变量为空 |
| `[ -d "$path" ]` | 判断目录存在 |
| `${1:?用法}` | 参数为空则报错退出 |
| `${2:-5}` | 参数未给时用默认值 5 |

可运行脚本范例见 `../03-shell-scripts/`。

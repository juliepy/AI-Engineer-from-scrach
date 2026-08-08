# Shell 日志处理实战题库 —— 答案与讲解

配套题目：`shell_日志实战题库.md`。所有命令在本目录下执行。

**验证说明**

- A / B / C / E / F 区的命令**全部在 Linux（WSL）上真跑过**，下面贴的输出就是实际输出。
- D 区（jq）：本机没装 jq，命令按 jq 1.6/1.7 语法手写，**期望结果用等价的 Python 计算过**，数值可信。
  装好 jq 后自己对一遍：`sudo apt install -y jq`。

---

## A. grep：检索与计数

### A1 统计 5xx 请求数

```bash
grep -cE 'HTTP/1\.1" 5[0-9]{2} ' access.log
```

```
7
```

要点：

- `-c` 只输出计数，不要再套 `| wc -l`（多一个进程）。
- `.` 在正则里是任意字符，`HTTP/1.1` 必须写成 `HTTP/1\.1`。
- 模式里带上 `HTTP/1.1" ` 前缀和末尾空格，是为了**锁死"状态码那一列"**。
  只写 `grep -cE '5[0-9]{2}'` 会把响应字节数 `1532`、耗时里的数字全匹配进去。

反例对照：`grep -cE '5[0-9]{2}'` 在本文件返回 **11**（真实值 7），多出来的 4 条是字节数/耗时里恰好出现 5xx 数字的行。

### A2 三个文件各自的 ERROR 数

```bash
grep -c ERROR app-*.log
```

```
app-2026-08-01.log:4
app-2026-08-02.log:8
app-2026-08-03.log:2
```

要点：grep 接**多个文件**时会自动加 `文件名:` 前缀。单文件想强制带文件名用 `-H`，多文件想去掉用 `-h`（B7/F3 会用到 `-h`）。

### A3 带上下文和行号

```bash
grep -n -C1 'quota exceeded' app-2026-08-02.log
```

```
17-2026-08-02 10:19:02 WARN  [rate-limiter] session=s-2004 msg="approaching quota" used=970 limit=1000
18:2026-08-02 10:19:30 ERROR [rate-limiter] session=s-2004 msg="quota exceeded" used=1001 limit=1000
19-2026-08-02 11:02:44 INFO  [agent-core] session=s-2005 msg="agent started" model=gpt-4o
```

要点：

- `-A n` 后 n 行 / `-B n` 前 n 行 / `-C n` 前后各 n 行。
- 看分隔符能区分匹配行和上下文行：命中行是 `18:`（冒号），上下文行是 `17-`（减号）。
- 排查线上问题基本都是 `grep -n -C5 ERROR`，光看一行 ERROR 没有用。

### A4 排除 200 和 304

```bash
grep -vcE ' (200|304) ' access.log
```

```
15
```

要点：

- `-v` 反选，`-c` 计数，两个可以合写成 `-vc`。
- **为什么模式两边要留空格**：不留空格的话，字节数 `2001`、耗时 `0.200` 里的 `200` 都会被当成状态码，导致本该保留的行被误排除。空格把这一列"框"起来，是纯 grep 处理列数据的常用土办法。
- 更严谨的写法是交给 awk 按列判断：`awk '$9!=200 && $9!=304' access.log | wc -l`。列数据能用 awk 就别硬用 grep。

### A5 精确统计 status=error

```bash
# 错误写法
grep -c 'error' agent_trace.jsonl      # 26 —— 全中了

# 正确写法
grep -c '"status":"error"' agent_trace.jsonl
```

```
8
```

要点：`error` 这个词在每行里出现太多次——`"error":null` 字段每行都有，`"error":"upstream 502"` 也含它。所以必须连 key 一起匹配。

这题的真正答案其实是：**JSON 别用 grep**。正解见 D 区：

```bash
jq -r 'select(.status=="error")' agent_trace.jsonl | ...
# 或
jq -s '[.[] | select(.status=="error")] | length' agent_trace.jsonl
```

面试时说出"JSON 用 grep 是错的，应该用 jq"，比写对 grep 更加分。

### A6 列出包含关键字的文件名

```bash
grep -rl 'connection refused' .
```

```
./agent_trace.jsonl
./app-2026-08-01.log
./app-2026-08-02.log
./shell_日志实战题库.md
```

要点：

- `-r` 递归，`-l`（小写 L）只打印文件名，`-L` 是反过来"不包含的文件"。
- 注意题库 md 自己也被搜进去了。实战里要限定范围：

```bash
grep -rl --include='*.log' --include='*.jsonl' 'connection refused' .
```

---

## B. awk：分组统计与格式化

### B1 打印两列

```bash
awk '{print $1, $9}' access.log
```

```
10.0.0.1 200
10.0.0.2 200
10.0.0.1 200
172.16.5.9 200
10.0.0.3 500
...
```

要点：`print $1, $9` 中的逗号会输出 `OFS`（默认空格）；写成 `print $1 $9` 会直接拼在一起变成 `10.0.0.1200`。这是最常见的低级错误。

### B2 状态码分组计数（万能模板）

```bash
awk '{c[$9]++} END{for(k in c) print k, c[k]}' access.log | sort -k2 -nr
```

```
200 34
500 4
404 3
401 3
502 2
504 1
429 1
403 1
304 1
```

要点：

- **`{c[key]++} END{for(k in c) print k, c[k]}` 这个模板背下来**，B3/B6/B7/B8/B9/F1 全是它的变体。
- awk 的 `for (k in c)` 遍历顺序**不保证**，所以想要排序必须外接 `sort`。
- `sort -k2 -nr`：按第 2 列、按数值、倒序。

### B3 Top3 IP（两种写法）

```bash
# (a) awk 数组：注意 print 时把次数放前面，方便直接 sort -nr
awk '{c[$1]++} END{for(k in c) print c[k], k}' access.log | sort -nr | head -3

# (b) 经典管道流水线
awk '{print $1}' access.log | sort | uniq -c | sort -nr | head -3
```

```
12 10.0.0.1
10 10.0.0.2
8 10.0.0.3
```

要点：

- `uniq -c` **必须先 sort**，因为它只能合并"相邻"的重复行。这是笔试高频扣分点。
- 数据量大时 (a) 更快：(a) 是一次扫描 + 哈希；(b) 要做全量排序，O(n log n)。
- 但 (b) 好写好记，面试口述时说清"数据大用 awk 数组"就够了。

### B4 /api/chat 请求数与平均耗时（平均值陷阱）

```bash
awk '$7=="/api/chat" {s+=$11; n++} END{printf "count=%d avg=%.3f\n", n, s/n}' access.log
```

```
count=19 avg=2.455
```

**这题的重点是解释这个 2.455s 是假的。**

19 条请求里有 2 条是 30s 的超时。排除 5xx 之后：

```bash
awk '$7=="/api/chat" && $9<400 {s+=$11; n++} END{printf "count=%d avg=%.3fs\n", n, s/n}' access.log
```

```
count=15 avg=0.805s
```

平均值被少数极端值拉高了 3 倍。面试标准答法：

1. **平均值对长尾不敏感**，看耗时要看 **P95 / P99 或中位数**；
2. 超时/失败请求要么单独统计，要么先剔除，不能和成功请求混在一起算；
3. 顺手给出 P95 的算法（排序后取第 95% 位）：

```bash
awk '$7=="/api/chat" {print $11}' access.log | sort -n | \
  awk '{a[NR]=$1} END{printf "p50=%.3f p95=%.3f max=%.3f\n", a[int(NR*0.5)], a[int(NR*0.95)], a[NR]}'
```

### B5 慢请求对齐输出

```bash
awk '$11>1 {printf "%-22s %-14s %6.3f\n", substr($4,2), $7, $11}' access.log
```

```
02/Aug/2026:10:01:10   /api/embed      1.204
02/Aug/2026:10:07:55   /api/chat       1.512
02/Aug/2026:10:11:28   /api/embed     30.001
02/Aug/2026:10:17:12   /api/embed      1.088
02/Aug/2026:10:18:55   /api/chat       2.443
02/Aug/2026:10:23:31   /api/chat       1.205
02/Aug/2026:10:30:15   /api/chat      30.002
02/Aug/2026:10:31:47   /api/embed      1.377
02/Aug/2026:11:05:38   /api/chat       1.844
02/Aug/2026:11:13:02   /api/embed     60.001
02/Aug/2026:11:20:19   /api/chat       1.033
02/Aug/2026:11:31:05   /api/chat       2.109
02/Aug/2026:11:45:33   /api/embed      1.150
```

要点：

- `substr($4,2)` 从第 2 个字符开始截，去掉前导 `[`（awk 的字符串下标从 **1** 开始，不是 0）。
- `printf` 不自动换行，必须自己写 `\n`；`print` 才自动换行。
- `%-22s` 左对齐、`%6.3f` 右对齐保留 3 位——报表左边文字左对齐、右边数字右对齐，才看得清。
- `$11>1` 里 `$11` 会被自动当数字比较；如果字段带单位（如 `1.2s`）就得先 `substr`/`+0` 处理。

### B6 每个 IP 的流量（MB）

```bash
awk '{b[$1]+=$10} END{for(k in b) printf "%-12s %8.2f MB\n", k, b[k]/1024/1024}' access.log | sort -k2 -nr
```

```
172.16.5.9       0.18 MB
10.0.0.1         0.02 MB
192.168.1.7      0.01 MB
10.0.0.6         0.00 MB
...
```

要点：`b[$1]+=$10` 是"分组求和"，和 B2 的 `c[$1]++`（分组计数）是同一个模板的两种形态。计数 = 累加 1，求和 = 累加某列。

### B7 多文件日志级别统计

```bash
awk '{c[$3]++} END{for(k in c) print c[k], k}' app-*.log | sort -nr
```

```
33 INFO
14 ERROR
7 WARN
3 DEBUG
```

要点：

- awk 天生支持多文件：`app-*.log` 由 shell 展开成多个参数，awk 顺序读完，数组是**跨文件累积**的。
- 想按文件分别统计，用内置变量 `FILENAME`：`{c[FILENAME"|"$3]++}`。
- 相关内置变量：`NR`（全局行号）、`FNR`（当前文件行号）、`NF`（字段数）。`NR==FNR` 是双文件关联的经典技巧。

### B8 统计 tool 调用次数

```bash
awk -F'tool=' 'NF>1 {split($2, a, " "); c[a[1]]++} END{for(k in c) print c[k], k}' app-*.log | sort -nr
```

```
5 code_exec
4 web_search
2 terminal
2 read_file
2 browser_navigate
1 patch
1 delegate_task
```

要点：

- `-F'tool='` 用**字符串**做分隔符，切完 `$2` 就是 `web_search status=ok cost_ms=812`。
- `NF>1` 是关键：不含 `tool=` 的行切不开，`NF` 仍为 1，必须跳过，否则 `$2` 是空串会统计出一个空 key。
- `split($2, a, " ")` 再按空格切，`a[1]` 就是工具名。
- 另一种通用写法（不依赖字段位置，扫全行找 `k=v`）：

```bash
awk '{for(i=1;i<=NF;i++) if($i ~ /^tool=/) {sub(/^tool=/,"",$i); c[$i]++}} END{for(k in c) print c[k], k}' app-*.log | sort -nr
```

### B9 按小时统计请求数

```bash
awk '{split($4, a, ":"); c[a[2]]++} END{for(k in c) printf "%s:00  %d\n", k, c[k]}' access.log | sort
```

```
09:00  2
10:00  35
11:00  10
12:00  3
```

要点：`$4` 是 `[02/Aug/2026:09:58:12`，按 `:` 切开后 `a[1]="[02/Aug/2026"`、`a[2]="09"`、`a[3]="58"`。取 `a[2]` 即小时。做"每分钟"就再拼上 `a[3]`（见 F1）。

### B10 暴力破解告警（401 ≥ 3 次）

```bash
awk '$9==401 {c[$1]++} END{for(k in c) if(c[k]>=3) print k, c[k]}' access.log
```

```
10.0.0.4 3
```

要点：过滤条件写在 `END` 块里，先累加完再判断阈值。这是"告警类"题目的标准结构：**扫描聚合 → END 里比阈值 → 命中才输出**。F3 的 CI 巡检脚本是同一个思路。

---

## C. sed：清洗与替换

### C1 压缩连续空格

```bash
sed -E 's/ +/ /g' app-2026-08-01.log     # 推荐
sed 's/  */ /g'   app-2026-08-01.log     # 基础正则等价写法
```

```
2026-08-01 09:00:01 INFO [agent-core] session=s-1001 msg="agent started" model=gpt-4o
2026-08-01 09:00:04 DEBUG [tool-runner] session=s-1001 tool=web_search args_len=42
...
```

要点：

- **BRE vs ERE**：基础正则里 `+` 不是元字符，所以必须写 `  *`（一个空格 + 零或多个空格）或转义成 `\+`。加 `-E` 用扩展正则就能直接写 `+`，更好读。
- `g` 标志表示一行内替换所有匹配，不加只替换每行第一处。

### C2 删除空行和注释行

```bash
sed -E '/^\s*$/d; /^\s*#/d' somefile
```

要点：

- `/pattern/d` 删除匹配行；多条命令用 `;` 分隔或者写多个 `-e`。
- `^\s*$` 要匹配"只有空白的行"，光写 `^$` 漏掉纯空格行。
- grep 等价写法：`grep -vE '^\s*$|^\s*#'`。**删行用 grep -v 通常比 sed 更直观**，sed 的强项是替换。

### C3 从 5xx 行提取时间

```bash
grep -E ' 5[0-9]{2} ' access.log | sed -E 's/^.*\[([^]]+)\].*$/\1/'
```

```
02/Aug/2026:10:01:10 +0800
02/Aug/2026:10:11:28 +0800
02/Aug/2026:10:18:55 +0800
02/Aug/2026:10:30:15 +0800
02/Aug/2026:10:31:47 +0800
02/Aug/2026:11:13:02 +0800
02/Aug/2026:11:31:05 +0800
```

要点：

- `\(...\)`（BRE）/ `(...)`（ERE）捕获，`\1` 反向引用第一组——**sed 提取子串的唯一手段**。
- `[^]]+` 意思是"除 `]` 外的任意字符若干个"。`]` 放在字符类第一个位置不用转义。
- 用 `.*` 包住整行再整体替换，才能达到"只留捕获组"的效果。
- 更省事的做法其实是 `awk '{print substr($4,2)}'`，按列取比写正则稳。

### C4 IP 脱敏

```bash
sed -E 's/^([0-9]+\.[0-9]+\.[0-9]+)\.[0-9]+/\1.x/' access.log
```

```
10.0.0.x - - [02/Aug/2026:09:58:12 +0800] "GET /api/chat HTTP/1.1" 200 1532 0.312 "-" "curl/8.4.0"
10.0.0.x - - [02/Aug/2026:09:59:01 +0800] "GET /health HTTP/1.1" 200 12 0.002 "-" "kube-probe/1.29"
...
```

要点：

- 锚定 `^` 只改行首的 IP，避免误伤日志正文里出现的其他 IP/版本号。
- 前三段整体捕获成 `\1`，最后一段丢掉换成 `x`。
- 实战延伸：脱敏手机号 `s/(1[3-9][0-9])[0-9]{4}([0-9]{4})/\1****\2/g`、脱敏邮箱、脱敏 token —— 日志脱敏是运维/平台岗的高频真实需求。

### C5 打印指定行范围

```bash
sed -n '17,20p' access.log
```

```
10.0.0.4 - - [02/Aug/2026:10:15:31 +0800] "POST /api/login HTTP/1.1" 401 88 0.008 "-" "curl/8.4.0"
10.0.0.4 - - [02/Aug/2026:10:15:36 +0800] "POST /api/login HTTP/1.1" 401 88 0.007 "-" "curl/8.4.0"
10.0.0.4 - - [02/Aug/2026:10:15:41 +0800] "POST /api/login HTTP/1.1" 401 88 0.009 "-" "curl/8.4.0"
10.0.0.4 - - [02/Aug/2026:10:15:47 +0800] "POST /api/login HTTP/1.1" 200 312 0.121 "-" "curl/8.4.0"
```

要点：

- **不加 `-n` 会怎样**：sed 默认打印每一行，`p` 又打印一次，结果是全文输出 + 17~20 行重复两遍。`-n` 关掉默认输出，配合 `p` 才是"只打印选中行"。
- 大文件想取中间几行，`sed -n '17,20p;21q' file` 加个 `q` 提前退出，不用读完整个文件。
- 等价：`awk 'NR>=17 && NR<=20' access.log`。

### C6 原地替换 + 备份

```bash
# 1. 先 dry-run 确认影响面
sed 's/gpt-4o/gpt-5/g' app-2026-08-02.log | grep -c 'gpt-5'    # 2

# 2. 在副本上操作，别直接改题库数据
cp app-2026-08-02.log /tmp/t.log
sed -i.bak 's/gpt-4o/gpt-5/g' /tmp/t.log
ls /tmp/t.log*        # /tmp/t.log  /tmp/t.log.bak
```

要点：

- `-i` 原地修改；`-i.bak` 会先存一份 `原文件名.bak`。**没有备份的 `-i` 是不可逆的**，线上误操作没有后悔药。
- macOS/BSD 的 sed 里 `-i` 必须跟参数（`-i ''`），GNU sed 可以只写 `-i`。跨平台脚本要注意。
- 规范流程：**先不带 `-i` 跑一遍看输出 → 确认条数 → 再加 `-i.bak`**。

⚠️ 如果你已经直接改了 `app-2026-08-02.log`，用 `mv app-2026-08-02.log.bak app-2026-08-02.log` 还原。

---

## D. jq：JSON 日志解析

> 下面的命令按 jq 1.6/1.7 语法编写；输出值由等价的 Python 计算验证。
> 先装 jq：`sudo apt install -y jq`，然后自己跑一遍对照。

### D1 打印所有 tool

```bash
jq -r '.tool' agent_trace.jsonl
```

```
web_search
web_search
read_file
...
```

要点：

- **jq 天然支持 JSON Lines**：不加 `-s` 时，jq 会把输入当成"一个接一个的 JSON 值"逐个处理，正好对应每行一条日志。
- `-r`（raw output）去掉字符串两边的引号。要把结果喂给 awk/sort 时**必须加 `-r`**，否则引号会混进字段里。

### D2 非成功记录，压成一行

```bash
jq -c 'select(.status != "success")' agent_trace.jsonl
```

共 10 条：

```json
{"ts":"2026-08-02T08:31:12Z","session_id":"s-2001",...,"status":"error","error":"net::ERR_CONNECTION_REFUSED"}
{"ts":"2026-08-02T08:31:40Z","session_id":"s-2001",...,"status":"error","error":"net::ERR_CONNECTION_REFUSED"}
{"ts":"2026-08-02T09:47:20Z","session_id":"s-2002",...,"status":"error","error":"exit code 127: command not found"}
{"ts":"2026-08-02T10:11:28Z","session_id":"s-2003",...,"status":"error","error":"upstream 502"}
{"ts":"2026-08-02T10:11:33Z","session_id":"s-2003",...,"status":"error","error":"upstream 502"}
{"ts":"2026-08-02T10:18:55Z","session_id":"s-2004",...,"status":"timeout","error":"tool timed out after 30s"}
{"ts":"2026-08-02T10:19:30Z","session_id":"s-2004",...,"status":"error","error":"quota exceeded"}
{"ts":"2026-08-02T12:30:41Z","session_id":"s-2006",...,"status":"error","error":"vector store connection refused"}
{"ts":"2026-08-03T09:20:11Z","session_id":"s-3002",...,"status":"error","error":"SyntaxError: invalid syntax"}
{"ts":"2026-08-03T13:41:30Z","session_id":"s-3003",...,"status":"timeout","error":"upstream 504"}
```

要点：

- `select(条件)` 是 jq 的过滤器：条件为真就把当前输入原样传下去，为假就输出**空**（不是 null，是啥都不输出）。等价于 SQL 的 WHERE。
- `-c`（compact）一条一行，方便 `wc -l` 或后续管道；不加会格式化成多行缩进。
- 注意 `error` 和 `timeout` 是两种不同状态，所以用 `!= "success"` 而不是 `== "error"`——**统计失败率时漏掉 timeout 是最常见的口径错误**。

### D3 error 记录四列输出

```bash
jq -r 'select(.status=="error") | [.ts, .session_id, .tool, .error] | join(" | ")' agent_trace.jsonl
```

```
2026-08-02T08:31:12Z | s-2001 | browser_navigate | net::ERR_CONNECTION_REFUSED
2026-08-02T08:31:40Z | s-2001 | browser_navigate | net::ERR_CONNECTION_REFUSED
2026-08-02T09:47:20Z | s-2002 | terminal | exit code 127: command not found
2026-08-02T10:11:28Z | s-2003 | web_search | upstream 502
2026-08-02T10:11:33Z | s-2003 | web_search | upstream 502
2026-08-02T10:19:30Z | s-2004 | code_exec | quota exceeded
2026-08-02T12:30:41Z | s-2006 | memory_search | vector store connection refused
2026-08-03T09:20:11Z | s-3002 | code_exec | SyntaxError: invalid syntax
```

要点：

- `[.a, .b] | join(" | ")` 先构造数组再拼字符串。`join` 要求元素是字符串/数字，遇到 null 会当空串。
- 想喂给 awk 就换成 `@tsv`（制表符分隔，最安全，因为字段内容里几乎不会有 Tab）：

```bash
jq -r 'select(.status=="error") | [.ts,.session_id,.tool,.error] | @tsv' agent_trace.jsonl
```

- **`|` 在 jq 里就是管道**，语义和 shell 一致：左边的输出作为右边的输入。

### D4 按 tool 分组计数

```bash
# (a) 纯 jq
jq -s -r 'group_by(.tool) | map({tool: .[0].tool, n: length}) | sort_by(-.n) | .[] | "\(.n) \(.tool)"' agent_trace.jsonl

# (b) jq 只负责取字段，统计交给 shell（更好写、更常用）
jq -r '.tool' agent_trace.jsonl | sort | uniq -c | sort -nr
```

```
8 web_search
4 terminal
4 code_exec
3 read_file
2 browser_navigate
2 patch
2 delegate_task
1 memory_search
```

要点：

- **`-s`（slurp）是 jq 的核心开关**：把所有输入**吞成一个大数组**再处理。凡是需要跨行聚合（group_by / add / length / max_by / sort_by）就必须加 `-s`，否则 jq 一行一行独立处理，聚合不起来。
- `group_by(.tool)` 要求先按 key 排序——jq 内部会自动排，不用自己 sort。它返回的是"数组的数组"，所以取组名要写 `.[0].tool`。
- `\(...)` 是字符串插值，等价于 Python 的 f-string。
- 实战里 (b) 更常用：**jq 负责"从 JSON 里挑列"，sort/uniq/awk 负责"统计"**，各司其职。

### D5 token 总消耗

```bash
jq -s 'map(.tokens.prompt + .tokens.completion) | add' agent_trace.jsonl
```

```
51070
```

拆开看：

```bash
jq -s '{prompt: (map(.tokens.prompt) | add), completion: (map(.tokens.completion) | add)}' agent_trace.jsonl
# {"prompt": 41640, "completion": 9430}
```

要点：

- 嵌套字段直接用 `.a.b` 点下去。字段可能不存在时用 `.a.b // 0` 兜底。
- `map(f)` = 对数组每个元素求 f；`add` = 数组求和（空数组返回 `null`，不是 0，注意兜底：`add // 0`）。
- `map(.x) | add` 这个组合 = SQL 的 `SUM(x)`，背下来。

### D6 最慢的一条 + 平均耗时

```bash
jq -s -r 'max_by(.latency_ms) | "\(.tool) \(.latency_ms)"' agent_trace.jsonl
# web_search 60000

jq -s '[.[].latency_ms] | add / length' agent_trace.jsonl
# 5176.692307692308
```

要点：

- `max_by(.f)` / `min_by(.f)` 返回**整条记录**（不是字段值），所以后面还能继续取 `.tool`。
- `[.[].latency_ms]` 把所有值收集成数组；`add / length` = 平均值。
- 同 B4 的陷阱：这个 5176ms 的均值被 30s / 60s 两条超时严重拉高。看 P95：

```bash
jq -s '[.[].latency_ms] | sort | .[(length*0.95|floor)]' agent_trace.jsonl
```

### D7 缺字段处理（重点）

```bash
# (a) 找出缺 tags 的记录
jq -r 'select(has("tags") | not) | .ts' agent_trace.jsonl
```

```
2026-08-03T18:09:01Z
```

```bash
# (b) 打印所有 tags，缺字段输出空串
jq -r '(.tags // []) | join(",")' agent_trace.jsonl
```

最后三行：

```
subagent
fs,write
            <- 空行，缺 tags 的那条
```

要点（面试爱问）：

- `has("k")` 判断 key 是否存在（对象用 key，数组用下标）。`| not` 取反。
- **`//` 是"备选运算符"**：左边为 `null` 或 `false` 时取右边。`.tags // []` 就是"没有 tags 就当空数组"。
  注意它对 `false` 也生效，判断布尔字段时要小心。
- `?` 是错误抑制：`.tags[]?` 遇到类型不对不报错而是跳过。
- 三者区别：
  - `.tags` 缺字段 → 输出 `null`（不报错）
  - `.tags | join(",")` 缺字段 → **报错** `null (null) cannot be joined`
  - `(.tags // []) | join(",")` → 输出空串 ✅
- 真实日志里字段缺失/为 null 是常态，**写 jq 不做兜底 = 脚本在生产环境随机崩**。这是 D 区最实用的一题。

### D8 enabled provider 下的所有模型

```bash
jq -r '.providers[] | select(.enabled) | .models[].id' models.json
```

```
gpt-4o
gpt-4o-mini
o3-mini
claude-3-5-sonnet
claude-3-haiku
```

要点：

- `.providers[]` 把数组**展开成多个输出**（不是返回数组），之后每个元素独立往下走。
- 展开可以套娃：`.models[].id` 是在每个 provider 内部再展开一层。
- `select(.enabled)` 直接用布尔字段当条件，不用写 `== true`。
- 结果不含 deepseek 的两个模型（`enabled: false`），可以自己去掉 select 对比一下（共 7 个）。

### D9 每个 provider 的模型数量

```bash
jq -r '.providers[] | "\(.name) \(.models|length)"' models.json
```

```
openai 3
anthropic 2
deepseek 2
```

要点：`length` 是多态的——数组返回元素数、字符串返回字符数、对象返回 key 数、null 返回 0。

### D10 最贵的模型

```bash
jq -r '[.providers[].models[]] | max_by(.price_out) | .id' models.json
```

```
claude-3-5-sonnet
```

要点：

- **`[ ... ]` 把展开的多个输出重新收集成一个数组**——这是 jq 里"拍平嵌套"的标准手法。`.providers[].models[]` 展开出 7 个模型对象，外面套 `[]` 变成长度 7 的数组，才能用 `max_by`。
- 想连价格一起看：`... | max_by(.price_out) | "\(.id) \(.price_out)"` → `claude-3-5-sonnet 15`。
- Top3 最贵：`[.providers[].models[]] | sort_by(-.price_out) | .[:3][] | .id`。

### D11 导出 CSV（带表头）

```bash
jq -s -r '["ts","session_id","tool","status","latency_ms","error"],
          (.[] | select(.status != "success") | [.ts,.session_id,.tool,.status,.latency_ms,.error])
          | @csv' agent_trace.jsonl
```

```csv
"ts","session_id","tool","status","latency_ms","error"
"2026-08-02T08:31:12Z","s-2001","browser_navigate","error",5120,"net::ERR_CONNECTION_REFUSED"
"2026-08-02T08:31:40Z","s-2001","browser_navigate","error",5210,"net::ERR_CONNECTION_REFUSED"
"2026-08-02T09:47:20Z","s-2002","terminal","error",180,"exit code 127: command not found"
"2026-08-02T10:11:28Z","s-2003","web_search","error",2050,"upstream 502"
"2026-08-02T10:11:33Z","s-2003","web_search","error",1980,"upstream 502"
"2026-08-02T10:18:55Z","s-2004","code_exec","timeout",30000,"tool timed out after 30s"
"2026-08-02T10:19:30Z","s-2004","code_exec","error",150,"quota exceeded"
"2026-08-02T12:30:41Z","s-2006","memory_search","error",3010,"vector store connection refused"
"2026-08-03T09:20:11Z","s-3002","code_exec","error",402,"SyntaxError: invalid syntax"
"2026-08-03T13:41:30Z","s-3003","web_search","timeout",60000,"upstream 504"
```

要点：

- **表头只打印一次的关键是 `-s`**：slurp 之后整个输入只是"一个值"，`["ts",...]` 这个常量数组自然只产生一次输出。不加 `-s` 的话每行都会带一个表头。
- `A, (B) | @csv` 的优先级：jq 里 `|` 优先级**低于** `,`，所以等价于 `(A, B) | @csv`——表头和每行数据都各自过一遍 `@csv`。
- `@csv` 会自动给字符串加引号、转义内部引号；数字不加引号。比自己 `join(",")` 安全得多（字段里有逗号就废了）。
- 同族：`@tsv` `@json` `@base64` `@uri` `@sh`（`@sh` 用来安全拼 shell 命令）。

### D12 Top3 错误信息

```bash
# 组合写法（推荐，好记）
jq -r '.error | select(. != null)' agent_trace.jsonl | sort | uniq -c | sort -nr | head -3

# 纯 jq
jq -s -r '[.[].error | select(.)] | group_by(.) | map({e: .[0], n: length})
          | sort_by(-.n) | .[:3][] | "\(.n) \(.e)"' agent_trace.jsonl
```

```
2 net::ERR_CONNECTION_REFUSED
2 upstream 502
1 exit code 127: command not found
```

要点：

- `select(. != null)` 里的 `.` 指"当前值本身"，用来过掉 `"error": null` 的成功记录。简写 `select(.)` 利用了 null 的假值性。
- 第 3 名有并列（多条计数都是 1），`head -3` 取到哪条取决于 sort 的稳定性。**面试时主动说一句"这里有并列，需要定义 tie-break 规则"**，是加分项。
- `.[:3]` 是数组切片，和 Python 一样。

### D13 每个 tool 的失败率（压轴）

```bash
# (a) jq 取两列 + awk 聚合（推荐：好写、好调试）
jq -r '[.tool, .status] | @tsv' agent_trace.jsonl | \
awk -F'\t' '{t[$1]++; if($2!="success") f[$1]++}
            END{for(k in t) printf "%-18s %6.1f%%  (%d/%d)\n", k, f[k]*100/t[k], f[k], t[k]}' | \
sort -k2 -nr
```

```
memory_search        100.0%  (1/1)
browser_navigate     100.0%  (2/2)
code_exec             75.0%  (3/4)
web_search            37.5%  (3/8)
terminal              25.0%  (1/4)
read_file              0.0%  (0/3)
patch                  0.0%  (0/2)
delegate_task          0.0%  (0/2)
```

```bash
# (b) 纯 jq
jq -s -r 'group_by(.tool)
          | map({tool: .[0].tool,
                 total: length,
                 fail: (map(select(.status != "success")) | length)})
          | map(. + {rate: (.fail / .total * 100)})
          | sort_by(-.rate)
          | .[] | "\(.tool) \((.rate*10|round)/10)% (\(.fail)/\(.total))"' agent_trace.jsonl
```

要点：

- awk 里 `f[k]` 未赋值时在数值上下文自动当 0，所以 `read_file` 这类零失败的 tool 不会报错，直接是 0.0%。这是 awk 关联数组的便利之处。
- **分母口径**：失败 = `status != "success"`，把 timeout 算进去。只统计 `== "error"` 会漏掉 timeout，`web_search` 会从 37.5% 变成 25%——面试官经常拿这个追问。
- **样本量陷阱**：`memory_search` 100% 失败，但只有 1 次调用，没有统计意义。真实告警要加最小样本数：

```bash
... awk -F'\t' '{t[$1]++; if($2!="success") f[$1]++}
                END{for(k in t) if(t[k]>=3) printf "%-18s %6.1f%%\n", k, f[k]*100/t[k]}' | sort -k2 -nr
```

- 能主动说出"100% 那条是 1/1，不可信，要设最小样本量"，这题就满分了。

---

## E. 文件遍历 / 时间过滤 / 脚本

### E1 遍历文件输出行数

```bash
for f in app-*.log; do
    printf "%-22s %4d\n" "$f" "$(wc -l < "$f")"
done
```

```
app-2026-08-01.log       20
app-2026-08-02.log       24
app-2026-08-03.log       13
```

要点：

- `wc -l < "$f"` 用**重定向**而不是 `wc -l "$f"`：前者只输出数字，后者会带文件名，还得再 `awk '{print $1}'` 切一刀。
- `"$f"` 一定要加双引号，文件名带空格时才不会被拆成两个参数。
- 通配符没匹配到任何文件时，`for f in app-*.log` 会拿到字面量 `app-*.log`，所以循环体里习惯加一句 `[ -f "$f" ] || continue`。

### E2 24 小时内修改过的日志

```bash
find . -name '*.log' -mtime -1
```

```
./01-log-process/agent.log
./access.log
./app-2026-08-01.log
./app-2026-08-02.log
./app-2026-08-03.log
```

要点：

- `-mtime` 单位是**天**，`-mmin` 单位是**分钟**。
- 符号含义：`-1` = 1 天以内、`+7` = 7 天以前、`1` = 恰好第 1 天（很少用，容易踩坑）。
- 常用组合：
  - 最近 1 小时改过：`find . -name '*.log' -mmin -60`
  - 清理 7 天前的日志：`find /var/log -name '*.log' -mtime +7 -delete`
  - 大于 100MB 的日志：`find . -name '*.log' -size +100M`
  - 交给别的命令：`find . -name '*.log' -mtime -1 -exec grep -l ERROR {} \;`
- **删除类命令先去掉 `-delete` 跑一遍确认列表**，这是运维铁律。

### E3 时间范围过滤

```bash
awk '$2 >= "09:00:00" && $2 <= "11:00:00"' app-2026-08-02.log
```

```
2026-08-02 09:45:18 INFO  [agent-core] session=s-2002 msg="agent started" model=deepseek-v3
2026-08-02 09:45:33 DEBUG [memory] session=s-2002 msg="retrieved 12 memories" cost_ms=88
2026-08-02 09:46:01 INFO  [tool-runner] session=s-2002 tool=read_file status=ok cost_ms=22
...
```

共 12 行。

要点：

- **`HH:MM:SS` 是定长零填充格式，字典序 == 时间序**，所以字符串比较就等于时间比较，不需要 `date -d` 转时间戳（那样每行 fork 一个进程，10 万行日志能跑一分钟）。
- 加引号很重要：`$2 >= "09:00:00"` 是字符串比较；写成 `$2 >= 09:00:00` 是语法错误。
- 跨天要连日期一起比：`$0 >= "2026-08-02 09:00:00" && $0 <= "2026-08-02 11:00:00"`（利用日志行以时间戳开头）。
- 同理 sed 也能干，取"从某行到某行"的区间：`sed -n '/09:00:00/,/11:00:00/p'`——但它匹配的是**第一次出现**，日志里时间戳不一定精确存在，不如 awk 稳。

### E4 while read 逐行统计

```bash
n=0
while IFS= read -r line; do
    case "$line" in
        *ERROR*) n=$((n+1)) ;;
    esac
done < app-2026-08-03.log
echo "ERROR lines: $n"
```

```
ERROR lines: 2
```

要点（这是 shell 基本功考点）：

- **`IFS=`**：清空字段分隔符，否则 read 会吃掉行首行尾的空白（tab/空格），日志缩进就没了。
- **`-r`**：不解析反斜杠转义。日志里的 `\n`、Windows 路径 `C:\temp` 会被 read 吞掉或改写，加 `-r` 才是"原样读"。
- **`done < file` 而不是 `cat file | while ...`**：管道会开子 shell，循环里对 `n` 的修改在子 shell 里，循环结束后 `n` 还是 0。这是经典面试题。
- 但是——**这题真实场景应该用 `grep -c ERROR`**。while read 逐行是 shell 里最慢的做法（每行都要 fork/内建调用），10 万行能慢几十倍。会写，但知道什么时候不该写。

### E5 按状态码拆分文件

```bash
mkdir -p out
awk '{print > ("out/status_" $9 ".log")}' access.log
ls out/
```

```
status_200.log  status_304.log  status_401.log  status_403.log  status_404.log
status_429.log  status_500.log  status_502.log  status_504.log
```

要点：

- **括号必须加**：`print > "status_" $9 ".log"` 会被解析成 `(print > "status_") $9 ".log"`，把所有内容写进一个叫 `status_` 的文件。`print > (表达式)` 才对。
- awk 会保持文件句柄打开（是追加不是覆盖），所以**重复跑会累积内容**，测试前记得清空目录。文件很多时用 `close(f)` 主动关闭，避免超过打开文件数上限。
- 这是"日志按维度切分"的标准做法，比 `for code in 200 404 ...; do grep ...; done` 快得多——**一次扫描 vs N 次扫描**。

### E6 log_report.sh

```bash
#!/bin/bash
#
# 日志目录巡检报表

dir=$1

# 1. 参数校验
if [ -z "$dir" ]; then
    echo "用法: $0 <日志目录>" >&2
    exit 1
fi

# 2. 目录校验
if [ ! -d "$dir" ]; then
    echo "目录不存在: $dir" >&2
    exit 1
fi

# 3. 逐文件统计
printf "%-22s %8s %8s %8s\n" "FILE" "LINES" "ERROR" "WARN"
for f in "$dir"/app-*.log; do
    [ -f "$f" ] || continue
    total=$(wc -l < "$f")
    errors=$(grep -c ERROR "$f")
    warns=$(grep -c WARN "$f")
    printf "%-22s %8d %8d %8d\n" "$(basename "$f")" "$total" "$errors" "$warns"
done

# 4. 全局 ERROR Top3 模块
echo
echo "ERROR Top3 模块:"
grep -h ERROR "$dir"/app-*.log | awk '{print $4}' | sort | uniq -c | sort -nr | head -3
```

运行结果：

```
$ bash log_report.sh
用法: log_report.sh <日志目录>
$ echo $?
1

$ bash log_report.sh .
FILE                      LINES    ERROR     WARN
app-2026-08-01.log           20        4        3
app-2026-08-02.log           24        8        3
app-2026-08-03.log           13        2        1

ERROR Top3 模块:
      4 [tool-runner]
      4 [gateway]
      3 [agent-core]
```

要点：

- **错误信息输出到 stderr（`>&2`）**，正常报表走 stdout。这样 `bash log_report.sh > report.txt` 时报错依然能在终端看到。
- `exit 1` 表示异常退出，`exit 0` 正常。CI 全靠这个判断成败。
- `grep -h`：多文件时**去掉文件名前缀**，否则 `awk '{print $4}'` 取到的列会错位（因为 `文件名:2026-08-01` 粘成了 $1）。这是本题最容易踩的坑。
- `basename` 只留文件名，报表才对得齐。
- 进阶写法：参数校验可以压成一行 `dir=${1:?用法: $0 <日志目录>}`（见 F3）。

---

## F. 综合大题

### F1 每分钟错误数报表

```bash
awk '$3=="ERROR" {split($2, t, ":"); c[$1 " " t[1] ":" t[2]]++}
     END{for(k in c) print k, c[k]}' app-*.log | sort
```

```
2026-08-01 09:14 2
2026-08-01 10:03 1
2026-08-01 11:05 1
2026-08-02 08:31 3
2026-08-02 10:11 2
2026-08-02 10:18 1
2026-08-02 10:19 1
2026-08-02 12:30 1
2026-08-03 09:20 1
2026-08-03 13:41 1
```

要点：

- **把"日期 + 时:分"拼成一个字符串当数组下标**——这是多维分组的通用手法（awk 也支持 `c[$1, t[1]]` 这种真·多维数组，底层就是用 `SUBSEP` 拼接，原理一样）。
- 最后 `| sort` 就能按时间升序，因为 `YYYY-MM-DD HH:MM` 的字典序等于时间序（又是定长格式的好处）。
- 想找"错误尖峰"，再接一刀：`| sort -k3 -nr | head -5`，`2026-08-02 08:31` 一分钟 3 条错误就是最高峰。
- 这类"时间桶聚合"是监控告警的基本单元，能扩展到每 5 分钟（`int(minute/5)*5`）、每小时等。

### F2 平均耗时最高的 tool

```bash
jq -r '[.tool, .latency_ms] | @tsv' agent_trace.jsonl | \
awk -F'\t' '{s[$1]+=$2; c[$1]++}
            END{for(k in s) printf "%-18s %8.1f ms  (n=%d)\n", k, s[k]/c[k], c[k]}' | \
sort -k2 -nr
```

```
delegate_task        8800.0 ms  (n=2)
web_search           8743.5 ms  (n=8)
code_exec            8110.5 ms  (n=4)
browser_navigate     5165.0 ms  (n=2)
memory_search        3010.0 ms  (n=1)
terminal              280.0 ms  (n=4)
patch                  41.0 ms  (n=2)
read_file              20.7 ms  (n=3)
```

要点：

- 分工：**jq 负责从 JSON 里挑列 → awk 负责聚合 → sort 负责排序**。每个工具只干自己最擅长的事，这就是 Unix 哲学，也是面试想听的回答。
- `@tsv` 比 `join(",")` 安全：字段值里可能有逗号（错误信息尤其常见），但几乎不会有 Tab。对应 awk 侧要写 `-F'\t'`。
- 结果同样要警惕小样本：`delegate_task` 排第一但只有 2 次调用；`web_search` 8 次调用平均 8.7s（含一条 60s 超时）才是真问题。**输出里带上 `n=` 就是为了让人能判断可信度**。

### F3 check_errors.sh（CI 巡检）

```bash
#!/bin/bash
#
# CI 日志巡检：错误数超阈值就让流水线变红

dir=${1:?用法: $0 <日志目录> [阈值]}
threshold=${2:-5}

count=$(grep -h ERROR "$dir"/app-*.log 2>/dev/null | wc -l)
echo "ERROR 总数: $count (阈值 $threshold)"

if [ "$count" -gt "$threshold" ]; then
    echo "--- Top3 错误 ---"
    grep -h ERROR "$dir"/app-*.log \
        | sed -E 's/^.*(msg="[^"]*"|status=[a-z]+).*$/\1/' \
        | sort | uniq -c | sort -nr | head -3
    exit 1
fi

echo "OK"
exit 0
```

运行结果：

```
$ bash check_errors.sh .
ERROR 总数: 14 (阈值 5)
--- Top3 错误 ---
      3 msg="upstream 502 from provider"
      3 msg="tool call failed"
      2 status=timeout
$ echo $?
1

$ bash check_errors.sh . 100
ERROR 总数: 14 (阈值 100)
OK
$ echo $?
0
```

要点：

- **`${1:?消息}`**：参数为空时打印消息到 stderr 并以非 0 退出，一行顶 E6 的四行 if。
- **`${2:-5}`**：参数未提供时用默认值 5（`:-` 只取值不赋值，`:=` 会顺便赋给变量）。
  一张表记住：`${v:-默认}` 取默认 / `${v:=默认}` 取并赋值 / `${v:?报错}` 为空就报错 / `${v:+替代}` 非空才替换。
- **退出码就是 CI 的红绿灯**：0 = 通过，非 0 = 失败。脚本最后不写 `exit` 的话，退出码是最后一条命令的状态，容易出意外，显式写清楚。
- `2>/dev/null` 屏蔽"文件不存在"的报错，避免目录为空时刷屏；但要想清楚是不是把真错误也吞了。
- 生产版还应该加：`set -euo pipefail`（出错即停、未定义变量报错、管道任意环节失败即失败）。本题为了输出可读没加，实际 CI 脚本建议第一行就写上。

---

## 复盘：这 40 题在考什么

| 能力 | 对应题 | 一句话要点 |
| --- | --- | --- |
| 列定位 | A1 A4 B1 | 状态码/耗时是"列"，grep 靠空格框列，awk 靠 `$n` 直接取 |
| 分组聚合模板 | B2 B3 B6 B7 B8 B9 F1 | `{c[key]++} END{for(k in c) print}` 一个模板通吃 |
| 排序输出 | B2 B3 D4 | `sort -k2 -nr`、`uniq -c` 前必须 sort |
| 格式化 | B5 B6 E1 E6 | `printf "%-20s %8.2f\n"`，文字左对齐数字右对齐 |
| 正则提取 | C3 C4 | 捕获组 + `\1` 反向引用，sed 提取子串的唯一手段 |
| 原地修改 | C6 | `-i.bak`，先 dry-run 再动手 |
| JSON 处理 | D 全区 | `-r` 去引号、`-s` 才能聚合、`//` 兜底缺字段 |
| 缺字段容错 | D7 | 真实日志字段必缺，不兜底就是线上事故 |
| 时间过滤 | E3 F1 | 定长时间戳直接字符串比较，别 fork `date` |
| 脚本规范 | E6 F3 | 参数校验 + stderr + 退出码，CI 只认退出码 |
| 统计口径 | B4 D13 F2 | 平均值陷阱、timeout 算不算失败、小样本不可信 |

**最容易被追问的三个点**（想清楚再去面试）：

1. **B4 / F2 的平均值陷阱** —— 为什么要看 P95 而不是均值。
2. **D13 的失败率口径** —— timeout 算不算失败，样本量太小怎么办。
3. **E4 的 `cat | while read`** —— 为什么变量改了不生效（子 shell 问题）。

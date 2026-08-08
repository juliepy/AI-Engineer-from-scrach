# 03 · Shell 可运行脚本

对应题库 **E6 / E3 / F3**，并补齐 **grep / sed / awk / 日志筛选** 专项脚本。  
数据默认：`../02-log-process/`（也可用 `../01-log-process/`）。

## 脚本一览

### 题库落地（原有）

| 脚本 | 对应题 | 作用 |
| --- | --- | --- |
| `log_report.sh` | E6 | 目录巡检：行数 / ERROR / WARN + Top3 模块 |
| `time_filter.sh` | E3 | 定长时间戳字符串比较过滤 |
| `check_errors.sh` | F3 | CI 巡检：超阈值 `exit 1`，否则 `exit 0` |

### 专项补齐（新增）

| 脚本 | 覆盖点 | 作用 |
| --- | --- | --- |
| `grep_scan.sh` | grep | `-E/-c/-n/-C/-v/-rl/-h`、5xx、多文件计数 |
| `sed_clean.sh` | sed | 空白压缩、捕获组提取、IP 脱敏、`-n 'a,bp'`、删空行/注释 |
| `awk_stats.sh` | awk | `$n`、条件过滤、`{c[k]++} END`、tool 统计、均值、`-v` 时间窗 |
| `pipeline_filter.sh` | 综合 | 时间窗 + 级别 + sed TopN + access 4xx/5xx + jq/JSONL |

## 覆盖对照

| 能力 | 脚本 |
|------|------|
| 文本检索 / 计数 / 上下文 / 反选 / 找文件 | `grep_scan.sh` |
| 清洗 / 提取 / 脱敏 / 行区间 | `sed_clean.sh` |
| 按列统计 / 聚合 / 均值 / 多文件 | `awk_stats.sh` |
| 时间筛选 | `time_filter.sh` · `awk_stats.sh` §5 · `pipeline_filter.sh` |
| 管道串联 + CI 退出码 | `pipeline_filter.sh` · `check_errors.sh` |
| 目录报表 | `log_report.sh` |

更细的 40 题仍在 [`../02-log-process/`](../02-log-process/)；本目录是**可跑脚本版速通**。

## 怎么跑

在 **WSL / Linux** 下：

```bash
cd 03-shell-scripts

# 题库三件套
bash log_report.sh ../02-log-process
bash time_filter.sh ../02-log-process/app-2026-08-02.log
bash check_errors.sh ../02-log-process        # 期望 exit 1
bash check_errors.sh ../02-log-process 100    # 期望 exit 0

# 专项
bash grep_scan.sh ../02-log-process
bash sed_clean.sh ../02-log-process/app-2026-08-01.log
bash awk_stats.sh ../02-log-process
bash pipeline_filter.sh ../02-log-process
```

JSON 段需要 `jq`（可选）：`sudo apt install -y jq`

## 笔试要点

- 报错打到 `>&2`，正常输出走 stdout
- CI 只认退出码：`0` 绿 / 非 `0` 红
- `${1:?用法}` 一行完成空参校验；`${2:-5}` 给默认阈值
- 多文件 `grep` 要加 `-h`，否则 awk 列会错位
- 列数据用 awk 的 `$n`；grep「框列」靠两边空格（如 ` 5[0-9]{2} `）
- JSON 优先 jq，不要用 grep 硬切

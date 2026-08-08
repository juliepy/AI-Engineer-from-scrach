# 04 · Python 日志处理

场景：自动化测试脚本、日志分析、校验 Agent 输出、**筛异常任务**。  
有 C 底子、语法不熟：先 `00-python-core.md` + `00-containers-demo.py`，再 `01-python-basic.md`，再按编号跑脚本。

## 文件一览

| 文件 | 对应基础节 | 作用 |
| --- | --- | --- |
| `00-python-core.md` | — | C→Python 核心：容器 / 循环 / 文件 / 统计；async·类·装饰器能读即可 |
| `00-containers-demo.py` | `00` §1～§3 | list 过滤 / set 去重 / dict·Counter 计数手练 |
| `01-python-basic.md` | — | 必备清单（json / 读文件 / re / argparse / Counter / 异常） |
| `agent.log` | — | JSONL 练习数据（扁平） |
| `02-process-json.py` | §1 §2 §6 | 逐行 `json.loads` + 字段校验 + 筛 ERROR |
| `03-learn-re.py` | §3 | search / findall / 命名组 / sub |
| `04-count-stats.py` | §5 | dict / defaultdict / Counter |
| `05-json-log-process.py` | 综合 | 过滤 / 投影 / 分组 / 嵌套 / 写报告 |
| `06-argparse-cli.py` | §4 | 命令行入参过滤 JSONL |
| `07-parse-text-log.py` | 文本解析+清洗 | app/access 结构化、时间窗、IP 脱敏、去重 |
| `08-filter-abnormal-tasks.py` | **高频主剧本** | 按 session 聚合，超时/失败/重试/关键字 → 异常清单 |
| `09-scan-logs-cli.py` | CI 巡检 | 多文件 ERROR/WARN TopN，超阈值 `exit 1` |

## 覆盖对照

| 能力 | 脚本 |
|------|------|
| 日志解析（JSONL） | `02` · `05` · `06` |
| 日志解析（纯文本 app/access） | `07` |
| 文本过滤 | `03` · `05` · `06` · `07` |
| 统计聚合 | `04` · `05` · `08` · `09` |
| 数据清洗 | `05` 默认值/投影 · `07` 脱敏/去重/空白 |
| 筛异常任务 | **`08`** |
| 多文件 + 退出码 | **`09`**（对标 shell `check_errors.sh`） |

数据默认读 `../01-basic-shell/02-log-process/`（`app-*.log` / `access.log` / `agent_trace.jsonl`）。

## 怎么跑

```bash
cd 02-log-python

# 语法核心（C → Python）
python 00-containers-demo.py

# 基础链
python 02-process-json.py
python 03-learn-re.py
python 04-count-stats.py
python 05-json-log-process.py
python 06-argparse-cli.py --level ERROR
python 06-argparse-cli.py --module memory --level ERROR --json

# 缺口补齐
python 07-parse-text-log.py
python 07-parse-text-log.py --start "2026-08-01 09:00:00" --end "2026-08-01 12:00:00"
python 08-filter-abnormal-tasks.py
python 08-filter-abnormal-tasks.py --latency-ms 3000 --json
python 09-scan-logs-cli.py ../01-basic-shell/02-log-process              # 期望 exit 1
python 09-scan-logs-cli.py ../01-basic-shell/02-log-process --threshold 100  # 期望 exit 0
```

Windows / PowerShell 可直接跑；看退出码：

```powershell
python 09-scan-logs-cli.py ../01-basic-shell/02-log-process; echo $LASTEXITCODE
```

`05` 会写出 `out/error_report.json`、`out/errors.jsonl`（本地产物，不必提交）。

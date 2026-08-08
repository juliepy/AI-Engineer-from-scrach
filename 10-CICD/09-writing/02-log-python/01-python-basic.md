# Python 必备基础清单（Senior AI Agent SDET）

场景：自动化测试脚本、日志分析、校验 Agent 输出，不考复杂算法。

**先学语法核心？** → [`00-python-core.md`](./00-python-core.md)（list/dict/set、for/with/try、Counter、能读即可的 async/类/装饰器）  
**再练本清单** → json / 读文件 / re / argparse / 异常（下面各节）

---

## 1. json 模块（最高频）

```python
import json

# 读取单行 json 日志
line = '{"agent_id":"agent_01","level":"ERROR"}'
data = json.loads(line)
print(data["agent_id"])

# json 文件读取
with open("agent.log", "r", encoding="utf-8") as f:
    obj = json.load(f)

# json 对象对比、字段存在性校验
def check_json_field(data):
    # 判断 key 是否存在
    if "msg" not in data:
        return False
    return True

# json 格式化输出
json.dumps(data, indent=2)
```

---

## 2. 文件逐行读取

海量日志标准写法：不一次性载入内存。

```python
# 推荐：逐行读取大日志文件
with open("agent.log", "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        record = json.loads(line)
```

---

## 3. re 正则模块：提取文本信息

```python
import re

# 正则提取数字、字符串
text = "timeout 300 gpu_id: 2"
res = re.search(r"gpu_id:\s*(\d+)", text)
if res:
    gpu = res.group(1)

# re.findall 批量提取所有匹配内容
```

---

## 4. argparse 命令行参数

笔试多次出现。脚本接收外部入参，类似 shell 传参。

```python
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--module", type=str, required=True)
args = parser.parse_args()
print(args.module)
```

可运行完整示例：`06-argparse-cli.py`（`--level` / `--module` / `--contains`）。

进阶脚本：`07` 文本日志解析清洗 · `08` 按 session 筛异常任务 · `09` 多文件巡检退出码。
---

## 5. 数据统计、字典计数

对应 shell / awk 统计。

```python
# 统计每个 agent 错误数量，万能模板
error_counter = {}
record = {"agent_id": "agent_01", "level": "ERROR"}
aid = record["agent_id"]
if aid not in error_counter:
    error_counter[aid] = 0
error_counter[aid] += 1

# 进阶：collections.defaultdict / Counter
from collections import Counter
```

---

## 6. 异常处理（SDET 加分项）

日志经常出现非法 json、空行，一定要捕获异常。面试官看重健壮性。

```python
try:
    record = json.loads(line)
except json.JSONDecodeError:
    # 无效日志直接跳过
    continue
```

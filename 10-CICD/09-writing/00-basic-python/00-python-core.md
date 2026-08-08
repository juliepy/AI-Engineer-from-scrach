# Python 核心语法（C 转 Python 速通）

场景：有 C 底子、靠 AI 写过 Python，但缺系统语法。  
目标：**能手写日志过滤/去重/计数**；AI 生成的进阶写法能读懂。

学习顺序：

```
本文件（容器 + 循环 + 文件 + 统计）
  → 01-python-basic.md（json / re / argparse）
  → 02～06 脚本手敲一遍
  → 文末「能读即可」扫一眼
```

可跑练习：`00-containers-demo.py`

---

## 0. 和 C 的最大差别（先建立直觉）

| C | Python |
|---|--------|
| 先声明类型、管内存 | 变量随时赋值，GC 管内存 |
| `{}` 包块 | **缩进**包块（4 空格） |
| `strcmp(a,b)==0` | `a == b`（字符串也能直接比） |
| `NULL` | `None` |
| `true/false` | `True` / `False`（首字母大写） |
| `printf` | `print(...)` |
| 数组长度自己记 | `len(xs)` |

```python
# 合法
x = 1
x = "hello"   # 同一名字可换类型（灵活，也易踩坑）

# 块靠缩进
if x:
    print("ok")
```

---

## 1. list / dict / set（必会）

过滤、去重、计数的底层就是这三样。

### 1.1 list ≈ 动态数组

```python
xs = ["a", "b", "c"]
xs.append("d")          # 尾部追加
xs[0]                   # 下标从 0
xs[-1]                  # 最后一个
xs[1:3]                 # 切片，半开区间 [1,3) → ["b","c"]
len(xs)                 # 长度
"b" in xs               # 成员判断 → True

# 过滤（日志脚本最常用写法）
errors = []
for item in xs:
    if item.startswith("e"):
        errors.append(item)

# 等价列表推导（能读会写即可）
errors = [item for item in xs if item.startswith("e")]
```

**和 C 不同：** 可混类型；越界抛 `IndexError`，不会静默坏内存。

### 1.2 dict ≈ 哈希表（键值对）

日志里几乎每条记录都是 dict。

```python
r = {"agent_id": "a01", "level": "ERROR", "msg": "timeout"}

r["level"]              # 取值，键不存在 → KeyError
r.get("module")         # 安全取值 → None
r.get("module", "n/a")  # 带默认值

"msg" in r              # 判断键是否存在（不是判断值）
r["retry"] = 1          # 写入 / 覆盖
del r["retry"]          # 删除键

for k, v in r.items():  # 遍历键值
    print(k, v)
```

手写计数万能模板：

```python
counter = {}
for r in records:
    key = r["agent_id"]
    if key not in counter:
        counter[key] = 0
    counter[key] += 1
```

### 1.3 set ≈ 去重集合

只关心「有没有出现过」，不关心顺序、不存重复。

```python
seen = set()
seen.add("a01")
"a01" in seen           # O(1) 平均

# 去重保序（日志里常用）
unique = list(dict.fromkeys(["a", "b", "a", "c"]))  # ["a","b","c"]

# 集合运算
A = {"ERROR", "WARN"}
B = {"WARN", "INFO"}
A & B                   # 交：{"WARN"}
A | B                   # 并
A - B                   # 差：{"ERROR"}
```

### 1.4 三选一口诀

| 需求 | 用 |
|------|-----|
| 有序、可重复、按下标 | `list` |
| 按名字/字段取值 | `dict` |
| 去重、判重、集合运算 | `set` |

---

## 2. for / with open / try-except（读日志标配）

### 2.1 for

```python
for r in records:           # 遍历序列
    print(r["level"])

for i, r in enumerate(records, start=1):  # 带行号
    print(i, r)

for i in range(3):          # 0,1,2（类似 C 的 for i=0; i<3）
    pass
```

`continue` 跳过本轮，`break` 跳出循环 —— 和 C 一样。

### 2.2 with open（必用，别裸 open）

对应 C 的「打开 → 用 → 关闭」，`with` 保证异常时也会关文件。

```python
with open("agent.log", "r", encoding="utf-8") as f:
    for line in f:              # 逐行，不把整文件读进内存
        line = line.strip()
        if not line:
            continue
        ...
# 离开 with 块自动 f.close()
```

现代写法（同目录脚本常用）：

```python
from pathlib import Path
path = Path(__file__).with_name("agent.log")
with path.open("r", encoding="utf-8") as f:
    ...
```

### 2.3 try-except

日志脏数据（坏 JSON、缺字段）必须吞掉并继续，不能整脚本崩。

```python
try:
    record = json.loads(line)
except json.JSONDecodeError:
    continue

# 多种异常
try:
    n = int(text)
except (ValueError, TypeError):
    n = 0
```

**习惯：** 只捕获你预期的异常；不要无脑 `except Exception: pass` 把真 bug 藏掉。

---

## 3. Counter / defaultdict（统计几乎必用）

完整可跑示例见 `04-count-stats.py`。

```python
from collections import Counter, defaultdict

# --- defaultdict：省掉「if key not in」---
module_counter = defaultdict(int)   # 缺省值 0
for r in records:
    module_counter[r["module"]] += 1

# 分组收集
by_agent = defaultdict(list)
for r in records:
    by_agent[r["agent_id"]].append(r)

# --- Counter：计数 + 排行 ---
level_counter = Counter(r["level"] for r in records)
level_counter["ERROR"]              # 某个键的数量
level_counter.most_common(3)        # Top3
```

对应关系：

| 手写 dict | 升级 |
|-----------|------|
| `if k not in d: d[k]=0` 再 `+=1` | `defaultdict(int)` |
| 统计频次 + TopN | `Counter` |

---

## 4. json / re / argparse（高频考点）

细节和代码块在 `01-python-basic.md`，这里只记「何时用」：

| 模块 | 一句话 | 练习脚本 |
|------|--------|----------|
| `json` | JSONL：`json.loads(line)`；写出：`json.dumps` | `02` `05` |
| `re` | 从非 JSON 文本抠字段 | `03` `07` |
| `argparse` | 脚本接 `--level` 等参数 | `06` `09` |

最小记忆：

```python
import json, re, argparse

data = json.loads(line)
m = re.search(r"gpu_id:\s*(\d+)", text)
parser = argparse.ArgumentParser()
parser.add_argument("--level", type=str)
args = parser.parse_args()
```

---

## 5. 能读即可（先不系统练）

AI 会写这些；你要能看懂意图，面试口述「知道是干什么的」即可。需要手写时再回看。

### 5.1 类与继承

```python
class BaseParser:
    def parse(self, line: str) -> dict:
        raise NotImplementedError

class JsonParser(BaseParser):          # 继承
    def parse(self, line: str) -> dict:
        return json.loads(line)
```

日志脚本用函数就够；看到 `class Xxx(Yyy)` = 「Xxx 是一种 Yyy，复用/覆盖方法」。

### 5.2 装饰器

```python
def log_call(fn):
    def wrapper(*args, **kwargs):
        print("calling", fn.__name__)
        return fn(*args, **kwargs)
    return wrapper

@log_call                    # 等价于 process = log_call(process)
def process(x):
    return x
```

本质：用一个函数包装另一个函数。pytest 的 `@pytest.fixture`、Flask 的 `@app.route` 都是这个形态。

### 5.3 生成器

```python
def read_errors(path):
    with open(path, encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            if r.get("level") == "ERROR":
                yield r              # 一次产出一条，不先建大 list

for r in read_errors("agent.log"):   # 懒加载遍历
    print(r["msg"])
```

`yield` ≈ 「暂停函数，下次接着跑」。大日志流式处理会看到。

### 5.4 类型标注（类型体操入门）

```python
def load(path: str) -> list[dict]:
    ...
```

给人和 IDE / 类型检查器看，**运行时默认不管**。看到 `list[dict]`、`Optional[str]`、`dict[str, int]` 当文档读即可。

### 5.5 async / await

```python
import asyncio

async def fetch(url: str) -> str:
    await asyncio.sleep(0.1)     # 等待期间把控制权交还事件循环
    return "ok"

async def main():
    a, b = await asyncio.gather(fetch("u1"), fetch("u2"))

asyncio.run(main())
```

用于并发 IO（HTTP、多路连接）。**日志分析 / 笔试脚本用同步就够。**  
见到 `async def` = 协程；`await` = 等这个异步结果。

---

## 6. 自检清单（过完再进 02～06）

- [ ] 能手写：list 过滤、dict 计数、set 去重
- [ ] 能默写：`with open` + 逐行 + `try/except json`
- [ ] 知道 `defaultdict(int)` / `Counter` 各自省掉什么
- [ ] 知道 `json.loads` / `re.search` / `argparse` 各解决什么问题
- [ ] 看到 `@decorator` / `yield` / `async def` 能说出一句话用途

跑通：

```bash
python 00-containers-demo.py
python 04-count-stats.py
python 06-argparse-cli.py --level ERROR
```

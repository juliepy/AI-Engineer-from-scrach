# Day 1.5｜pytest（CI 向单独模块）

> 对应大纲：一补、pytest 基础  
> 目标：能本地跑用例，会用目录 + `-m` 区分门禁 case，并能接到 GitLab Job 的 `script`

## 为什么要单独学

多门禁不是「同一批测试换时间跑」：

| 门禁 | 典型命令（概念） |
|------|------------------|
| MR | `pytest tests/smoke -m smoke` |
| Gate1 | `pytest tests/gate1 -m gate1` |
| Daily | `pytest tests/full` |
| 发版 | `pytest tests/release -m release` |

不懂 pytest，就看不懂这些命令、也排不好「测挂了」。

## 今日学什么

| 序号 | 主题 | 文档 | 可运行 Demo | 掌握标准 |
|------|------|------|-------------|----------|
| 1 | 安装与第一次跑通 | [01-安装与运行.md](./01-安装与运行.md) | [demos/01-install-run](./demos/01-install-run/) | 本地 `pytest` 有绿有红 |
| 2 | 用例怎么写、怎么被发现 | [02-用例与发现规则.md](./02-用例与发现规则.md) | [demos/02-discovery](./demos/02-discovery/) | 会写最小 `test_*.py` |
| 3 | marker / 目录分流（重点） | [03-marker与门禁分流.md](./03-marker与门禁分流.md) | [demos/03-markers](./demos/03-markers/) | 说清四门禁各自跑啥 |
| 4 | 失败怎么读、怎么进 CI | [04-失败阅读与CI衔接.md](./04-失败阅读与CI衔接.md) | [demos/04-ci](./demos/04-ci/) | 退出码、报告、yml 片段 |
| 5 | 自测题 | [05-自测题.md](./05-自测题.md) | [demos/05-selfcheck](./demos/05-selfcheck/) | A 部分可被 pytest 判分 |

Demo 总索引：[demos/README.md](./demos/README.md)

## 建议顺序

1. 读文档 → 进对应 `demos/0x-*` 动手跑  
2. `01` → `02` → `03`（核心）→ `04` → `05`  
3. 再进 **[03-gitlab-ci/](../03-gitlab-ci/README.md)**，把命令写进 `.gitlab-ci.yml`

```bash
# WSL/Linux：不要直接 pip install 到系统 Python
python3 -m venv .venv && source .venv/bin/activate
python -m pip install -r requirements.txt
```

## 今日完成标志

- [ ] 本地能跑 `pytest`，知道绿/红含义  
- [ ] 会用 `-m smoke` / 目录限制范围  
- [ ] 能口述：MR / Gate1 / Daily / 发版 case 为何不同  
- [ ] 知道 pytest 非 0 退出码会让 CI Job 失败  

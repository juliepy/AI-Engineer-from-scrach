# Day 2~3｜GitLab CI 核心【重中之重】

> 对应大纲：二、GitLab CI 核心  
> 前置：[02-pytest/](../02-pytest/README.md)（会跑 pytest + `-m` / 目录分流）  
> 目标：看懂、改写 `.gitlab-ci.yml`，把 pytest 正确挂进 Job

## 今日学什么

| 序号 | 主题 | 文件 | 掌握标准 |
|------|------|------|----------|
| 0 | 安装与部署概览 | [00-安装与部署概览.md](./00-安装与部署概览.md) | 分清 Server / Runner；能口述 Omnibus + register |
| 1 | 核心组件 | [01-核心组件.md](./01-核心组件.md) | 说清 yml / Runner / 执行器关系 |
| 2 | 必须掌握语法 | [02-必须掌握语法.md](./02-必须掌握语法.md) | 听到关键字能立刻说作用 |
| 3 | 标准流水线流程 | [03-标准流水线流程.md](./03-标准流水线流程.md) | 背出 MR→制品 完整链路 |
| 4 | pytest 挂进 CI | [04-与pytest衔接.md](./04-与pytest衔接.md) | 能写多 Job + rules + artifacts |
| 5 | 自测题 | [05-自测题.md](./05-自测题.md) | 闭卷过一遍 |

可运行 Demo：[demos/mini-pipeline/](./demos/mini-pipeline/)（默认 `python run_pipeline.py` = 完整标准流程；不依赖真实 GitLab）

## 建议学习顺序

1. `01` → `02`（语法是重点）→ `03` → `04`  
2. 进 `demos/mini-pipeline`：`pip install -r requirements.txt` → `python run_pipeline.py`（全步骤）  
3. 对照 `.gitlab-ci.yml.example` 与 `artifacts/archive/`，做自测题，口述「从 MR 到归档」

## 今日完成标志

- [ ] 能解释：`.gitlab-ci.yml` 是仓库内「代码即流水线」
- [ ] 能区分：Shell 执行器 vs Docker 执行器
- [ ] 会用：`stages` / `script` / `rules` / `cache` / `artifacts` / `needs`
- [ ] 能写出：MR smoke Job + Gate1 Job + JUnit artifacts 片段
- [ ] 能口述：Cache 加速依赖，Artifacts 保存产物

## 下一步

进入 **[04-ci-features/](../04-ci-features/README.md)**（特色知识点，拉开差距）。

# CICD-DEVOPS AI 面试｜短期学习清单 

> **主线**：GitLab CI（新手友好，精简、直奔面试考点）  
> **定位**：开发转岗，主攻 CI，弱化 CD；通用软件研发场景  
> **时间**：约 6 天突击（理论 → **pytest** → GitLab CI → 特色/排查 → 复盘）  
> **说明**：多门禁里不同 case 集常用 pytest 标记/目录分流，需**单独学**，不能只在 CI 里「听说有单测」。

---

## 学习节奏总览

| 天数 | 主题 | 目标 |
|------|------|------|
| Day 1 | 基础理论 | 能口述 CI / CD 区别与核心名词 |
| **Day 1.5 / Day 2 上午** | **pytest（单独模块）** | 能写/跑用例，会用 `-m` / 目录区分门禁 case |
| Day 2~3 | GitLab CI 核心 | 看懂、改写 `.gitlab-ci.yml`，把 pytest 挂进 Job |
| Day 3 | CI 特色知识点 | 拉开与普通候选人差距 |
| Day 4 | 故障排查 + Jenkins 保底 | 有排查话术，懂 Jenkins 架构 |
| Day 5 | 复盘模拟 | 串流程、刷题、包装经历 |

---

## 一、基础理论（Day 1）

> 完整学习材料见：[01/](./01/README.md)

### 1. 三者定义与落地结论（必背）

| 概念 | 含义 |
|------|------|
| **持续集成 CI** | 频繁合入 + 自动构建 / 测试 |
| **持续交付 Continuous Delivery** | 制品随时可上线，上线需人工确认 |
| **持续部署 Continuous Deployment** | 通过门禁后自动上生产 |

**落地区分结论**：大多数企业做到「持续交付」；生产环境一般不启用全自动持续部署。

### 2. 核心名词（熟记）

Pipeline、Stage、Job、Step、Webhook、Runner / Agent、Artifact（制品）

### 3. 分支策略

- **GitLab Flow**
- MR 合并
- 流水线作为合并门禁

### 4. DevOps 基础认知

能简单口述即可：**DevOps ≠ CI/CD**（CI/CD 是 DevOps 的落地实践之一）。

---

## 一补、pytest 基础【单独学】（Day 1.5）

> 完整学习材料见：[02-pytest/](./02-pytest/README.md)  
> **为何单独一节**：Gate1 / Daily / 发版跑的 case 不一致，落地时多靠 pytest **目录 + marker（`-m`）** 分流；不懂 pytest，CI 脚本只能死记，排不起测例失败。

### 必掌握（CI 向，不求框架百科）

| 点 | 用途 |
|----|------|
| 安装与基本运行 | `pytest` / `pytest path` |
| 用例发现规则 | `test_*.py`、`Test*`、`test_*` |
| **marker（`-m`）** | `smoke` / `gate1` / `full` / `release` 分流门禁 |
| 目录拆分 | `tests/smoke`、`tests/gate1`、`tests/full`、`tests/release` |
| 失败信息阅读 | 断言失败、导入错误、路径问题（对接 CI 日志） |
| 退出码 | 非 0 → Job 失败（门禁变红） |
| 报告（了解） | JUnit XML → 给 CI `artifacts` 归档 |

### 和多门禁的衔接（背过）

```
MR     → pytest tests/smoke -m smoke
Gate1  → pytest tests/gate1 -m gate1
Daily  → pytest tests/full
发版   → pytest tests/release -m release  + 打包脚本
```

### 实操目标

本地能跑通一小组用例；能解释「为什么 Daily 不在 MR 里跑同一批 case」。

---

## 二、GitLab CI 核心【重中之重】（Day 2~3）

> 完整学习材料见：[03-gitlab-ci/](./03-gitlab-ci/README.md)

### 1. 核心组件

| 组件 | 要点 |
|------|------|
| `.gitlab-ci.yml` | 流水线配置文件，仓库内管理（代码即流水线） |
| GitLab Runner | 执行 Job 的工人 |
| Runner 类型 | 共享 Runner / 私有 Runner |
| 执行器 | **Shell**、**Docker**（重点掌握 Docker 执行器优势） |

### 2. 必须掌握语法

| 关键字 | 作用 |
|--------|------|
| `stages` | 定义执行顺序 |
| `script` | 执行命令 |
| `rules` | 控制触发（push / MR / tag / 手动） |
| `cache` | 缓存依赖、编译中间文件，加速构建 |
| `artifacts` | 保存构建产物、测试报告 |
| `needs` | Job 并行 / 依赖，缩短流水线时长 |

### 3. 标准 CI 流水线流程（背诵）

```
MR 触发
  → 代码拉取
  → Lint 规范检查
  → 静态代码扫描
  → 单元测试
  → 编译构建
  → 产出制品
  → 报告归档
```

### 4. 实操目标

能看懂 yml，能修改、仿写简易流水线模板；**能在 `script` 里正确调用 pytest（含 `-m` / 路径）**。

### 5. 与 pytest 的衔接

- `script: pytest ...` 写进不同 Job + 不同 `rules`
- 测试报告作为 `artifacts`（如 `--junitxml=report.xml`）
- `cache` 可缓存 `.venv` / pip 依赖，加速测试 Job

---

## 三、CI 特色知识点（Day 3）【拉开差距】

> 完整学习材料见：[04-ci-features/](./04-ci-features/README.md)

### 1. 交叉编译

嵌入式场景重点；通用开发了解概念即可。

### 2. 构建痛点优化

编译耗时久 → **缓存**、**并行 Job**、**增量编译**。

### 3. 制品管理

- 程序包 / 镜像
- 用 **Commit SHA** 标记版本
- **禁止** 使用 `latest` 标签

### 4. 软件研发合规要点

- 构建全程可追溯
- 日志 / 产物留存
- 流水线变更需要评审
- 门禁不可随意关闭

---

## 四、故障排查 + 流水线优化（Day 4）

> 完整学习材料见：[05-troubleshoot/](./05-troubleshoot/README.md)  
> 贴合「维护 CI 系统」的经历包装。

### 1. 优化方向（熟记）

1. Cache 缓存加速构建  
2. Job 并行执行  
3. Docker 构建环境统一，避免环境污染  
4. 设置流水线超时、失败重试  

### 2. 标准排查思路（固定话术）

1. 流水线是否正常触发（Webhook、`rules`）  
2. Runner 是否正常，资源 / 网络是否通畅  
3. 脚本报错：工具链、权限、环境变量  
4. 外部服务连通性（代码仓库、制品库、扫描服务）  
5. 凭证 / 密钥是否失效  

---

## 五、Jenkins 保底认知（Day 4）

> 完整学习材料见：[06-jenkins/](./06-jenkins/README.md)  
> 不用实操，看懂基础即可。

| 考点 | 要点 |
|------|------|
| 架构 | Master + Agent 分布式 |
| 流水线 | `Jenkinsfile`（声明式），思想与 `.gitlab-ci.yml` 一致 |
| 其他 | 凭证管理、分布式构建概念 |

**面试话术**：主力使用 GitLab CI；理解 Jenkins 架构与流水线理念互通，可快速上手。

---

## 六、工具认知（知道用途即可）

> 完整学习材料见：[07-tools/](./07-tools/README.md)

| 类别 | 工具 | 用途 |
|------|------|------|
| 测试框架 | **pytest** | 单测/门禁用例执行与标记分流（需单独学） |
| 代码扫描 | SonarQube | 静态分析 / 质量门禁 |
| 制品仓库 | Nexus | 程序包、固件、安装包 |
| 容器 | Docker | 封装构建环境、编译工具链 |

---

## 七、Day 5 复盘模拟

> 完整学习材料见：[08-review/](./08-review/README.md)

1. 梳理整条标准 CI 流水线流程  
2. 自测高频面试题  
3. 整理过往经历包装话术（修复 CI 故障、脚本调试）  

---

## 学习材料目录（按大纲顺序）

| 大纲 | 文件夹 |
|------|--------|
| 一、基础理论 | [01/](./01/README.md) |
| 一补、pytest | [02-pytest/](./02-pytest/README.md) |
| 二、GitLab CI | [03-gitlab-ci/](./03-gitlab-ci/README.md) |
| 三、特色知识点 | [04-ci-features/](./04-ci-features/README.md) |
| 四、排查与优化 | [05-troubleshoot/](./05-troubleshoot/README.md) |
| 五、Jenkins | [06-jenkins/](./06-jenkins/README.md) |
| 六、工具认知 | [07-tools/](./07-tools/README.md) |
| 七、复盘模拟 | [08-review/](./08-review/README.md) |
| 附、Shell / Linux / 日志 Python | [09-writing/](./09-writing/README.md) |

---

## 附：极易混淆考点（必背）

### Cache vs Artifacts

| | Cache | Artifacts |
|---|--------|-----------|
| **目的** | 加速本次 / 后续流水线 | 保存输出产物 |
| **典型内容** | 依赖、编译中间文件 | 程序包、测试报告 |
| **用途** | 临时缓存，提升速度 | 可下载，供后续 Job 使用 |

### Docker 执行器优势

- 干净、统一的构建环境  
- 方便封装各类编译工具链  
- 不污染宿主机  

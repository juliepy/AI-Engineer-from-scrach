# mini-pipeline｜完整标准流水线 Demo

本地模拟整条教科书 CI（**不需要**真实 GitLab Runner）：

```
MR 触发 / 代码拉取
  → Lint 规范检查
  → 静态代码扫描（Sonar 替身）
  → 单元测试
  → 编译构建 / 产出制品
  → 报告归档
```

对应文档：[03-标准流水线流程.md](../../03-标准流水线流程.md)  
对应配置：[.gitlab-ci.yml.example](./.gitlab-ci.yml.example)

---

## 一、一次跑通（推荐）

```powershell
cd ...\03-gitlab-ci\demos\mini-pipeline

python -m venv .venv
.\.venv\Scripts\Activate.ps1          # WSL: source .venv/bin/activate
pip install -r requirements.txt

# 默认 = 标准全流程（全部步骤）
python run_pipeline.py
```

成功时看到 `PIPELINE PASSED (gate=standard)`，并产出：

| 步骤 | Job | 产物 |
|------|------|------|
| 触发 + 拉代码 | `checkout` | `artifacts/checkout-meta.json` |
| Lint | `lint` | 控制台 ruff 结果 |
| 静态扫描 | `scan` | `artifacts/scan-report.json` |
| 单元测试 | `unit_test` | `artifacts/report-standard.xml` |
| 构建 / 制品 | `build_pkg` | `dist/mini-app-*.txt` |
| 报告归档 | `archive` | `artifacts/archive/<时间戳>/` + `MANIFEST.json` |

打开 `artifacts/archive/` 下最新目录，即可看到「一次流水线留下的全部归档物」。

---

## 二、步骤 ↔ 真实 GitLab 对照

| 教科书步骤 | Demo 怎么做 | 真实 GitLab |
|------------|-------------|-------------|
| MR 触发 | `checkout_sim.py` 写入 event | Webhook / MR 事件 |
| 代码拉取 | 同上，记录 commit / 文件列表 | Runner 自动 clone（通常无单独 Job） |
| Lint | `ruff check` | 同左 |
| 静态扫描 | `scripts/scan.py`（教学替身） | SonarQube 等 |
| 单元测试 | `pytest tests/smoke -m smoke` | 同左 |
| 编译构建 | `scripts/build.py` | 编译 / 打包脚本 |
| 产出制品 | `dist/` + SHA 文件名 | 包 / 镜像（禁 latest） |
| 报告归档 | `scripts/archive.py` | `artifacts:` 可下载归档 |

---

## 三、目录结构

```
mini-pipeline/
├── app/                       # 被测小应用
├── tests/smoke|gate1|full|release/
├── scripts/
│   ├── checkout_sim.py        # 触发 + 拉代码（模拟）
│   ├── scan.py                # 静态扫描（模拟 Sonar）
│   ├── build.py               # 构建制品
│   └── archive.py             # 报告归档
├── run_pipeline.py            # 本地流水线模拟器
├── .gitlab-ci.yml.example
└── requirements.txt
```

---

## 四、其它门禁（可选，学多门禁时）

标准全流程之外，仍可用 `--gate` 看「同一仓库、不同触发、不同 case」：

| 命令 | 含义 |
|------|------|
| `python run_pipeline.py --gate standard` | **完整教科书路径（默认）** |
| `python run_pipeline.py --gate mr_fast` | MR 快路径：checkout → lint → test |
| `python run_pipeline.py --gate gate1` | 合入主干：含 scan / gate1 case / build / archive |
| `python run_pipeline.py --gate daily` | Daily：全量 case |
| `python run_pipeline.py --gate release` | 发版：构建 + 发版验收 + 归档 |
| `python run_pipeline.py --all` | standard + 上述门禁依次跑 |

---

## 五、建议学习顺序

1. 先跑 `python run_pipeline.py`，按 Job 日志对照教科书 7 步  
2. 打开 `artifacts/archive/*/MANIFEST.json` 看归档清单  
3. 对照 `.gitlab-ci.yml.example` 的 `stages:`  
4. 故意在 `app/` 加一行 `eval("1")`，再跑，观察 **scan 质量门禁变红**  
5. 改测试让断言失败，观察 **unit_test 红 → 流水线停**  
6. 再学 `--gate mr_fast` 等，理解「全流程」与「多门禁裁剪」的关系  

---

## 六、常见问题

**直接敲 `ruff check ...` 提示找不到命令？**  
`.gitlab-ci.yml` 不会在本机自动生效。本地必须先进入本目录并装依赖：

```powershell
cd ...\demos\mini-pipeline
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 推荐（不依赖 PATH 里有没有 ruff.exe）
python -m ruff check app tests scripts

# 或直接跑整条流水线（含 lint）
python run_pipeline.py
```

yml 里的 `before_script`（建 venv + `pip install`）在 **GitLab Runner** 上才会自动执行；你本机要自己做等价步骤。

**为什么真实 GitLab 很少单独写 checkout Job？**  
Runner 接 Job 前已经 clone 好仓库。Demo 把它写成 Job，只为让「代码拉取」这一步可见、可对照背诵。

**scan 是真 Sonar 吗？**  
不是。是本地轻量规则引擎，角色等价于「静态扫描 + 质量门禁」；面试说 SonarQube 即可。

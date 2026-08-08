# 4. 与 pytest 的衔接

> 前置能力来自 [02-pytest/](../02-pytest/README.md)。这里只讲「怎么写进 GitLab Job」。

## 三件套

1. **`script: pytest ...`** → 不同 Job + 不同 `rules`  
2. **报告当 artifacts** → `--junitxml=report.xml`  
3. **cache 加速** → `.venv` / pip 缓存（可选）

---

## 多门禁 Job 示意

```yaml
stages:
  - test

mr_smoke:
  stage: test
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
  script:
    - pip install -r requirements.txt
    - pytest tests/smoke -m smoke -v --junitxml=report-mr.xml
  artifacts:
    when: always
    paths: [report-mr.xml]
    reports:
      junit: report-mr.xml

gate1_critical:
  stage: test
  rules:
    - if: $CI_COMMIT_BRANCH == "main" && $CI_PIPELINE_SOURCE == "push"
  script:
    - pip install -r requirements.txt
    - pytest tests/gate1 -m gate1 -v --junitxml=report-gate1.xml
  artifacts:
    when: always
    paths: [report-gate1.xml]
    reports:
      junit: report-gate1.xml
```

本地可对照：[../02-pytest/demos/04-ci/](../02-pytest/demos/04-ci/) 与本目录 [demos/mini-pipeline/](./demos/mini-pipeline/)。

---

## 为什么 `when: always`？

测试失败时也要留下 JUnit / 日志片段，否则「红了但报告没了」，排查更慢。

---

## cache 示例（测 Job）

```yaml
.test_template:
  cache:
    key: venv-$CI_COMMIT_REF_SLUG
    paths:
      - .venv/
  before_script:
    - python -m venv .venv
    - source .venv/bin/activate
    - pip install -r requirements.txt
```

注意：Cache 丢了最多变慢，不能当「制品交付」；正式包仍走 artifacts。

---

## 失败链路（面试常问）

```
pytest 断言失败
  → 进程退出码非 0
  → Job failed
  → Pipeline 红
  → MR 合并门禁拦住（若开启）
```

排查时：先打开 Job 日志读 pytest 失败栈，再对照本地同命令复现（见 pytest 模块「失败阅读」）。

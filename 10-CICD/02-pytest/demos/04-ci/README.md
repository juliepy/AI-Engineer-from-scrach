# Demo 04｜失败阅读与 CI 衔接

对应文档：[04-失败阅读与CI衔接.md](../../04-失败阅读与CI衔接.md)

## 1）模拟 MR Job（含故意失败 + JUnit 报告）

```bash
cd demos/04-ci
pip install -r requirements.txt

# 等同 .gitlab-ci.yml.example 里 mr_smoke 的 script
pytest tests/smoke -m smoke -v --junitxml=report-mr.xml
echo $LASTEXITCODE   # Windows：应为非 0

# 打开报告看 XML 里是否记录了失败
# report-mr.xml
```

读日志时盯三行：

1. `FAILED tests/smoke/test_mr.py::test_mr_smoke_fail_for_log_reading`  
2. `assert 2 == 3`  
3. 退出码非 0 → 门禁红  

只要绿报告时：

```bash
pytest tests/smoke -m smoke -k "not fail_for_log" -v --junitxml=report-mr.xml
echo $LASTEXITCODE   # 应为 0
```

## 2）模拟 Gate1 Job

```bash
pytest tests/gate1 -m gate1 -v --junitxml=report-gate1.xml
```

## 3）模拟依赖缺失（Error，不是普通 Failed）

```bash
pytest tests/broken -v
```

会看到 `ModuleNotFoundError` / ERROR，体会和断言失败的差别。

## 4）对照 yml

打开 [.gitlab-ci.yml.example](./.gitlab-ci.yml.example)：  
本地刚才敲的命令 = CI 里 `script:` 做的事；`report-*.xml` = `artifacts` / JUnit 报告。

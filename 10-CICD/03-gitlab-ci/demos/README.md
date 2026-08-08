# demos｜GitLab CI

| Demo | 说明 |
|------|------|
| [mini-pipeline/](./mini-pipeline/) | **可本地跑通的完整流水线**：lint → 多门禁 pytest → 构建制品 → 发版验收 |

入口：

```bash
cd mini-pipeline
python -m venv .venv
# Windows: .\.venv\Scripts\Activate.ps1
# Linux:   source .venv/bin/activate
pip install -r requirements.txt
python run_pipeline.py          # 完整：checkout→lint→scan→test→build→archive
```

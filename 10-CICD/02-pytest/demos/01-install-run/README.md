# Demo 01｜安装与第一次跑通

对应文档：[01-安装与运行.md](../../01-安装与运行.md)

## 准备（WSL 务必用 venv）

若直接 `pip install` 报 `externally-managed-environment`，先回上两级建环境：

```bash
cd ../..                                    # 到 02-pytest/
python3 -m venv .venv
source .venv/bin/activate
python -m pip install pytest
cd demos/01-install-run
pytest --version
```

## 运行

```bash
# 详细输出：会看到 1 passed, 1 failed
pytest -v

# 看退出码（失败应为非 0）
echo $?                 # bash / WSL
# echo $LASTEXITCODE    # Windows PowerShell
```

## 你要观察到什么

| 现象 | 含义 |
|------|------|
| `test_add_pass` PASSED | 绿 |
| `test_add_fail` FAILED | 红，并打印 `assert 2 == 3` |
| 退出码非 0 | CI 里就会让 Job 失败 |

练完后可把 `test_add_fail` 改成 `== 2` 再跑一次，确认退出码变 0。

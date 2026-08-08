# Demo 03｜marker 与门禁分流

对应文档：[03-marker与门禁分流.md](../../03-marker与门禁分流.md)

## 运行（请在本目录执行）

```bash
cd demos/03-markers

# 四门禁各自跑（推荐背这四条）
pytest -m smoke -v
pytest -m gate1 -v
pytest -m full -v
pytest -m release -v

# 按目录跑
pytest tests/smoke -v
pytest tests/gate1 -v

# 组合 / 排除
pytest -m "smoke or gate1" -v
pytest -m "not full" -v
```

## 陷阱对比（必做）

```bash
# 按目录：会包含 test_mismatch_trap（虽标了 full）
pytest tests/smoke -v

# 按 marker：MR 正确，不会包含那个 full
pytest -m smoke -v
```

## 预期用例数（大约）

| 命令 | 大约条数 | 说明 |
|------|----------|------|
| `-m smoke` | 2 | 不含 mismatch |
| `tests/smoke` | 3 | 含 mismatch（陷阱） |
| `-m gate1` | 2 | |
| `-m full` | 3 | full 目录 2 条 + smoke 里那条陷阱 |
| `-m release` | 2 | |

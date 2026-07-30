# Environments Demo · 真源码 LocalEnvironment

**不改 Hermes 源码。** 把完整 `hermes-agent` 加到 `PYTHONPATH`，直接 `from tools.environments.local import LocalEnvironment`。

对照讲稿：[`../notes/01_base_environment.md`](../notes/01_base_environment.md)、[`../notes/02_local_vs_docker.md`](../notes/02_local_vs_docker.md)。

---

## 跑法

```bash
cd 05-env/demo

# 默认会找与 AI_coding_interview 同级的 hermes-agent/
# 找不到时手动指定：
#   set HERMES_AGENT_ROOT=D:\workspace\doc\面试狂魔\人工智能面试题\hermes-agent

python run_local_env.py
```

产物：`exports/local_env/01_report.md`、`00_raw.json`。

---

## 调了哪段真源码

| 调用 | 文件（hermes-agent） |
|------|----------------------|
| `LocalEnvironment` | `tools/environments/local.py` |
| `init_session` / `execute` / `_wrap_command` / `_wait_for_process` | `tools/environments/base.py` |
| `_run_bash` → `Popen(bash -c)` | `local.py` |

教材剪枝对照：[`../hermes_src/tools/environments/`](../hermes_src/tools/environments/)（只读；本 demo **不**从剪枝树 import）。

---

## Call flow

```text
run_local_env.main()
  sys.path ← hermes-agent/
  LocalEnvironment(cwd=demo/)
       └─ init_session()
  for cmd in [echo / pwd / HOME / true]:
       env.execute(cmd)   # 真 BaseEnvironment.execute
  env.cleanup()
  → exports/local_env/
```

# LocalEnvironment demo

- hermes_agent_root: `D:\workspace\doc\面试狂魔\人工智能面试题\hermes-agent`
- source: `tools/environments/local.py` (unmodified)
- generated: 2026-07-30T02:36:39.092270+00:00

## Probes

| command | rc | output | cwd_after |
|---------|----|--------|-----------|
| `echo hermes-env-ok` | 0 | `hermes-env-ok` | `D:\workspace\doc\面试狂魔\人工智能面试题\AI_coding_interview\08-hermes-agent\05-env\demo` |
| `pwd` | 0 | `/d/workspace/doc/面试狂魔/人工智能面试题/AI_coding_interview/08-hermes-agent/05-env/demo` | `D:\workspace\doc\面试狂魔\人工智能面试题\AI_coding_interview\08-hermes-agent\05-env\demo` |
| `echo HOME=$HOME` | 0 | `HOME=/c/Users/86137` | `D:\workspace\doc\面试狂魔\人工智能面试题\AI_coding_interview\08-hermes-agent\05-env\demo` |
| `true` | 0 | `` | `D:\workspace\doc\面试狂魔\人工智能面试题\AI_coding_interview\08-hermes-agent\05-env\demo` |

## Call flow

```text
LocalEnvironment(cwd)
  └─ init_session()          # BaseEnvironment
execute(cmd)
  ├─ _wrap_command()         # source snapshot → cd → eval → CWD marker
  ├─ _run_bash()             # local.py · Popen(bash -c)
  ├─ _wait_for_process()     # base.py
  └─ _update_cwd()
```

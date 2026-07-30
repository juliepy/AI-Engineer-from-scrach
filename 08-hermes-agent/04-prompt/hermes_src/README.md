# hermes_src · Prompt 相关源码剪枝

只读对照。来源：

| 文件 | 来源 |
|------|------|
| `agent/prompt_builder.py` | 上游 main（2026-07 拉取） |
| `agent/system_prompt.py` | 上游 main |
| `agent/title_generator.py` | 上游 main |
| `agent/curator.py` | 上游 main |
| `agent/skill_commands.py` | 上游 main |
| `agent/subdirectory_hints.py` | 上游 main |
| `agent/context_compressor.py` | 本地 `hermes-study` 副本 |
| `agent/prompt_template_teaching.py` | 本地 `01-memory` 教学拆解 |
| `prompt-assembly.md` | 上游 docs |

刷新上游文件后跑：

```powershell
python ../scripts/extract_prompts.py
```

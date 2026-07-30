# Session Log Slice

session_id: `sess_eval_demo`

## Live emit (teaching logger)

```text
2026-07-29 20:19:45,371 INFO [sess_eval_demo] agent.conversation_loop: API call #1: model=deepseek cache=hit
2026-07-29 20:19:45,372 INFO [sess_eval_demo] tools.web_search: web_search query=conversation_loop
2026-07-29 20:19:45,372 INFO [sess_eval_demo] gateway.platforms.telegram: delivery ok chat=123
2026-07-29 20:19:45,372 WARNING [sess_eval_demo] agent.conversation_loop: budget remaining=0 → grace call
2026-07-29 20:19:45,372 ERROR [sess_eval_demo] tools.registry: dispatch failed: tool not found
2026-07-29 20:19:45,373 INFO hermes_cli.main: cli idle
```

## errors.log (WARNING+)

```text
2026-07-29 20:19:45,372 WARNING [sess_eval_demo] agent.conversation_loop: budget remaining=0 → grace call
2026-07-29 20:19:45,372 ERROR [sess_eval_demo] tools.registry: dispatch failed: tool not found
```

## component=agent

```text
2026-07-29 20:19:45,371 INFO [sess_eval_demo] agent.conversation_loop: API call #1: model=deepseek cache=hit
2026-07-29 20:19:45,372 WARNING [sess_eval_demo] agent.conversation_loop: budget remaining=0 → grace call
```

## Filter live agent log by session

```text
2026-07-29 20:19:45,371 INFO [sess_eval_demo] agent.conversation_loop: API call #1: model=deepseek cache=hit
2026-07-29 20:19:45,372 INFO [sess_eval_demo] tools.web_search: web_search query=conversation_loop
2026-07-29 20:19:45,372 INFO [sess_eval_demo] gateway.platforms.telegram: delivery ok chat=123
2026-07-29 20:19:45,372 WARNING [sess_eval_demo] agent.conversation_loop: budget remaining=0 → grace call
2026-07-29 20:19:45,372 ERROR [sess_eval_demo] tools.registry: dispatch failed: tool not found
```

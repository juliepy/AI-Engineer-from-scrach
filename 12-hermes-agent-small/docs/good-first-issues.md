# Good first issues (to file on GitHub after publishing)

Each of these is deliberately shaped like a first PR: one file, a clear reference
implementation to imitate, and a way to verify.

1. **Discord gateway** — `waku/gateway/discord.py` mirroring the Telegram one
   (discord.py, message-in → `waku.respond()` → message-out). Reference:
   `waku/gateway/telegram.py`. Verify: chat with your bot.

2. **WhatsApp gateway (Meta Cloud API)** — same shape, webhook-based; document the
   Meta setup pain honestly in the module docstring. Reference: `waku/gateway/telegram.py`.

3. **Google Calendar adapter** — swap the internals of `waku/tools/calendar.py`
   behind the same tool schema (env-gated, mock stays the default). Verify: the
   deterministic eval still passes against the mock.

4. **Notion episodic adapter** — `waku/memory/episodic/notion_store.py` with the
   same `add`/`search`/`recent` interface. Reference: `SqliteEpisodeStore`.

5. **`/memory` CLI command** — in the REPL, show what Waku knows: facts, episodes,
   and unconsolidated chat count. Pure SQLite reads; great for demos.

6. **Trace pretty-printer** — `python -m waku.ops.show_trace [file]` renders a
   JSONL trace as an indented timeline in the terminal (rich). No OTel needed.

7. **Community skills** — not an issue, a standing invitation: `skills/TEMPLATE.md`.

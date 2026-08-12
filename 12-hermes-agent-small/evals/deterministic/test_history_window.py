"""DETERMINISTIC EVAL — working memory is a bounded sliding window.

Sean's insight while testing Telegram: its one always-on session accumulated
history forever, and every turn resent the whole thing (unbounded context ->
cost/latency climb -> eventual context-limit break). Working memory must be a
fixed window; older turns live in state.db + consolidation, not the prompt.

Note: chat_log keeps *all* turns (consolidation reads them). The window only
applies when assembling the prompt from session.history."""

from __future__ import annotations

from evals.helpers import ScriptedClient, make_waku, response, text_block


def _gate_skip():
    return response([text_block('{"retrieve": false, "query": "", "reason": "t"}')])


def test_prompt_history_is_windowed(tmp_path, monkeypatch):
    monkeypatch.setenv("WAKU_HISTORY_TURNS", "3")
    script = []
    for _ in range(5):
        script += [_gate_skip(), response([text_block("ok")])]
    app = make_waku(tmp_path / "home", client=ScriptedClient(script))
    for i in range(5):
        app.respond(f"message number {i}")

    # same slice respond() feeds the model: last N turns (2 rows each)
    window = app.settings.history_turns * 2
    prompt_msgs = app.session.history[-window:]
    blob = " ".join(m["content"] for m in prompt_msgs)

    assert len(prompt_msgs) <= window
    assert "message number 0" not in blob   # oldest turn dropped from prompt
    assert "message number 4" in blob       # newest turn still there

    # chat_log still has the full thread (5 turns × user+assistant)
    n = app.conn.execute("SELECT COUNT(*) FROM chat_log").fetchone()[0]
    assert n == 10


def test_default_window_is_generous_but_finite(tmp_path, monkeypatch):
    monkeypatch.delenv("WAKU_HISTORY_TURNS", raising=False)
    app = make_waku(tmp_path / "home", client=ScriptedClient([]))
    assert app.settings.history_turns == 12

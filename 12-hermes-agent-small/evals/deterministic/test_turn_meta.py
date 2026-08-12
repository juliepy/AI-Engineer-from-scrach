"""DETERMINISTIC EVAL — per-turn telemetry is persisted and reloadable.

Sean's catch: reopening a chat thread dropped the gate decision, seconds, and
iterations because they were only ever computed live, never saved. Now the
assistant row carries a meta JSON so a restored thread renders the full card."""

from __future__ import annotations

import json

from evals.helpers import ScriptedClient, make_waku, response, text_block, tool_block


def test_turn_meta_is_saved_with_gate_and_iterations(tmp_path):
    """有工具调用时，assistant 行应持久化 gate、iterations、tools、model 等 meta。"""
    gate = response([text_block('{"retrieve": true, "query": "alex", "reason": "asks about alex"}')])
    turn = [
        response([tool_block("save_note", {"subject": "alex", "content": "likes mornings"})], "tool_use"),
        response([text_block("Noted.")]),
    ]
    app = make_waku(tmp_path / "home", client=ScriptedClient([gate] + turn))
    app.respond("remember alex likes mornings")

    row = app.conn.execute(
        "SELECT meta FROM chat_log WHERE role='assistant' ORDER BY id DESC LIMIT 1"
    ).fetchone()
    meta = json.loads(row["meta"])
    assert meta["gate"]["decision"] == "retrieve"
    assert meta["iterations"] == 2                    # tool turn + final answer
    assert isinstance(meta["latency_ms"], int)
    assert [t["tool"] for t in meta["tools"]] == ["save_note"]
    # which brain answered — shown per card, survives a reopened thread
    assert meta["model"] == app.settings.model
    assert meta["provider"] == app.settings.provider


def test_no_tool_turn_still_saves_meta(tmp_path):
    """无工具调用时仍应写入 meta，gate 为 skip，tools 为空列表。"""
    gate = response([text_block('{"retrieve": false, "query": "", "reason": "math"}')])
    app = make_waku(tmp_path / "home", client=ScriptedClient([gate, response([text_block("4")])]))
    app.respond("what is 2+2?")
    row = app.conn.execute(
        "SELECT meta FROM chat_log WHERE role='assistant' ORDER BY id DESC LIMIT 1"
    ).fetchone()
    meta = json.loads(row["meta"])
    assert meta["gate"]["decision"] == "skip"
    assert meta["tools"] == []


def test_old_rows_without_meta_are_tolerated(tmp_path):
    """meta 出现前写入的旧行（NULL）必须能兼容，不能导致崩溃。"""
    app = make_waku(tmp_path / "home", client=ScriptedClient([]))
    app.memory.log_chat("hi", "hello", session_id="s1", source="cli", meta=None)
    row = app.conn.execute(
        "SELECT meta FROM chat_log WHERE role='assistant'"
    ).fetchone()
    assert row["meta"] is None

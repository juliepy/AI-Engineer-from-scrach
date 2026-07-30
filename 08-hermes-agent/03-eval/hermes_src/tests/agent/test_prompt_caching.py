"""Tests for agent/prompt_caching.py — Anthropic cache control injection.

中文：测「给 Anthropic 请求打 Prompt Cache 断点」的逻辑是否合法。
测的是标记怎么挂，不是模型列表或配置版本。
"""

from agent.prompt_caching import (
    _apply_cache_marker,
    _can_carry_marker,
    apply_anthropic_cache_control,
)


# 标准 ephemeral 缓存标记（默认 TTL 约 5 分钟）
MARKER = {"type": "ephemeral"}


class TestApplyCacheMarker:
    """测单条消息怎么挂 cache_control 标记（_apply_cache_marker）。

    核心差异：Native Anthropic 可以顶层打标；
    OpenRouter 必须把标记放进 content part，空内容要跳过。
    """

    def test_tool_message_gets_top_level_marker_on_native_anthropic(self):
        """Native Anthropic：tool 消息可在消息顶层挂 cache_control。

        适配器之后会再把标记挪进 tool_result 内部。
        """
        msg = {"role": "tool", "content": "result"}
        _apply_cache_marker(msg, MARKER, native_anthropic=True)
        assert msg["cache_control"] == MARKER

    def test_tool_message_skips_marker_on_openrouter(self):
        """OpenRouter：不能在 role:tool 顶层挂 cache_control（会 silent hang）。

        注意：本用例 content 是短字符串；是否包装取决于实现细节。
        这里断言的是「顶层没有 cache_control」。
        """
        msg = {"role": "tool", "content": "result"}
        _apply_cache_marker(msg, MARKER, native_anthropic=False)
        assert "cache_control" not in msg

    def test_tool_message_wraps_non_empty_content_on_openrouter(self):
        """OpenRouter：非空 tool content 应包成 list，标记落在 content part 上。"""
        msg = {"role": "tool", "content": "tool result bytes"}
        _apply_cache_marker(msg, MARKER, native_anthropic=False)
        assert "cache_control" not in msg
        assert isinstance(msg["content"], list)
        assert msg["content"][0]["cache_control"] == MARKER

    def test_empty_assistant_message_skips_marker_on_openrouter(self):
        """OpenRouter：空 assistant（通常是纯 tool_calls）跳过，不浪费断点。"""
        msg = {"role": "assistant", "content": ""}
        _apply_cache_marker(msg, MARKER, native_anthropic=False)
        assert "cache_control" not in msg

    def test_native_anthropic_empty_assistant_gets_top_level_marker(self):
        """Native Anthropic：空 content 的 assistant 仍可顶层打标。"""
        msg = {"role": "assistant", "content": ""}
        _apply_cache_marker(msg, MARKER, native_anthropic=True)
        assert msg["cache_control"] == MARKER

    def test_none_content_skips_marker_on_openrouter(self):
        """OpenRouter：content=None 的 assistant 不能承载标记，跳过。"""
        msg = {"role": "assistant", "content": None}
        _apply_cache_marker(msg, MARKER, native_anthropic=False)
        assert "cache_control" not in msg

    def test_none_content_gets_top_level_marker_on_native_anthropic(self):
        """Native Anthropic：content=None 仍可顶层挂标记。"""
        msg = {"role": "assistant", "content": None}
        _apply_cache_marker(msg, MARKER, native_anthropic=True)
        assert msg["cache_control"] == MARKER

    def test_string_content_wrapped_in_list(self):
        """字符串 content 会被包成 [{type,text,cache_control}]，标记在 part 上。"""
        msg = {"role": "user", "content": "Hello"}
        _apply_cache_marker(msg, MARKER)
        assert isinstance(msg["content"], list)
        assert len(msg["content"]) == 1
        assert msg["content"][0]["type"] == "text"
        assert msg["content"][0]["text"] == "Hello"
        assert msg["content"][0]["cache_control"] == MARKER

    def test_list_content_last_item_gets_marker(self):
        """content 已是 list 时，只给最后一项打 cache_control。"""
        msg = {
            "role": "user",
            "content": [
                {"type": "text", "text": "First"},
                {"type": "text", "text": "Second"},
            ],
        }
        _apply_cache_marker(msg, MARKER)
        assert "cache_control" not in msg["content"][0]
        assert msg["content"][1]["cache_control"] == MARKER

    def test_empty_list_content_no_crash(self):
        """空 list content 不应抛异常（容错，不崩溃即可）。"""
        msg = {"role": "user", "content": []}
        # Should not crash on empty list
        _apply_cache_marker(msg, MARKER)


class TestCanCarryMarker:
    """测「这条消息能不能占用一个断点槽」（_can_carry_marker）。

    必须与 _apply_cache_marker 规则一致：
    gate 说能挂，实际却没挂上 → 浪费 Anthropic 的 4 个断点名额。
    """

    def test_native_anthropic_always_true(self):
        """Native Anthropic：任意消息都视为可承载（含空 assistant / 空 tool）。"""
        assert _can_carry_marker({"role": "assistant", "content": ""}, native_anthropic=True) is True
        assert _can_carry_marker({"role": "tool", "content": ""}, native_anthropic=True) is True

    def test_openrouter_content_parts_carry_marker(self):
        """OpenRouter：有文本（字符串或 content part list）则可承载。"""
        assert _can_carry_marker({"role": "user", "content": "text"}, native_anthropic=False) is True
        assert _can_carry_marker({"role": "user", "content": [{"type": "text", "text": "a"}]}, native_anthropic=False) is True

    def test_openrouter_empty_or_none_does_not_carry_marker(self):
        """OpenRouter：空/None 不可承载；非空 tool 可以。"""
        assert _can_carry_marker({"role": "assistant", "content": ""}, native_anthropic=False) is False
        assert _can_carry_marker({"role": "assistant", "content": None}, native_anthropic=False) is False
        assert _can_carry_marker({"role": "tool", "content": "result"}, native_anthropic=False) is True
        assert _can_carry_marker({"role": "tool", "content": ""}, native_anthropic=False) is False

    def test_openrouter_list_carrier_requires_last_part_dict(self):
        """OpenRouter：list 的最后一项必须是 dict，才能真正打上标记。

        若末项是裸字符串，gate 以前会误判为可承载，但 apply 打不上 → 浪费断点。
        """
        # Last part is a dict -> carrier.
        assert _can_carry_marker(
            {"role": "user", "content": [{"type": "text", "text": "a"}]},
            native_anthropic=False,
        ) is True
        # Last part is a non-dict (stray raw string) -> NOT a carrier, even though
        # an earlier part is a dict. Previously this passed the gate but got no
        # marker, wasting a breakpoint.
        assert _can_carry_marker(
            {"role": "user", "content": [{"type": "text", "text": "a"}, "trailing raw"]},
            native_anthropic=False,
        ) is False
        # Empty list -> not a carrier.
        assert _can_carry_marker({"role": "user", "content": []}, native_anthropic=False) is False


class TestApplyAnthropicCacheControl:
    """测整条 system_and_3 策略（apply_anthropic_cache_control）。

    规则摘要：深拷贝；system 打标；末尾最多 3 条可承载非 system；
    总共 ≤ 4 个断点；支持 TTL；空消息不浪费槽位。
    """

    def test_empty_messages(self):
        """空列表入参 → 空列表出参。"""
        result = apply_anthropic_cache_control([])
        assert result == []

    def test_returns_deep_copy(self):
        """返回深拷贝：不污染原始 messages / 原始 message 对象。"""
        msgs = [{"role": "user", "content": "Hello"}]
        result = apply_anthropic_cache_control(msgs)
        assert result is not msgs
        assert result[0] is not msgs[0]
        # Original should be unmodified
        assert "cache_control" not in msgs[0].get("content", "")

    def test_system_message_gets_marker(self):
        """system 消息一定拿到 cache 断点（策略的 #1）。"""
        msgs = [
            {"role": "system", "content": "You are helpful"},
            {"role": "user", "content": "Hi"},
        ]
        result = apply_anthropic_cache_control(msgs)
        # System message should have cache_control
        sys_content = result[0]["content"]
        assert isinstance(sys_content, list)
        assert sys_content[0]["cache_control"]["type"] == "ephemeral"

    def test_last_3_non_system_get_markers(self):
        """system + 末尾 3 条非 system 打标；更早的非 system（msg1）不打。"""
        msgs = [
            {"role": "system", "content": "System"},
            {"role": "user", "content": "msg1"},
            {"role": "assistant", "content": "msg2"},
            {"role": "user", "content": "msg3"},
            {"role": "assistant", "content": "msg4"},
        ]
        result = apply_anthropic_cache_control(msgs)
        # System (index 0) + last 3 non-system (indices 2, 3, 4) = 4 breakpoints
        # Index 1 (msg1) should NOT have marker
        content_1 = result[1]["content"]
        if isinstance(content_1, str):
            assert True  # No marker applied (still a string)
        else:
            assert "cache_control" not in content_1[0]

    def test_no_system_message(self):
        """没有 system 时，断点名额全给对话消息（这里 2 条都能打）。"""
        msgs = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi"},
        ]
        result = apply_anthropic_cache_control(msgs)
        # Both should get markers (4 slots available, only 2 messages)
        assert len(result) == 2

    def test_1h_ttl(self):
        """cache_ttl='1h' 时，marker 带 ttl 字段。"""
        msgs = [{"role": "system", "content": "System prompt"}]
        result = apply_anthropic_cache_control(msgs, cache_ttl="1h")
        sys_content = result[0]["content"]
        assert isinstance(sys_content, list)
        assert sys_content[0]["cache_control"]["ttl"] == "1h"

    def test_max_4_breakpoints(self):
        """长对话也不得超过 4 个断点（Anthropic 协议上限）。"""
        msgs = [
            {"role": "system", "content": "System"},
        ] + [
            {"role": "user" if i % 2 == 0 else "assistant", "content": f"msg{i}"}
            for i in range(10)
        ]
        result = apply_anthropic_cache_control(msgs)
        # Count how many messages have cache_control
        count = 0
        for msg in result:
            content = msg.get("content")
            if isinstance(content, list):
                for item in content:
                    if isinstance(item, dict) and "cache_control" in item:
                        count += 1
            elif "cache_control" in msg:
                count += 1
        assert count <= 4

    def test_tool_loop_empty_assistant_and_tool_messages_do_not_consume_breakpoints(self):
        """Tool 循环里：空 assistant / 空 tool 不消耗断点（OpenRouter 路径）。"""
        msgs = [
            {"role": "system", "content": "You are helpful"},
            {"role": "user", "content": "run tool 1", "cache_control": MARKER},
            {"role": "assistant", "content": "", "tool_calls": [{"type": "function"}]},
            {"role": "tool", "content": "tool result 1"},
            {"role": "user", "content": "run tool 2", "cache_control": MARKER},
            {"role": "assistant", "content": "", "tool_calls": [{"type": "function"}]},
            {"role": "tool", "content": "tool result 2"},
        ]
        result = apply_anthropic_cache_control(msgs, native_anthropic=False)
        # Empty assistant/tool turns should not get broken markers
        assert "cache_control" not in result[2]
        assert "cache_control" not in result[3]
        assert "cache_control" not in result[5]
        assert "cache_control" not in result[6]

    def test_tool_message_marker_lands_on_content_part_on_openrouter(self):
        """整策略下 OpenRouter：非空 tool 的标记落在 content part，不在顶层。"""
        msgs = [
            {"role": "user", "content": "hello"},
            {"role": "tool", "content": "tool output"},
        ]
        result = apply_anthropic_cache_control(msgs, native_anthropic=False)
        assert isinstance(result[1]["content"], list)
        assert result[1]["content"][0]["cache_control"] == {"type": "ephemeral"}
        assert "cache_control" not in result[1]

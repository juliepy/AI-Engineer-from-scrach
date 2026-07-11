from agent import FakeLLM, run_agent_stub


def test_agent_calls_tool_once():
    replies = [
        '{"tool":"search","args":{"q":"Python"}}',
        "最终答案基于工具结果。",
    ]
    calls = []

    def search(q: str):
        calls.append(q)
        return ["doc1"]

    tools = {"search": search}
    out = run_agent_stub("查 Python", tools, FakeLLM(replies))
    assert calls == ["Python"]
    assert "最终" in out

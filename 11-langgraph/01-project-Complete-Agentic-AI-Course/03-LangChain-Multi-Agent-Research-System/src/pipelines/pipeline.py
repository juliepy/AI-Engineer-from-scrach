from src.agents.agents import build_search_agent, build_reader_agent, writer_chain, critic_chain


def _banner(title: str) -> None:
    line = "=" * 60
    print(f"\n{line}")
    print(f"  {title}")
    print(f"{line}")


def _pretty_print_messages(messages) -> None:
    """同 02：逐条 msg.pretty_print()，便于对照 Human / AI(tool_calls) / Tool / Final。"""
    print("\n--- messages (pretty_print) ---")
    for msg in messages:
        msg.pretty_print()
    print("--- end messages ---\n")


def _summarize_agent_trace(step_name: str, messages) -> dict:
    """从 messages 抽出本步 ReAct 圈数，方便末尾画 workflow 图。"""
    tool_rounds = 0
    tool_names: list[str] = []
    thoughts: list[str] = []

    for msg in messages:
        role = getattr(msg, "type", None) or msg.__class__.__name__
        tool_calls = getattr(msg, "tool_calls", None) or []
        content = (getattr(msg, "content", None) or "")
        if isinstance(content, list):
            content = " ".join(
                str(block.get("text", block)) if isinstance(block, dict) else str(block)
                for block in content
            )

        if tool_calls:
            tool_rounds += 1
            for tc in tool_calls:
                name = tc.get("name") if isinstance(tc, dict) else getattr(tc, "name", "?")
                tool_names.append(name)
            if content.strip():
                thoughts.append(content.strip()[:120])
        elif role in ("ai", "AIMessage") and content.strip() and not tool_calls:
            # 最终回答（无 tool_calls）
            thoughts.append(f"[final] {content.strip()[:120]}")

    summary = {
        "step": step_name,
        "message_count": len(messages),
        "tool_rounds": tool_rounds,
        "tools_called": tool_names,
        "calls_llm": True,
    }
    print(f"\n[trace] {step_name}: messages={summary['message_count']} | "
          f"tool_rounds={tool_rounds} | tools={tool_names}")
    return summary


def _print_chain_io(step_name: str, *, inputs: dict, output: str) -> None:
    """Writer / Critic 没有 messages，用相近格式打印一次 LLM 调用。"""
    print(f"\n--- {step_name} (chain · single LLM call) ---")
    print(f"type: Human")
    for key, value in inputs.items():
        text = value if isinstance(value, str) else str(value)
        preview = text if len(text) <= 500 else text[:500] + "\n... [truncated]"
        print(f"  {key}:\n{preview}\n")
    print(f"type: AI (final)")
    print(output)
    print(f"--- end {step_name} ---\n")


def _print_workflow_summary(topic: str, traces: list[dict]) -> None:
    """根据本次实际日志打印可直接画图的 workflow 摘要。"""
    _banner("WORKFLOW SUMMARY（根据本次 pretty log 绘制）")
    print(f"topic: {topic}\n")
    print("pipeline:")
    print("  User → Search Agent → Reader Agent → Writer Chain → Critic Chain → Out\n")

    for t in traces:
        step = t["step"]
        if t.get("kind") == "agent":
            rounds = t["tool_rounds"]
            tools = ", ".join(t["tools_called"]) or "(none)"
            print(f"  · {step}")
            print(f"      ⚡ LLM  yes | ReAct tool_rounds={rounds} | tools=[{tools}]")
            print(f"      messages={t['message_count']}  "
                  f"(Human → AI[+tool_calls] → Tool → … → AI final)")
        else:
            print(f"  · {step}")
            print(f"      ⚡ LLM  yes | kind=chain | single prompt→llm→parser call")

    print("\n画图提示:")
    print("  Agent 节点 = create_agent 内 ReAct 环（对照上面 tool_rounds）")
    print("  Chain 节点 = 一次 LLM 调用，无工具")
    print("  Tool 节点  = web_search / scrape_url（不 call LLM）")
    print("=" * 60 + "\n")


def run_research_pipeline(topic: str) -> dict:
    state: dict = {"topic": topic, "traces": []}

    # ── 1. Search Agent ──────────────────────────────────────────────────────
    _banner("STEP 1 · Search Agent ⚡ LLM + web_search")
    search_agent = build_search_agent()
    search_result = search_agent.invoke({
        "messages": [("user", f"Find recent, reliable and detailed information about: {topic}")]
    })
    search_messages = search_result["messages"]
    _pretty_print_messages(search_messages)
    state["search_results"] = search_messages[-1].content
    state["search_messages"] = search_messages
    state["traces"].append({
        **_summarize_agent_trace("Search Agent", search_messages),
        "kind": "agent",
    })

    # ── 2. Reader Agent ──────────────────────────────────────────────────────
    _banner("STEP 2 · Reader Agent ⚡ LLM + scrape_url")
    reader_agent = build_reader_agent()
    reader_result = reader_agent.invoke({
        "messages": [("user",
            f"Based on the following search results about '{topic}', "
            f"pick the most relevant URL and scrape it for deeper content.\n\n"
            f"Search Results:\n{state['search_results'][:800]}"
        )]
    })
    reader_messages = reader_result["messages"]
    _pretty_print_messages(reader_messages)
    state["scraped_content"] = reader_messages[-1].content
    state["reader_messages"] = reader_messages
    state["traces"].append({
        **_summarize_agent_trace("Reader Agent", reader_messages),
        "kind": "agent",
    })

    # ── 3. Writer Chain ──────────────────────────────────────────────────────
    _banner("STEP 3 · Writer Chain ⚡ LLM (prompt | llm | parser)")
    research_combined = (
        f"SEARCH RESULTS : \n {state['search_results']} \n\n"
        f"DETAILED SCRAPED CONTENT : \n {state['scraped_content']}"
    )
    writer_inputs = {"topic": topic, "research": research_combined}
    state["report"] = writer_chain.invoke(writer_inputs)
    _print_chain_io("Writer Chain", inputs=writer_inputs, output=state["report"])
    state["traces"].append({
        "step": "Writer Chain",
        "kind": "chain",
        "calls_llm": True,
        "tool_rounds": 0,
        "tools_called": [],
        "message_count": 2,  # human prompt + ai output（逻辑上）
    })

    # ── 4. Critic Chain ──────────────────────────────────────────────────────
    _banner("STEP 4 · Critic Chain ⚡ LLM (prompt | llm | parser)")
    critic_inputs = {"report": state["report"]}
    state["feedback"] = critic_chain.invoke(critic_inputs)
    _print_chain_io("Critic Chain", inputs=critic_inputs, output=state["feedback"])
    state["traces"].append({
        "step": "Critic Chain",
        "kind": "chain",
        "calls_llm": True,
        "tool_rounds": 0,
        "tools_called": [],
        "message_count": 2,
    })

    # ── 末尾：根据本次日志汇总，方便画 workflow 图 ───────────────────────────
    _print_workflow_summary(topic, state["traces"])
    return state

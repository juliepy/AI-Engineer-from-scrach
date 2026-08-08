""EXCERPT — not runnable. From agent/turn_context.py. Full file in hermes-agent.""

# --- L550-L579 ---
    # Notify memory providers of the new turn (BEFORE prefetch_all).
    if agent._memory_manager:
        try:
            _turn_msg = original_user_message if isinstance(original_user_message, str) else ""
            agent._memory_manager.on_turn_start(agent._user_turn_count, _turn_msg)
        except Exception:
            pass

    # External memory provider: prefetch once before the tool loop.
    ext_prefetch_cache = ""
    if agent._memory_manager:
        try:
            _query = original_user_message if isinstance(original_user_message, str) else ""
            ext_prefetch_cache = agent._memory_manager.prefetch_all(_query) or ""
        except Exception:
            pass

    return TurnContext(
        user_message=user_message,
        original_user_message=original_user_message,
        messages=messages,
        conversation_history=conversation_history,
        active_system_prompt=active_system_prompt,
        effective_task_id=effective_task_id,
        turn_id=turn_id,
        current_turn_user_idx=current_turn_user_idx,
        should_review_memory=should_review_memory,
        plugin_user_context=plugin_user_context,
        ext_prefetch_cache=ext_prefetch_cache,
    )

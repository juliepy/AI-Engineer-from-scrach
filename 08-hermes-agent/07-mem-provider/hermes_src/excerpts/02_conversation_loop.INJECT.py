""EXCERPT — not runnable. From agent/conversation_loop.py. Full file in hermes-agent.""

# --- L801-L856 ---
            if idx == current_turn_user_idx and msg.get("role") == "user":
                _injections = []
                if _ext_prefetch_cache:
                    _fenced = build_memory_context_block(_ext_prefetch_cache)
                    if _fenced:
                        _injections.append(_fenced)
                if _plugin_user_context:
                    _injections.append(_plugin_user_context)
                if _injections:
                    _base = api_msg.get("content", "")
                    if isinstance(_base, str):
                        api_msg["content"] = _base + "\n\n" + "\n\n".join(_injections)

            # For ALL assistant messages, pass reasoning back to the API
            # This ensures multi-turn reasoning context is preserved
            agent._copy_reasoning_content_for_api(msg, api_msg)

            # Remove 'reasoning' field - it's for trajectory storage only
            # We've copied it to 'reasoning_content' for the API above
            if "reasoning" in api_msg:
                api_msg.pop("reasoning")
            # Remove finish_reason - not accepted by strict APIs (e.g. Mistral)
            if "finish_reason" in api_msg:
                api_msg.pop("finish_reason")
            # Strip internal thinking-prefill marker
            api_msg.pop("_thinking_prefill", None)
            # Strip Codex Responses API fields (call_id, response_item_id) for
            # strict providers like Mistral, Fireworks, etc. that reject unknown fields.
            # Uses new dicts so the internal messages list retains the fields
            # for Codex Responses compatibility.
            if agent._should_sanitize_tool_calls():
                agent._sanitize_tool_calls_for_strict_api(api_msg, model=agent.model)
            # Keep 'reasoning_details' - OpenRouter uses this for multi-turn reasoning context
            # The signature field helps maintain reasoning continuity
            api_messages.append(api_msg)

        # Build the final system message: cached prompt + ephemeral system prompt.
        # Ephemeral additions are API-call-time only (not persisted to session DB).
        # External recall context is injected into the user message, not the system
        # prompt, so the stable cache prefix remains unchanged.
        #
        # NOTE: Plugin context from pre_llm_call hooks is injected into the
        # user message (see injection block above), NOT the system prompt.
        # This is intentional — system prompt modifications break the prompt
        # cache prefix.  The system prompt is reserved for Hermes internals.
        #
        # Hermes invariant: the system prompt is built ONCE per session
        # (cached on ``_cached_system_prompt``) and replayed verbatim on
        # every turn.  We send it as a single content string so the
        # bytes are byte-stable across turns and upstream prompt caches
        # stay warm.
        effective_system = active_system_prompt or ""
        if agent.ephemeral_system_prompt:
            effective_system = (effective_system + "\n\n" + agent.ephemeral_system_prompt).strip()
        if effective_system:
            api_messages = [{"role": "system", "content": effective_system}] + api_messages

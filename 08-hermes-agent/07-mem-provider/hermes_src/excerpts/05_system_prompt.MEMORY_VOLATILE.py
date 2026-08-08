""EXCERPT — not runnable. From agent/system_prompt.py. Full file in hermes-agent.""

# --- L457-L501 ---
    # ── Volatile tier (changes per session/turn — never cached) ───
    volatile_parts: List[str] = []

    if agent._memory_store:
        if agent._memory_enabled:
            mem_block = agent._memory_store.format_for_system_prompt("memory")
            if mem_block:
                volatile_parts.append(mem_block)
        # USER.md is always included when enabled.
        if agent._user_profile_enabled:
            user_block = agent._memory_store.format_for_system_prompt("user")
            if user_block:
                volatile_parts.append(user_block)

    # External memory provider system prompt block (additive to built-in)
    if agent._memory_manager:
        try:
            _ext_mem_block = agent._memory_manager.build_system_prompt()
            if _ext_mem_block:
                volatile_parts.append(_ext_mem_block)
        except Exception:
            pass

    from hermes_time import now as _hermes_now
    now = _hermes_now()
    # Date-only (not minute-precision) so the system prompt is byte-stable
    # for the full day.  Minute-precision changes invalidate prefix-cache KV
    # on every rebuild path (compression boundary, fresh-agent gateway turns,
    # session resume without a stored prompt).  The model can still query the
    # exact wall-clock time via tools when it actually needs it.
    # Credit: @iamfoz (PR #20451).
    timestamp_line = f"Conversation started: {now.strftime('%A, %B %d, %Y')}"
    if agent.pass_session_id and agent.session_id:
        timestamp_line += f"\nSession ID: {agent.session_id}"
    if agent.model:
        timestamp_line += f"\nModel: {agent.model}"
    if agent.provider:
        timestamp_line += f"\nProvider: {agent.provider}"
    volatile_parts.append(timestamp_line)

    return {
        "stable":   "\n\n".join(p.strip() for p in stable_parts   if p and p.strip()),
        "context":  "\n\n".join(p.strip() for p in context_parts  if p and p.strip()),
        "volatile": "\n\n".join(p.strip() for p in volatile_parts if p and p.strip()),
    }

# --- L504-L527 ---
def build_system_prompt(agent: Any, system_message: Optional[str] = None) -> str:
    """Assemble the full system prompt from all layers.

    Called once per session (cached on ``agent._cached_system_prompt``) and
    only rebuilt after context compression events. This ensures the system
    prompt is stable across all turns in a session, maximizing prefix cache
    hits.

    Layers are ordered cache-friendly: stable identity/guidance first,
    then session-stable context files, then per-call volatile content
    (memory, USER profile, timestamp).  The whole string is treated as
    one cached block — Hermes never rebuilds or reinjects parts of it
    mid-session, which is the only way to keep upstream prompt caches
    warm across turns.
    """
    parts = build_system_prompt_parts(agent, system_message=system_message)
    joined = "\n\n".join(p for p in (parts["stable"], parts["context"], parts["volatile"]) if p)

    # Surface context-file truncation warnings through the normal agent status
    # channel so gateway/CLI users see them in chat instead of only in logs.
    for warning in drain_truncation_warnings():
        agent._emit_status(warning)

    return joined

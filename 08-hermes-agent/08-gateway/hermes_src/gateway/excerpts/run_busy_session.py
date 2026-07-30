# Excerpt from gateway/run.py
# Runner busy-session guard (level 2)

# ===== lines 5360-5570 =====
                    # command text so the slash handlers parse modifiers via
                    # event.get_command_args().  Always use a literal "/" —
                    # MessageEvent.is_command()/get_command_args() only
                    # recognize the "/" prefix, not the per-platform display
                    # prefix ("!" on Slack/Matrix).
                    _verb = "approve" if _approval_handler is self._handle_approve_command else "deny"
                    _synth = f"/{_verb}"
                    if _normalized_args:
                        _synth = f"{_synth} {_normalized_args}"
                    event.text = _synth
                    _reply = await _approval_handler(event)
                    logger.info(
                        "Approval response via plain text: session=%s verb=%s args=%r",
                        session_key, _verb, _normalized_args,
                    )
                    _adapter = self._adapter_for_source(event.source)
                    if _adapter and _reply:
                        _text, _eph_ttl = _adapter._unwrap_ephemeral(_reply)
                        if _text:
                            _anchor = self._reply_anchor_for_event(event)
                            await _adapter._send_with_retry(
                                chat_id=event.source.chat_id,
                                content=_text,
                                reply_to=_anchor,
                                metadata=self._thread_metadata_for_source(event.source, _anchor),
                            )
                    return True
        except Exception:
            logger.warning(
                "Plain-text approval routing failed for session %s; "
                "falling through to busy handling",
                session_key, exc_info=True,
            )

        # Normal busy case (agent actively running a task)
        adapter = self._adapter_for_source(event.source)
        if not adapter:
            return False  # let default path handle it

        # --- Internal synthetic events must never interrupt/steer ---
        # Async-delegation completions (delegate_task(background=true)) and
        # background-process completions (terminal notify_on_complete) re-enter
        # the originating session as internal MessageEvents. When the session
        # is busy, treating them like a user TEXT message means interrupt-mode
        # (the default busy_text_mode) aborts the active turn AND sends a "⚡
        # Interrupting current task" ack — exactly the opposite of the design
        # invariant that a completion surfaces as a NEW turn only when idle and
        # never splices into a running turn. Fall through to the base adapter,
        # which queues internal events silently (no interrupt, no ack) so they
        # cascade after the current turn finishes.
        if getattr(event, "internal", False):
            return False

        running_agent = self._running_agents.get(session_key)

        effective_mode = self._busy_input_mode
        busy_text_mode = getattr(self, "_busy_text_mode", "interrupt")
        if (
            event.message_type == MessageType.TEXT
            and busy_text_mode == "queue"
            and effective_mode != "steer"
        ):
            return False

        # Steer mode: inject mid-run via running_agent.steer() instead of
        # queueing + interrupting.  If the agent isn't running yet
        # (sentinel) or lacks steer(), or the payload is empty, fall back
        # to queue semantics so nothing is lost.
        # #30170 — Subagent protection. ``AIAgent.interrupt()`` cascades
        # to every entry in the parent's ``_active_children`` list and
        # aborts in-flight ``delegate_task`` work. Demote ``interrupt``
        # to ``queue`` when the parent is currently driving subagents so
        # a conversational follow-up doesn't destroy minutes of subagent
        # work. Explicit ``/stop`` and ``/new`` slash commands go through
        # ``_interrupt_and_clear_session`` and are unaffected — the
        # operator still has a way to force-cancel everything.
        demoted_for_subagents = (
            effective_mode == "interrupt"
            and self._agent_has_active_subagents(running_agent)
        )
        if demoted_for_subagents:
            logger.info(
                "Demoting busy_input_mode 'interrupt' to 'queue' for session %s "
                "because the running agent has active subagents (#30170)",
                session_key,
            )
            effective_mode = "queue"
        demoted_for_compression = (
            effective_mode == "interrupt"
            and await self._session_has_compression_in_flight(session_key)
        )
        if demoted_for_compression:
            logger.info(
                "Demoting busy_input_mode 'interrupt' to 'queue' for session %s "
                "because context compression is in flight (#56391)",
                session_key,
            )
            effective_mode = "queue"
        steered = False
        if effective_mode == "steer":
            steer_text = (event.text or "").strip()
            can_steer = (
                steer_text
                and running_agent is not None
                and running_agent is not _AGENT_PENDING_SENTINEL
                and hasattr(running_agent, "steer")
            )
            if can_steer:
                try:
                    steered = bool(running_agent.steer(steer_text))
                except Exception as exc:
                    logger.warning("Gateway steer failed for session %s: %s", session_key, exc)
                    steered = False
            if not steered:
                # Fall back to queue (merge into pending messages, no interrupt)
                effective_mode = "queue"

        # Store the message so it's processed as the next turn after the
        # current run finishes (or is interrupted).  Skip this for a
        # successful steer — the text already landed inside the run and
        # must NOT also be replayed as a next-turn user message.
        #
        # Route through _queue_or_replace_pending_event (the same FIFO
        # infrastructure used by busy queue-mode and /queue) rather than a
        # raw merge_pending_message_event(merge_text=True). The raw merge
        # newline-joins consecutive TEXT follow-ups into a SINGLE pending
        # turn, destroying message boundaries — so two separate user
        # messages sent while the agent was busy (interrupt mode, or a
        # steer that fell back to queue) arrived as one mashed-together
        # turn (#43066 sub-bug 2). The FIFO path gives each text its own
        # turn in arrival order while still preserving photo-burst / album
        # merge semantics for media.
        if not steered:
            self._queue_or_replace_pending_event(session_key, event)

        is_queue_mode = effective_mode == "queue"
        is_steer_mode = effective_mode == "steer"

        # If not in queue/steer mode, interrupt the running agent immediately.
        # This aborts in-flight tool calls and causes the agent loop to exit
        # at the next check point.
        if effective_mode == "interrupt" and running_agent and running_agent is not _AGENT_PENDING_SENTINEL:
            try:
                running_agent.interrupt(event.text)
            except Exception:
                pass  # don't let interrupt failure block the ack

        # Check if busy ack is disabled — skip sending but still process the input.
        # Placed before debounce so we don't stamp a "last ack" timestamp that was
        # never actually delivered.
        busy_ack_enabled = os.environ.get("HERMES_GATEWAY_BUSY_ACK_ENABLED", "true").lower() == "true"
        if not busy_ack_enabled:
            logger.debug("Busy ack suppressed for session %s", session_key)
            return True  # input still processed, just no ack sent

        # Debounce before consulting config-heavy display settings. Rapid
        # follow-ups should be processed but should not trigger another config
        # read just to discover that no ack will be sent.
        _BUSY_ACK_COOLDOWN = 30
        now = time.time()
        last_ack = self._busy_ack_ts.get(session_key, 0)
        if now - last_ack < _BUSY_ACK_COOLDOWN:
            return True  # interrupt sent (if not queue), ack already delivered recently

        from gateway.display_config import resolve_display_setting
        platform_key = _platform_config_key(event.source.platform)

        # In steer mode the user's text has already been injected into the
        # active run. Some mobile chat setups want that steering to be silent,
        # like STT transcript echo suppression: keep the behavior, drop only
        # the confirmation bubble.
        if is_steer_mode:
            steer_ack_env = os.environ.get("HERMES_GATEWAY_BUSY_STEER_ACK_ENABLED")
            if steer_ack_env is not None:
                steer_ack_enabled = steer_ack_env.strip().lower() in {"1", "true", "yes", "on"}
            else:
                steer_ack_enabled = bool(
                    resolve_display_setting(
                        _load_gateway_config(),
                        platform_key,
                        "busy_steer_ack_enabled",
                        True,
                    )
                )
            if not steer_ack_enabled:
                logger.debug("Busy steer ack suppressed for session %s", session_key)
                return True

        self._busy_ack_ts[session_key] = now

        # Build a status-rich acknowledgment. Mobile chat defaults keep this
        # terse; detailed iteration/tool state is still available in logs and
        # can be opted in per platform via display.platforms.<platform>.busy_ack_detail.
        status_parts = []
        busy_ack_detail_enabled = bool(
            resolve_display_setting(
                _load_gateway_config(),
                _platform_config_key(event.source.platform),
                "busy_ack_detail",
                True,
            )
        )

        if busy_ack_detail_enabled and running_agent and running_agent is not _AGENT_PENDING_SENTINEL:
            try:
                summary = running_agent.get_activity_summary()
                iteration = summary.get("api_call_count", 0)
                max_iter = summary.get("max_iterations", 0)
                current_tool = summary.get("current_tool")
                start_ts = self._running_agents_ts.get(session_key, 0)
                if start_ts:


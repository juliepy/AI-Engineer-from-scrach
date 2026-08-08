""EXCERPT — not runnable. From run_agent.py. Full file in hermes-agent.""

# --- L3367-L3426 ---
    def _sync_external_memory_for_turn(
        self,
        *,
        original_user_message: Any,
        final_response: Any,
        interrupted: bool,
        messages: list | None = None,
    ) -> None:
        """Mirror a completed turn into external memory providers.

        Called at the end of ``run_conversation`` with the cleaned user
        message (``original_user_message``) and the finalised assistant
        response.  The external memory backend gets both ``sync_all`` (to
        persist the exchange) and ``queue_prefetch_all`` (to start
        warming context for the next turn) in one shot.

        Uses ``original_user_message`` rather than ``user_message``
        because the latter may carry injected skill content that bloats
        or breaks provider queries.

        Interrupted turns are skipped entirely (#15218).  A partial
        assistant output, an aborted tool chain, or a mid-stream reset
        is not durable conversational truth — mirroring it into an
        external memory backend pollutes future recall with state the
        user never saw completed.  The prefetch is gated on the same
        flag: the user's next message is almost certainly a retry of
        the same intent, and a prefetch keyed on the interrupted turn
        would fire against stale context.

        Normal completed turns still sync as before.  The whole body is
        wrapped in ``try/except Exception`` because external memory
        providers are strictly best-effort — a misconfigured or offline
        backend must not block the user from seeing their response.
        """
        if interrupted:
            return
        if not (self._memory_manager and final_response and original_user_message):
            return
        # Multimodal turns carry content as a list of typed parts; providers
        # expect plain strings, so flatten to text first (newline-joined for
        # memory, vs the default space-join used for log/trajectory previews).
        user_text = _summarize_user_message_for_log(original_user_message, sep="\n")
        response_text = _summarize_user_message_for_log(final_response, sep="\n")
        if not (user_text and response_text):
            return
        try:
            sync_kwargs = {"session_id": self.session_id or ""}
            if messages is not None:
                sync_kwargs["messages"] = messages
            self._memory_manager.sync_all(
                user_text,
                response_text,
                **sync_kwargs,
            )
            self._memory_manager.queue_prefetch_all(
                user_text,
                session_id=self.session_id or "",
            )
        except Exception:
            pass

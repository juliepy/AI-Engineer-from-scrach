import streamlit as st
from langchain_core.messages import AIMessage, ToolMessage
from langgraph.types import Command

from backend import chatbot
from backend.logger import get_logger

logger = get_logger(__name__)


def get_pending_interrupt(thread_id: str):
    """
    Return the first unresolved LangGraph interrupt for a thread.

    Returns:
        The pending Interrupt object, or None.
    """
    config = {
        "configurable": {
            "thread_id": thread_id,
        }
    }

    try:
        state_snapshot = chatbot.get_state(config)

        direct_interrupts = getattr(state_snapshot, "interrupts", ()) or ()
        if direct_interrupts:
            return direct_interrupts[0]

        tasks = getattr(state_snapshot, "tasks", ()) or ()
        for task in tasks:
            task_interrupts = getattr(task, "interrupts", ()) or ()
            if task_interrupts:
                return task_interrupts[0]

    except Exception:
        logger.debug(
            "No interrupt state yet | thread_id=%s",
            thread_id,
            exc_info=True,
        )
        return None

    return None


def save_pending_interrupt(thread_id: str, interrupt_object) -> None:
    """Save the pending interrupt information inside Streamlit state."""
    prompt = str(interrupt_object.value)
    st.session_state["pending_hitl"] = {
        "thread_id": thread_id,
        "prompt": prompt,
    }
    logger.info("Saved pending HITL | thread_id=%s | prompt=%s", thread_id, prompt)


def sync_pending_interrupt(thread_id: str) -> None:
    """
    Synchronize Streamlit HITL state with the LangGraph checkpoint.

    This allows a pending approval request to reappear after:
    - a Streamlit rerun
    - a browser refresh
    - switching between conversations
    """
    pending_interrupt = get_pending_interrupt(thread_id)

    if pending_interrupt is not None:
        save_pending_interrupt(thread_id, pending_interrupt)
        return

    current_pending = st.session_state.get("pending_hitl")
    if (
        current_pending is not None
        and current_pending.get("thread_id") == thread_id
    ):
        st.session_state["pending_hitl"] = None


def current_thread_has_pending_hitl() -> bool:
    pending_hitl = st.session_state.get("pending_hitl")
    return (
        pending_hitl is not None
        and pending_hitl.get("thread_id") == st.session_state["thread_id"]
    )


def resume_hitl_execution(decision: str) -> None:
    """
    Resume an interrupted LangGraph execution.

    Args:
        decision:
            "yes" approves the stock purchase.
            "no" rejects the stock purchase.
    """
    pending_hitl = st.session_state.get("pending_hitl")

    if not pending_hitl:
        logger.warning("HITL resume requested but no pending action exists")
        st.warning("There is no pending action to approve or reject.")
        return

    interrupted_thread_id = pending_hitl["thread_id"]
    logger.info(
        "Resuming HITL | thread_id=%s | decision=%s",
        interrupted_thread_id,
        decision,
    )
    resume_config = {
        "configurable": {
            "thread_id": interrupted_thread_id,
        },
        "metadata": {
            "thread_id": interrupted_thread_id,
        },
        "run_name": "hitl_resume_trace",
    }

    try:
        with st.chat_message("assistant"):
            status_holder = {
                "box": st.status(
                    "🔄 Resuming the requested action...",
                    expanded=True,
                )
            }

            def resumed_ai_only_stream():
                for message_chunk, metadata in chatbot.stream(
                    Command(resume=decision),
                    config=resume_config,
                    stream_mode="messages",
                ):
                    if isinstance(message_chunk, ToolMessage):
                        tool_name = getattr(message_chunk, "name", "tool")
                        status_holder["box"].update(
                            label=f"🔧 Using `{tool_name}` …",
                            state="running",
                            expanded=True,
                        )

                    if isinstance(message_chunk, AIMessage) and message_chunk.content:
                        yield message_chunk.content

            resumed_ai_message = st.write_stream(resumed_ai_only_stream())

            next_interrupt = get_pending_interrupt(interrupted_thread_id)

            if next_interrupt is not None:
                save_pending_interrupt(interrupted_thread_id, next_interrupt)
                status_holder["box"].update(
                    label="⚠️ Another approval is required",
                    state="complete",
                    expanded=False,
                )
            else:
                st.session_state["pending_hitl"] = None
                status_holder["box"].update(
                    label="✅ Action completed",
                    state="complete",
                    expanded=False,
                )

        if resumed_ai_message:
            st.session_state["message_history"].append(
                {
                    "role": "assistant",
                    "content": resumed_ai_message,
                }
            )

        logger.info("HITL resume completed | thread_id=%s", interrupted_thread_id)
        st.rerun()

    except Exception as error:
        logger.exception(
            "HITL resume failed | thread_id=%s | decision=%s",
            interrupted_thread_id,
            decision,
        )
        st.error(f"Could not resume the requested action: {error}")

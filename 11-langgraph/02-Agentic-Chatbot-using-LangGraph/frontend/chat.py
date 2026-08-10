import os
import tempfile

import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from backend import chatbot, ingest_rag_document
from backend.logger import get_logger
from frontend.hitl import (
    current_thread_has_pending_hitl,
    get_pending_interrupt,
    resume_hitl_execution,
    save_pending_interrupt,
)

logger = get_logger(__name__)


def render_message_history() -> None:
    for message in st.session_state["message_history"]:
        with st.chat_message(message["role"]):
            st.text(message["content"])


def render_hitl_approval() -> None:
    pending_hitl = st.session_state.get("pending_hitl")

    if not current_thread_has_pending_hitl():
        return

    st.warning(
        "🧑 Human approval required\n\n"
        f"{pending_hitl['prompt']}"
    )

    approve_column, reject_column = st.columns(2)

    with approve_column:
        if st.button(
            "✅ Approve Purchase",
            key=f"approve_{st.session_state['thread_id']}",
            type="primary",
            use_container_width=True,
        ):
            resume_hitl_execution("yes")

    with reject_column:
        if st.button(
            "❌ Reject Purchase",
            key=f"reject_{st.session_state['thread_id']}",
            use_container_width=True,
        ):
            resume_hitl_execution("no")


def _process_uploaded_pdf(uploaded_pdf) -> None:
    temporary_file_path = None
    logger.info("PDF upload received | name=%s", uploaded_pdf.name)

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temporary_file:
            temporary_file.write(uploaded_pdf.getvalue())
            temporary_file_path = temporary_file.name

        with st.spinner(f"Processing {uploaded_pdf.name}..."):
            ingest_rag_document(temporary_file_path)

        st.toast(
            f"{uploaded_pdf.name} processed successfully.",
            icon="✅",
        )
        logger.info("PDF upload processed | name=%s", uploaded_pdf.name)

    except Exception as error:
        logger.exception("PDF upload failed | name=%s", uploaded_pdf.name)
        st.error(f"PDF processing failed: {error}")

    finally:
        if temporary_file_path and os.path.exists(temporary_file_path):
            os.remove(temporary_file_path)


def _stream_assistant_response(user_input: str):
    thread_id = st.session_state["thread_id"]
    config = {
        "configurable": {
            "thread_id": thread_id,
        },
        "metadata": {
            "thread_id": thread_id,
        },
        "run_name": "chat_trace",
    }
    logger.info(
        "Streaming assistant response | thread_id=%s | input=%s",
        thread_id,
        user_input[:120],
    )

    with st.chat_message("assistant"):
        status_holder = {"box": None}

        def ai_only_stream():
            for message_chunk, metadata in chatbot.stream(
                {
                    "messages": [
                        HumanMessage(content=user_input),
                    ]
                },
                config=config,
                stream_mode="messages",
            ):
                if isinstance(message_chunk, ToolMessage):
                    tool_name = getattr(message_chunk, "name", "tool")
                    logger.info("Tool message received | tool=%s", tool_name)

                    if status_holder["box"] is None:
                        status_holder["box"] = st.status(
                            f"🔧 Using `{tool_name}` …",
                            expanded=True,
                        )
                    else:
                        status_holder["box"].update(
                            label=f"🔧 Using `{tool_name}` …",
                            state="running",
                            expanded=True,
                        )

                if isinstance(message_chunk, AIMessage):
                    yield message_chunk.content

            pending_interrupt = get_pending_interrupt(thread_id)

            if pending_interrupt is not None:
                logger.info("HITL interrupt detected | thread_id=%s", thread_id)
                save_pending_interrupt(thread_id, pending_interrupt)
                yield (
                    "\n\n⚠️ This stock purchase requires your approval. "
                    "Use the Approve Purchase or Reject Purchase "
                    "button below."
                )

        ai_message = st.write_stream(ai_only_stream())

        if status_holder["box"] is not None:
            if get_pending_interrupt(thread_id) is not None:
                status_holder["box"].update(
                    label="⏸️ Waiting for human approval",
                    state="complete",
                    expanded=False,
                )
            else:
                status_holder["box"].update(
                    label="✅ Tool finished",
                    state="complete",
                    expanded=False,
                )

    logger.info("Assistant stream finished | thread_id=%s", thread_id)
    return ai_message


def handle_chat_input() -> None:
    submission = st.chat_input(
        "Type here",
        accept_file=True,
        file_type=["pdf"],
        disabled=current_thread_has_pending_hitl(),
    )

    user_input = None

    if submission:
        user_input = submission.text
        uploaded_files = submission.files

        if uploaded_files:
            _process_uploaded_pdf(uploaded_files[0])

    if not user_input:
        return

    st.session_state["message_history"].append(
        {
            "role": "user",
            "content": user_input,
        }
    )

    with st.chat_message("user"):
        st.text(user_input)

    ai_message = _stream_assistant_response(user_input)

    st.session_state["message_history"].append(
        {
            "role": "assistant",
            "content": ai_message,
        }
    )

    if (
        st.session_state.get("pending_hitl") is not None
        and st.session_state["pending_hitl"].get("thread_id")
        == st.session_state["thread_id"]
    ):
        st.rerun()
